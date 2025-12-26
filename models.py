import uuid
from datetime import datetime, timezone
from enum import Enum

from sqlalchemy import DateTime, ForeignKey, String, Uuid
from sqlalchemy import Enum as SqlEnum
from sqlalchemy.ext.asyncio import AsyncAttrs
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(AsyncAttrs, DeclarativeBase):
    pass


class FileType(str, Enum):
    Pdf = "pdf"
    Ppt = "ppt"
    Docx = "docx"
    Pptx = "pptx"


class ProviderType(str, Enum):
    Google = "google"
    Email = "email"


class User(Base):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4, nullable=False
    )
    supabase_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), unique=True, nullable=False
    )
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    email: Mapped[str] = mapped_column(String(120), unique=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    flashcards: Mapped[list["FlashCard"]] = relationship(
        back_populates="user",
        cascade="all, delete-orphan",
    )
    quizzes: Mapped[list["Quiz"]] = relationship(
        back_populates="user",
        cascade="all, delete-orphan",
    )
    files: Mapped[list["File"]] = relationship(
        back_populates="user",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        return f"<User id={self.id} name='{self.name}'>"


class AuthProvider(Base):
    __tablename__ = "auth_providers"

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4, nullable=False
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )
    provider_type: Mapped[ProviderType] = mapped_column(
        SqlEnum(ProviderType), nullable=False
    )
    provider_id: Mapped[str] = mapped_column(String, nullable=False)

    user: Mapped["User"] = relationship(back_populates="auth_providers")

    def __repr__(self) -> str:
        return f"<AuthProvider id={self.id} provider_type='{self.provider_type}'>"


class File(Base):
    __tablename__ = "files"

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4, nullable=False
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    filename: Mapped[str] = mapped_column(String, nullable=False)
    filepath: Mapped[str] = mapped_column(
        String, nullable=False
    )  # supabase storage path
    uploaded_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    file_type: Mapped[FileType] = mapped_column(SqlEnum(FileType), nullable=False)

    user: Mapped["User"] = relationship(back_populates="files")

    def __repr__(self) -> str:
        return f"<File id={self.id} filename='{self.filename}'>"


class FlashCard(Base):
    __tablename__ = "flashcards"

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4, nullable=False
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    question: Mapped[str] = mapped_column(String, nullable=False)
    answer: Mapped[str] = mapped_column(String, nullable=False)
    explanation: Mapped[str] = mapped_column(String, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    user: Mapped["User"] = relationship(back_populates="flashcards")

    def __repr__(self) -> str:
        return f"<FlashCard id={self.id} question='{self.question[:50]}...'>"


class Quiz(Base):
    __tablename__ = "quizzes"

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4, nullable=False
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    question: Mapped[str] = mapped_column(String, nullable=False)
    option_1: Mapped[str] = mapped_column(String, nullable=False, name="Option_1")
    option_2: Mapped[str] = mapped_column(String, nullable=False, name="Option_2")
    option_3: Mapped[str] = mapped_column(String, nullable=False, name="Option_3")
    option_4: Mapped[str] = mapped_column(String, nullable=False, name="Option_4")
    correct_option: Mapped[int] = mapped_column(nullable=False)  # 1 to 4
    explanation: Mapped[str] = mapped_column(String, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    user: Mapped["User"] = relationship(back_populates="quizzes")

    def __repr__(self) -> str:
        return f"<Quiz id={self.id} question='{self.question[:50]}...'>"
