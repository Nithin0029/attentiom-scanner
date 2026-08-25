"""
Headless integration tests for the Attention Scanner API.

These tests do not require:
- webcam hardware
- OpenCV windows
- MediaPipe model loading
- manual input
"""

import sys
import types
from unittest.mock import MagicMock, patch


# ------------------------------------------------------------
# Mock FastAPI TestClient before importing the API if needed.
# The actual API uses FastAPI; these tests mock ScannerService
# so no real CV pipeline is started.
# ------------------------------------------------------------

from fastapi.testclient import TestClient


def print_header():
    print("=" * 60)
    print("API SCANNER TEST")
    print("=" * 60)
    print()


def print_pass(number, message):
    print(f"[PASS] {number}. {message}")


def run_tests():
    print_header()

    with patch("src.api.server.ScannerService") as mock_service_class:
        # ----------------------------------------------------
        # Create a fully mocked scanner service.
        # ----------------------------------------------------
        mock_service = MagicMock()
        mock_service_class.return_value = mock_service

        # Import/reload server so it uses the mocked service.
        import importlib
        import src.api.server as server_module

        importlib.reload(server_module)

        # Replace the global service explicitly.
        server_module.scanner_service = mock_service

        client = TestClient(server_module.app)

        # ----------------------------------------------------
        # Test 1: Health endpoint.
        # ----------------------------------------------------
        response = client.get("/health")

        assert response.status_code == 200
        assert response.json()["status"] == "ok"

        print_pass(1, "Health endpoint works.")

        # ----------------------------------------------------
        # Test 2: Initial status.
        # ----------------------------------------------------
        mock_service.get_status.return_value = {
            "status": "stopped",
            "running": False,
            "completed_sessions": 0,
        }

        response = client.get("/api/scanner/status")

        assert response.status_code == 200
        assert response.json()["status"] == "stopped"

        print_pass(2, "Initial scanner status works.")

        # ----------------------------------------------------
        # Test 3: Start scanner.
        # ----------------------------------------------------
        mock_service.start.return_value = {
            "success": True,
            "status": "running",
            "message": "Scanner started successfully.",
        }

        response = client.post("/api/scanner/start")

        assert response.status_code == 200
        assert response.json()["success"] is True
        assert response.json()["status"] == "running"

        mock_service.start.assert_called_once()

        print_pass(3, "Scanner starts successfully.")

        # ----------------------------------------------------
        # Test 4: Running status.
        # ----------------------------------------------------
        mock_service.get_status.return_value = {
            "status": "running",
            "running": True,
            "completed_sessions": 0,
        }

        response = client.get("/api/scanner/status")

        assert response.status_code == 200
        assert response.json()["running"] is True

        print_pass(4, "Scanner status reports running.")

        # ----------------------------------------------------
        # Test 5: Frame endpoint rejects empty upload.
        # ----------------------------------------------------
        response = client.post(
            "/api/scanner/frame",
            files={
                "file": (
                    "empty.jpg",
                    b"",
                    "image/jpeg",
                )
            },
        )

        assert response.status_code == 400

        print_pass(5, "Empty frame is rejected safely.")

        # ----------------------------------------------------
        # Test 6: Frame endpoint rejects invalid image data.
        # ----------------------------------------------------
        response = client.post(
            "/api/scanner/frame",
            files={
                "file": (
                    "invalid.jpg",
                    b"this-is-not-an-image",
                    "image/jpeg",
                )
            },
        )

        assert response.status_code == 400

        print_pass(6, "Invalid image frame is rejected safely.")

        # ----------------------------------------------------
        # Test 7: Scanner must be running for frame processing.
        # ----------------------------------------------------
        mock_service.get_status.return_value = {
            "status": "stopped",
            "running": False,
            "completed_sessions": 0,
        }

        response = client.post(
            "/api/scanner/frame",
            files={
                "file": (
                    "test.jpg",
                    b"fake-image",
                    "image/jpeg",
                )
            },
        )

        assert response.status_code == 400
        assert "not running" in response.json()["detail"].lower()

        print_pass(7, "Frame processing requires scanner to be running.")

        # ----------------------------------------------------
        # Test 8: Stop scanner.
        # ----------------------------------------------------
        mock_service.stop.return_value = {
            "success": True,
            "status": "stopped",
            "message": "Scanner stopped and active sessions finalized.",
        }

        response = client.post("/api/scanner/stop")

        assert response.status_code == 200
        assert response.json()["success"] is True
        assert response.json()["status"] == "stopped"

        mock_service.stop.assert_called_once()

        print_pass(8, "Scanner stops successfully.")

        # ----------------------------------------------------
        # Test 9: Final summary.
        # ----------------------------------------------------
        expected_summary = {
            "completed_sessions": [
                {
                    "track_id": 1,
                    "session": {
                        "duration_seconds": 10.0,
                        "total_frames": 100,
                    },
                    "attention_score": {
                        "score": 82.5,
                    },
                    "completed_at": 1234567890.0,
                }
            ],
            "analytics": {
                "total_sessions": 1,
                "average_attention_score": 82.5,
                "overall_attention_percentages": {
                    "ATTENTIVE": 80.0,
                    "DISTRACTED": 10.0,
                    "DROWSY": 5.0,
                    "YAWNING": 5.0,
                },
            },
        }

        mock_service.get_summary.return_value = expected_summary

        response = client.get("/api/scanner/summary")

        assert response.status_code == 200

        summary = response.json()

        assert summary["completed_sessions"][0]["track_id"] == 1
        assert summary["analytics"]["total_sessions"] == 1
        assert summary["analytics"]["average_attention_score"] == 82.5

        print_pass(9, "Final summary is returned correctly.")

        # ----------------------------------------------------
        # Test 10: Summary is JSON serializable.
        # ----------------------------------------------------
        import json

        json.dumps(summary)

        print_pass(10, "Summary response is JSON serializable.")

        # ----------------------------------------------------
        # Test 11: Scanner service API is available.
        # ----------------------------------------------------
        from src.api.scanner_service import ScannerService

        assert hasattr(ScannerService, "start")
        assert hasattr(ScannerService, "process_frame")
        assert hasattr(ScannerService, "get_status")
        assert hasattr(ScannerService, "stop")
        assert hasattr(ScannerService, "get_summary")

        print_pass(11, "Scanner service exposes required methods.")

        # ----------------------------------------------------
        # Test 12: API application exists.
        # ----------------------------------------------------
        assert server_module.app is not None

        print_pass(12, "FastAPI application is available.")

    print()
    print("=" * 60)
    print("ALL API SCANNER TESTS PASSED")
    print("=" * 60)


if __name__ == "__main__":
    try:
        run_tests()
    except AssertionError as error:
        print()
        print("[FAIL]", error)
        sys.exit(1)
    except Exception as error:
        print()
        print("[ERROR]", type(error).__name__, "-", error)
        sys.exit(1)