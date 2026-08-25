import copy
from src.analytics.session_analytics import SessionAnalytics
from src.session.session_history import SessionHistory


def create_mock_session(
    track_id=1,
    duration=10.0,
    attentive_frames=80,
    distracted_frames=10,
    drowsy_frames=5,
    yawning_frames=5,
    blinks=4,
    yawns=1,
    prolonged_closures=0,
    look_aways=1,
    score=85.0,
):
    total = attentive_frames + distracted_frames + drowsy_frames + yawning_frames
    return {
        "track_id": track_id,
        "session": {
            "track_id": track_id,
            "start_time": 100.0,
            "last_seen_time": 100.0 + duration,
            "duration_seconds": duration,
            "total_frames": total,
            "attention_frames": {
                "ATTENTIVE": attentive_frames,
                "DISTRACTED": distracted_frames,
                "DROWSY": drowsy_frames,
                "YAWNING": yawning_frames,
            },
            "attention_percentages": {
                "ATTENTIVE": (attentive_frames / total) * 100 if total > 0 else 0.0,
                "DISTRACTED": (distracted_frames / total) * 100 if total > 0 else 0.0,
                "DROWSY": (drowsy_frames / total) * 100 if total > 0 else 0.0,
                "YAWNING": (yawning_frames / total) * 100 if total > 0 else 0.0,
            },
            "event_counts": {
                "blinks": blinks,
                "yawns": yawns,
                "prolonged_eye_closures": prolonged_closures,
                "look_away_events": look_aways,
            },
        },
        "attention_score": {
            "score": score,
            "attentive_percentage": (attentive_frames / total) * 100 if total > 0 else 0.0,
            "distracted_percentage": (distracted_frames / total) * 100 if total > 0 else 0.0,
            "drowsy_percentage": (drowsy_frames / total) * 100 if total > 0 else 0.0,
            "yawning_percentage": (yawning_frames / total) * 100 if total > 0 else 0.0,
        },
        "completed_at": 100.0 + duration,
    }


def main():
    print("=" * 60)
    print("SESSION ANALYTICS TEST")
    print("=" * 60)

    analytics = SessionAnalytics()

    empty_result = analytics.analyze_history([])
    assert empty_result["total_sessions"] == 0
    assert empty_result["total_duration_seconds"] == 0.0
    assert empty_result["total_frames"] == 0
    assert empty_result["average_attention_score"] == 0.0
    print("[PASS] 1. Empty history returns safe zero values.")

    assert empty_result["best_session"] is None
    print("[PASS] 2. Empty history returns best_session = None.")

    assert empty_result["worst_session"] is None
    print("[PASS] 3. Empty history returns worst_session = None.")

    s1 = create_mock_session(track_id=1, duration=5.0, attentive_frames=10, distracted_frames=0, drowsy_frames=0, yawning_frames=0, score=100.0)
    single_res = analytics.analyze_history([s1])
    assert single_res["total_sessions"] == 1
    assert single_res["total_duration_seconds"] == 5.0
    assert single_res["total_frames"] == 10
    assert single_res["average_attention_score"] == 100.0
    print("[PASS] 4. One session produces correct totals.")

    s2 = create_mock_session(track_id=2, duration=15.0, attentive_frames=90, distracted_frames=10, drowsy_frames=0, yawning_frames=0, score=95.0)
    multi_res = analytics.analyze_history([s1, s2])

    assert multi_res["total_duration_seconds"] == 20.0
    print("[PASS] 5. Multiple sessions calculate total duration correctly.")

    assert multi_res["total_frames"] == 110
    print("[PASS] 6. Multiple sessions calculate total frames correctly.")

    assert multi_res["average_attention_score"] == 97.5
    print("[PASS] 7. Average attention score is correct.")

    assert multi_res["best_session"]["track_id"] == 1
    assert multi_res["best_session"]["score"] == 100.0
    print("[PASS] 8. Best session is selected correctly.")

    assert multi_res["worst_session"]["track_id"] == 2
    assert multi_res["worst_session"]["score"] == 95.0
    print("[PASS] 9. Worst session is selected correctly.")

    s_tie1 = create_mock_session(track_id=10, score=80.0)
    s_tie2 = create_mock_session(track_id=20, score=80.0)
    tie_res = analytics.analyze_history([s_tie1, s_tie2])
    assert tie_res["best_session"]["track_id"] == 10
    assert tie_res["worst_session"]["track_id"] == 10
    print("[PASS] 10. Equal scores produce deterministic results.")

    s_small = create_mock_session(track_id=1, attentive_frames=0, distracted_frames=2, drowsy_frames=0, yawning_frames=0, score=50.0)
    s_large = create_mock_session(track_id=2, attentive_frames=100, distracted_frames=0, drowsy_frames=0, yawning_frames=0, score=100.0)
    fw_res = analytics.analyze_history([s_small, s_large])

    assert fw_res["overall_attention_percentages"]["ATTENTIVE"] == 98.04
    assert fw_res["overall_attention_percentages"]["DISTRACTED"] == 1.96
    print("[PASS] 11. Overall attention percentages are FRAME-WEIGHTED.")

    sum_pcts = sum(fw_res["overall_attention_percentages"].values())
    assert abs(sum_pcts - 100.0) < 0.1
    print("[PASS] 12. Attention percentages add up to approximately 100%.")

    se1 = create_mock_session(blinks=3, yawns=1, prolonged_closures=2, look_aways=4)
    se2 = create_mock_session(blinks=5, yawns=2, prolonged_closures=1, look_aways=3)
    evt_res = analytics.analyze_history([se1, se2])

    assert evt_res["total_events"]["blinks"] == 8
    print("[PASS] 13. Total blink count is aggregated correctly.")

    assert evt_res["total_events"]["yawns"] == 3
    print("[PASS] 14. Total yawn count is aggregated correctly.")

    assert evt_res["total_events"]["prolonged_eye_closures"] == 3
    print("[PASS] 15. Total prolonged eye closure count is aggregated correctly.")

    assert evt_res["total_events"]["look_away_events"] == 7
    print("[PASS] 16. Total look-away count is aggregated correctly.")

    s_high = create_mock_session(track_id=1, score=85.0)
    s_mod = create_mock_session(track_id=2, score=60.0)
    s_low = create_mock_session(track_id=3, score=30.0)
    dist_res = analytics.analyze_history([s_high, s_mod, s_low])

    assert dist_res["score_distribution"]["HIGH"] == 1
    print("[PASS] 17. Score distribution correctly categorizes HIGH sessions.")

    assert dist_res["score_distribution"]["MODERATE"] == 1
    print("[PASS] 18. Score distribution correctly categorizes MODERATE sessions.")

    assert dist_res["score_distribution"]["LOW"] == 1
    print("[PASS] 19. Score distribution correctly categorizes LOW sessions.")

    s_dis = create_mock_session(track_id=2, attentive_frames=10, distracted_frames=80, drowsy_frames=0, yawning_frames=0)
    eng_res = analytics.analyze_history([s_high, s_dis])

    assert eng_res["engagement"]["attentive_sessions"] == 1
    assert eng_res["engagement"]["sessions_with_distraction"] == 2
    assert eng_res["engagement"]["sessions_with_drowsiness"] == 1
    assert eng_res["engagement"]["sessions_with_yawning"] == 1
    print("[PASS] 20. Engagement metrics are calculated correctly.")

    raw_history = [s_high, s_dis]
    history_copy = copy.deepcopy(raw_history)
    analytics.analyze_history(raw_history)
    assert raw_history == history_copy
    print("[PASS] 21. Original input history is not mutated.")

    print()
    print("=" * 60)
    print("ALL SESSION ANALYTICS TESTS PASSED")
    print("=" * 60)


if __name__ == "__main__":
    main()
