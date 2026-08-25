from src.analysis.attention_analyzer import AttentionAnalyzer


def print_result(title, result):
    print()
    print(title)
    print("-" * 50)

    print(f"State:  {result['state']}")
    print(f"Reason: {result['reason']}")
    print(f"Events: {result['events']}")


def main():
    analyzer = AttentionAnalyzer()

    print("=" * 50)
    print("ATTENTION ANALYZER TEST")
    print("=" * 50)


    behavior = {
        "prolonged_eye_closure": False,
        "looking_away": False,
        "events": [],
    }

    result = analyzer.analyze(behavior)

    print_result(
        "TEST 1: NORMAL BEHAVIOR",
        result,
    )


    behavior = {
        "prolonged_eye_closure": False,
        "looking_away": True,
        "events": ["looking_away"],
    }

    result = analyzer.analyze(behavior)

    print_result(
        "TEST 2: DISTRACTED",
        result,
    )


    behavior = {
        "prolonged_eye_closure": False,
        "looking_away": False,
        "events": ["yawn"],
    }

    result = analyzer.analyze(behavior)

    print_result(
        "TEST 3: YAWNING",
        result,
    )


    behavior = {
        "prolonged_eye_closure": True,
        "looking_away": True,
        "events": [
            "prolonged_eye_closure",
            "looking_away",
        ],
    }

    result = analyzer.analyze(behavior)

    print_result(
        "TEST 4: DROWSY HAS HIGHEST PRIORITY",
        result,
    )

    print()
    print("=" * 50)
    print("ALL TESTS COMPLETED")
    print("=" * 50)


if __name__ == "__main__":
    main()