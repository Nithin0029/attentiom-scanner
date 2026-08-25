import time

from src.session.session_history import SessionHistory


def main():
    print("=" * 50)
    print("SESSION HISTORY TEST")
    print("=" * 50)

    history = SessionHistory()

    assert history.get_all_sessions() == [], "Expected empty list"
    print("[PASS] 1. New history is empty.")

    assert len(history) == 0, "Expected len 0"
    print("[PASS] 2. len(history) is initially 0.")

    sample_summary_1 = {
        "track_id": 1,
        "duration_seconds": 12.5,
        "total_frames": 120,
        "attention_percentages": {"ATTENTIVE": 80.0, "DISTRACTED": 20.0},
    }
    sample_score_1 = {"score": 90.0, "attentive_percentage": 80.0}

    res_1 = history.add_completed_session(
        track_id=1,
        session_summary=sample_summary_1,
        attention_score=sample_score_1,
        completed_at=1000.0,
    )
    assert res_1 is not None, "Failed to return stored record"
    print("[PASS] 3. Adding one session works.")

    assert res_1["track_id"] == 1, "Expected track_id 1"
    print("[PASS] 4. Stored track_id is correct.")

    assert res_1["session"]["duration_seconds"] == 12.5
    assert res_1["session"]["total_frames"] == 120
    print("[PASS] 5. Stored session summary is correct.")

    assert res_1["attention_score"]["score"] == 90.0
    print("[PASS] 6. Stored attention_score is correct.")

    assert res_1["completed_at"] == 1000.0
    print("[PASS] 7. Explicitly provided completed_at is preserved.")

    t_before = time.time()
    res_auto = history.add_completed_session(
        track_id=2,
        session_summary={"track_id": 2, "total_frames": 50},
        attention_score={"score": 85.0},
    )
    t_after = time.time()
    assert res_auto["completed_at"] is not None
    assert t_before <= res_auto["completed_at"] <= t_after
    print("[PASS] 8. Omitted completed_at is automatically created.")

    sample_summary_3 = {"track_id": 1, "total_frames": 200}
    sample_score_3 = {"score": 95.0}
    history.add_completed_session(
        track_id=1,
        session_summary=sample_summary_3,
        attention_score=sample_score_3,
        completed_at=2000.0,
    )

    all_sessions = history.get_all_sessions()
    assert len(all_sessions) == 3
    assert (
        all_sessions[0]["track_id"] == 1
        and all_sessions[0]["completed_at"] == 1000.0
    )
    assert all_sessions[1]["track_id"] == 2
    assert (
        all_sessions[2]["track_id"] == 1
        and all_sessions[2]["completed_at"] == 2000.0
    )
    print("[PASS] 9. Multiple sessions preserve insertion/completion order.")

    latest = history.get_latest_session()
    assert latest["track_id"] == 1
    assert latest["completed_at"] == 2000.0
    assert latest["attention_score"]["score"] == 95.0
    print("[PASS] 10. get_latest_session returns the newest session.")

    track_1_sessions = history.get_sessions_by_track_id(1)
    assert len(track_1_sessions) == 2
    assert track_1_sessions[0]["completed_at"] == 1000.0
    assert track_1_sessions[1]["completed_at"] == 2000.0

    track_2_sessions = history.get_sessions_by_track_id(2)
    assert len(track_2_sessions) == 1

    track_99_sessions = history.get_sessions_by_track_id(99)
    assert track_99_sessions == []
    print("[PASS] 11. get_sessions_by_track_id correctly filters sessions.")

    fetched_all = history.get_all_sessions()
    fetched_all[0]["session"]["total_frames"] = 99999
    fetched_all.append({"track_id": 999})
    re_fetched = history.get_all_sessions()
    assert len(re_fetched) == 3
    assert re_fetched[0]["session"]["total_frames"] == 120
    print("[PASS] 12. get_all_sessions returns a deep copy.")

    fetched_latest = history.get_latest_session()
    fetched_latest["attention_score"]["score"] = 0.0
    re_fetched_latest = history.get_latest_session()
    assert re_fetched_latest["attention_score"]["score"] == 95.0
    print("[PASS] 13. get_latest_session returns a copy.")

    history.clear()
    assert history.get_all_sessions() == []
    assert history.get_latest_session() is None
    print("[PASS] 14. clear removes everything.")

    assert len(history) == 0
    history.add_completed_session(
        track_id=5,
        session_summary={"total_frames": 10},
        attention_score={"score": 100.0},
    )
    assert len(history) == 1
    history.clear()
    assert len(history) == 0
    print("[PASS] 15. len(history) returns correct count after operations.")

    print()
    print("=" * 50)
    print("ALL SESSION HISTORY TESTS PASSED SUCCESSFULLY")
    print("=" * 50)


if __name__ == "__main__":
    main()
