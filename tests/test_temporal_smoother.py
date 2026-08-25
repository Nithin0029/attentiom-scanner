from src.analysis.temporal_smoother import TemporalSmoother


def main():
    smoother = TemporalSmoother(
        window_size=5
    )

    test_values = [
        {
            "ear": 0.36,
            "mar": 0.02,
            "yaw": 1.0,
            "pitch": -2.0,
            "roll": 0.5,
        },
        {
            "ear": 0.34,
            "mar": 0.03,
            "yaw": 2.0,
            "pitch": -1.0,
            "roll": 1.0,
        },
        {
            "ear": 0.38,
            "mar": 0.02,
            "yaw": 0.0,
            "pitch": -3.0,
            "roll": 0.0,
        },
        {
            "ear": 0.31,
            "mar": 0.04,
            "yaw": 3.0,
            "pitch": -2.0,
            "roll": 1.5,
        },
        {
            "ear": 0.36,
            "mar": 0.03,
            "yaw": 1.0,
            "pitch": -2.0,
            "roll": 0.5,
        },
        {
            "ear": 0.35,
            "mar": 0.02,
            "yaw": 2.0,
            "pitch": -1.0,
            "roll": 1.0,
        },
    ]

    print("Temporal Smoother Test")
    print("-" * 50)

    for index, values in enumerate(
        test_values,
        start=1,
    ):
        smoothed = smoother.update(
            ear=values["ear"],
            mar=values["mar"],
            yaw=values["yaw"],
            pitch=values["pitch"],
            roll=values["roll"],
        )

        print(f"\nFrame {index}")

        print(
            f"Raw EAR:      "
            f"{values['ear']:.3f}"
        )

        print(
            f"Smoothed EAR: "
            f"{smoothed['ear']:.3f}"
        )

        print(
            f"Raw Yaw:      "
            f"{values['yaw']:.2f}"
        )

        print(
            f"Smoothed Yaw: "
            f"{smoothed['yaw']:.2f}"
        )

        print(
            f"Warm: "
            f"{smoother.is_warmed_up()}"
        )

    print("\n" + "-" * 50)

    print(
        "Resetting smoother..."
    )

    smoother.reset()

    print(
        f"Warm after reset: "
        f"{smoother.is_warmed_up()}"
    )


if __name__ == "__main__":
    main()