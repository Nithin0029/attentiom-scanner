# Model Files Directory

This directory contains pre-trained Machine Learning model files used by the Attention Scanner pipeline:

1. `blaze_face_short_range.tflite`
   - **Purpose**: MediaPipe BlazeFace short-range face detection model.
   - **Usage**: Used by `src/core/face_detector.py` to locate face bounding boxes in webcam frames.

2. `face_landmarker.task`
   - **Purpose**: MediaPipe Face Landmarker bundle model.
   - **Usage**: Used by `src/core/face_landmarker.py` to extract 468 3D facial landmarks for EAR, MAR, and head pose estimation.

**Note**: Keep these files in the `models/` directory. They are required at runtime when initializing `FaceDetector` and `FaceLandmarker`.
