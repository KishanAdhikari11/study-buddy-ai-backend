from sqlalchemy.ext.asyncio import AsyncAttrs
from sqlalchemy.orm import DeclarativeBase,Mapped, mapped_column
import uuid
from sqlalchemy import Uuid, String,DateTime, ForeignKey
from datetime import datetime


class Base(AsyncAttrs, DeclarativeBase):
    """Base class for all models."""

    pass

class User(Base):
    __tablename__="users"
    id: Mapped[uuid.UUID]=mapped_column(Uuid(as_uuid=True),primary_key=True, nullable=False)
    name: Mapped[str]=mapped_column(String(100))
    email: Mapped[str]=mapped_column(String(120))
    created_at: Mapped[datetime]=mapped_column(DateTime, default=datetime.now)

    def __repr__(self):
        return f"<User: {self.name}>"


class FlashCard(Base):
    __tablename__="flashcards"
    id:Mapped[uuid.UUID]=mapped_column(Uuid(as_uuid=True),primary_key=True,nullable=False)
    user_id: Mapped[uuid.UUID]=mapped_column(Uuid(as_uuid=True),ForeignKey("users.id"))
    question: Mapped[str] = mapped_column(String)
    answer:Mapped[str]=mapped_column(String)
    explanation: Mapped[str]= mapped_column(String)
    created_at: Mapped[datetime]=mapped_column(DateTime, default=datetime.now)

    def __repr__(self):
        return f"<Flashcard: {self.question}>"

class Quiz(Base):
    __tablename__="quizzes"
    id:Mapped[uuid.UUID]=mapped_column(Uuid(as_uuid=True),primary_key=True,nullable=False)
    user_id: Mapped[uuid.UUID]=mapped_column(Uuid(as_uuid=True),ForeignKey("users.id"))
    question: Mapped[str] = mapped_column(String)
    Option_1:Mapped[str]=mapped_column(String)
    Option_2:Mapped[str]=mapped_column(String)
    Option_3:Mapped[str]=mapped_column(String)
    Option_4:Mapped[str]=mapped_column(String)
    explanation:Mapped[str]=mapped_column(String)
    created_at: Mapped[datetime]=mapped_column(DateTime, default=datetime.now)
    def __repr__(self):
        return f"<Quiz: {self.question}>"

    

        