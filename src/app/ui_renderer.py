import cv2
from src.config.settings import (
    CARD_DEFAULT_WIDTH,
    COLOR_ATTENTIVE,
    COLOR_BG_PANEL,
    COLOR_DEFAULT,
    COLOR_DISTRACTED,
    COLOR_DROWSY,
    COLOR_PANEL_BORDER,
    COLOR_RUNNING,
    COLOR_TEXT_PRIMARY,
    COLOR_YAWNING,
    FONT_SCALE_BODY,
    FONT_SCALE_CARD_TITLE,
    FONT_SCALE_HEADER,
    FONT_SCALE_SMALL,
    FONT_SCALE_STATUS,
    FONT_SCALE_SUBHEADER,
    PANEL_ALPHA_DEFAULT,
    PANEL_ALPHA_HEADER,
)


def get_state_color(state):
    if state == "ATTENTIVE":
        return COLOR_ATTENTIVE
    if state == "DISTRACTED":
        return COLOR_DISTRACTED
    if state == "DROWSY":
        return COLOR_DROWSY
    if state == "YAWNING":
        return COLOR_YAWNING
    return COLOR_DEFAULT


def format_duration(seconds):
    if seconds is None:
        seconds = 0.0
    try:
        sec = max(0, int(seconds))
    except (ValueError, TypeError):
        sec = 0

    hours = sec // 3600
    minutes = (sec % 3600) // 60
    remaining_seconds = sec % 60

    if hours > 0:
        return f"{hours:02d}:{minutes:02d}:{remaining_seconds:02d}"
    return f"{minutes:02d}:{remaining_seconds:02d}"


def draw_panel(
    frame,
    x1,
    y1,
    x2,
    y2,
    bg_color=COLOR_BG_PANEL,
    border_color=COLOR_PANEL_BORDER,
    alpha=PANEL_ALPHA_DEFAULT,
):
    frame_h, frame_w = frame.shape[:2]
    x1 = max(0, min(int(x1), frame_w - 1))
    x2 = max(x1 + 1, min(int(x2), frame_w))
    y1 = max(0, min(int(y1), frame_h - 1))
    y2 = max(y1 + 1, min(int(y2), frame_h))

    overlay = frame.copy()
    cv2.rectangle(overlay, (x1, y1), (x2, y2), bg_color, -1)
    cv2.addWeighted(overlay, alpha, frame, 1.0 - alpha, 0, frame)
    cv2.rectangle(frame, (x1, y1), (x2, y2), border_color, 1)


def draw_header(frame, fps, people_count, session_duration=0.0):
    frame_h, frame_w = frame.shape[:2]
    header_h = max(54, int(frame_h * 0.08)) if frame_h < 400 else 54

    draw_panel(
        frame,
        x1=0,
        y1=0,
        x2=frame_w,
        y2=header_h,
        bg_color=(15, 15, 15),
        border_color=(45, 45, 45),
        alpha=PANEL_ALPHA_HEADER,
    )

    cv2.putText(
        frame,
        "ATTENTION SCANNER",
        (15, 24),
        cv2.FONT_HERSHEY_SIMPLEX,
        FONT_SCALE_HEADER,
        COLOR_RUNNING,
        2,
        cv2.LINE_AA,
    )

    cv2.putText(
        frame,
        "Real-time Engagement Monitoring",
        (15, 43),
        cv2.FONT_HERSHEY_SIMPLEX,
        FONT_SCALE_SUBHEADER,
        (170, 170, 170),
        1,
        cv2.LINE_AA,
    )

    fps_val = float(fps) if fps is not None else 0.0
    dur_str = format_duration(session_duration)
    status_str = f"FPS: {fps_val:.1f}  |  PEOPLE: {people_count}  |  SESSION: {dur_str}  |  RUNNING"
    (text_w, _), _ = cv2.getTextSize(
        status_str, cv2.FONT_HERSHEY_SIMPLEX, FONT_SCALE_STATUS, 1
    )

    status_x = max(240, frame_w - text_w - 20)
    if status_x < frame_w - 5:
        cv2.putText(
            frame,
            status_str,
            (status_x, 32),
            cv2.FONT_HERSHEY_SIMPLEX,
            FONT_SCALE_STATUS,
            (240, 240, 240),
            1,
            cv2.LINE_AA,
        )


def draw_summary_panel(frame, people, fps, session_duration=0.0):
    count = len(people) if people is not None else 0
    draw_header(
        frame=frame,
        fps=fps,
        people_count=count,
        session_duration=session_duration,
    )


def draw_score_bar(frame, x, y, width, height, score, max_score=100.0):
    try:
        val = float(score) if score is not None else 0.0
    except (ValueError, TypeError):
        val = 0.0

    val = max(0.0, min(float(max_score), val))

    if val >= 75.0:
        bar_color = COLOR_ATTENTIVE
    elif val >= 50.0:
        bar_color = COLOR_DISTRACTED
    else:
        bar_color = COLOR_DROWSY

    x, y = int(x), int(y)
    width, height = int(width), int(height)

    cv2.rectangle(frame, (x, y), (x + width, y + height), (40, 40, 40), -1)

    fill_width = int((val / max_score) * width)
    if fill_width > 0:
        cv2.rectangle(
            frame,
            (x, y),
            (x + fill_width, y + height),
            bar_color,
            -1,
        )

    cv2.rectangle(frame, (x, y), (x + width, y + height), (90, 90, 90), 1)

    score_text = f"{val:.1f}"
    cv2.putText(
        frame,
        score_text,
        (x + width + 8, y + height - 2),
        cv2.FONT_HERSHEY_SIMPLEX,
        FONT_SCALE_SUBHEADER,
        COLOR_TEXT_PRIMARY,
        1,
        cv2.LINE_AA,
    )


def draw_no_person_notice(frame):
    frame_h, frame_w = frame.shape[:2]
    notice_w, notice_h = 320, 36
    x1 = (frame_w - notice_w) // 2
    y1 = 65
    x2 = x1 + notice_w
    y2 = y1 + notice_h

    draw_panel(
        frame,
        x1,
        y1,
        x2,
        y2,
        bg_color=(20, 20, 20),
        border_color=(60, 60, 60),
        alpha=0.75,
    )

    msg = "Waiting for a person... (No face detected)"
    (tw, th), _ = cv2.getTextSize(msg, cv2.FONT_HERSHEY_SIMPLEX, 0.43, 1)
    text_x = x1 + (notice_w - tw) // 2
    text_y = y1 + (notice_h + th) // 2 - 2

    cv2.putText(
        frame,
        msg,
        (text_x, text_y),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.43,
        (180, 180, 180),
        1,
        cv2.LINE_AA,
    )


def draw_controls_hint(frame):
    frame_h, frame_w = frame.shape[:2]
    hint_str = "Q / ESC  Quit Scanner"
    (tw, th), _ = cv2.getTextSize(hint_str, cv2.FONT_HERSHEY_SIMPLEX, FONT_SCALE_SUBHEADER, 1)

    box_w = tw + 20
    box_h = th + 12
    x1 = max(0, frame_w - box_w - 12)
    y1 = max(0, frame_h - box_h - 10)
    x2 = min(frame_w, x1 + box_w)
    y2 = min(frame_h, y1 + box_h)

    draw_panel(
        frame,
        x1,
        y1,
        x2,
        y2,
        bg_color=(15, 15, 15),
        border_color=(50, 50, 50),
        alpha=0.80,
    )

    cv2.putText(
        frame,
        hint_str,
        (x1 + 10, y1 + th + 4),
        cv2.FONT_HERSHEY_SIMPLEX,
        FONT_SCALE_SUBHEADER,
        (200, 200, 200),
        1,
        cv2.LINE_AA,
    )


def draw_person_overlay(frame, person, index=0, total_people=1):
    frame_height, frame_width = frame.shape[:2]

    bbox = person.get("bbox", (0, 0, 10, 10))
    x1, y1, x2, y2 = bbox
    track_id = person.get("track_id", index + 1)
    features = person.get("features", {})
    analysis = person.get("analysis", {})
    behavior = analysis.get("behavior", {}) if isinstance(analysis, dict) else {}
    attention = person.get("attention", {})
    session = person.get("session", {})

    state = attention.get("state", "UNKNOWN") if isinstance(attention, dict) else "UNKNOWN"
    reason = attention.get("reason", "N/A") if isinstance(attention, dict) else "N/A"
    events = behavior.get("events", []) if isinstance(behavior, dict) else []

    color = get_state_color(state)

    # Draw face box
    bx1 = max(0, min(int(x1), frame_width - 1))
    by1 = max(0, min(int(y1), frame_height - 1))
    bx2 = max(bx1 + 1, min(int(x2), frame_width))
    by2 = max(by1 + 1, min(int(y2), frame_height))
    cv2.rectangle(frame, (bx1, by1), (bx2, by2), color, 2)

    # Header banner over bbox
    header_text = f"ID: {track_id} | {state}"
    (text_w, text_h), _ = cv2.getTextSize(
        header_text, cv2.FONT_HERSHEY_SIMPLEX, FONT_SCALE_CARD_TITLE, 2
    )

    banner_x2 = min(frame_width - 2, bx1 + text_w + 16)
    banner_y1 = max(56, by1 - text_h - 12)
    banner_y2 = max(banner_y1 + text_h + 10, by1)

    cv2.rectangle(frame, (bx1, banner_y1), (banner_x2, banner_y2), color, -1)

    text_y = banner_y1 + text_h + 3
    cv2.putText(
        frame,
        header_text,
        (bx1 + 7, text_y),
        cv2.FONT_HERSHEY_SIMPLEX,
        FONT_SCALE_CARD_TITLE,
        (0, 0, 0),
        2,
        cv2.LINE_AA,
    )

    # Behavior indicators
    indicators = []
    if isinstance(behavior, dict):
        if behavior.get("eyes_closed"):
            duration = behavior.get("eye_closure_duration", 0.0)
            indicators.append(f"Eyes Closed ({duration:.1f}s)")
        if behavior.get("mouth_open"):
            duration = behavior.get("mouth_open_duration", 0.0)
            indicators.append(f"Mouth Open ({duration:.1f}s)")
        if behavior.get("looking_away"):
            duration = behavior.get("look_away_duration", 0.0)
            indicators.append(f"Looking Away ({duration:.1f}s)")

    active_str = ", ".join(indicators) if indicators else "None"
    events_str = ", ".join(events) if events else "None"

    attention_score = person.get("attention_score", {})
    score = attention_score.get("score", 100.0) if isinstance(attention_score, dict) else 100.0

    session_duration = session.get("duration_seconds", 0.0) if isinstance(session, dict) else 0.0
    attention_percentages = session.get("attention_percentages", {}) if isinstance(session, dict) else {}
    event_counts = session.get("event_counts", {}) if isinstance(session, dict) else {}

    attentive_percent = attention_percentages.get("ATTENTIVE", 0.0) if isinstance(attention_percentages, dict) else 0.0
    distracted_percent = attention_percentages.get("DISTRACTED", 0.0) if isinstance(attention_percentages, dict) else 0.0
    drowsy_percent = attention_percentages.get("DROWSY", 0.0) if isinstance(attention_percentages, dict) else 0.0
    yawning_percent = attention_percentages.get("YAWNING", 0.0) if isinstance(attention_percentages, dict) else 0.0

    blinks = event_counts.get("blinks", 0) if isinstance(event_counts, dict) else 0
    yawns = event_counts.get("yawns", 0) if isinstance(event_counts, dict) else 0
    prolonged_eye_closures = event_counts.get("prolonged_eye_closures", 0) if isinstance(event_counts, dict) else 0
    look_away_events = event_counts.get("look_away_events", 0) if isinstance(event_counts, dict) else 0

    ear_val = features.get("ear", 0.0) if isinstance(features, dict) else 0.0
    mar_val = features.get("mar", 0.0) if isinstance(features, dict) else 0.0
    yaw_val = features.get("yaw", 0.0) if isinstance(features, dict) else 0.0
    pitch_val = features.get("pitch", 0.0) if isinstance(features, dict) else 0.0

    info_lines = [
        f"Session: {format_duration(session_duration)}",
        f"EAR: {ear_val:.3f} | MAR: {mar_val:.3f}",
        f"Yaw: {yaw_val:.1f} | Pitch: {pitch_val:.1f}",
        f"Attentive: {attentive_percent:.1f}% | Distracted: {distracted_percent:.1f}%",
        f"Drowsy: {drowsy_percent:.1f}% | Yawning: {yawning_percent:.1f}%",
        f"Blinks: {blinks} | Yawns: {yawns}",
        f"Look Away: {look_away_events} | Closures: {prolonged_eye_closures}",
        f"Active: {active_str}",
        f"Reason: {reason}",
        f"Events: {events_str}",
    ]

    card_width = min(CARD_DEFAULT_WIDTH, max(200, frame_width - 20))
    line_height = 18
    total_info_height = len(info_lines) * line_height + 42

    # Horizontal positioning with multi-person offset
    base_x = bx1
    if total_people > 1 and index > 0:
        base_x = base_x + (index * 30)

    card_x1 = max(10, min(base_x, frame_width - card_width - 10))
    card_x2 = min(frame_width - 5, card_x1 + card_width)

    # Vertical positioning with frame edge check
    info_y = by2 + 10
    if info_y + total_info_height > frame_height - 35:
        info_y = max(60, by1 - total_info_height - 10)

    card_y1 = max(56, min(info_y, frame_height - total_info_height - 5))
    card_y2 = min(frame_height - 5, card_y1 + total_info_height)

    draw_panel(
        frame,
        card_x1,
        card_y1,
        card_x2,
        card_y2,
        bg_color=COLOR_BG_PANEL,
        border_color=color,
        alpha=PANEL_ALPHA_DEFAULT,
    )

    cv2.putText(
        frame,
        "ATTENTION SCORE",
        (card_x1 + 10, card_y1 + 18),
        cv2.FONT_HERSHEY_SIMPLEX,
        FONT_SCALE_SMALL,
        (180, 180, 180),
        1,
        cv2.LINE_AA,
    )

    score_bar_w = max(40, card_width - 180)
    draw_score_bar(
        frame,
        x=card_x1 + 125,
        y=card_y1 + 8,
        width=score_bar_w,
        height=14,
        score=score,
    )

    y_curr = card_y1 + 36
    for line in info_lines:
        if y_curr + line_height > card_y2:
            break
        line_color = COLOR_TEXT_PRIMARY
        if "Attentive:" in line:
            line_color = (220, 245, 220)
        elif "Active:" in line:
            line_color = (255, 230, 180)

        cv2.putText(
            frame,
            line,
            (card_x1 + 10, y_curr),
            cv2.FONT_HERSHEY_SIMPLEX,
            FONT_SCALE_BODY,
            line_color,
            1,
            cv2.LINE_AA,
        )
        y_curr += line_height
