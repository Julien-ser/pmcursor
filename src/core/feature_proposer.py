"""Core module for feature proposal generation."""

from openai import OpenAI
from src.config import settings


class FeatureProposer:
    """Generates feature proposals using AI analysis."""

    def __init__(self):
        self.client = OpenAI(api_key=settings.openai_api_key)

    def generate_proposal(
        self, context_text: str, query: str = "What should we build next?"
    ) -> dict:
        """Generate a feature proposal based on the provided context."""
        system_prompt = """You are an expert product manager and AI assistant.
        Based on the provided customer interviews and product usage data, analyze the information
        and generate a comprehensive feature proposal.

        Respond with a JSON object containing:
        {
            "title": "Feature title",
            "description": "Detailed feature description",
            "justification": "Why this feature based on customer feedback",
            "ui_changes": "Specific UI/UX changes needed",
            "data_model_changes": "Database/data structure modifications",
            "workflow_changes": "How user workflows would change",
            "priority": "high|medium|low",
            "tasks": [
                {
                    "title": "Task title",
                    "description": "Task details",
                    "task_type": "backend|frontend|database|testing|devops",
                    "estimated_hours": 8
                }
            ]
        }

        Base your analysis strictly on the provided data. If data is insufficient, note that in the justification.
        """

        try:
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {
                        "role": "user",
                        "content": f"Query: {query}\n\nContext:\n{context_text}",
                    },
                ],
                temperature=0.7,
                max_tokens=2000,
            )

            content = response.choices[0].message.content
            # Extract JSON from response
            import json

            # Find JSON in the response (in case there's additional text)
            try:
                # Try to parse entire response as JSON
                proposal = json.loads(content)
            except json.JSONDecodeError:
                # Try to extract JSON from markdown code block
                import re

                json_match = re.search(r"```json\s*(.*?)\s*```", content, re.DOTALL)
                if json_match:
                    proposal = json.loads(json_match.group(1))
                else:
                    raise ValueError("Could not extract JSON from AI response")

            return proposal

        except Exception as e:
            return {
                "error": str(e),
                "title": "Analysis failed",
                "description": "Could not generate feature proposal due to an error.",
                "justification": "",
                "ui_changes": "",
                "data_model_changes": "",
                "workflow_changes": "",
                "priority": "low",
                "tasks": [],
            }
