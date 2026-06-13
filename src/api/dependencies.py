from collections.abc import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.session import async_session_local
from src.db.extensions import SetLocal
# from src.api.auth import get_current_user  # TODO: Replace with dependency for user context

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency injector to provide async database sessions per request.
    Automatically injects the current user's RLS context into the session transaction.
    """
    # TODO: Replace with actual session context (workspace_id, scope_ids) once auth is integrated.
    # Temporary mock data for RLS testing
    current_workspace_id = "your-workspace-uuid"
    accessible_scope_ids = ["scope-uuid-1", "scope-uuid-2"]

    async with async_session_local() as session:
        try:
            # Set PostgreSQL local variables for Row-Level Security (RLS)
            await session.execute(SetLocal("app.current_workspace_id", current_workspace_id))

            # Format list as a PostgreSQL text array literal: {uuid1,uuid2}
            scopes_str = f"{{{','.join(accessible_scope_ids)}}}"
            await session.execute(SetLocal("app.accessible_scopes", scopes_str))

            yield session
        finally:
            await session.close()