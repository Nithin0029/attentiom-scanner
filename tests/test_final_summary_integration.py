import copy
from unittest.mock import MagicMock
import numpy as np

from src.pipeline.realtime_pipeline import RealtimePipeline
from src.reporting.session_report import SessionReport


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
    print("FINAL SUMMARY INTEGRATION TEST")
    print("=" * 60)

    reporter = SessionReport()
    dummy_frame = np.zeros((480, 640, 3), dtype=np.uint8)

    pipeline_empty = setup_mock_pipeline()
    pipeline_empty.close()

    empty_sessions = pipeline_empty.get_completed_sessions()
    empty_analytics = pipeline_empty.get_session_analytics()
    empty_reports = [reporter.generate_session_report(s) for s in empty_sessions]

    empty_text = reporter.format_final_summary_text(empty_analytics, empty_reports)
    assert "No completed person sessions were recorded." in empty_text
    print("[PASS] 1. Empty history handled safely.")

    pipeline = setup_mock_pipeline()

    pipeline.face_tracker.update = MagicMock(return_value=[DummyTrack(track_id=1)])
    pipeline.process_frame(dummy_frame, timestamp=100.0)
    pipeline.process_frame(dummy_frame, timestamp=101.0)
    pipeline.face_tracker.update = MagicMock(return_value=[])
    pipeline.process_frame(dummy_frame, timestamp=102.0)

    pipeline.face_tracker.update = MagicMock(return_value=[DummyTrack(track_id=2)])
    pipeline.process_frame(dummy_frame, timestamp=200.0)
    pipeline.face_tracker.update = MagicMock(return_value=[])
    pipeline.process_frame(dummy_frame, timestamp=201.0)

    completed_sessions = pipeline.get_completed_sessions()
    analytics = pipeline.get_session_analytics()
    assert analytics["total_sessions"] == 2
    print("[PASS] 2. Multiple completed sessions produce analytics.")

    assert "total_sessions" in analytics and analytics["total_sessions"] == 2
    print("[PASS] 3. Final summary data contains total sessions.")

    assert "average_attention_score" in analytics and isinstance(analytics["average_attention_score"], float)
    print("[PASS] 4. Final summary data contains average attention score.")

    assert "overall_attention_percentages" in analytics and "ATTENTIVE" in analytics["overall_attention_percentages"]
    print("[PASS] 5. Final summary data contains overall attention percentages.")

    assert "score_distribution" in analytics and "HIGH" in analytics["score_distribution"]
    print("[PASS] 6. Final summary data contains score distribution.")

    assert "total_events" in analytics and "blinks" in analytics["total_events"]
    print("[PASS] 7. Final summary data contains total events.")

    assert "best_session" in analytics and analytics["best_session"] is not None
    assert "track_id" in analytics["best_session"]
    print("[PASS] 8. Final summary data contains best session.")

    assert "worst_session" in analytics and analytics["worst_session"] is not None
    assert "track_id" in analytics["worst_session"]
    print("[PASS] 9. Final summary data contains worst session.")

    session_reports = [reporter.generate_session_report(s) for s in completed_sessions]
    assert len(session_reports) == 2
    assert session_reports[0]["track_id"] == 1
    assert session_reports[1]["track_id"] == 2
    print("[PASS] 10. Individual session report generated for every completed session.")

    pipeline_active = setup_mock_pipeline()
    pipeline_active.face_tracker.update = MagicMock(return_value=[DummyTrack(track_id=99)])
    pipeline_active.process_frame(dummy_frame, timestamp=300.0)

    assert len(pipeline_active.get_completed_sessions()) == 0

    pipeline_active.close()

    active_completed = pipeline_active.get_completed_sessions()
    assert len(active_completed) == 1
    assert active_completed[0]["track_id"] == 99
    active_analytics = pipeline_active.get_session_analytics()
    assert active_analytics["total_sessions"] == 1
    print("[PASS] 11. Active sessions finalized during pipeline.close() appear in final output.")

    history_before = copy.deepcopy(completed_sessions)
    analytics_run = pipeline.get_session_analytics()
    reports_run = [reporter.generate_session_report(s) for s in completed_sessions]
    text_output = reporter.format_final_summary_text(analytics_run, reports_run)

    history_after = pipeline.get_completed_sessions()
    assert history_before == history_after
    print("[PASS] 12. Summary flow does not mutate session history.")

    print()
    print("=" * 60)
    print("ALL FINAL SUMMARY INTEGRATION TESTS PASSED")
    print("=" * 60)


if __name__ == "__main__":
    main()
