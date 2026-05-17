from datetime import datetime, UTC
from typing import List, Optional
from sqlalchemy import String, Text, Float, DateTime, ForeignKey, Integer, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.infrastructure.database import Base

class User(Base):
    __tablename__ = "users"
    
    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    # FIX: Use lambda for UTC-aware datetime in Python 3.12
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(UTC))
    
    # Relationships
    preferences: Mapped["UserPreference"] = relationship(back_populates="user", cascade="all, delete-orphan")
    weaknesses: Mapped[List["CodingWeakness"]] = relationship(back_populates="user", cascade="all, delete-orphan")
    solved_problems: Mapped[List["SolvedProblem"]] = relationship(back_populates="user", cascade="all, delete-orphan")
    memories: Mapped[List["Memory"]] = relationship(back_populates="user", cascade="all, delete-orphan")

class UserPreference(Base):
    __tablename__ = "user_preferences"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id"), unique=True)
    
    coding_level: Mapped[str] = mapped_column(String(50), default="beginner")
    preferred_languages: Mapped[list] = mapped_column(JSON, default=list)
    mentor_style: Mapped[str] = mapped_column(String(50), default="socratic")
    
    user: Mapped["User"] = relationship(back_populates="preferences")

class CodingWeakness(Base):
    __tablename__ = "coding_weaknesses"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id"), index=True)
    
    topic: Mapped[str] = mapped_column(String(100))
    description: Mapped[str] = mapped_column(Text)
    severity_score: Mapped[float] = mapped_column(Float, default=0.5)
    last_observed: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(UTC))
    
    user: Mapped["User"] = relationship(back_populates="weaknesses")

class SolvedProblem(Base):
    __tablename__ = "solved_problems"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id"), index=True)
    
    problem_title: Mapped[str] = mapped_column(String(200))
    difficulty: Mapped[str] = mapped_column(String(50))
    solved_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(UTC))
    key_learnings: Mapped[str] = mapped_column(Text, nullable=True)
    
    user: Mapped["User"] = relationship(back_populates="solved_problems")

class Memory(Base):
    __tablename__ = "memories"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id"), index=True)
    
    content: Mapped[str] = mapped_column(Text)
    content_hash: Mapped[str] = mapped_column(String(64), index=True)
    utility_score: Mapped[float] = mapped_column(Float, default=1.0)
    
    embedding_status: Mapped[str] = mapped_column(String(20), default="pending")
    
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(UTC))
    last_accessed: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(UTC))
    
    user: Mapped["User"] = relationship(back_populates="memories")
