from enum import Enum


class SubscriptionPlan(str, Enum):
    TRIAL = "trial"
    STARTER = "starter"
    BUSINESS = "business"
    ENTERPRISE = "enterprise"

class UserRole(str, Enum):
    OWNER = "owner"
    ADMIN = "admin"
    EDITOR = "editor"
    VIEWER = "viewer"

class ContactRole(str, Enum):
    OWNER = "owner"
    TENANT = "tenant"
    CO_OWNER = "co_owner"

class SourceType(str, Enum):
    AGENCY = "agency"
    WALK_IN = "walk_in"
    COLD_SOURCE = "cold_source"

class PriceType(str, Enum):
    SALE = "sale"
    JEONSE = "jeonse"
    RENT = "rent"
    RENT_SHORT = "rent_short"

class AccessControlType(str, Enum):
    ADMIN = "admin"
    WRITE = "write"
    READ = "read"

class CustomFieldType(str, Enum):
    STRING = "string"
    SELECT = "select"
    INT = "int"
    FLOAT = "float"
    BOOLEAN = "boolean"
    DATE = "date"

class AuditActionType(str, Enum):
    CREATE = "create"
    UPDATE = "update"
    DELETE = "delete"
    READ = "read"

class AuditTableName(str, Enum):
    AGENCY = "AGENCY"
    AGENT = "AGENT"
    ASSET = "ASSET"
    ASSET_PRICE_OPTION = "ASSET_PRICE_OPTION"
    ASSET_CONSULT_LOG = "ASSET_CONSULT_LOG"
    ASSET_CONTACT = "ASSET_CONTACT"
    AUDIT_LOG = "AUDIT_LOG"
    COMPLEX = "COMPLEX"
    UNIT_TYPE = "UNIT_TYPE"
    CONTACT = "CONTACT"
    CONTACT_PHONE = "CONTACT_PHONE"
    CONTACT_TAG = "CONTACT_TAG"
    CUSTOM_FIELD_DEFINITION = "CUSTOM_FIELD_DEFINITION"
    CUSTOM_FIELD_SCOPE = "CUSTOM_FIELD_SCOPE"
    DIRECTORY = "DIRECTORY"
    SCOPE_ACCESS_CONTROL = "SCOPE_ACCESS_CONTROL"
    SCOPE = "SCOPE"
    USER = "USER"
    WORKSPACE = "WORKSPACE"

    @property
    def table_name(self) -> str:
        """Lazy load models to return table names"""
        import src.models as models

        mapping = {
            AuditTableName.AGENCY: models.Agency.__tablename__,
            AuditTableName.AGENT: models.Agent.__tablename__,
            AuditTableName.ASSET: models.Asset.__tablename__,
            AuditTableName.ASSET_PRICE_OPTION: models.AssetPriceOption.__tablename__,
            AuditTableName.ASSET_CONSULT_LOG: models.AssetConsultLog.__tablename__,
            AuditTableName.ASSET_CONTACT: models.AssetContact.__tablename__,
            AuditTableName.AUDIT_LOG: models.AuditLog.__tablename__,
            AuditTableName.COMPLEX: models.Complex.__tablename__,
            AuditTableName.UNIT_TYPE: models.UnitType.__tablename__,
            AuditTableName.CONTACT: models.Contact.__tablename__,
            AuditTableName.CONTACT_PHONE: models.ContactPhone.__tablename__,
            AuditTableName.CONTACT_TAG: models.ContactTag.__tablename__,
            AuditTableName.CUSTOM_FIELD_DEFINITION: models.CustomFieldDefinition.__tablename__,
            AuditTableName.CUSTOM_FIELD_SCOPE: models.CustomFieldScope.__tablename__,
            AuditTableName.DIRECTORY: models.Directory.__tablename__,
            AuditTableName.SCOPE_ACCESS_CONTROL: models.ScopeAccessControl.__tablename__,
            AuditTableName.SCOPE: models.Scope.__tablename__,
            AuditTableName.USER: models.User.__tablename__,
            AuditTableName.WORKSPACE: models.Workspace.__tablename__,
        }

        return mapping[self]