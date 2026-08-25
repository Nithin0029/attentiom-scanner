from src.session.session_manager import SessionManager


def print_summary(title, summary):
    print()
    print(title)
    print("-" * 60)

    if summary is None:
        print("No session found.")
        return

    print("Track ID:", summary["track_id"])
    print("Duration:", f"{summary['duration_seconds']:.2f}s")
    print("Total frames:", summary["total_frames"])

    print()
    print("Attention frames:")

    for state, count in summary["attention_frames"].items():
        print(f"{state}: {count}")

    print()
    print("Attention percentages:")

    for state, percentage in summary[
        "attention_percentages"
    ].items():
        print(f"{state}: {percentage:.2f}%")

    print()
    print("Event counts:")

    for event, count in summary["event_counts"].items():
        print(f"{event}: {count}")

    print()
    print("Event history:")

    if not summary["event_history"]:
        print("[]")
    else:
        for event in summary["event_history"]:
            print(
                f"{event['event']} at "
                f"{event['timestamp']:.2f}"
            )


def update_person(
    manager,
    track_id,
    state,
    events,
    timestamp,
):
    attention = {
        "state": state,
        "reason": "test",
        "events": events,
    }

    behavior = {
        "events": events,
    }

    return manager.update_person(
        track_id=track_id,
        attention=attention,
        behavior=behavior,
        timestamp=timestamp,
    )


def main():
    print("=" * 60)
    print("SESSION MANAGER TEST")
    print("=" * 60)

    manager = SessionManager()

    print()
    print("TEST 1: PERSON A SESSION")
    print("=" * 60)

    summary = update_person(
        manager=manager,
        track_id=1,
        state="ATTENTIVE",
        events=[],
        timestamp=100.0,
    )

    summary = update_person(
        manager=manager,
        track_id=1,
        state="ATTENTIVE",
        events=["blink"],
        timestamp=101.0,
    )

    summary = update_person(
        manager=manager,
        track_id=1,
        state="DISTRACTED",
        events=["look_away_started"],
        timestamp=102.0,
    )

    summary = update_person(
        manager=manager,
        track_id=1,
        state="DISTRACTED",
        events=["looking_away"],
        timestamp=103.5,
    )

    summary = update_person(
        manager=manager,
        track_id=1,
        state="YAWNING",
        events=["yawn"],
        timestamp=105.0,
    )

    summary = update_person(
        manager=manager,
        track_id=1,
        state="DROWSY",
        events=["prolonged_eye_closure"],
        timestamp=106.0,
    )

    print_summary(
        "PERSON A FINAL SESSION",
        summary,
    )

    print()
    print("=" * 60)
    print("TEST 2: PERSON B SESSION")
    print("=" * 60)

    update_person(
        manager=manager,
        track_id=2,
        state="ATTENTIVE",
        events=[],
        timestamp=200.0,
    )

    summary_b = update_person(
        manager=manager,
        track_id=2,
        state="ATTENTIVE",
        events=["blink"],
        timestamp=201.0,
    )

    print_summary(
        "PERSON B FINAL SESSION",
        summary_b,
    )

    print()
    print("=" * 60)
    print("TEST 3: TRACK ISOLATION")
    print("=" * 60)

    print(
        "Active track IDs:",
        manager.get_active_track_ids(),
    )

    person_a = manager.get_session(
        track_id=1,
        timestamp=110.0,
    )

    person_b = manager.get_session(
        track_id=2,
        timestamp=210.0,
    )

    print(
        "Person A total frames:",
        person_a["total_frames"],
    )

    print(
        "Person B total frames:",
        person_b["total_frames"],
    )

    print(
        "Person A blinks:",
        person_a["event_counts"]["blinks"],
    )

    print(
        "Person B blinks:",
        person_b["event_counts"]["blinks"],
    )

    print()
    print("=" * 60)
    print("TEST 4: REMOVE SESSION")
    print("=" * 60)

    removed = manager.remove_session(
        track_id=1,
        timestamp=120.0,
    )

    print_summary(
        "REMOVED PERSON A SESSION",
        removed,
    )

    print(
        "Active track IDs after removal:",
        manager.get_active_track_ids(),
    )

    print()
    print("=" * 60)
    print("TEST 5: FULL RESET")
    print("=" * 60)

    manager.reset()

    print(
        "Active track IDs after reset:",
        manager.get_active_track_ids(),
    )

    print()
    print("=" * 60)
    print("ALL SESSION MANAGER TESTS COMPLETED")
    print("=" * 60)


if __name__ == "__main__":
    main()