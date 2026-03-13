"""Pytest configuration and shared fixtures."""

import os
import tempfile
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from src.models.database import (
    Base,
    get_db,
    Project,
    Upload,
    Analysis,
    FeatureProposal,
    DevelopmentTask,
)
from src.storage.file_manager import FileManager
from src.core.data_processor import DataProcessor
from src.core.feature_proposer import FeatureProposer
from src.utils.helpers import is_allowed_file, truncate_text, format_output


# Test database setup
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    """Override the get_db dependency for testing."""
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


@pytest.fixture(scope="function")
def db():
    """Create a fresh database for each test."""
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def temp_upload_dir():
    """Create a temporary upload directory."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield tmpdir


@pytest.fixture(scope="function")
def file_manager(temp_upload_dir):
    """Create a FileManager instance with temp directory."""
    from src.config import Settings

    settings = Settings()
    settings.upload_dir = temp_upload_dir
    settings.data_dir = temp_upload_dir
    return FileManager()


@pytest.fixture(scope="function")
def data_processor(file_manager):
    """Create a DataProcessor instance."""
    return DataProcessor(file_manager)


@pytest.fixture(scope="function")
def feature_proposer():
    """Create a FeatureProposer instance."""
    return FeatureProposer()


@pytest.fixture(scope="function")
def sample_project(db):
    """Create a sample project for testing."""
    project = Project(name="Test Project", description="A test project")
    db.add(project)
    db.commit()
    db.refresh(project)
    return project


@pytest.fixture(scope="function")
def sample_upload(db, sample_project, temp_upload_dir):
    """Create a sample upload record."""
    upload = Upload(
        project_id=sample_project.id,
        filename="test.txt",
        file_path=os.path.join(temp_upload_dir, "test.txt"),
        file_type="txt",
        status="completed",
    )
    db.add(upload)
    db.commit()
    db.refresh(upload)
    return upload


@pytest.fixture(scope="function")
def sample_analysis(db, sample_project):
    """Create a sample analysis record."""
    analysis = Analysis(
        project_id=sample_project.id,
        query="What should we build next?",
        status="completed",
        summary="Test analysis summary",
    )
    db.add(analysis)
    db.commit()
    db.refresh(analysis)
    return analysis


@pytest.fixture(scope="function")
def sample_feature(db, sample_analysis):
    """Create a sample feature proposal."""
    feature = FeatureProposal(
        analysis_id=sample_analysis.id,
        title="Test Feature",
        description="A test feature",
        justification="Customer feedback",
        ui_changes="Add new button",
        data_model_changes="Add new table",
        workflow_changes="New workflow",
        priority="high",
    )
    db.add(feature)
    db.commit()
    db.refresh(feature)
    return feature


@pytest.fixture(scope="function")
def sample_task(db, sample_feature):
    """Create a sample development task."""
    task = DevelopmentTask(
        feature_id=sample_feature.id,
        title="Implement feature",
        description="Implement the test feature",
        task_type="backend",
        estimated_hours=8,
    )
    db.add(task)
    db.commit()
    db.refresh(task)
    return task
