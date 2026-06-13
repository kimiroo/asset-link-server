from uuid import UUID
from typing import List, Sequence
from redis.asyncio import Redis
from sqlalchemy import select, or_
from sqlalchemy.ext.asyncio import AsyncSession

from src.models import User, Directory, Scope, ScopeAccessControl
from src.infrastructure.redis import auth_cache_redis


class AuthCacheService:
    def __init__(self, redis_client: Redis = auth_cache_redis) -> None:
        self.redis = redis_client
        self.redis_prefix = "auth:ws"

    def _get_redis_key(self, workspace_id: UUID, user_id: UUID) -> str:
        """Isolate keys by workspace_id to prevent cross-tenant data pollution."""
        return f"{self.redis_prefix}:{workspace_id}:user:{user_id}:scopes"

    async def build_and_cache_user_scopes(
        self,
        db: AsyncSession,
        user_id: UUID,
        workspace_id: UUID
    ) -> List[str]:
        """Flatten hierarchies and atomically cache scopes with atmoic replace."""

        # 1. Recursive CTE: Fetch all sub-directories under the user's directory
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

        # 2. Recursive CTE: Inherit allowed scopes top-down from parent scopes
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

        # 3. Optimize memory overhead by using .scalars() instead of raw rows
        statement = select(scopes_cte.c.scope_id).distinct()
        result = await db.scalars(statement)
        uids: Sequence[UUID] = result.all()
        scope_uuids: List[str] = [str(uid) for uid in uids]

        # 4. Atomic Async Pipeline with Chunked Swapping
        redis_key = self._get_redis_key(workspace_id, user_id)
        tmp_key = f"{redis_key}:tmp"

        async with self.redis.pipeline(transaction=True) as pipe:  # pyright: ignore[reportUnknownMemberType]
            if scope_uuids:
                # Ensure the temporary key is clean before writing
                pipe.unlink(tmp_key)

                # Chunk payload to avoid Python argument unpacking limits and Redis memory spikes
                chunk_size = 500
                for i in range(0, len(scope_uuids), chunk_size):
                    pipe.sadd(tmp_key, *scope_uuids[i:i + chunk_size])

                # Atomically swap the temporary key to the target key
                pipe.expire(tmp_key, 3600)
                pipe.rename(tmp_key, redis_key)
            else:
                # Wipe out permission key on total revocation using non-blocking unlink
                pipe.unlink(redis_key)

            # Execute all pipeline operations atomically
            await pipe.execute()

        return scope_uuids

    async def clear_user_cache(self, workspace_id: UUID, user_id: UUID) -> None:
        """Evict cache asynchronously on permission changes or logout."""
        redis_key = self._get_redis_key(workspace_id, user_id)
        # Unlink both main and potential temporary keys to ensure full cleanup
        await self.redis.unlink(redis_key, f"{redis_key}:tmp")