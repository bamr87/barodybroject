import pytest  # noqa: F401
from rest_framework.test import APIClient


@pytest.mark.django_db
def test_assistant_create_api():
    client = APIClient()
    payload = {
        "name": "APITestAssistant",
        "description": "This assistant was created via an API test.",
        "instructions": "you are a helpful assistant.",
        "model": "gpt-4o-mini",  # Adjust as necessary based on your model field
        "json_schema": None,
        "assistant_group_memberships": []
    }
    response = client.post("/api/assistants/", payload, format="json")
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "APITestAssistant"
