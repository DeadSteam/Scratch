import uuid

from sqlalchemy import UUID
from sqlalchemy.orm import Mapped, mapped_column

from ..core.database import Base

__all__ = ["Base", "UUIDBase"]


class UUIDBase(Base):  # type: ignore[misc]
    """Base class for all models with UUID primary key."""

    __abstract__ = True

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
