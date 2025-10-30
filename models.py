import uuid
from datetime import datetime


from sqlalchemy.ext.asyncio import AsyncAttrs
from  sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID




class Base(AsyncAttrs, DeclarativeBase):
    """Base class for all models."""
    pass

