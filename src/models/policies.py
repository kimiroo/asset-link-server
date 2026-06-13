from alembic_utils.pg_policy import PGPolicy


assets_policy = PGPolicy(
    schema="public",
    signature="assets_tenant_isolation_policy", # policy name
    on_entity="public.assets",                  # table name
    definition="""
        FOR ALL
        USING (workspace_id = NULLIF(current_setting('app.current_workspace_id', true), '')::uuid)
    """
)

contacts_policy = PGPolicy(
    schema="public",
    signature="contacts_tenant_isolation_policy",
    on_entity="public.contacts",
    definition="""
        FOR ALL
        USING (workspace_id = NULLIF(current_setting('app.current_workspace_id', true), '')::uuid)
    """
)

all_policies = [assets_policy, contacts_policy]