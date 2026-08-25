from unittest.mock import MagicMock
import numpy as np

from src.pipeline.realtime_pipeline import RealtimePipeline


class DummyTrack:
    def __init__(self, track_id, bbox=(100, 100, 200, 200)):
        self.track_id = track_id
        self.bbox = bbox
        self.lost_frames = 0
        self.confidence = 0.95


def setup_mock_pipeline():
    pipeline = RealtimePipeline()

    pipeline.face_detector.detect = MagicMock(return_value=[MagicMock()])
    pipeline.face_landmarker.detect = MagicMock(
        return_value=MagicMock(face_landmarks=[MagicMock()])
    )
    pipeline.feature_extractor.extract_ear = MagicMock(
        return_value={"average_ear": 0.3}
    )
    pipeline.feature_extractor.extract_mouth_features = MagicMock(
        return_value={"mar": 0.1}
    )
    pipeline.feature_extractor.calculate_head_pose = MagicMock(
        return_value={"yaw": 0.0, "pitch": 0.0, "roll": 0.0}
    )

    return pipeline


def main():
    print("=" * 60)
    print("PIPELINE ANALYTICS INTEGRATION TEST")
    print("=" * 60)

    dummy_frame = np.zeros((480, 640, 3), dtype=np.uint8)
    pipeline = setup_mock_pipeline()

    analytics_empty = pipeline.get_session_analytics()
    assert analytics_empty["total_sessions"] == 0
    assert analytics_empty["total_duration_seconds"] == 0.0
    assert analytics_empty["best_session"] is None
    print("[PASS] 1. Pipeline returns analytics for empty history.")

    pipeline.face_tracker.update = MagicMock(
        return_value=[DummyTrack(track_id=1)]
    )
    pipeline.process_frame(dummy_frame, timestamp=100.0)
    pipeline.process_frame(dummy_frame, timestamp=101.0)

    pipeline.face_tracker.update = MagicMock(return_value=[])
    pipeline.process_frame(dummy_frame, timestamp=102.0)

    analytics_1 = pipeline.get_session_analytics()
    assert analytics_1["total_sessions"] == 1
    assert analytics_1["total_frames"] == 2
    assert analytics_1["total_duration_seconds"] == 2.0
    print("[PASS] 2. Completed sessions are reflected in pipeline analytics.")

    required_keys = [
        "total_sessions",
        "total_duration_seconds",
        "total_frames",
        "average_attention_score",
        "best_session",
        "worst_session",
        "overall_attention_percentages",
        "total_events",
        "score_distribution",
        "engagement",
    ]
    for key in required_keys:
        assert key in analytics_1, f"Missing required key '{key}' in analytics result"

    assert analytics_1["best_session"]["track_id"] == 1
    assert analytics_1["worst_session"]["track_id"] == 1
    print("[PASS] 3. Analytics contains the required sections.")

    pipeline.reset()
    analytics_reset = pipeline.get_session_analytics()
    assert analytics_reset["total_sessions"] == 0
    assert analytics_reset["total_duration_seconds"] == 0.0
    assert analytics_reset["best_session"] is None
    assert analytics_reset["worst_session"] is None
    print("[PASS] 4. pipeline.reset() returns analytics to an empty state.")

    print()
    print("=" * 60)
    print("ALL PIPELINE ANALYTICS INTEGRATION TESTS PASSED")
    print("=" * 60)


if __name__ == "__main__":
    main()
