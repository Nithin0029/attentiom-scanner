import time
import cv2

from src.config.settings import (
    BEHAVIOR_CONFIG,
    CAMERA_INDEX,
    CAMERA_MAX_CONSECUTIVE_FAILURES,
    COLOR_ATTENTIVE,
    COLOR_DEFAULT,
    COLOR_DISTRACTED,
    COLOR_DROWSY,
    COLOR_YAWNING,
    SMOOTHING_WINDOW_SIZE,
    WINDOW_NAME,
)
from src.pipeline.realtime_pipeline import RealtimePipeline
from src.reporting.session_report import SessionReport
from src.app.ui_renderer import (
    draw_controls_hint,
    draw_header,
    draw_no_person_notice,
    draw_panel,
    draw_person_overlay,
    draw_score_bar,
    draw_summary_panel,
    format_duration,
    get_state_color,
)

__all__ = [
    "COLOR_ATTENTIVE",
    "COLOR_DEFAULT",
    "COLOR_DISTRACTED",
    "COLOR_DROWSY",
    "COLOR_YAWNING",
    "draw_controls_hint",
    "draw_header",
    "draw_no_person_notice",
    "draw_panel",
    "draw_person_overlay",
    "draw_score_bar",
    "draw_summary_panel",
    "format_duration",
    "get_state_color",
    "main",
]


def main():
    print()
    print("=" * 60)
    print("ATTENTION SCANNER")
    print("Real-time Engagement Monitoring")
    print("=" * 60)
    print("Initializing camera...")
    print("Loading vision models...")
    print("Starting realtime analysis...")
    print()
    print("Press Q or ESC to stop scanning.")
    print("=" * 60)
    print()

    try:
        pipeline = RealtimePipeline(
            smoothing_window_size=SMOOTHING_WINDOW_SIZE,
            behavior_config=BEHAVIOR_CONFIG,
        )
    except FileNotFoundError as e:
        print()
        print("=" * 60)
        print("MODEL ERROR")
        print("=" * 60)
        print("ERROR: Required model file not found.")
        print()
        print(e)
        print()
        print("Please verify that all required model files are present in the models/ directory.")
        print("=" * 60)
        return 1

    camera = cv2.VideoCapture(CAMERA_INDEX)

    if not camera.isOpened():
        print()
        print("=" * 60)
        print("CAMERA ERROR")
        print("=" * 60)
        print("ERROR: Could not open webcam.")
        print()
        print("Check that:")
        print("- a webcam is connected")
        print("- another application is not using the camera")
        print(f"- the configured camera index ({CAMERA_INDEX}) is correct")
        print("=" * 60)
        pipeline.close()
        return 1

    prev_time = time.perf_counter()
    start_time = prev_time
    fps = 0.0
    consecutive_failures = 0

    try:
        while True:
            success, frame = camera.read()
            if not success or frame is None:
                consecutive_failures += 1
                if consecutive_failures >= CAMERA_MAX_CONSECUTIVE_FAILURES:
                    print()
                    print(
                        f"ERROR: Failed to read frame from camera {consecutive_failures} consecutive times. Exiting scanner."
                    )
                    break
                time.sleep(0.05)
                continue

            consecutive_failures = 0

            curr_time = time.perf_counter()
            delta = curr_time - prev_time
            prev_time = curr_time

            if delta > 0:
                instant_fps = 1.0 / delta
                fps = (
                    instant_fps
                    if fps == 0.0
                    else (0.9 * fps + 0.1 * instant_fps)
                )

            session_duration = curr_time - start_time

            result = pipeline.process_frame(frame)
            people = result["people"]
            display_frame = frame.copy()

            if people:
                for idx, person in enumerate(people):
                    draw_person_overlay(
                        display_frame,
                        person,
                        index=idx,
                        total_people=len(people),
                    )
            else:
                draw_no_person_notice(display_frame)

            draw_summary_panel(
                display_frame,
                people,
                fps,
                session_duration=session_duration,
            )

            draw_controls_hint(display_frame)

            cv2.imshow(
                WINDOW_NAME if WINDOW_NAME else "Attention Scanner - Live Session Tracking",
                display_frame,
            )

            key = cv2.waitKey(1) & 0xFF
            if key == ord("q") or key == 27:
                break

    finally:
        camera.release()
        cv2.destroyAllWindows()
        pipeline.close()

        completed_sessions = pipeline.get_completed_sessions()
        analytics = pipeline.get_session_analytics()

        reporter = SessionReport()
        session_reports = [
            reporter.generate_session_report(s) for s in completed_sessions
        ]

        summary_text = reporter.format_final_summary_text(
            analytics=analytics,
            session_reports=session_reports,
        )

        print()
        print(summary_text)

        if completed_sessions or analytics.get("total_sessions", 0) > 0:
            reporter.prompt_and_export_reports(
                history_records=completed_sessions,
                analytics=analytics,
            )

        print()
        print("Attention Scanner closed.")
    return 0


if __name__ == "__main__":
    main()