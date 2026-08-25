from src.analysis.behavior_analyzer import BehaviorAnalyzer


def print_result(name, result):
    print(f"\n{name}")
    print("-" * 50)

    print("Eyes closed:", result["eyes_closed"])

    print(
        "Eye closure duration:",
        f"{result['eye_closure_duration']:.2f}s",
    )

    print(
        "Prolonged closure:",
        result["prolonged_eye_closure"],
    )

    print("Mouth open:", result["mouth_open"])

    print(
        "Mouth duration:",
        f"{result['mouth_open_duration']:.2f}s",
    )

    print("Looking away:", result["looking_away"])

    print(
        "Look away duration:",
        f"{result['look_away_duration']:.2f}s",
    )

    print("Events:", result["events"])


def update(
    analyzer,
    timestamp,
    ear=0.35,
    mar=0.10,
    yaw=0.0,
    pitch=0.0,
    roll=0.0,
):
    """
    Helper function to send one frame of
    simulated facial features to the analyzer.
    """

    features = {
        "ear": ear,
        "mar": mar,
        "yaw": yaw,
        "pitch": pitch,
        "roll": roll,
    }

    return analyzer.update(
        features,
        timestamp=timestamp,
    )


def main():
    analyzer = BehaviorAnalyzer(
        eye_closed_threshold=0.20,
        eye_open_threshold=0.23,
        yawn_threshold=0.30,
        yawn_end_threshold=0.18,
        yaw_threshold=25.0,
        pitch_threshold=25.0,
        prolonged_eye_closure_seconds=1.5,
        yawn_min_duration_seconds=0.5,
        look_away_min_duration_seconds=1.0,
    )

    print("=" * 50)
    print("BEHAVIOR ANALYZER TEST")
    print("=" * 50)


    print("\nTEST 1: BLINK")

    result = update(
        analyzer,
        timestamp=0.0,
        ear=0.35,
    )

    print_result(
        "Eyes initially open",
        result,
    )

    result = update(
        analyzer,
        timestamp=0.1,
        ear=0.18,
    )

    print_result(
        "Eyes close",
        result,
    )

    result = update(
        analyzer,
        timestamp=0.3,
        ear=0.25,
    )

    print_result(
        "Eyes reopen - should detect blink",
        result,
    )


    print("\n" + "=" * 50)
    print("TEST 2: PROLONGED EYE CLOSURE")
    print("=" * 50)

    result = update(
        analyzer,
        timestamp=1.0,
        ear=0.18,
    )

    print_result(
        "Eyes close",
        result,
    )

    result = update(
        analyzer,
        timestamp=2.0,
        ear=0.18,
    )

    print_result(
        "Still closed - 1 second",
        result,
    )

    result = update(
        analyzer,
        timestamp=2.6,
        ear=0.18,
    )

    print_result(
        "Still closed - should detect prolonged closure",
        result,
    )

    result = update(
        analyzer,
        timestamp=2.8,
        ear=0.28,
    )

    print_result(
        "Eyes reopen",
        result,
    )


    print("\n" + "=" * 50)
    print("TEST 3: YAWN")
    print("=" * 50)

    result = update(
        analyzer,
        timestamp=3.0,
        mar=0.10,
    )

    print_result(
        "Mouth closed",
        result,
    )

    result = update(
        analyzer,
        timestamp=3.1,
        mar=0.35,
    )

    print_result(
        "Mouth opens",
        result,
    )

    result = update(
        analyzer,
        timestamp=3.8,
        mar=0.40,
    )

    print_result(
        "Mouth remains open",
        result,
    )

    result = update(
        analyzer,
        timestamp=4.0,
        mar=0.10,
    )

    print_result(
        "Mouth closes - should detect yawn",
        result,
    )


    print("\n" + "=" * 50)
    print("TEST 4: LOOKING AWAY")
    print("=" * 50)

    result = update(
        analyzer,
        timestamp=5.0,
        yaw=0.0,
    )

    print_result(
        "Looking forward",
        result,
    )

    result = update(
        analyzer,
        timestamp=5.1,
        yaw=35.0,
    )

    print_result(
        "Turns head away",
        result,
    )

    result = update(
        analyzer,
        timestamp=5.5,
        yaw=35.0,
    )

    print_result(
        "Still looking away",
        result,
    )

    result = update(
        analyzer,
        timestamp=6.2,
        yaw=35.0,
    )

    print_result(
        "Away long enough - should detect once",
        result,
    )

    result = update(
        analyzer,
        timestamp=7.0,
        yaw=35.0,
    )

    print_result(
        "Still away - should NOT emit again",
        result,
    )

    result = update(
        analyzer,
        timestamp=7.3,
        yaw=5.0,
    )

    print_result(
        "Returns forward",
        result,
    )

    print("\n" + "=" * 50)
    print("ALL TESTS COMPLETED")
    print("=" * 50)


if __name__ == "__main__":
    main()