import uuid
from uuid import UUID
from typing import List, Sequence, Tuple
from redis.asyncio import Redis
from sqlalchemy import select, or_
from sqlalchemy.ext.asyncio import AsyncSession

from src.models import User, Directory, Scope, ScopeAccessControl
from src.infrastructure.redis import auth_cache_redis


class AuthCacheService:
    def __init__(self, redis_client: Redis = auth_cache_redis) -> None:
        self.redis = redis_client
        self.redis_prefix = "auth:ws"

    def _get_redis_keys(self, workspace_id: UUID, user_id: UUID) -> Tuple[str, str]:
        """Isolate keys by workspace_id and separate access from inheritance scopes."""
        base_key = f"{self.redis_prefix}:{workspace_id}:user:{user_id}"
        return f"{base_key}:available_scopes", f"{base_key}:parent_scopes"

    async def build_and_cache_user_scopes(
        self,
        db: AsyncSession,
        user_id: UUID,
        workspace_id: UUID
    ) -> Tuple[List[str], List[str]]:
        """Flatten hierarchies and atomically cache both child access and parent inheritance scopes."""

        # 1. Recursive CTE: Fetch all sub-directories for the user
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

        # 2. Top-Down Recursive CTE: Fetch accessible descendant scopes
        scope_anchor = select(ScopeAccessControl.scope_id).where(
            ScopeAccessControl.workspace_id == workspace_id,
            or_(
                ScopeAccessControl.user_id == user_id,
                ScopeAccessControl.directory_id.in_(select(user_dirs_cte.c.id))
            )
        )
        accessible_scopes_cte = scope_anchor.cte(name="accessible_scopes", recursive=True)

        scope_child_recursive = select(Scope.id).join(
            accessible_scopes_cte,
            Scope.parent_id == accessible_scopes_cte.c.scope_id
        )
        accessible_scopes_cte = accessible_scopes_cte.union_all(scope_child_recursive)

        # 3. Bottom-Up Recursive CTE: Fetch ancestor scopes for inheritance
        # Seed with parent_ids of the discovered accessible scopes and traverse upward
        parent_anchor = (
            select(Scope.parent_id)
            .select_from(Scope)
            .where(Scope.id.in_(select(accessible_scopes_cte.c.scope_id)))
        )
        parent_scopes_cte = parent_anchor.cte(name="parent_scopes", recursive=True)

        scope_parent_recursive = select(Scope.parent_id).join(
            parent_scopes_cte,
            Scope.id == parent_scopes_cte.c.parent_id
        )
        parent_scopes_cte = parent_scopes_cte.union_all(scope_parent_recursive)

        # 4. Execute Queries and Map to String Lists
        # 4-1. Map data access scope IDs (Top-Down results)
        stmt_available = select(accessible_scopes_cte.c.scope_id).distinct()
        res_available = await db.scalars(stmt_available)
        uids_available: Sequence[uuid.UUID] = res_available.all()
        available_uuids: List[str] = [str(uid) for uid in uids_available]

        # 4-2. Map configuration inheritance scope IDs (Bottom-Up results, excluding Root parents)
        stmt_parent = select(parent_scopes_cte.c.parent_id).where(parent_scopes_cte.c.parent_id.is_not(None)).distinct()
        res_parent = await db.scalars(stmt_parent)
        uids_parent: Sequence[uuid.UUID] = res_parent.all()
        parent_uuids: List[str] = [str(uid) for uid in uids_parent]

        # 5. Atomic Redis Pipeline with Temporary Key Swapping
        avail_key, parent_key = self._get_redis_keys(workspace_id, user_id)
        tmp_avail_key = f"{avail_key}:tmp"
        tmp_parent_key = f"{parent_key}:tmp"

        async with self.redis.pipeline(transaction=True) as pipe:  # pyright: ignore[reportUnknownMemberType]
            # 5-1. Process Available Scopes
            if available_uuids:
                pipe.unlink(tmp_avail_key)
                chunk_size = 500
                for i in range(0, len(available_uuids), chunk_size):
                    pipe.sadd(tmp_avail_key, *available_uuids[i:i + chunk_size])
                pipe.expire(tmp_avail_key, 3600)
                pipe.rename(tmp_avail_key, avail_key)
            else:
                pipe.unlink(avail_key)

            # 5-2. Process Parent Scopes
            if parent_uuids:
                pipe.unlink(tmp_parent_key)
                chunk_size = 500
                for i in range(0, len(parent_uuids), chunk_size):
                    pipe.sadd(tmp_parent_key, *parent_uuids[i:i + chunk_size])
                pipe.expire(tmp_parent_key, 3600)
                pipe.rename(tmp_parent_key, parent_key)
            else:
                pipe.unlink(parent_key)

            # Commit pipeline operations atomically
            await pipe.execute()

        return available_uuids, parent_uuids

    async def clear_user_cache(self, workspace_id: UUID, user_id: UUID) -> None:
        """Evict both cache groups asynchronously on permission changes or logout."""
        avail_key, parent_key = self._get_redis_keys(workspace_id, user_id)
        await self.redis.unlink(
            avail_key, f"{avail_key}:tmp",
            parent_key, f"{parent_key}:tmp"
        )