"""
Backward-compatible interactive application runner for RealtimePipeline.
Delegates to the canonical application entry point in src.app.main.
"""

from src.app.main import (
    COLOR_ATTENTIVE,
    COLOR_DEFAULT,
    COLOR_DISTRACTED,
    COLOR_DROWSY,
    COLOR_YAWNING,
    draw_person_overlay,
    draw_summary_panel,
    format_duration,
    get_state_color,
    main,
)

if __name__ == "__main__":
    main()