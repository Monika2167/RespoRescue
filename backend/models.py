from datetime import datetime

from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship

from backend.database import Base


# =========================================================
# USER MODEL
# =========================================================
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)

    username = Column(
        String(100),
        unique=True,
        nullable=False,
        index=True
    )

    email = Column(
        String(255),
        unique=True,
        nullable=False,
        index=True
    )

    password_hash = Column(
        String(255),
        nullable=False
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow
    )

    # User -> Repositories
    repositories = relationship(
        "Repository",
        back_populates="owner",
        cascade="all, delete-orphan"
    )

    # User -> GitHub connection
    github_connection = relationship(
        "GitHubConnection",
        back_populates="user",
        uselist=False,
        cascade="all, delete-orphan"
    )


# =========================================================
# GITHUB CONNECTION MODEL
# =========================================================
class GitHubConnection(Base):
    __tablename__ = "github_connections"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    user_id = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=False,
        unique=True
    )

    github_user_id = Column(
        String(100),
        nullable=False
    )

    github_username = Column(
        String(255),
        nullable=False
    )

    # OAuth access token
    access_token = Column(
        Text,
        nullable=False
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow
    )

    updated_at = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow
    )

    # GitHubConnection -> User
    user = relationship(
        "User",
        back_populates="github_connection"
    )


# =========================================================
# REPOSITORY MODEL
# =========================================================
class Repository(Base):
    __tablename__ = "repositories"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    name = Column(
        String(255),
        nullable=False
    )

    github_url = Column(
        String(500),
        nullable=False
    )

    owner_id = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=False
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow
    )

    # Repository -> User
    owner = relationship(
        "User",
        back_populates="repositories"
    )

    # Repository -> Analyses
    analyses = relationship(
        "Analysis",
        back_populates="repository",
        cascade="all, delete-orphan"
    )


# =========================================================
# ANALYSIS MODEL
# =========================================================
class Analysis(Base):
    __tablename__ = "analyses"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    repository_id = Column(
        Integer,
        ForeignKey("repositories.id"),
        nullable=False
    )

    pr_number = Column(
        Integer,
        nullable=False
    )

    probability = Column(
        Float,
        nullable=True
    )

    prediction = Column(
        String(100),
        nullable=True
    )

    threshold = Column(
        Float,
        nullable=True
    )

    semantic_signal = Column(
        String(100),
        nullable=True
    )

    semantic_strength = Column(
        Float,
        nullable=True
    )

    top_evidence = Column(
        Text,
        nullable=True
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow
    )

    # Analysis -> Repository
    repository = relationship(
        "Repository",
        back_populates="analyses"
    )