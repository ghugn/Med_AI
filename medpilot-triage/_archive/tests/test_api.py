import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_read_main():
    """Test frontend rendering from the root level"""
    response = client.get("/")
    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]

def test_api_validation_error():
    """Test standard validation exception mapping to APIResponse"""
    # Gửi payload rỗng (thiếu trường required)
    response = client.post("/api/v1/cases/create", json={})
    assert response.status_code == 422
    
    data = response.json()
    assert data["success"] is False
    assert data["message"] == "Dữ liệu không hợp lệ."
    assert "errors" in data["data"]
    
def test_create_case_endpoint():
    """Test create case logic with standard AI format."""
    payload = {
        "bac_si_id": "TEST_DOC",
        "ho_ten": "Test Patient",
        "tuoi": 25,
        "gioi_tinh": "Nam",
        "trieu_chung_transcript": "ho và sốt"
    }
    response = client.post("/api/v1/cases/create", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "case_id" in data["data"]

def test_chat_endpoint():
    """Test basic chat routing."""
    payload = {
        "user_role": "patient",
        "message": "Xin chào bác sĩ",
        "history": [],
        "case_id": "test_case_id"
    }
    response = client.post("/api/v1/chat/", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "reply" in data
