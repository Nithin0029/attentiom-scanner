from src.analysis.analysis_manager import AnalysisManager


def print_result(label, result):
    print(f"\n{label}")
    print("-" * 55)

    print("Track ID:", result["track_id"])
    print("Warmed up:", result["is_warmed_up"])

    print("\nSmoothed features:")

    for key, value in result["smoothed_features"].items():
        print(f"{key}: {value:.3f}")

    print("\nBehavior:")
    print("Eyes closed:", result["behavior"]["eyes_closed"])
    print(
        "Eye closure duration:",
        f"{result['behavior']['eye_closure_duration']:.2f}s",
    )
    print("Mouth open:", result["behavior"]["mouth_open"])
    print("Looking away:", result["behavior"]["looking_away"])
    print(
        "Look away duration:",
        f"{result['behavior']['look_away_duration']:.2f}s",
    )
    print("Events:", result["behavior"]["events"])


def update_person(
    manager,
    track_id,
    timestamp,
    ear=0.35,
    mar=0.10,
    yaw=0.0,
    pitch=0.0,
    roll=0.0,
):
    return manager.update_features(
        track_id=track_id,
        ear=ear,
        mar=mar,
        yaw=yaw,
        pitch=pitch,
        roll=roll,
        timestamp=timestamp,
    )


def main():
    manager = AnalysisManager(
        window_size=3,
        behavior_config={
            "eye_closed_threshold": 0.20,
            "eye_open_threshold": 0.23,
            "yawn_threshold": 0.45,
            "yawn_end_threshold": 0.30,
            "yaw_threshold": 25.0,
            "pitch_threshold": 25.0,
            "prolonged_eye_closure_seconds": 1.5,
            "yawn_min_duration_seconds": 0.5,
            "look_away_min_duration_seconds": 1.0,
        },
    )

    print("=" * 60)
    print("ANALYSIS MANAGER INTEGRATION TEST")
    print("=" * 60)


    print("\nPERSON A - TRACK ID 1")
    print("Testing eye closure after temporal smoothing")

    result = update_person(
        manager,
        track_id=1,
        timestamp=0.0,
        ear=0.35,
    )
    print_result("Frame 1 - eyes open", result)

    result = update_person(
        manager,
        track_id=1,
        timestamp=0.1,
        ear=0.35,
    )
    print_result("Frame 2 - eyes open", result)

    result = update_person(
        manager,
        track_id=1,
        timestamp=0.2,
        ear=0.18,
    )
    print_result(
        "Frame 3 - closure starts, smoothing delays detection",
        result,
    )

    result = update_person(
        manager,
        track_id=1,
        timestamp=0.3,
        ear=0.18,
    )
    print_result(
        "Frame 4 - eyes remain closed",
        result,
    )

    result = update_person(
        manager,
        track_id=1,
        timestamp=0.4,
        ear=0.18,
    )
    print_result(
        "Frame 5 - should now detect eyes closed",
        result,
    )


    print("\n" + "=" * 60)
    print("PERSON B - TRACK ID 2")
    print("Testing look-away after temporal smoothing")
    print("=" * 60)

    result = update_person(
        manager,
        track_id=2,
        timestamp=0.0,
        yaw=0.0,
    )
    print_result("Frame 1 - looking forward", result)

    result = update_person(
        manager,
        track_id=2,
        timestamp=0.1,
        yaw=35.0,
    )
    print_result(
        "Frame 2 - turns away, smoothing delays detection",
        result,
    )

    result = update_person(
        manager,
        track_id=2,
        timestamp=0.5,
        yaw=35.0,
    )
    print_result(
        "Frame 3 - still away",
        result,
    )

    result = update_person(
        manager,
        track_id=2,
        timestamp=1.3,
        yaw=35.0,
    )
    print_result(
        "Frame 4 - should cross yaw threshold",
        result,
    )

    result = update_person(
        manager,
        track_id=2,
        timestamp=2.5,
        yaw=35.0,
    )
    print_result(
        "Frame 5 - should detect prolonged looking away",
        result,
    )

    result = update_person(
        manager,
        track_id=2,
        timestamp=3.0,
        yaw=35.0,
    )
    print_result(
        "Frame 6 - should NOT repeat looking_away event",
        result,
    )


    print("\n" + "=" * 60)
    print("TRACK ISOLATION CHECK")
    print("=" * 60)

    print("\nActive track IDs:", manager.get_active_track_ids())
    print("Track 1 warmed up:", manager.is_warmed_up(1))
    print("Track 2 warmed up:", manager.is_warmed_up(2))


    print("\n" + "=" * 60)
    print("REMOVE TRACK 1")
    print("=" * 60)

    manager.remove_track(1)

    print("Active track IDs:", manager.get_active_track_ids())


    print("\n" + "=" * 60)
    print("FULL RESET")
    print("=" * 60)

    manager.reset()

    print("Active track IDs:", manager.get_active_track_ids())

    print("\n" + "=" * 60)
    print("ANALYSIS MANAGER TEST COMPLETED")
    print("=" * 60)


if __name__ == "__main__":
    main()