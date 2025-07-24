from enum import Enum


class EnumUserRoles(str, Enum):
    ADMIN = "admin"
    OWNER = "owner"
    TENANT = "tenant"
