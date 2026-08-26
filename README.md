# Attention Scanner

Realtime multi-person computer vision attention, drowsiness, and distraction monitoring system built with Python, OpenCV, and MediaPipe — with a FastAPI backend and a React web dashboard for live browser-based monitoring.

---

## Overview

**Attention Scanner** is a real-time computer vision pipeline that detects faces, tracks unique individuals across frames, extracts facial landmarks, analyzes eye/mouth behaviors and head pose, classifies attention states (Attentive, Distracted, Drowsy, Yawning), maintains per-person session metrics, calculates attention scores (0–100), archives completed session histories upon person disappearance, produces aggregate session analytics, and formats/exports session reports (JSON & CSV).

The project ships in two forms that share the same backend pipeline:

1. **Desktop application** (`src/app/main.py`) — an OpenCV window driven directly by a local webcam, for offline/CLI use.
2. **Web application** (`src/api/` + `frontend/`) — a FastAPI backend exposing the same pipeline over HTTP, paired with a React dashboard that streams the browser's webcam to the backend and renders live analytics, session history, and a final summary report.

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
- **Reporting & Export**: Plain-text summary reports and interactive export to JSON (`.json`) and CSV (`.csv`) in `reports/` (desktop app).
- **Web Dashboard**: Live camera feed with bounding-box overlays per tracked face, real-time per-person attention cards, session history browser, and a final analytics summary after stopping a scan.

---

## Tech Stack

| Layer | Technology |
|---|---|
| Computer Vision | OpenCV, MediaPipe Tasks (Face Detector, Face Landmarker) |
| Backend API | FastAPI, Uvicorn |
| Frontend | React 18, Vite |
| Language | Python 3.10, JavaScript (JSX) |

---

## Project Architecture

```text
attentiom-scanner/
├── src/
│   ├── core/         # Face detection, 468-landmark mesh, EAR/MAR & head pose extraction
│   ├── tracking/     # Multi-face centroid tracker with lost-frame handling
│   ├── analysis/     # Temporal smoother, behavior analyzer, and attention analyzer
│   ├── pipeline/      # RealtimePipeline orchestrating detection, tracking, analysis, & sessions
│   ├── session/       # PersonSession, SessionManager, and SessionHistory
│   ├── scoring/        # AttentionScore penalty-based scoring model (0 to 100)
│   ├── analytics/     # SessionAnalytics multi-session aggregate statistics
│   ├── reporting/      # SessionReport text formatting, JSON export, and CSV export
│   ├── api/            # FastAPI app, CORS config, and ScannerService (pipeline lifecycle)
│   └── app/             # Desktop OpenCV application launcher (src.app.main)
├── frontend/            # React + Vite web dashboard
│   └── src/
│       ├── components/  # CameraFeed, Header, StatusCards, ScannerControls,
│       │                # LiveMetrics, PersonAnalytics, SessionHistory, FinalSummary
│       └── services/    # scannerApi.js — typed fetch wrapper for the backend API
├── models/              # MediaPipe TFLite model weights
├── reports/             # Output directory for exported JSON and CSV reports (desktop app)
├── tests/               # Automated integration & unit test suite
├── requirements.txt     # Python dependency requirements
└── README.md
```

---

## Requirements

- **Python Version**: Python 3.10 is the recommended and supported runtime environment (due to MediaPipe C++ bindings and OpenCV ABI compatibility).
- **Node.js**: Node 18+ and npm, for the React frontend.
- **Hardware**: Standard USB/laptop webcam (used directly by the desktop app, or via the browser for the web app).
- **Model Files**: Pre-trained MediaPipe face detection and landmarker task models placed in `models/`.

---

## Installation

### Backend setup

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

### Frontend setup

```bash
cd frontend
npm install
```

---

## Model Files

The system requires two model files inside the `models/` directory:

- `models/blaze_face_short_range.tflite`: MediaPipe BlazeFace short-range face detector.
- `models/face_landmarker.task`: MediaPipe Face Landmarker model for 468 3D facial landmarks.

---

## Running the Application

### Web application (FastAPI backend + React dashboard)

Run the backend and frontend in two terminals.

**1. Start the API server** (from the project root, with the virtual environment activated):

```bash
python -m uvicorn src.api.server:app --reload --port 8000
```

The API is available at `http://127.0.0.1:8000`, with interactive docs at `http://127.0.0.1:8000/docs`.

**2. Start the React dev server**:

```bash
cd frontend
npm run dev
```

Open `http://localhost:5173` in a browser, click **Start Scanner**, and grant camera access when prompted.

### Desktop application (OpenCV window)

To launch the live webcam scanner directly, with an on-screen overlay, session tracking, and report exports:

```bash
python -m src.app.main
```

**Controls**:
- **`Q` Key**: Press `Q` while focusing on the video window to quit scanning.
- **Report Export Options** (prompted after quitting): `[J]` JSON, `[C]` CSV, `[B]` both, `[N]` skip export.

---

## How Live Scanning Works (Web Application)

1. The browser captures the webcam via `getUserMedia` and displays it in a `<video>` element (`CameraFeed`).
2. Roughly once per second, the current video frame is drawn to a canvas, encoded as a JPEG blob, and `POST`ed to `/api/scanner/frame` as `multipart/form-data` (field name `file`).
3. On the backend, `ScannerService.process_frame` decodes the image and runs it through `RealtimePipeline`: face detection → multi-face tracking → landmark extraction → EAR/MAR/head-pose feature extraction → temporal smoothing → behavior analysis (blinks, yawns, prolonged eye closure, looking away) → attention classification → per-person session update → attention scoring.
4. The pipeline returns one JSON object per frame containing every detected/tracked person's bounding box, attention state, attention score, and running session statistics, plus the currently active and completed sessions.
5. The frontend renders this response live: bounding boxes and labels are drawn over the video feed, per-person cards show attention score/state/duration/event counts, and summary badges show people-detected and session counts.
6. When a tracked person leaves the frame, their session is automatically finalized and archived into session history, visible under the **Session History** tab (backed by `/api/scanner/summary`).
7. Clicking **Stop Scanner** immediately releases the camera, calls `/api/scanner/stop` to finalize any remaining active sessions, and fetches the final aggregate analytics from `/api/scanner/summary` for the **Final Summary** dashboard.

---

## API Endpoints

| Method | Path | Description |
|---|---|---|
| `GET` | `/health` | Basic API health check. |
| `POST` | `/api/scanner/start` | Starts a new `RealtimePipeline` instance and clears any previous scan's results. |
| `GET` | `/api/scanner/status` | Returns `{ status, running, completed_sessions }`. |
| `POST` | `/api/scanner/frame` | Accepts one JPEG frame (`multipart/form-data`, field `file`) and returns the full per-frame pipeline result. |
| `POST` | `/api/scanner/stop` | Finalizes all active sessions and stops the pipeline. |
| `GET` | `/api/scanner/summary` | Returns completed session history and aggregate analytics (works both while running and after stopping). |

---

## Testing

Run the automated headless unit and integration test suites:

```bash
python -m tests.test_api_scanner
python -m tests.test_realtime_pipeline
python -m tests.test_pipeline_scoring_integration
python -m tests.test_pipeline_session_history_integration
python -m tests.test_pipeline_analytics_integration
python -m tests.test_final_summary_integration
python -m tests.test_session_history
python -m tests.test_session_manager
python -m tests.test_session_analytics
python -m tests.test_session_report
python -m tests.test_attention_score
```

Build the frontend to verify it compiles cleanly:

```bash
cd frontend
npm run build
```

---

## Limitations

- Frame capture runs on a fixed client-side interval (roughly 1 frame/second) rather than a persistent stream, so very fast behavior changes between captured frames are not observed.
- The `FaceLandmarker` in the pipeline is configured for a single face per crop; multi-person landmark accuracy depends on the upstream tracker producing clean, non-overlapping crops.
- All scanner state is in-memory and per-process — restarting the backend clears any session history that was not already read from `/api/scanner/summary`.
- No authentication/authorization is implemented; the API is intended for local/single-user use.

## Future Improvements

- WebSocket or MJPEG streaming instead of periodic still-frame uploads, for lower latency.
- Persistent storage (database) for session history across backend restarts.
- Multi-session/user support with authentication.
- Configurable detection/behavior thresholds exposed through the dashboard.
