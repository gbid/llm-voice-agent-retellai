import pytest
from unittest.mock import patch, MagicMock
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


class TestWebhooks:
    @patch("api.webhooks.retell")
    def test_call_ended_success(self, mock_retell, setup):
        """Test successful call_ended webhook handling with valid signature"""
        mock_retell.verify.return_value = True
        webhook_payload = {
            "event": "call_ended",
            "call": {
                "call_id": "test-call-123",
                "agent_id": "agent-456",
                "agent_version": 1,
                "call_status": "ended",
                "call_type": "phone_call",
                "direction": "inbound",
                "from_number": "+1234567890",
                "to_number": "+0987654321",
                "transcript": "Customer called about package PKG001",
            },
        }

        response = client.post(
            "/api/webhooks/events",
            json=webhook_payload,
            headers={"X-Retell-Signature": "valid-signature"},
        )
        assert response.status_code == 204

    def test_invalid_signature(self, setup):
        """Test invalid signature returns 401"""
        webhook_payload = {
            "event": "call_ended",
            "call": {
                "call_id": "test-call-456",
                "agent_id": "agent-456",
                "agent_version": 1,
                "call_status": "ended",
                "call_type": "phone_call",
                "direction": "inbound",
                "from_number": "+1234567890",
                "to_number": "+0987654321",
            },
        }
        response = client.post(
            "/api/webhooks/events",
            json=webhook_payload,
            headers={"X-Retell-Signature": "invalid-signature"},
        )
        assert response.status_code == 401
