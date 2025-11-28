# realtime_pipeline.py
# Multi-student realtime classroom engagement pipeline (MediaPipe face detection)
# Self-contained: computes EAR, MAR, head-pose (yaw), iris gaze eye-contact,
# per-track smoothing, two-hand detection, per-student status + "Distraction" field.
#
# Requirements: mediapipe, opencv-python, numpy
# Optional: face_detector.FaceDetector and face_recognition.FaceRecognition (will be used if present)

import time
import traceback
from collections import deque, defaultdict

import cv2
import numpy as np

# try optional local modules (recognizer/detector). If absent, fallbacks used.
USE_CUSTOM_FACE_DETECTOR = False
USE_CUSTOM_FACE_RECOGNIZER = False
try:
    from face_detector import FaceDetector
    USE_CUSTOM_FACE_DETECTOR = True
except Exception:
    FaceDetector = None

try:
    from face_recognition import FaceRecognition
    USE_CUSTOM_FACE_RECOGNIZER = True
except Exception:
    FaceRecognition = None

# try mediapipe
try:
    import mediapipe as mp
except Exception as e:
    print("ERROR: mediapipe is required. Install with `pip install mediapipe`.")
    raise e

# ---------------- CONFIG ----------------
SMOOTH_WINDOW = 8
YAW_THRESHOLD = 20.0           # degrees -> looking away
EYE_CONTACT_MIN = 0.6          # fraction of recent frames with eye-contact
EAR_SLEEP = 0.14
EAR_DROWSY = 0.19
MAR_YAWN = 0.60
HAND_MARGIN = 0.05             # pose margin for wrists above shoulders

# MediaPipe initializations
mp_face_mesh = mp.solutions.face_mesh.FaceMesh(
    static_image_mode=False, max_num_faces=8, refine_landmarks=True,
    min_detection_confidence=0.5, min_tracking_confidence=0.5
)
mp_face_detection = mp.solutions.face_detection.FaceDetection(
    model_selection=1, min_detection_confidence=0.5
)
mp_pose = mp.solutions.pose.Pose(
    static_image_mode=False, model_complexity=1,
    min_detection_confidence=0.5, min_tracking_confidence=0.5
)

# landmark index groups
LEFT_EYE_IDX = [33, 160, 158, 133, 153, 144]
RIGHT_EYE_IDX = [362, 385, 387, 263, 373, 380]
MOUTH_IDX = [13, 14, 78, 308]  # top, bottom, left, right

# ---------------- utilities ----------------
def bbox_center(box):
    x1, y1, x2, y2 = box
    return ((x1 + x2) / 2.0, (y1 + y2) / 2.0)

def get_landmark_pts(lm, idxs, w, h):
    pts = []
    for i in idxs:
        p = lm.landmark[i]
        pts.append((p.x * w, p.y * h))
    return pts

def eye_aspect_ratio(eye):
    eye = np.array(eye, dtype=np.float32)
    A = np.linalg.norm(eye[1] - eye[5])
    B = np.linalg.norm(eye[2] - eye[4])
    C = np.linalg.norm(eye[0] - eye[3])
    return (A + B) / (2.0 * C) if C != 0 else 0.0

def mouth_aspect_ratio(mouth):
    top = np.array(mouth[0])
    bottom = np.array(mouth[1])
    left = np.array(mouth[2])
    right = np.array(mouth[3])
    horiz = np.linalg.norm(left - right)
    vert = np.linalg.norm(top - bottom)
    return (vert / horiz) if horiz != 0 else 0.0

def estimate_head_pose(landmarks, w, h):
    try:
        image_points = np.array([
            (landmarks.landmark[1].x * w, landmarks.landmark[1].y * h),     # nose tip
            (landmarks.landmark[152].x * w, landmarks.landmark[152].y * h), # chin
            (landmarks.landmark[33].x * w, landmarks.landmark[33].y * h),   # left eye outer
            (landmarks.landmark[263].x * w, landmarks.landmark[263].y * h), # right eye outer
            (landmarks.landmark[61].x * w, landmarks.landmark[61].y * h),   # left mouth
            (landmarks.landmark[291].x * w, landmarks.landmark[291].y * h)  # right mouth
        ], dtype="double")

        model_points = np.array([
            (0.0, 0.0, 0.0),
            (0.0, -63.6, -12.5),
            (-43.3, 32.7, -26.0),
            (43.3, 32.7, -26.0),
            (-28.9, -28.9, -24.1),
            (28.9, -28.9, -24.1)
        ], dtype="double")

        focal = w
        cam_matrix = np.array([[focal, 0, w/2],
                               [0, focal, h/2],
                               [0, 0, 1]], dtype="double")
        dist = np.zeros((4, 1))

        ok, rvec, tvec = cv2.solvePnP(model_points, image_points, cam_matrix, dist, flags=cv2.SOLVEPNP_ITERATIVE)
        if not ok:
            return 0.0, 0.0, 0.0

        rmat, _ = cv2.Rodrigues(rvec)
        proj = np.hstack((rmat, tvec))
        _, _, _, _, _, _, euler = cv2.decomposeProjectionMatrix(proj)
        pitch, yaw, roll = euler.flatten()
        return float(pitch), float(yaw), float(roll)
    except Exception:
        return 0.0, 0.0, 0.0

def gaze_from_iris(landmarks, w, h):
    # iris indices available when refine_landmarks=True
    try:
        l = landmarks.landmark[468]
        r = landmarks.landmark[473]
        lx, ly = l.x * w, l.y * h
        rx, ry = r.x * w, r.y * h
        gx = (lx + rx) / 2.0
        gy = (ly + ry) / 2.0
        return gx / w, gy / h
    except Exception:
        return None, None

def is_eye_contact(gx, gy):
    if gx is None or gy is None:
        return False
    return (0.38 <= gx <= 0.62) and (0.35 <= gy <= 0.62)

# temporal eye contact buffer (per-track)
class EyeContactBuffer:
    def __init__(self):
        self.eye_contact_start = None
        self.eye_off_start = None
        self.current_state = "unknown"
        self.min_eye_contact_duration = 0.8
        self.min_eye_off_duration = 0.8

    def update_eye_contact(self, is_contact):
        t = time.time()
        if is_contact:
            self.eye_off_start = None
            if self.eye_contact_start is None:
                self.eye_contact_start = t
            elif t - self.eye_contact_start >= self.min_eye_contact_duration:
                self.current_state = "eye_contact"
        else:
            self.eye_contact_start = None
            if self.eye_off_start is None:
                self.eye_off_start = t
            elif t - self.eye_off_start >= self.min_eye_off_duration:
                self.current_state = "no_eye_contact"

# ---------------- Simple centroid tracker ----------------
class SimpleTracker:
    def __init__(self, max_lost=10):
        self.next_id = 0
        self.tracks = {}   # id -> box
        self.lost = {}
        self.max_lost = max_lost

    def center(self, box):
        x1, y1, x2, y2 = box
        return ((x1 + x2) / 2.0, (y1 + y2) / 2.0)

    def update(self, detections):
        if not self.tracks:
            for d in detections:
                self.tracks[self.next_id] = d
                self.lost[self.next_id] = 0
                self.next_id += 1
            return dict(self.tracks)

        new_tracks = {}
        used = set()
        for tid, old_box in list(self.tracks.items()):
            ox, oy = self.center(old_box)
            best = None
            bestD = float('inf')
            for d in detections:
                if tuple(d) in used:
                    continue
                cx, cy = self.center(d)
                dist = (ox - cx)**2 + (oy - cy)**2
                if dist < bestD:
                    bestD = dist
                    best = d
            if best is not None and bestD < ((old_box[2]-old_box[0])**2 + (old_box[3]-old_box[1])**2)*4 + 10000:
                new_tracks[tid] = best
                used.add(tuple(best))
                self.lost[tid] = 0
            else:
                self.lost[tid] = self.lost.get(tid, 0) + 1
                if self.lost[tid] <= self.max_lost:
                    new_tracks[tid] = old_box

        for d in detections:
            if tuple(d) not in used:
                new_tracks[self.next_id] = d
                self.lost[self.next_id] = 0
                self.next_id += 1

        self.tracks = new_tracks
        return dict(self.tracks)

# ---------------- choose detector & recognizer ----------------
if USE_CUSTOM_FACE_DETECTOR:
    try:
        face_detector = FaceDetector()
        print("Using custom FaceDetector()")
    except Exception:
        face_detector = None
        print("Failed to init custom FaceDetector; will use MediaPipe detection")
else:
    face_detector = None  # we'll use MediaPipe face detection

if USE_CUSTOM_FACE_RECOGNIZER:
    try:
        face_recognizer = FaceRecognition()
        print("Using custom FaceRecognition()")
    except Exception:
        face_recognizer = None
        print("Failed to init custom FaceRecognition; recognizer disabled")
else:
    face_recognizer = None

# ---------------- Main pipeline ----------------
def run_camera(camera_id=0):
    print("▶ Starting Realtime Classroom Analyzer (MediaPipe detector)")
    cap = cv2.VideoCapture(camera_id, cv2.CAP_DSHOW)
    if not cap.isOpened():
        print("❌ Cannot open camera", camera_id)
        return

    tracker = SimpleTracker()

    # smoothing buffers per track
    buf_ear = defaultdict(lambda: deque(maxlen=SMOOTH_WINDOW))
    buf_mar = defaultdict(lambda: deque(maxlen=SMOOTH_WINDOW))
    buf_yaw = defaultdict(lambda: deque(maxlen=SMOOTH_WINDOW))
    buf_eye = defaultdict(lambda: deque(maxlen=SMOOTH_WINDOW))
    ec_buffers = defaultdict(lambda: EyeContactBuffer())

    last_t = time.time()
    print("✔ Camera opened. Press ESC to exit.")

    while True:
        ret, frame = cap.read()
        if not ret:
            print("Frame read failed")
            break

        H, W = frame.shape[:2]
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        # 1) face detection - use custom detector if available else MediaPipe
        boxes = []
        if face_detector is not None:
            try:
                boxes = face_detector.detect(rgb) or []
            except Exception:
                try:
                    boxes = face_detector.detect(frame) or []
                except Exception:
                    boxes = []
        if (not boxes) and mp_face_detection is not None:
            try:
                det_res = mp_face_detection.process(rgb)
                if det_res.detections:
                    for d in det_res.detections:
                        bb = d.location_data.relative_bounding_box
                        x1 = int(max(0, bb.xmin * W))
                        y1 = int(max(0, bb.ymin * H))
                        x2 = int(min(W-1, (bb.xmin + bb.width) * W))
                        y2 = int(min(H-1, (bb.ymin + bb.height) * H))
                        if x2 - x1 > 20 and y2 - y1 > 20:
                            boxes.append([x1, y1, x2, y2])
            except Exception:
                boxes = boxes  # leave as-is

        tracked = tracker.update(boxes)

        # 2) pose (hand raise) once per frame
        left_up = right_up = False
        try:
            pose_res = mp_pose.process(rgb)
            if pose_res.pose_landmarks:
                pl = pose_res.pose_landmarks.landmark
                try:
                    ls = pl[11].y; rs = pl[12].y
                    lw = pl[15].y; rw = pl[16].y
                    left_up = lw < ls - HAND_MARGIN and pl[15].visibility > 0.4
                    right_up = rw < rs - HAND_MARGIN and pl[16].visibility > 0.4
                except Exception:
                    left_up = right_up = False
        except Exception:
            left_up = right_up = False

        # 3) face mesh for all faces (so we can map each mesh to tracked box)
        mesh_map = []
        try:
            mesh_res = mp_face_mesh.process(rgb)
            if mesh_res.multi_face_landmarks:
                for lm in mesh_res.multi_face_landmarks:
                    xs = [p.x for p in lm.landmark]
                    ys = [p.y for p in lm.landmark]
                    mesh_map.append((np.mean(xs) * W, np.mean(ys) * H, lm))
        except Exception:
            mesh_map = []

        # 4) per tracked person -> match nearest mesh and compute metrics
        for tid, box in tracked.items():
            x1, y1, x2, y2 = [int(v) for v in box]
            cx, cy = bbox_center(box)

            # recognition
            usn = "UNKNOWN"
            try:
                if face_recognizer is not None:
                    face_roi = frame[y1:y2, x1:x2]
                    gray = cv2.cvtColor(face_roi, cv2.COLOR_BGR2GRAY)
                    usn, _ = face_recognizer.recognize(gray)
            except Exception:
                usn = "UNKNOWN"

            # find nearest mesh to this bbox centroid
            matched = None
            bestd = float('inf')
            for mx, my, lm in mesh_map:
                d = (mx - cx)**2 + (my - cy)**2
                if d < bestd:
                    bestd = d
                    matched = lm

            # defaults
            ear_v = 0.0
            mar_v = 0.0
            pitch_v = yaw_v = roll_v = 0.0
            gaze_x = gaze_y = None
            eye_contact_flag = False

            if matched is not None:
                try:
                    left_eye = get_landmark_pts(matched, LEFT_EYE_IDX, W, H)
                    right_eye = get_landmark_pts(matched, RIGHT_EYE_IDX, W, H)
                    ear_v = (eye_aspect_ratio(left_eye) + eye_aspect_ratio(right_eye)) / 2.0
                except Exception:
                    ear_v = ear_v

                try:
                    mouth_pts = get_landmark_pts(matched, MOUTH_IDX, W, H)
                    mar_v = mouth_aspect_ratio(mouth_pts)
                except Exception:
                    mar_v = mar_v

                try:
                    pitch_v, yaw_v, roll_v = estimate_head_pose(matched, W, H)
                except Exception:
                    pitch_v, yaw_v, roll_v = 0.0, 0.0, 0.0

                try:
                    gaze_x, gaze_y = gaze_from_iris(matched, W, H)
                    eye_contact_flag = is_eye_contact(gaze_x, gaze_y)
                except Exception:
                    eye_contact_flag = False

            # push into buffers & smooth
            buf_ear[tid].append(ear_v)
            buf_mar[tid].append(mar_v)
            buf_yaw[tid].append(yaw_v)
            buf_eye[tid].append(1 if eye_contact_flag else 0)
            ec_buffers[tid].update_eye_contact(bool(eye_contact_flag))

            sEAR = float(np.mean(buf_ear[tid])) if len(buf_ear[tid]) > 0 else ear_v
            sMAR = float(np.mean(buf_mar[tid])) if len(buf_mar[tid]) > 0 else mar_v
            sYaw = float(np.mean(buf_yaw[tid])) if len(buf_yaw[tid]) > 0 else yaw_v
            contact_ratio = float(np.mean(buf_eye[tid])) if len(buf_eye[tid]) > 0 else (1.0 if eye_contact_flag else 0.0)

            # decide status following priority:
            # Hand raise (notify, not distracted) > Sleeping/Drowsy/Yawning >
            # Disturbed (yaw > threshold or low eye contact) > Engaged
            status = "UNKNOWN"
            reason = ""
            distraction = "OFF"

            # hand raise priority
            if left_up and right_up:
                status = "HANDS RAISED"; reason = "Both hands"; distraction = "OFF"
            elif left_up or right_up:
                status = "HAND RAISED"; reason = "Single hand"; distraction = "OFF"
            else:
                if sEAR < EAR_SLEEP:
                    status = "SLEEPING"; reason = f"EAR {sEAR:.2f}"; distraction = "OFF"
                elif sEAR < EAR_DROWSY:
                    status = "DROWSY"; reason = f"EAR {sEAR:.2f}"; distraction = "OFF"
                elif sMAR > MAR_YAWN:
                    status = "YAWNING"; reason = f"MAR {sMAR:.2f}"; distraction = "OFF"
                else:
                    if abs(sYaw) > YAW_THRESHOLD:
                        status = "DISTRACTED"; reason = f"Looking Away (yaw {sYaw:.1f}°)"; distraction = "ON"
                    elif contact_ratio < EYE_CONTACT_MIN:
                        status = "DISTRACTED"; reason = f"No Eye Contact ({contact_ratio:.2f})"; distraction = "ON"
                    else:
                        status = "ENGAGED"; reason = "Facing + Eye Contact"; distraction = "OFF"

            # draw UI
            color = (0, 200, 50)  # engaged green
            if status == "DISTRACTED":
                color = (0, 165, 255)
            elif status == "SLEEPING":
                color = (0, 0, 255)
            elif status == "DROWSY":
                color = (0, 140, 255)
            elif status == "YAWNING":
                color = (0, 128, 255)
            elif "HAND" in status:
                color = (255, 200, 0)

            cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
            cv2.putText(frame, f"{usn}", (x1, max(0, y1 - 8)),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
            cv2.putText(frame, status, (x1, y2 + 18), cv2.FONT_HERSHEY_SIMPLEX, 0.75, color, 2)
            cv2.putText(frame, f"Reason: {reason}", (x1, y2 + 40), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (220, 220, 220), 1)
            cv2.putText(frame, f"Distraction: {distraction}", (x1, y2 + 60), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (200, 200, 200), 1)
            cv2.putText(frame, f"Yaw:{sYaw:.1f} EAR:{sEAR:.2f} MAR:{sMAR:.2f} CR:{contact_ratio:.2f}",
                        (x1, y2 + 80), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (180, 180, 180), 1)

        # FPS
        now = time.time()
        fps = 1.0 / (now - last_t) if (now - last_t) > 0 else 0.0
        last_t = now
        cv2.putText(frame, f"FPS:{fps:.1f}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)

        cv2.imshow("Realtime Classroom Analyzer - MultiStudent", frame)
        if cv2.waitKey(1) & 0xFF == 27:
            break

    cap.release()
    cv2.destroyAllWindows()
    print("▶ Pipeline stopped.")

if __name__ == "__main__":
    try:
        run_camera(0)
    except Exception:
        print("Unhandled exception:")
        traceback.print_exc()
