from src.scoring.attention_score import AttentionScore


def print_result(title, result):
    print()
    print(title)
    print("-" * 50)
    print(f"Score:                 {result['score']:.2f}")
    print(f"Attentive Percentage:  {result['attentive_percentage']:.2f}%")
    print(f"Distracted Percentage: {result['distracted_percentage']:.2f}%")
    print(f"Drowsy Percentage:     {result['drowsy_percentage']:.2f}%")
    print(f"Yawning Percentage:    {result['yawning_percentage']:.2f}%")


def main():
    print("=" * 50)
    print("ATTENTION SCORE TEST")
    print("=" * 50)

    scorer = AttentionScore()

    session_1 = {
        "attention_percentages": {
            "ATTENTIVE": 100.0,
            "DISTRACTED": 0.0,
            "DROWSY": 0.0,
            "YAWNING": 0.0,
        }
    }
    result_1 = scorer.calculate(session_1)
    print_result("TEST 1: 100% ATTENTIVE", result_1)
    assert result_1["score"] == 100.0, f"Expected 100.0, got {result_1['score']}"

    session_2 = {
        "attention_percentages": {
            "ATTENTIVE": 0.0,
            "DISTRACTED": 100.0,
            "DROWSY": 0.0,
            "YAWNING": 0.0,
        }
    }
    result_2 = scorer.calculate(session_2)
    print_result("TEST 2: 100% DISTRACTED", result_2)
    assert result_2["score"] == 50.0, f"Expected 50.0, got {result_2['score']}"

    session_3 = {
        "attention_percentages": {
            "ATTENTIVE": 0.0,
            "DISTRACTED": 0.0,
            "DROWSY": 100.0,
            "YAWNING": 0.0,
        }
    }
    result_3 = scorer.calculate(session_3)
    print_result("TEST 3: 100% DROWSY", result_3)
    assert result_3["score"] == 0.0, f"Expected 0.0, got {result_3['score']}"

    session_4 = {
        "attention_percentages": {
            "ATTENTIVE": 0.0,
            "DISTRACTED": 0.0,
            "DROWSY": 0.0,
            "YAWNING": 100.0,
        }
    }
    result_4 = scorer.calculate(session_4)
    print_result("TEST 4: 100% YAWNING", result_4)
    assert result_4["score"] == 25.0, f"Expected 25.0, got {result_4['score']}"

    session_5 = {
        "attention_percentages": {
            "ATTENTIVE": 70.0,
            "DISTRACTED": 15.0,
            "DROWSY": 10.0,
            "YAWNING": 5.0,
        }
    }
    result_5 = scorer.calculate(session_5)
    print_result("TEST 5: REALISTIC MIXED SESSION", result_5)
    assert result_5["score"] == 78.75, f"Expected 78.75, got {result_5['score']}"

    session_6 = {
        "attention_percentages": {
            "ATTENTIVE": 0.0,
            "DISTRACTED": 50.0,
            "DROWSY": 80.0,
            "YAWNING": 0.0,
        }
    }
    result_6 = scorer.calculate(session_6)
    print_result("TEST 6: SCORE NEVER GOES BELOW 0", result_6)
    assert result_6["score"] == 0.0, f"Expected 0.0, got {result_6['score']}"

    custom_scorer = AttentionScore(
        distracted_weight=0.2,
        drowsy_weight=0.5,
        yawning_weight=0.3,
    )
    session_7 = {
        "attention_percentages": {
            "ATTENTIVE": 40.0,
            "DISTRACTED": 30.0,
            "DROWSY": 20.0,
            "YAWNING": 10.0,
        }
    }
    result_7 = custom_scorer.calculate(session_7)
    print_result("TEST 7: CUSTOM WEIGHTS", result_7)
    assert result_7["score"] == 81.0, f"Expected 81.0, got {result_7['score']}"

    print()
    print("=" * 50)
    print("ALL TESTS COMPLETED SUCCESSFULLY")
    print("=" * 50)


if __name__ == "__main__":
    main()