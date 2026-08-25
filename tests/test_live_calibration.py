import cv2

from src.pipeline.realtime_pipeline import RealtimePipeline


def put_text(
    frame,
    text,
    x,
    y,
    scale=0.6,
    color=(255, 255, 255),
    thickness=2,
):
    cv2.putText(
        frame,
        text,
        (x, y),
        cv2.FONT_HERSHEY_SIMPLEX,
        scale,
        color,
        thickness,
        cv2.LINE_AA,
    )


def main():
    print("=" * 60)
    print("LIVE FEATURE CALIBRATION")
    print("=" * 60)
    print("Press Q to quit.")
    print()

    pipeline = RealtimePipeline(
        smoothing_window_size=5,
        behavior_config={
            "eye_closed_threshold": 0.18,
            "eye_open_threshold": 0.22,

            "yawn_threshold": 0.30,
            "yawn_end_threshold": 0.18,

            "yaw_threshold": 25.0,
            "pitch_threshold": 20.0,

            "prolonged_eye_closure_seconds": 1.5,
            "yawn_min_duration_seconds": 0.8,
            "look_away_min_duration_seconds": 1.0,
        },

        tracker_max_lost_frames=180,
        tracker_max_distance=180.0,
    )

    camera = cv2.VideoCapture(0)

    if not camera.isOpened():
        print("ERROR: Could not open webcam.")
        pipeline.close()
        return

    print("Camera opened successfully.")

    try:
        while True:
            success, frame = camera.read()

            if not success:
                print("ERROR: Could not read frame.")
                break

            result = pipeline.process_frame(frame)

            display = frame.copy()


            put_text(
                display,
                "LIVE CALIBRATION MODE",
                20,
                35,
                scale=0.8,
                color=(0, 255, 255),
            )

            put_text(
                display,
                "Q = Quit",
                20,
                65,
                scale=0.5,
                color=(200, 200, 200),
            )


            people = result["people"]

            if not people:
                put_text(
                    display,
                    "NO FACE DETECTED",
                    20,
                    105,
                    scale=0.8,
                    color=(0, 0, 255),
                )

            for person in people:


                track_id = person["track_id"]

                x1, y1, x2, y2 = person["bbox"]

                features = person["features"]

                analysis = person["analysis"]

                behavior = analysis["behavior"]

                events = behavior["events"]


                cv2.rectangle(
                    display,
                    (x1, y1),
                    (x2, y2),
                    (0, 255, 0),
                    2,
                )


                put_text(
                    display,
                    f"ID: {track_id}",
                    x1,
                    max(30, y1 - 15),
                    scale=0.7,
                    color=(0, 255, 0),
                )


                info_x = x1
                info_y = y2 + 30

                if info_y + 260 > display.shape[0]:
                    info_x = 20
                    info_y = 110

                put_text(
                    display,
                    f"EAR: {features['ear']:.3f}",
                    info_x,
                    info_y,
                )

                put_text(
                    display,
                    f"MAR: {features['mar']:.3f}",
                    info_x,
                    info_y + 30,
                )

                put_text(
                    display,
                    f"Yaw: {features['yaw']:.1f}",
                    info_x,
                    info_y + 60,
                )

                put_text(
                    display,
                    f"Pitch: {features['pitch']:.1f}",
                    info_x,
                    info_y + 90,
                )

                put_text(
                    display,
                    f"Roll: {features['roll']:.1f}",
                    info_x,
                    info_y + 120,
                )


                state_y = info_y + 160

                eyes_state = (
                    "CLOSED"
                    if behavior["eyes_closed"]
                    else "OPEN"
                )

                mouth_state = (
                    "OPEN"
                    if behavior["mouth_open"]
                    else "CLOSED"
                )

                looking_state = (
                    "AWAY"
                    if behavior["looking_away"]
                    else "FORWARD"
                )

                put_text(
                    display,
                    f"Eyes: {eyes_state}",
                    info_x,
                    state_y,
                    scale=0.6,
                )

                put_text(
                    display,
                    f"Mouth: {mouth_state}",
                    info_x,
                    state_y + 30,
                    scale=0.6,
                )

                put_text(
                    display,
                    f"Looking: {looking_state}",
                    info_x,
                    state_y + 60,
                    scale=0.6,
                )


                if events:

                    put_text(
                        display,
                        "EVENTS:",
                        info_x,
                        state_y + 95,
                        scale=0.55,
                        color=(0, 0, 255),
                    )

                    put_text(
                        display,
                        ", ".join(events),
                        info_x,
                        state_y + 120,
                        scale=0.55,
                        color=(0, 0, 255),
                    )


            cv2.imshow(
                "Attention Scanner - Live Calibration",
                display,
            )

            key = cv2.waitKey(1) & 0xFF

            if key == ord("q"):
                break

    finally:
        camera.release()
        cv2.destroyAllWindows()
        pipeline.close()

        print()
        print("Calibration session closed.")


if __name__ == "__main__":
    main()