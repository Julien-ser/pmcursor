"""Tests for database models and operations."""

import pytest
from datetime import datetime

from src.models.database import (
    Base,
    Project,
    Upload,
    Analysis,
    FeatureProposal,
    DevelopmentTask,
    ProcessingStatus,
    get_db,
)


class TestDatabaseModels:
    """Test suite for database models."""

    def test_project_creation(self, db):
        """Test creating a project."""
        project = Project(name="Test Project", description="Test description")
        db.add(project)
        db.commit()
        db.refresh(project)

        assert project.id is not None
        assert project.name == "Test Project"
        assert project.description == "Test description"
        assert project.created_at is not None
        assert project.updated_at is not None

    def test_project_relationships(self, db, sample_project):
        """Test project relationships with uploads and analyses."""
        # Create uploads
        upload1 = Upload(
            project_id=sample_project.id,
            filename="file1.txt",
            file_path="/path/to/file1.txt",
            file_type="txt",
        )
        upload2 = Upload(
            project_id=sample_project.id,
            filename="file2.pdf",
            file_path="/path/to/file2.pdf",
            file_type="pdf",
        )
        db.add_all([upload1, upload2])
        db.commit()

        # Create analysis
        analysis = Analysis(
            project_id=sample_project.id,
            query="What should we build?",
            status=ProcessingStatus.COMPLETED,
            summary="Analysis complete",
        )
        db.add(analysis)
        db.commit()

        # Refresh project to load relationships
        db.refresh(sample_project)

        # Check relationships
        assert len(sample_project.uploads) == 2
        assert len(sample_project.analyses) == 1
        assert sample_project.uploads[0].filename in ["file1.txt", "file2.pdf"]
        assert sample_project.analyses[0].query == "What should we build?"

    def test_upload_creation(self, db, sample_project):
        """Test creating an upload."""
        upload = Upload(
            project_id=sample_project.id,
            filename="test.pdf",
            file_path="/path/to/test.pdf",
            file_type="pdf",
            status=ProcessingStatus.PENDING,
        )
        db.add(upload)
        db.commit()
        db.refresh(upload)

        assert upload.id is not None
        assert upload.project_id == sample_project.id
        assert upload.filename == "test.pdf"
        assert upload.file_type == "pdf"
        assert upload.uploaded_at is not None

    def test_upload_status_enum(self, db, sample_project):
        """Test upload status can be set to enum values."""
        for status in ProcessingStatus:
            upload = Upload(
                project_id=sample_project.id,
                filename=f"test_{status.value}.txt",
                file_path="/path/to/test.txt",
                file_type="txt",
                status=status,
            )
            db.add(upload)
            db.commit()
            db.refresh(upload)
            assert upload.status == status

    def test_analysis_creation(self, db, sample_project):
        """Test creating an analysis."""
        analysis = Analysis(
            project_id=sample_project.id,
            query="What features should we add?",
            status=ProcessingStatus.PROCESSING,
        )
        db.add(analysis)
        db.commit()
        db.refresh(analysis)

        assert analysis.id is not None
        assert analysis.project_id == sample_project.id
        assert analysis.query == "What features should we add?"
        assert analysis.status == ProcessingStatus.PROCESSING
        assert analysis.created_at is not None

    def test_feature_proposal_creation(self, db, sample_analysis):
        """Test creating a feature proposal."""
        feature = FeatureProposal(
            analysis_id=sample_analysis.id,
            title="New Dashboard",
            description="A comprehensive dashboard",
            justification="Users requested it",
            ui_changes="Add widgets",
            data_model_changes="Add metrics table",
            workflow_changes="Enable daily views",
            priority="high",
        )
        db.add(feature)
        db.commit()
        db.refresh(feature)

        assert feature.id is not None
        assert feature.analysis_id == sample_analysis.id
        assert feature.title == "New Dashboard"
        assert feature.priority == "high"

    def test_development_task_creation(self, db, sample_feature):
        """Test creating a development task."""
        task = DevelopmentTask(
            feature_id=sample_feature.id,
            title="Implement API",
            description="Create REST endpoint",
            task_type="backend",
            estimated_hours=8,
        )
        db.add(task)
        db.commit()
        db.refresh(task)

        assert task.id is not None
        assert task.feature_id == sample_feature.id
        assert task.title == "Implement API"
        assert task.task_type == "backend"
        assert task.estimated_hours == 8

    def test_cascade_delete_project(self, db, sample_project):
        """Test that deleting a project cascades to related records."""
        # Create upload and analysis
        upload = Upload(
            project_id=sample_project.id,
            filename="test.txt",
            file_path="/path/test.txt",
            file_type="txt",
        )
        analysis = Analysis(project_id=sample_project.id, query="Test query")
        db.add_all([upload, analysis])
        db.commit()

        upload_id = upload.id
        analysis_id = analysis.id

        # Delete project
        db.delete(sample_project)
        db.commit()

        # Check that related records are deleted
        assert db.query(Upload).filter(Upload.id == upload_id).first() is None
        assert db.query(Analysis).filter(Analysis.id == analysis_id).first() is None

    def test_cascade_delete_feature(self, db, sample_feature):
        """Test that deleting a feature cascades to tasks."""
        task = DevelopmentTask(
            feature_id=sample_feature.id,
            title="Task 1",
            description="Description",
            task_type="frontend",
            estimated_hours=4,
        )
        db.add(task)
        db.commit()
        db.refresh(task)

        task_id = task.id
        feature_id = sample_feature.id

        # Delete feature
        db.delete(sample_feature)
        db.commit()

        # Check task is deleted
        assert (
            db.query(DevelopmentTask).filter(DevelopmentTask.id == task_id).first()
            is None
        )
        assert (
            db.query(FeatureProposal).filter(FeatureProposal.id == feature_id).first()
            is None
        )

    def test_full_feature_chain(self, db, sample_project):
        """Test full chain: Project -> Analysis -> Feature -> Tasks."""
        # Create analysis
        analysis = Analysis(
            project_id=sample_project.id,
            query="What should we build?",
            status=ProcessingStatus.COMPLETED,
        )
        db.add(analysis)
        db.commit()
        db.refresh(analysis)

        # Create feature
        feature = FeatureProposal(
            analysis_id=analysis.id,
            title="Feature X",
            description="Description X",
            priority="high",
        )
        db.add(feature)
        db.commit()
        db.refresh(feature)

        # Create tasks
        tasks = [
            DevelopmentTask(
                feature_id=feature.id,
                title=f"Task {i}",
                description=f"Description {i}",
                task_type="backend" if i % 2 == 0 else "frontend",
                estimated_hours=i * 2,
            )
            for i in range(1, 4)
        ]
        db.add_all(tasks)
        db.commit()

        # Verify relationships
        db.refresh(feature)
        assert len(feature.tasks) == 3
        assert feature.analysis.query == "What should we build?"
        assert feature.analysis.project.name == "Test Project"
