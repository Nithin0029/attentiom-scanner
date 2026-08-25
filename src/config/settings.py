SMOOTHING_WINDOW_SIZE = 5

BEHAVIOR_CONFIG = {
    "eye_closed_threshold": 0.20,
    "eye_open_threshold": 0.23,
    "yawn_threshold": 0.30,
    "yawn_end_threshold": 0.18,
    "yaw_threshold": 25.0,
    "pitch_threshold": 25.0,
    "prolonged_eye_closure_seconds": 1.5,
    "yawn_min_duration_seconds": 0.5,
    "look_away_min_duration_seconds": 1.0,
}

CAMERA_INDEX = 0
CAMERA_MAX_CONSECUTIVE_FAILURES = 10

WINDOW_NAME = "Attention Scanner"

COLOR_ATTENTIVE = (0, 220, 0)
COLOR_DISTRACTED = (0, 165, 255)
COLOR_DROWSY = (0, 0, 235)
COLOR_YAWNING = (235, 0, 235)
COLOR_DEFAULT = (220, 220, 220)
COLOR_BG_PANEL = (18, 18, 18)
COLOR_PANEL_BORDER = (60, 60, 60)
COLOR_TEXT_PRIMARY = (245, 245, 245)
COLOR_TEXT_MUTED = (160, 160, 160)

# UI Aesthetics & Layout Configuration
COLOR_RUNNING = (0, 230, 255)
COLOR_CARD_HEADER_BG = (30, 30, 30)
COLOR_HEADER_BG = (15, 15, 15)
COLOR_HEADER_BORDER = (45, 45, 45)
COLOR_SCORE_BAR_BG = (40, 40, 40)
COLOR_SCORE_BAR_BORDER = (90, 90, 90)

FONT_SCALE_HEADER = 0.65
FONT_SCALE_SUBHEADER = 0.42
FONT_SCALE_STATUS = 0.45
FONT_SCALE_CARD_TITLE = 0.52
FONT_SCALE_BODY = 0.41
FONT_SCALE_SMALL = 0.40

PANEL_ALPHA_DEFAULT = 0.80
PANEL_ALPHA_HEADER = 0.85
CARD_DEFAULT_WIDTH = 340