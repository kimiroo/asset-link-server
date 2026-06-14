"""Row-Level Security (RLS) policies for core data tables.

Defines multi-tenant (workspace) and hierarchical (scope) isolation criteria
automatically bound to table creation events.
"""

import uuid
from typing import Any, cast as type_cast

from sqlalchemy import event, func
from sqlalchemy.engine import Connection
from sqlalchemy.schema import Table
from sqlalchemy.dialects.postgresql import UUID, ARRAY
from sqlalchemy.sql.expression import ColumnElement

from src.db.extensions import EnableRLS, CreatePolicy
from src.models.agency import Agency, Agent
from src.models.asset import Asset, AssetPriceOption, AssetConsultLog, AssetContact
from src.models.complex import Complex, UnitType
from src.models.contact import Contact, ContactPhone, ContactTag


# ==============================================================================
# RLS Criteria Definition
# ==============================================================================

# Map PostgreSQL session variables using strict type casting for UUID and ARRAY(UUID)
current_workspace = type_cast(
    ColumnElement[uuid.UUID],
    func.current_setting("app.current_workspace_id", True).cast(UUID)
)

accessible_scopes = type_cast(
    ColumnElement[list[uuid.UUID]],
    func.current_setting("app.accessible_scopes", True).cast(type_cast(Any, ARRAY(UUID)))
)

# ==============================================================================
# Dynamic RLS Policy Generator & Automated Event Bindings
# ==============================================================================

def apply_workspace_rls(target: Table, connection: Connection, policy_name: str) -> None:
    """
    Dynamically extracts the 'workspace_id' column from the specific target table
    to build and execute a valid PostgreSQL Row-Level Security policy.
    """
    # Dynamically extract the 'workspace_id' column from the target table
    target_workspace_id_col: Any = target.c.workspace_id

    # Build the isolation criteria using the extracted column
    dynamic_criterion: Any = (target_workspace_id_col == current_workspace)

    # Execute RLS enforcement and policy creation
    connection.execute(EnableRLS(target))
    connection.execute(CreatePolicy(policy_name, target, dynamic_criterion))


# ==============================================================================
# Automated Event Bindings
# ==============================================================================

@event.listens_for(Agency.__table__, "after_create")
def setup_agency_rls(target: Table, connection: Connection, **kw: Any) -> None:
    """Apply RLS and isolation policy to the 'agencies' table immediately after creation."""
    apply_workspace_rls(target, connection, "agency_isolation_policy")

@event.listens_for(Agent.__table__, "after_create")
def setup_agent_rls(target: Table, connection: Connection, **kw: Any) -> None:
    """Apply RLS and isolation policy to the 'agents' table immediately after creation."""
    apply_workspace_rls(target, connection, "agent_isolation_policy")

@event.listens_for(Asset.__table__, "after_create")
def setup_asset_rls(target: Table, connection: Connection, **kw: Any) -> None:
    """Apply RLS and isolation policy to the 'assets' table immediately after creation."""
    apply_workspace_rls(target, connection, "asset_isolation_policy")

@event.listens_for(AssetPriceOption.__table__, "after_create")
def setup_asset_price_option_rls(target: Table, connection: Connection, **kw: Any) -> None:
    """Apply RLS and isolation policy to the 'asset_price_options' table immediately after creation."""
    apply_workspace_rls(target, connection, "asset_price_option_isolation_policy")

@event.listens_for(AssetConsultLog.__table__, "after_create")
def setup_asset_consult_log_rls(target: Table, connection: Connection, **kw: Any) -> None:
    """Apply RLS and isolation policy to the 'asset_consult_log' table immediately after creation."""
    apply_workspace_rls(target, connection, "asset_consult_log_isolation_policy")

@event.listens_for(AssetContact.__table__, "after_create")
def setup_asset_contact_rls(target: Table, connection: Connection, **kw: Any) -> None:
    """Apply RLS and isolation policy to the 'asset_contacts' table immediately after creation."""
    apply_workspace_rls(target, connection, "asset_contact_isolation_policy")

@event.listens_for(Complex.__table__, "after_create")
def setup_complex_rls(target: Table, connection: Connection, **kw: Any) -> None:
    """Apply RLS and isolation policy to the 'complexes' table immediately after creation."""
    apply_workspace_rls(target, connection, "complex_isolation_policy")

@event.listens_for(UnitType.__table__, "after_create")
def setup_unit_type_rls(target: Table, connection: Connection, **kw: Any) -> None:
    """Apply RLS and isolation policy to the 'unit_types' table immediately after creation."""
    apply_workspace_rls(target, connection, "unit_type_isolation_policy")

@event.listens_for(Contact.__table__, "after_create")
def setup_contact_rls(target: Table, connection: Connection, **kw: Any) -> None:
    """Apply RLS and isolation policy to the 'contacts' table immediately after creation."""
    apply_workspace_rls(target, connection, "contact_isolation_policy")

@event.listens_for(ContactPhone.__table__, "after_create")
def setup_contact_phone_rls(target: Table, connection: Connection, **kw: Any) -> None:
    """Apply RLS and isolation policy to the 'contact_phones' table immediately after creation."""
    apply_workspace_rls(target, connection, "contact_phone_isolation_policy")

@event.listens_for(ContactTag.__table__, "after_create")
def setup_contact_tag_rls(target: Table, connection: Connection, **kw: Any) -> None:
    """Apply RLS and isolation policy to the 'contact_tags' table immediately after creation."""
    apply_workspace_rls(target, connection, "contact_tag_isolation_policy")
