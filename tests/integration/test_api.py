"""Integration tests for API endpoints."""

import os
import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, Mock

from src.api.server import app
from src.models.database import Base, get_db, ProcessingStatus
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool


# Create test database - use in-memory SQLite
engine = create_engine(
    "sqlite:///:memory:",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# Override the get_db dependency
def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(scope="function")
def client():
    """Create a test client."""
    Base.metadata.create_all(bind=engine)
    with TestClient(app) as c:
        yield c
    Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def db():
    """Create a database session for tests that need direct DB access."""
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


class TestHealthEndpoint:
    """Tests for the health check endpoint."""

    def test_health_check(self, client):
        """Test health endpoint returns healthy status."""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["service"] == "pmcursor"


class TestProjectsAPI:
    """Tests for project-related endpoints."""

    def test_create_project(self, client, db):
        """Test creating a new project."""
        response = client.post(
            "/api/projects",
            params={"name": "Test Project", "description": "A test project"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Test Project"
        assert data["description"] == "A test project"
        assert "id" in data

    def test_list_projects_empty(self, client):
        """Test listing projects when none exist."""
        response = client.get("/api/projects")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 0

    def test_list_projects_with_data(self, client, db):
        """Test listing projects with data."""
        # Create a project first
        response = client.post(
            "/api/projects", params={"name": "Project 1", "description": "Desc 1"}
        )
        assert response.status_code == 200

        # List projects
        response = client.get("/api/projects")
        assert response.status_code == 200
        data = response.json()
        assert len(data) >= 1
        assert any(p["name"] == "Project 1" for p in data)


class TestUploadsAPI:
    """Tests for file upload endpoints."""

    def test_upload_file_invalid_type(self, client, db):
        """Test uploading an invalid file type."""
        # Create a project first
        response = client.post(
            "/api/projects",
            params={"name": "Upload Test Project", "description": "Test"},
        )
        project_id = response.json()["id"]

        # Try to upload an invalid file
        response = client.post(
            f"/api/projects/{project_id}/uploads",
            files={"file": ("test.py", b"print('hello')", "text/plain")},
        )
        assert response.status_code == 400
        assert "File type not allowed" in response.json()["detail"]

    def test_upload_file_valid_txt(self, client, db, tmp_path):
        """Test uploading a valid text file."""
        # Create a project
        response = client.post(
            "/api/projects", params={"name": "Text Upload Test", "description": "Test"}
        )
        project_id = response.json()["id"]

        # Create test file
        test_content = "This is test content for analysis."
        response = client.post(
            f"/api/projects/{project_id}/uploads",
            files={"file": ("test.txt", test_content.encode(), "text/plain")},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["filename"] == "test.txt"
        assert data["status"] == "pending"
        assert "id" in data

    def test_upload_file_valid_json(self, client, db):
        """Test uploading a valid JSON file."""
        response = client.post(
            "/api/projects", params={"name": "JSON Upload Test", "description": "Test"}
        )
        project_id = response.json()["id"]

        test_content = '{"key": "value", "array": [1, 2, 3]}'
        response = client.post(
            f"/api/projects/{project_id}/uploads",
            files={"file": ("data.json", test_content.encode(), "application/json")},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["filename"] == "data.json"

    def test_upload_file_nonexistent_project(self, client):
        """Test uploading to a non-existent project."""
        response = client.post(
            "/api/projects/999/uploadss",
            files={"file": ("test.txt", b"content", "text/plain")},
        )
        # Should get project not found error
        assert response.status_code in [404, 422]

    def test_list_uploads(self, client, db):
        """Test listing project uploads."""
        # Create project and upload
        response = client.post(
            "/api/projects", params={"name": "List Uploads Test", "description": "Test"}
        )
        project_id = response.json()["id"]

        # Initially should be empty
        response = client.get(f"/api/projects/{project_id}/uploads")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 0

        # Upload a file
        client.post(
            f"/api/projects/{project_id}/uploads",
            files={"file": ("test1.txt", b"content1", "text/plain")},
        )

        # Should now have one upload
        response = client.get(f"/api/projects/{project_id}/uploads")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["filename"] == "test1.txt"


class TestAnalysisAPI:
    """Tests for analysis endpoints."""

    @patch("src.api.routes.feature_proposer")
    def test_analyze_project_success(self, mock_proposer, client, db):
        """Test successful project analysis."""
        # Mock the feature proposer
        mock_proposal = {
            "title": "Recommended Feature",
            "description": "A recommended feature based on data",
            "justification": "Customer feedback indicates need",
            "ui_changes": "Add dashboard widget",
            "data_model_changes": "Add metrics table",
            "workflow_changes": "Daily metrics review",
            "priority": "high",
            "tasks": [
                {
                    "title": "Create backend API",
                    "description": "Implement metrics endpoint",
                    "task_type": "backend",
                    "estimated_hours": 4,
                }
            ],
        }
        mock_proposer.generate_proposal.return_value = mock_proposal

        # Create project
        response = client.post(
            "/api/projects",
            params={"name": "Analysis Test Project", "description": "Test"},
        )
        project_id = response.json()["id"]

        # Upload a file
        client.post(
            f"/api/projects/{project_id}/uploads",
            files={
                "file": (
                    "feedback.txt",
                    b"Customers want metrics dashboard",
                    "text/plain",
                )
            },
        )

        # Run analysis
        response = client.post(
            f"/api/projects/{project_id}/analyze",
            params={"query": "What should we build next?"},
        )
        assert response.status_code == 200
        data = response.json()
        assert "analysis_id" in data
        assert "feature" in data
        assert data["feature"]["title"] == "Recommended Feature"
        assert len(data["feature"]["tasks"]) == 1

    def test_analyze_project_no_data(self, client, db):
        """Test analysis with no uploaded data."""
        # Create project without uploads
        response = client.post(
            "/api/projects", params={"name": "No Data Project", "description": "Test"}
        )
        project_id = response.json()["id"]

        # Try to analyze without data
        response = client.post(
            f"/api/projects/{project_id}/analyze",
            params={"query": "What should we build?"},
        )
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "No data" in data["message"]

    def test_analyze_nonexistent_project(self, client):
        """Test analyzing a non-existent project."""
        response = client.post(
            "/api/projects/999/analyze", params={"query": "What should we build?"}
        )
        assert response.status_code == 404

    @patch("src.api.routes.feature_proposer")
    def test_analyze_project_api_error(self, mock_proposer, client, db):
        """Test analysis when proposer returns an error."""
        mock_proposer.generate_proposal.return_value = {
            "error": "OpenAI API error",
            "title": "Analysis failed",
            "tasks": [],
        }

        response = client.post(
            "/api/projects",
            params={"name": "Error Test Project", "description": "Test"},
        )
        project_id = response.json()["id"]

        client.post(
            f"/api/projects/{project_id}/uploads",
            files={"file": ("test.txt", b"content", "text/plain")},
        )

        response = client.post(
            f"/api/projects/{project_id}/analyze",
            params={"query": "What should we build?"},
        )
        assert response.status_code == 500

    def test_list_analyses(self, client, db):
        """Test listing analyses for a project."""
        # Create project
        response = client.post(
            "/api/projects",
            params={"name": "List Analyses Test", "description": "Test"},
        )
        project_id = response.json()["id"]

        # Initially should be empty
        response = client.get(f"/api/projects/{project_id}/analyses")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 0
