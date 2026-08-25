import copy
import numpy as np

from src.app.ui_renderer import (
    draw_controls_hint,
    draw_header,
    draw_no_person_notice,
    draw_person_overlay,
    draw_score_bar,
    draw_summary_panel,
)


def create_synthetic_frame(width=640, height=480):
    return np.zeros((height, width, 3), dtype=np.uint8)


def create_synthetic_person(
    track_id=1,
    bbox=(100, 100, 200, 200),
    state="ATTENTIVE",
    score=85.5,
    session_duration=42.3,
):
    return {
        "track_id": track_id,
        "bbox": bbox,
        "confidence": 0.95,
        "features": {
            "ear": 0.28,
            "mar": 0.12,
            "yaw": 2.5,
            "pitch": -1.0,
            "roll": 0.5,
        },
        "analysis": {
            "behavior": {
                "eyes_closed": False,
                "mouth_open": False,
                "looking_away": False,
                "events": ["blink"],
            }
        },
        "attention": {
            "state": state,
            "reason": "Normal visual engagement",
        },
        "session": {
            "duration_seconds": session_duration,
            "attention_percentages": {
                "ATTENTIVE": 85.0,
                "DISTRACTED": 15.0,
                "DROWSY": 0.0,
                "YAWNING": 0.0,
            },
            "event_counts": {
                "blinks": 12,
                "yawns": 0,
                "prolonged_eye_closures": 0,
                "look_away_events": 2,
            },
        },
        "attention_score": {
            "score": score,
        },
    }


def test_app_ui_rendering():
    print()
    print("=" * 60)
    print("APP UI RENDERING TEST")
    print("=" * 60)

    # 1. Header rendering returns valid frame
    frame = create_synthetic_frame()
    draw_header(frame, fps=29.8, people_count=2, session_duration=124.0)
    assert frame is not None and frame.shape == (480, 640, 3)
    print("[PASS] 1. Header rendering works.")

    # 2. Person card rendering does not crash
    frame = create_synthetic_frame()
    person = create_synthetic_person()
    draw_person_overlay(frame, person, index=0, total_people=1)
    assert frame is not None
    print("[PASS] 2. Person card rendering works.")

    # 3. Score bar handles score 0
    frame = create_synthetic_frame()
    draw_score_bar(frame, x=10, y=10, width=100, height=15, score=0)
    assert frame is not None
    print("[PASS] 3. Score bar handles score 0.")

    # 4. Score bar handles score 100
    frame = create_synthetic_frame()
    draw_score_bar(frame, x=10, y=10, width=100, height=15, score=100)
    assert frame is not None
    print("[PASS] 4. Score bar handles score 100.")

    # 5. Score bar handles a normal decimal score
    frame = create_synthetic_frame()
    draw_score_bar(frame, x=10, y=10, width=100, height=15, score=85.5)
    assert frame is not None
    print("[PASS] 5. Score bar handles normal decimal score.")

    # 6. Missing attention score is handled safely
    frame = create_synthetic_frame()
    person_no_score = create_synthetic_person()
    person_no_score["attention_score"] = None
    draw_person_overlay(frame, person_no_score)
    assert frame is not None
    print("[PASS] 6. Missing attention score handled safely.")

    # 7. Missing session duration is handled safely
    frame = create_synthetic_frame()
    person_no_dur = create_synthetic_person()
    person_no_dur["session"]["duration_seconds"] = None
    draw_person_overlay(frame, person_no_dur)
    assert frame is not None
    print("[PASS] 7. Missing session duration handled safely.")

    # 8. Different attention states render without crashing
    for state in ["ATTENTIVE", "DISTRACTED", "DROWSY", "YAWNING", "UNKNOWN"]:
        frame = create_synthetic_frame()
        p = create_synthetic_person(state=state)
        draw_person_overlay(frame, p)
    print("[PASS] 8. Different attention states render cleanly.")

    # 9. Multiple people render without crashing
    frame = create_synthetic_frame()
    p1 = create_synthetic_person(track_id=1, bbox=(50, 50, 150, 150))
    p2 = create_synthetic_person(track_id=2, bbox=(300, 100, 420, 220))
    people = [p1, p2]
    for idx, p in enumerate(people):
        draw_person_overlay(frame, p, index=idx, total_people=len(people))
    draw_summary_panel(frame, people, fps=30.0, session_duration=60.0)
    print("[PASS] 9. Multiple people render cleanly.")

    # 10. No-person state renders without crashing
    frame = create_synthetic_frame()
    draw_no_person_notice(frame)
    assert frame is not None
    print("[PASS] 10. No-person state renders cleanly.")

    # 11. Controls hint renders without crashing
    frame = create_synthetic_frame()
    draw_controls_hint(frame)
    assert frame is not None
    print("[PASS] 11. Controls hint renders cleanly.")

    # 12. Rendering does not change the input person data
    frame = create_synthetic_frame()
    p_orig = create_synthetic_person()
    p_copy = copy.deepcopy(p_orig)
    draw_person_overlay(frame, p_orig)
    assert p_orig == p_copy
    print("[PASS] 12. Input person data remains unchanged.")

    # 13. Rendering preserves valid frame dimensions
    frame = create_synthetic_frame(width=1280, height=720)
    initial_shape = frame.shape
    draw_header(frame, fps=60.0, people_count=1, session_duration=10.0)
    draw_person_overlay(frame, create_synthetic_person())
    draw_controls_hint(frame)
    assert frame.shape == initial_shape
    print("[PASS] 13. Frame dimensions preserved.")

    # 14. Person card remains safely renderable near frame edges
    edge_bboxes = [
        (0, 0, 50, 50),
        (580, 0, 640, 60),
        (0, 420, 80, 480),
        (550, 400, 639, 479),
    ]
    for bbox in edge_bboxes:
        frame = create_synthetic_frame(width=640, height=480)
        p_edge = create_synthetic_person(bbox=bbox)
        draw_person_overlay(frame, p_edge)
        assert frame is not None
    print("[PASS] 14. Person card remains renderable near frame edges.")

    print()
    print("=" * 60)
    print("ALL APP UI RENDERING TESTS PASSED")
    print("=" * 60)


if __name__ == "__main__":
    test_app_ui_rendering()
