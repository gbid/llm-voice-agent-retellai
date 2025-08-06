import pytest
from unittest.mock import patch
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


@pytest.fixture(scope="module")
def setup():
    """Basic setup - assume for now that database is already initialized"""
    pass


class TestVerifyPackage:
    def test_verify_success(self, setup):
        """Test successful package verification"""
        response = client.post(
            "/api/functions/verify_package",
            json={"tracking_number": "PKG001", "postal_code": "12345"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["tracking_number"] == "PKG001"
        assert data["customer_name"] == "John Smith"

    def test_verify_package_not_found(self, setup):
        """Test package not found error"""
        response = client.post(
            "/api/functions/verify_package",
            json={"tracking_number": "INVALID", "postal_code": "99999"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["error_type"] == "package_not_found"

    def test_verify_package_already_delivered(self, setup):
        """Test package already delivered error"""
        response = client.post(
            "/api/functions/verify_package",
            json={"tracking_number": "PKG003", "postal_code": "54321"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["error_type"] == "package_already_delivered"


class TestReschedule:
    @patch("api.functions.send_reschedule_confirmation_email")
    def test_reschedule_success(self, mock_email, setup):
        """Test successful package reschedule"""
        mock_email.return_value = True
        response = client.post(
            "/api/functions/reschedule",
            json={
                "tracking_number": "PKG002",
                "postal_code": "67890",
                "target_time": "2025-08-10T14:00:00",
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "Package rescheduled successfully"

    def test_reschedule_package_not_found(self, setup):
        """Test package not found error"""
        response = client.post(
            "/api/functions/reschedule",
            json={
                "tracking_number": "INVALID",
                "postal_code": "99999",
                "target_time": "2025-08-10T14:00:00",
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert data["error_type"] == "package_not_found"

    def test_reschedule_package_already_delivered(self, setup):
        """Test package already delivered error"""
        response = client.post(
            "/api/functions/reschedule",
            json={
                "tracking_number": "PKG003",
                "postal_code": "54321",
                "target_time": "2025-08-10T14:00:00",
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert data["error_type"] == "package_already_delivered"

    @patch("api.functions.send_reschedule_confirmation_email")
    def test_reschedule_email_error(self, mock_email, setup):
        """Test email sending error"""
        mock_email.return_value = False
        response = client.post(
            "/api/functions/reschedule",
            json={
                "tracking_number": "PKG002",
                "postal_code": "67890",
                "target_time": "2025-08-10T14:00:00",
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert data["error_type"] == "email_error"


class TestEscalate:
    @patch("api.functions.send_escalation_email")
    def test_escalate_success(self, mock_email, setup):
        """Test successful escalation"""
        mock_email.return_value = True
        response = client.post(
            "/api/functions/escalate",
            json={"tracking_number": "PKG001", "postal_code": "12345"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "Escalation email sent successfully"

    def test_escalate_package_not_found(self, setup):
        """Test package not found error"""
        response = client.post(
            "/api/functions/escalate",
            json={"tracking_number": "INVALID", "postal_code": "99999"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["error_type"] == "package_not_found"

    @patch("api.functions.send_escalation_email")
    def test_escalate_email_error(self, mock_email, setup):
        """Test email sending error"""
        mock_email.return_value = False
        response = client.post(
            "/api/functions/escalate",
            json={"tracking_number": "PKG001", "postal_code": "12345"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["error_type"] == "email_error"
