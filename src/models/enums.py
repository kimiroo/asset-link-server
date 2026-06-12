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