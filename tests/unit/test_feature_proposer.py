"""Tests for FeatureProposer class."""

import json
from unittest.mock import Mock, patch
import pytest

from src.core.feature_proposer import FeatureProposer


class TestFeatureProposer:
    """Test suite for FeatureProposer."""

    def test_init(self):
        """Test FeatureProposer initialization."""
        proposer = FeatureProposer()
        assert proposer.client is not None

    @patch("src.core.feature_proposer.OpenAI")
    def test_generate_proposal_success(self, mock_openai, feature_proposer):
        """Test successful feature proposal generation."""
        # Mock the OpenAI response
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = json.dumps(
            {
                "title": "Test Feature",
                "description": "A test feature description",
                "justification": "Customer feedback shows demand",
                "ui_changes": "Add new button",
                "data_model_changes": "Add users table",
                "workflow_changes": "Enable new workflow",
                "priority": "high",
                "tasks": [
                    {
                        "title": "Backend task",
                        "description": "Implement backend",
                        "task_type": "backend",
                        "estimated_hours": 8,
                    }
                ],
            }
        )

        # Replace the client with the mock
        feature_proposer.client = mock_openai.return_value
        feature_proposer.client.chat.completions.create.return_value = mock_response

        result = feature_proposer.generate_proposal(
            "Sample context", "What should we build?"
        )

        assert result["title"] == "Test Feature"
        assert result["description"] == "A test feature description"
        assert result["priority"] == "high"
        assert len(result["tasks"]) == 1
        assert result["tasks"][0]["title"] == "Backend task"

    @patch("src.core.feature_proposer.OpenAI")
    def test_generate_proposal_with_markdown_json(self, mock_openai, feature_proposer):
        """Test parsing JSON from markdown code block."""
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = """
        ```json
        {
            "title": "Feature in code block",
            "description": "Description",
            "justification": "",
            "ui_changes": "",
            "data_model_changes": "",
            "workflow_changes": "",
            "priority": "medium",
            "tasks": []
        }
        ```
        """

        feature_proposer.client = mock_openai.return_value
        feature_proposer.client.chat.completions.create.return_value = mock_response

        result = feature_proposer.generate_proposal("Context", "Query")

        assert result["title"] == "Feature in code block"

    @patch("src.core.feature_proposer.OpenAI")
    def test_generate_proposal_invalid_json(self, mock_openai, feature_proposer):
        """Test handling invalid JSON response."""
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = "Not JSON at all"

        feature_proposer.client = mock_openai.return_value
        feature_proposer.client.chat.completions.create.return_value = mock_response

        result = feature_proposer.generate_proposal("Context", "Query")

        assert "error" in result
        assert "Could not extract JSON" in result["error"]
        assert result["title"] == "Analysis failed"

    @patch("src.core.feature_proposer.OpenAI")
    def test_generate_proposal_api_error(self, mock_openai, feature_proposer):
        """Test handling API errors."""
        feature_proposer.client = mock_openai.return_value
        feature_proposer.client.chat.completions.create.side_effect = Exception(
            "API Error"
        )

        result = feature_proposer.generate_proposal("Context", "Query")

        assert "error" in result
        assert "API Error" in result["error"]
        assert result["title"] == "Analysis failed"

    def test_generate_proposal_empty_context(self, feature_proposer):
        """Test proposal with empty context."""
        result = feature_proposer.generate_proposal("", "Query")

        # Should still return a valid structure with error or empty results
        assert "title" in result
        assert "description" in result
        assert "tasks" in result

    def test_generate_proposal_default_query(self, feature_proposer):
        """Test that default query is used when not provided."""
        with patch.object(
            feature_proposer.client.chat.completions, "create"
        ) as mock_create:
            mock_response = Mock()
            mock_response.choices = [Mock()]
            mock_response.choices[0].message.content = json.dumps(
                {
                    "title": "Default Query Test",
                    "description": "Test",
                    "justification": "",
                    "ui_changes": "",
                    "data_model_changes": "",
                    "workflow_changes": "",
                    "priority": "medium",
                    "tasks": [],
                }
            )
            mock_create.return_value = mock_response

            result = feature_proposer.generate_proposal("Context")

            # Check that the default query was used
            call_args = mock_create.call_args
            messages = call_args[1]["messages"]
            user_message = next(m for m in messages if m["role"] == "user")
            assert "What should we build next?" in user_message["content"]
