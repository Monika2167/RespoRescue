from datetime import datetime

from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship

from backend.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(100), unique=True, nullable=False, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    repositories = relationship(
        "Repository",
        back_populates="owner",
        cascade="all, delete-orphan"
    )


class Repository(Base):
    __tablename__ = "repositories"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    github_url = Column(String(500), nullable=False)
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    owner = relationship(
        "User",
        back_populates="repositories"
    )

    analyses = relationship(
        "Analysis",
        back_populates="repository",
        cascade="all, delete-orphan"
    )


class Analysis(Base):
    __tablename__ = "analyses"

    id = Column(Integer, primary_key=True, index=True)
    repository_id = Column(
        Integer,
        ForeignKey("repositories.id"),
        nullable=False
    )

    pr_number = Column(Integer, nullable=False)
    probability = Column(Float, nullable=True)
    prediction = Column(String(100), nullable=True)
    threshold = Column(Float, nullable=True)
    semantic_signal = Column(String(100), nullable=True)
    semantic_strength = Column(Float, nullable=True)
    top_evidence = Column(Text, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)

    repository = relationship(
        "Repository",
        back_populates="analyses"
    )