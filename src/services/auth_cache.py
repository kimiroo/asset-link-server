from uuid import UUID

import redis
from sqlalchemy import select, or_
from sqlalchemy.ext.asyncio import AsyncSession

from src.models import User, Directory, Scope, ScopeAccessControl
from src.infrastructure.redis import auth_cache_redis


class AuthCacheService:
    def __init__(self, redis_client: redis.Redis = auth_cache_redis) -> None:
        self.redis = redis_client
        self.redis_prefix = "auth:user"

    def _get_redis_key(self, user_id: UUID) -> str:
        return f"{self.redis_prefix}:{user_id}:allowed_scopes"

    async def build_and_cache_user_scopes(
        self,
        db: AsyncSession,
        user_id: UUID,
        workspace_id: UUID
    ) -> list[str]:
        """Flatten organizational and scope hierarchies and cache them in Redis"""

        # 1. Recursive CTE for fetching user's all sub-directories
        dir_anchor = (
            select(Directory.id)
            .join(User, Directory.id == User.directory_id)
            .where(User.id == user_id)
        )
        user_dirs_cte = dir_anchor.cte(name="user_directories", recursive=True)

        dir_recursive = select(Directory.id).join(
            user_dirs_cte,
            Directory.parent_id == user_dirs_cte.c.id
        )
        user_dirs_cte = user_dirs_cte.union_all(dir_recursive)

        # 2. Recursive CTE for inheriting allowed scopes top-down
        scope_anchor = select(ScopeAccessControl.scope_id).where(
            ScopeAccessControl.workspace_id == workspace_id,
            or_(
                ScopeAccessControl.user_id == user_id,
                ScopeAccessControl.directory_id.in_(select(user_dirs_cte.c.id))
            )
        )
        scopes_cte = scope_anchor.cte(name="accessible_scopes", recursive=True)

        scope_recursive = select(Scope.id).join(
            scopes_cte,
            Scope.parent_id == scopes_cte.c.scope_id
        )
        scopes_cte = scopes_cte.union_all(scope_recursive)

        # 3. Execute and extract flat UUID list
        statement = select(scopes_cte.c.scope_id).distinct()
        result = await db.execute(statement)
        scope_uuids: list[str] = [
            str(row[0]) for row in result.fetchall() if row[0] is not None
        ]

        # 4. Atomic cache update via Redis Pipeline
        if scope_uuids:
            redis_key = self._get_redis_key(user_id)
            with self.redis.pipeline() as pipe: # pyright: ignore[reportUnknownMemberType]
                pipe.delete(redis_key)             # Prevent stale data
                pipe.sadd(redis_key, *scope_uuids) # Store as Redis Set
                pipe.expire(redis_key, 3600)       # 1-hour TTL safety net
                pipe.execute()

        return scope_uuids

    def clear_user_cache(self, user_id: UUID) -> None:
        """Evict cache immediately on permission changes or logout."""
        redis_key = self._get_redis_key(user_id)
        self.redis.delete(redis_key)