# Attention Scanner

Realtime multi-person computer vision attention, drowsiness, and distraction monitoring system built with Python, OpenCV, and MediaPipe.

---

## Overview

**Attention Scanner** is a real-time computer vision pipeline that detects faces, tracks unique individuals across frames, extracts facial landmarks, analyzes eye/mouth behaviors and head pose, classifies attention states (Attentive, Distracted, Drowsy, Yawning), maintains per-person session metrics, calculates attention scores (0–100), archives completed session histories upon person disappearance, produces aggregate session analytics, and formats/exports session reports (JSON & CSV).

---

## Features

- **Realtime Face Detection**: High-speed single/multi-person face detection.
- **Multi-Person Face Tracking**: Centroid-based tracking maintaining stable `track_id` assignments.
- **Facial Landmark Analysis**: 468-point 3D facial landmark mesh extraction.
- **Feature Extraction**:
  - Eye Aspect Ratio (EAR) calculation & eye closure tracking.
  - Mouth Aspect Ratio (MAR) calculation & yawn tracking.
  - Head Pose Estimation (Yaw, Pitch, Roll).
- **Behavior Analysis**: Temporal smoothing and event detection:
  - Blinks
  - Yawns
  - Prolonged eye closures
  - Looking-away events
- **Attention Classification**: Priority-based attention state classification (`ATTENTIVE`, `DISTRACTED`, `DROWSY`, `YAWNING`).
- **Per-Person Session Tracking**: Real-time session state, frame counts, state percentages, and event logs per `track_id`.
- **Attention Scoring**: Weighted penalty calculation scoring session attention from 0.0 to 100.0.
- **Session History & Archiving**: Automatic archiving of completed sessions when individuals disappear or when scanning finishes.
- **Session Analytics**: Frame-weighted attention distribution, total duration/frames, score breakdown (`HIGH`, `MODERATE`, `LOW`), total event counts, and best/worst session tracking.
- **Reporting & Export**: Plain-text summary reports and interactive export to JSON (`.json`) and CSV (`.csv`) in `reports/`.

---

## Project Architecture

```text
attentiom-scanner/
├── src/
│   ├── core/         # Face detection, 468-landmark mesh, EAR/MAR & head pose extraction
│   ├── tracking/     # Multi-face centroid tracker with lost-frame handling
│   ├── analysis/     # Temporal smoother, behavior analyzer, and attention analyzer
│   ├── pipeline/     # RealtimePipeline orchestrating detection, tracking, analysis, & sessions
│   ├── session/      # PersonSession, SessionManager, and SessionHistory
│   ├── scoring/      # AttentionScore penalty-based scoring model (0 to 100)
│   ├── analytics/    # SessionAnalytics multi-session aggregate statistics
│   ├── reporting/    # SessionReport text formatting, JSON export, and CSV export
│   └── app/          # Main application launcher (src.app.main)
├── models/           # MediaPipe TFLite model weights
├── reports/          # Output directory for exported JSON and CSV reports
├── tests/            # Automated integration & unit test suite
├── requirements.txt  # Python dependency requirements
└── README.md
```

---

## Requirements

- **Python Version**: Python 3.10 is the recommended and supported runtime environment (due to MediaPipe C++ bindings and OpenCV ABI compatibility).
- **Hardware**: Standard USB/laptop webcam.
- **Model Files**: Pre-trained MediaPipe face detection and landmarker task models placed in `models/`.

---

## Installation

1. **Clone or open the repository**:
   ```bash
   cd c:\Users\NITHIN\Projects\attentiom-scanner
   ```

2. **Create a virtual environment (Python 3.10)**:
   ```bash
   python -m venv venv
   ```

3. **Activate the virtual environment**:
   - **Windows**:
     ```powershell
     .\venv\Scripts\activate
     ```
   - **Linux / macOS**:
     ```bash
     source venv/bin/activate
     ```

4. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

---

## Model Files

The system requires two model files inside the `models/` directory:

- `models/blaze_face_short_range.tflite`: MediaPipe BlazeFace short-range face detector.
- `models/face_landmarker.task`: MediaPipe Face Landmarker model for 468 3D facial landmarks.

---

## Running the Application

### Official Application Entry Point
To launch the live webcam scanner with real-time UI, session tracking, and report exports:

```bash
python -m src.app.main
```

### Legacy / Development Runner
The legacy runner is available as a thin wrapper:

```bash
python -m tests.test_realtime_pipeline
```

---

## Controls & Export Options

- **`Q` Key**: Press `Q` while focusing on the video window to quit scanning.
- **Report Export Options** (prompted after quitting):
  - `[J]`: Export JSON report to `reports/attention_report_YYYYMMDD_HHMMSS.json`.
  - `[C]`: Export CSV report to `reports/attention_report_YYYYMMDD_HHMMSS.csv`.
  - `[B]`: Export both JSON and CSV reports.
  - `[N]`: Exit without exporting.

---

## Testing

Run the automated headless unit and integration test suites:

```bash
python -m tests.test_session_history
python -m tests.test_attention_score
python -m tests.test_session_report
python -m tests.test_session_analytics
python -m tests.test_pipeline_scoring_integration
python -m tests.test_pipeline_session_history_integration
python -m tests.test_pipeline_analytics_integration
python -m tests.test_final_summary_integration
```
