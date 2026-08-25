import csv
import json
import os
import shutil
import tempfile

from src.reporting.session_report import SessionReport
from src.session.session_history import SessionHistory


def create_sample_session(track_id=1, attentive=80, distracted=10, drowsy=5, yawning=5):
    total = attentive + distracted + drowsy + yawning
    return {
        "track_id": track_id,
        "start_time": 100.0,
        "last_seen_time": 110.0,
        "duration_seconds": 10.0,
        "total_frames": total,
        "attention_frames": {
            "ATTENTIVE": attentive,
            "DISTRACTED": distracted,
            "DROWSY": drowsy,
            "YAWNING": yawning,
        },
        "attention_percentages": {
            "ATTENTIVE": (attentive / total) * 100 if total > 0 else 0.0,
            "DISTRACTED": (distracted / total) * 100 if total > 0 else 0.0,
            "DROWSY": (drowsy / total) * 100 if total > 0 else 0.0,
            "YAWNING": (yawning / total) * 100 if total > 0 else 0.0,
        },
        "event_counts": {
            "blinks": 4,
            "yawns": 1,
            "prolonged_eye_closures": 0,
            "look_away_events": 1,
        },
        "event_history": [
            {"event": "blink", "timestamp": 102.0},
            {"event": "yawn", "timestamp": 105.0},
        ],
    }


def main():
    print("=" * 60)
    print("SESSION REPORT TEST")
    print("=" * 60)

    reporter = SessionReport()

    print("\nTEST 1: Single Session Report Generation")
    sample_summary = create_sample_session(track_id=1, attentive=80, distracted=10, drowsy=5, yawning=5)
    report_single = reporter.generate_session_report(sample_summary)

    assert report_single["track_id"] == 1
    assert report_single["total_frames"] == 100
    assert report_single["duration_seconds"] == 10.0
    assert report_single["rating"] == "HIGH"
    assert "text_summary" in report_single
    assert "SESSION REPORT (Track ID: 1)" in report_single["text_summary"]
    print("[PASS] Single session report generated correctly with score rating 'HIGH'")

    print("\nTEST 2: Low Attention Rating")
    low_summary = create_sample_session(track_id=2, attentive=10, distracted=30, drowsy=50, yawning=10)
    report_low = reporter.generate_session_report(low_summary)
    assert report_low["rating"] == "LOW"
    print(f"[PASS] Low attention score rating correctly identified: score={report_low['attention_score']}, rating={report_low['rating']}")

    print("\nTEST 3: History Record Unpacking")
    history = SessionHistory()
    score_b = {"score": 92.5, "attentive_percentage": 90.0, "distracted_percentage": 10.0, "drowsy_percentage": 0.0, "yawning_percentage": 0.0}
    history.add_completed_session(
        track_id=10,
        session_summary=sample_summary,
        attention_score=score_b,
        completed_at=120.0,
    )
    rec = history.get_latest_session()
    report_rec = reporter.generate_session_report(rec)
    assert report_rec["track_id"] == 10
    assert report_rec["attention_score"] == 92.5
    assert report_rec["rating"] == "HIGH"
    print("[PASS] SessionHistory completed session record unpacked successfully")

    print("\nTEST 4: History Report Aggregation")
    history_obj = SessionHistory()
    s1 = create_sample_session(track_id=1, attentive=80, distracted=10, drowsy=10, yawning=0)
    s2 = create_sample_session(track_id=2, attentive=50, distracted=20, drowsy=20, yawning=10)
    score1 = {"score": 85.0}
    score2 = {"score": 57.5}

    history_obj.add_completed_session(1, s1, score1, 110.0)
    history_obj.add_completed_session(2, s2, score2, 130.0)

    hist_report = reporter.generate_history_report(history_obj)
    assert hist_report["total_sessions"] == 2
    assert hist_report["total_frames"] == 200
    assert hist_report["total_duration_seconds"] == 20.0
    assert hist_report["average_attention_score"] == 71.25
    assert hist_report["overall_rating"] == "MODERATE"
    assert hist_report["total_event_counts"]["blinks"] == 8
    assert "SESSION HISTORY SUMMARY REPORT" in hist_report["text_summary"]
    print("[PASS] History report aggregated 2 sessions correctly")

    print("\nTEST 5: Empty History Report")
    empty_report = reporter.generate_history_report([])
    assert empty_report["total_sessions"] == 0
    assert empty_report["average_attention_score"] == 0.0
    assert empty_report["total_duration_seconds"] == 0.0
    print("[PASS] Empty history report handled safely")

    print("\nTEST 6: JSON Export")
    temp_dir = tempfile.mkdtemp()
    try:
        json_file = os.path.join(temp_dir, "report.json")
        json_str = reporter.export_json(hist_report, filepath=json_file)
        assert os.path.exists(json_file)

        with open(json_file, "r", encoding="utf-8") as f:
            loaded_json = json.load(f)

        assert loaded_json["total_sessions"] == 2
        assert loaded_json["average_attention_score"] == 71.25
        print("[PASS] JSON report exported and re-loaded cleanly")

        print("\nTEST 7: CSV Export")
        csv_file = os.path.join(temp_dir, "report.csv")
        reporter.export_csv(history_obj, filepath=csv_file)
        assert os.path.exists(csv_file)

        with open(csv_file, "r", encoding="utf-8", newline="") as f:
            reader = list(csv.DictReader(f))

        assert len(reader) == 2
        assert reader[0]["track_id"] == "1"
        assert reader[1]["track_id"] == "2"
        assert "attention_score" in reader[0]
        assert "attentive_percentage" in reader[0]
        print("[PASS] CSV export generated valid header and 2 rows")

    finally:
        shutil.rmtree(temp_dir)

    print("\n" + "=" * 60)
    print("ALL SESSION REPORT TESTS PASSED SUCCESSFULLY!")
    print("=" * 60)


if __name__ == "__main__":
    main()
