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
    print("TEST PIPELINE SCORING INTEGRATION")
    print("=" * 60)

    dummy_frame = np.zeros((480, 640, 3), dtype=np.uint8)

    pipeline = setup_mock_pipeline()

    pipeline.face_tracker.update = MagicMock(
        return_value=[DummyTrack(track_id=1)]
    )

    result_1 = pipeline.process_frame(dummy_frame, timestamp=100.0)

    assert len(result_1["people"]) == 1, "Expected 1 person processed"
    person_1 = result_1["people"][0]

    assert "session" in person_1, "Output must contain 'session'"
    assert person_1["session"]["track_id"] == 1, "Session track_id should be 1"
    assert person_1["session"]["total_frames"] == 1, "Expected 1 frame in session"
    print("[PASS] Requirement 1 passed: Processing a person creates a session.")

    result_2 = pipeline.process_frame(dummy_frame, timestamp=101.0)
    person_2 = result_2["people"][0]

    assert person_2["session"]["total_frames"] == 2, "Expected 2 frames in session"
    print("[PASS] Requirement 2 passed: Processing same track increases total_frames.")

    assert "session" in person_2 and isinstance(person_2["session"], dict)
    print("[PASS] Requirement 3 passed: Output contains 'session' dictionary.")

    assert "attention_score" in person_2 and isinstance(
        person_2["attention_score"], dict
    )
    print("[PASS] Requirement 4 passed: Output contains 'attention_score' dictionary.")

    score = person_2["attention_score"]["score"]
    assert 0.0 <= score <= 100.0, f"Score {score} out of bounds [0, 100]"
    print(f"[PASS] Requirement 5 passed: Score ({score}) is between 0 and 100.")

    pipeline.face_tracker.update = MagicMock(
        return_value=[DummyTrack(track_id=2)]
    )

    result_b = pipeline.process_frame(dummy_frame, timestamp=102.0)
    person_b = result_b["people"][0]

    assert person_b["track_id"] == 2, "Expected track_id 2"
    assert person_b["session"]["track_id"] == 2, "Expected session track_id 2"
    assert person_b["session"]["total_frames"] == 1, "Expected new session for track_id 2"
    print("[PASS] Requirement 6 passed: Different track IDs have separate sessions.")

    pipeline.reset()

    active_track_ids = pipeline.session_manager.get_active_track_ids()
    completed_sessions = pipeline.get_completed_sessions()

    assert len(active_track_ids) == 0, "Active track IDs should be empty after reset"
    assert len(completed_sessions) == 0, "Completed sessions should be empty after reset"
    print("[PASS] Requirement 7 passed: pipeline.reset() clears all sessions.")

    print()
    print("=" * 60)
    print("ALL INTEGRATION TESTS PASSED SUCCESSFULLY")
    print("=" * 60)


if __name__ == "__main__":
    main()
