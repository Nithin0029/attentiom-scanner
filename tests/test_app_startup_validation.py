import importlib
from unittest.mock import MagicMock, patch
import numpy as np

from src.core.face_detector import FaceDetector
from src.pipeline.realtime_pipeline import RealtimePipeline

main_module = importlib.import_module("src.app.main")


def main():
    print("=" * 60)
    print("APP STARTUP VALIDATION TEST")
    print("=" * 60)

    # --------------------------------------------------
    # 1. Missing model validation handled safely
    # --------------------------------------------------
    try:
        FaceDetector(model_path="models/non_existent_model_file.tflite")
        assert False, "Expected FileNotFoundError for missing model path"
    except FileNotFoundError as e:
        assert "not found" in str(e).lower()
        print("[PASS] 1. Missing model validation handled safely.")

    # --------------------------------------------------
    # 2. Camera-open failure handled safely
    # --------------------------------------------------
    with patch("cv2.VideoCapture") as mock_cap_cls:
        mock_cap = MagicMock()
        mock_cap.isOpened.return_value = False
        mock_cap_cls.return_value = mock_cap

        with patch.object(main_module, "RealtimePipeline") as mock_pipe_cls:
            mock_pipe = MagicMock()
            mock_pipe_cls.return_value = mock_pipe

            exit_code = main_module.main()
            assert exit_code == 1
            mock_pipe.close.assert_called()
            print("[PASS] 2. Camera-open failure handled safely.")

    # --------------------------------------------------
    # 3-4. Invalid/None frame handling and consecutive failure exit
    # --------------------------------------------------
    with patch("cv2.VideoCapture") as mock_cap_cls:
        mock_cap = MagicMock()
        mock_cap.isOpened.return_value = True
        mock_cap.read.return_value = (False, None)
        mock_cap_cls.return_value = mock_cap

        with patch.object(main_module, "RealtimePipeline") as mock_pipe_cls:
            mock_pipe = MagicMock()
            mock_pipe.get_completed_sessions.return_value = []
            mock_pipe.get_session_analytics.return_value = {"total_sessions": 0}
            mock_pipe_cls.return_value = mock_pipe

            with patch("cv2.imshow"), patch("cv2.waitKey"):
                exit_code = main_module.main()
                assert exit_code == 0
                mock_pipe.process_frame.assert_not_called()
                print("[PASS] 3. Invalid/None frame is not sent to pipeline.")
                print("[PASS] 4. Consecutive frame failures stop loop safely.")

    # --------------------------------------------------
    # 5-6. Normal mocked startup path succeeds & cleanup called
    # --------------------------------------------------
    dummy_frame = np.zeros((480, 640, 3), dtype=np.uint8)
    with patch("cv2.VideoCapture") as mock_cap_cls:
        mock_cap = MagicMock()
        mock_cap.isOpened.return_value = True
        mock_cap.read.return_value = (True, dummy_frame)
        mock_cap_cls.return_value = mock_cap

        with patch.object(main_module, "RealtimePipeline") as mock_pipe_cls:
            mock_pipe = MagicMock()
            mock_pipe.process_frame.return_value = {"people": []}
            mock_pipe.get_completed_sessions.return_value = []
            mock_pipe.get_session_analytics.return_value = {"total_sessions": 0}
            mock_pipe_cls.return_value = mock_pipe

            with patch("cv2.imshow"), patch("cv2.waitKey", return_value=ord("q")), patch("cv2.destroyAllWindows") as mock_destroy:
                exit_code = main_module.main()
                assert exit_code == 0
                mock_cap.release.assert_called()
                mock_destroy.assert_called()
                mock_pipe.close.assert_called()
                print("[PASS] 5. Normal mocked startup path succeeds.")
                print("[PASS] 6. Cleanup methods are called correctly.")

    # --------------------------------------------------
    # 7. Expected startup failure skips report generation
    # --------------------------------------------------
    with patch.object(main_module, "RealtimePipeline", side_effect=FileNotFoundError("Mock model missing")):
        with patch.object(main_module, "SessionReport") as mock_report_cls:
            exit_code = main_module.main()
            assert exit_code == 1
            mock_report_cls.assert_not_called()
            print("[PASS] 7. Expected startup failure skips report generation.")

    # --------------------------------------------------
    # 8. Pipeline APIs remain unbroken
    # --------------------------------------------------
    pipe = RealtimePipeline()
    assert hasattr(pipe, "process_frame")
    assert hasattr(pipe, "get_completed_sessions")
    assert hasattr(pipe, "get_session_analytics")
    assert hasattr(pipe, "reset")
    assert hasattr(pipe, "close")
    pipe.close()
    pipe.close()
    print("[PASS] 8. Pipeline APIs remain unbroken.")

    print()
    print("=" * 60)
    print("ALL APP STARTUP VALIDATION TESTS PASSED")
    print("=" * 60)


if __name__ == "__main__":
    main()
