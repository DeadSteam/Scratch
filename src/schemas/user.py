from uuid import UUID

from pydantic import EmailStr, Field, field_validator

from .base import SchemaBase


class RoleRead(SchemaBase):
    id: UUID
    name: str


class RoleCreate(SchemaBase):
    name: str = Field(..., min_length=1, max_length=50, description="Role name")

    @field_validator("name")
    @classmethod
    def name_alphanumeric(cls, v: str) -> str:
        """Validate role name is alphanumeric with underscores."""
        if not v.replace("_", "").replace("-", "").isalnum():
            raise ValueError(
                "Role name must be alphanumeric (underscores and hyphens allowed)"
            )
        return v.lower()


class RoleUpdate(SchemaBase):
    name: str | None = Field(None, min_length=1, max_length=50)


class UserBase(SchemaBase):
    username: str = Field(..., min_length=3, max_length=50, description="Username")
    email: EmailStr
    is_active: bool | None = True


class UserCreate(UserBase):
    password: str = Field(..., min_length=8, description="User password")

    @field_validator("username")
    @classmethod
    def username_alphanumeric(cls, v: str) -> str:
        """Validate username is alphanumeric with underscores."""
        if not v.replace("_", "").isalnum():
            raise ValueError("Username must be alphanumeric (underscores allowed)")
        return v.lower()

    @field_validator("password")
    @classmethod
    def password_strength(cls, v: str) -> str:
        """Validate password strength."""
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters")
        if not any(c.isupper() for c in v):
            raise ValueError("Password must contain at least one uppercase letter")
        if not any(c.islower() for c in v):
            raise ValueError("Password must contain at least one lowercase letter")
        if not any(c.isdigit() for c in v):
            raise ValueError("Password must contain at least one digit")
        return v


class UserUpdate(SchemaBase):
    username: str | None = Field(None, min_length=3, max_length=50)
    email: EmailStr | None = None
    is_active: bool | None = None
    password: str | None = Field(None, min_length=8)

    @field_validator("password")
    @classmethod
    def password_strength(cls, v: str | None) -> str | None:
        """Validate password strength if provided."""
        if v is None:
            return v
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters")
        if not any(c.isupper() for c in v):
            raise ValueError("Password must contain at least one uppercase letter")
        if not any(c.islower() for c in v):
            raise ValueError("Password must contain at least one lowercase letter")
        if not any(c.isdigit() for c in v):
            raise ValueError("Password must contain at least one digit")
        return v


class UserRead(UserBase):
    id: UUID
    roles: list[RoleRead] = []

    model_config = {"from_attributes": True}
