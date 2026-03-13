from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    DateTime,
    ForeignKey,
    Enum as SQLEnum,
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy import create_engine
from datetime import datetime
import enum
from src.config import settings


Base = declarative_base()


# Database engine and session factory
DATABASE_URL = settings.database_url
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {},
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    """Dependency for database sessions."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


class ProcessingStatus(str, enum.Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class Project(Base):
    """Represents a product project with uploaded data."""

    __tablename__ = "projects"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    description = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    uploads = relationship(
        "Upload", back_populates="project", cascade="all, delete-orphan"
    )
    analyses = relationship(
        "Analysis", back_populates="project", cascade="all, delete-orphan"
    )


class Upload(Base):
    """Represents an uploaded file (interview, usage data, etc.)."""

    __tablename__ = "uploads"

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"))
    filename = Column(String(255), nullable=False)
    file_path = Column(String(500), nullable=False)
    file_type = Column(String(50))  # pdf, txt, csv, json, etc.
    uploaded_at = Column(DateTime, default=datetime.utcnow)
    status = Column(SQLEnum(ProcessingStatus), default=ProcessingStatus.PENDING)

    project = relationship("Project", back_populates="uploads")


class Analysis(Base):
    """Represents an analysis run that generates feature recommendations."""

    __tablename__ = "analyses"

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"))
    query = Column(Text, nullable=False)  # e.g., "what should we build next?"
    summary = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    status = Column(SQLEnum(ProcessingStatus), default=ProcessingStatus.PENDING)

    project = relationship("Project", back_populates="analyses")
    features = relationship(
        "FeatureProposal", back_populates="analysis", cascade="all, delete-orphan"
    )


class FeatureProposal(Base):
    """Represents a proposed feature with UI, data model, and workflow changes."""

    __tablename__ = "feature_proposals"

    id = Column(Integer, primary_key=True, index=True)
    analysis_id = Column(Integer, ForeignKey("analyses.id"))
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=False)
    justification = Column(Text)  # Based on customer feedback
    ui_changes = Column(Text)  # Proposed UI modifications
    data_model_changes = Column(Text)  # Proposed data model changes
    workflow_changes = Column(Text)  # Proposed workflow changes
    priority = Column(String(20), default="medium")  # high, medium, low

    analysis = relationship("Analysis", back_populates="features")
    tasks = relationship(
        "DevelopmentTask", back_populates="feature", cascade="all, delete-orphan"
    )


class DevelopmentTask(Base):
    """Represents a development task for implementing a feature."""

    __tablename__ = "development_tasks"

    id = Column(Integer, primary_key=True, index=True)
    feature_id = Column(Integer, ForeignKey("feature_proposals.id"))
    title = Column(String(200), nullable=False)
    description = Column(Text)
    task_type = Column(String(50))  # backend, frontend, database, etc.
    estimated_hours = Column(Integer)
    dependencies = Column(Text)  # Comma-separated task IDs

    feature = relationship("FeatureProposal", back_populates="tasks")
