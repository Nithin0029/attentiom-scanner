from unittest.mock import MagicMock
import numpy as np

from src.pipeline.realtime_pipeline import RealtimePipeline
from src.session.session_history import SessionHistory


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
    print("PIPELINE SESSION HISTORY INTEGRATION TEST")
    print("=" * 60)

    dummy_frame = np.zeros((480, 640, 3), dtype=np.uint8)
    pipeline = setup_mock_pipeline()

    assert len(pipeline.get_completed_sessions()) == 0
    print("[PASS] 1. New pipeline history is empty.")

    pipeline.face_tracker.update = MagicMock(
        return_value=[DummyTrack(track_id=1)]
    )
    pipeline.process_frame(dummy_frame, timestamp=100.0)
    active_sessions_1 = pipeline.get_all_active_sessions()

    assert len(active_sessions_1) == 1
    assert 1 in active_sessions_1
    assert active_sessions_1[1]["total_frames"] == 1
    print("[PASS] 2. Active person creates a session.")

    pipeline.process_frame(dummy_frame, timestamp=101.0)
    assert len(pipeline.get_completed_sessions()) == 0
    print("[PASS] 3. Active session is not archived prematurely.")

    pipeline.face_tracker.update = MagicMock(return_value=[])
    pipeline.process_frame(dummy_frame, timestamp=102.0)

    completed_4 = pipeline.get_completed_sessions()
    assert len(completed_4) == 1
    record_1 = completed_4[0]
    print("[PASS] 4. Removed track is archived.")

    assert record_1["track_id"] == 1
    assert "session" in record_1 and isinstance(record_1["session"], dict)
    assert "attention_score" in record_1 and isinstance(record_1["attention_score"], dict)
    assert "completed_at" in record_1 and record_1["completed_at"] == 102.0
    print("[PASS] 5. Archived record contains track_id, session, attention_score, and completed_at.")

    score_val = record_1["attention_score"]["score"]
    assert 0.0 <= score_val <= 100.0
    print(f"[PASS] 6. Archived attention score ({score_val}) is between 0 and 100.")

    assert pipeline.get_session(1) is None
    assert len(pipeline.get_all_active_sessions()) == 0
    print("[PASS] 7. Disappeared person active session is removed.")

    pipeline.process_frame(dummy_frame, timestamp=103.0)
    assert len(pipeline.get_completed_sessions()) == 1
    print("[PASS] 8. Removed track is not archived twice.")

    pipeline.face_tracker.update = MagicMock(
        return_value=[DummyTrack(track_id=2)]
    )
    pipeline.process_frame(dummy_frame, timestamp=200.0)

    pipeline.face_tracker.update = MagicMock(return_value=[])
    pipeline.process_frame(dummy_frame, timestamp=201.0)

    completed_9 = pipeline.get_completed_sessions()
    assert len(completed_9) == 2
    print("[PASS] 9. Different track IDs create separate history records.")

    assert completed_9[0]["track_id"] == 1
    assert completed_9[1]["track_id"] == 2
    assert completed_9[0]["completed_at"] == 102.0
    assert completed_9[1]["completed_at"] == 201.0
    print("[PASS] 10. History preserves completion and insertion order.")

    latest = pipeline.get_latest_completed_session()
    assert latest is not None
    assert latest["track_id"] == 2
    assert latest["completed_at"] == 201.0
    print("[PASS] 11. get_latest_completed_session returns the latest archived session.")

    pipeline.clear_session_history()
    assert len(pipeline.get_completed_sessions()) == 0
    assert pipeline.get_latest_completed_session() is None
    print("[PASS] 12. clear_session_history clears completed history.")

    pipeline.face_tracker.update = MagicMock(
        return_value=[DummyTrack(track_id=3)]
    )
    pipeline.process_frame(dummy_frame, timestamp=300.0)
    pipeline.face_tracker.update = MagicMock(return_value=[])
    pipeline.process_frame(dummy_frame, timestamp=301.0)

    pipeline.face_tracker.update = MagicMock(
        return_value=[DummyTrack(track_id=4)]
    )
    pipeline.process_frame(dummy_frame, timestamp=302.0)

    assert len(pipeline.get_all_active_sessions()) == 1
    assert len(pipeline.get_completed_sessions()) == 1

    pipeline.reset()
    assert len(pipeline.get_all_active_sessions()) == 0
    assert len(pipeline.get_completed_sessions()) == 0
    assert pipeline.get_latest_completed_session() is None
    print("[PASS] 13. pipeline.reset clears active sessions and completed history.")

    print()
    print("=" * 60)
    print("ALL PIPELINE SESSION HISTORY INTEGRATION TESTS PASSED")
    print("=" * 60)


if __name__ == "__main__":
    main()
