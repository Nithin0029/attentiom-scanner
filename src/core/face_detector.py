from pathlib import Path

import cv2
import mediapipe as mp


class FaceDetector:
    """
    Face detector using the modern MediaPipe Tasks API.
    """

    def __init__(
        self,
        model_path: str | None = None,
        min_detection_confidence: float = 0.5,
    ):
        if model_path is None:
            project_root = Path(__file__).resolve().parents[2]
            model_path = (
                project_root
                / "models"
                / "blaze_face_short_range.tflite"
            )

        self.model_path = Path(model_path)

        if not self.model_path.exists():
            raise FileNotFoundError(
                f"Face detector model not found: {self.model_path}"
            )

        base_options = mp.tasks.BaseOptions(
            model_asset_path=str(self.model_path)
        )

        options = mp.tasks.vision.FaceDetectorOptions(
            base_options=base_options,
            min_detection_confidence=min_detection_confidence,
        )

        self.detector = mp.tasks.vision.FaceDetector.create_from_options(
            options
        )

    def detect(self, frame):
        """
        Detect faces in a BGR OpenCV frame.

        Returns:
            list[dict]:
                {
                    "bbox": [x1, y1, x2, y2],
                    "confidence": float
                }
        """

        if frame is None:
            raise ValueError("Frame cannot be None")

        if len(frame.shape) != 3:
            raise ValueError("Expected a color image frame")

        height, width = frame.shape[:2]

        rgb_frame = cv2.cvtColor(
            frame,
            cv2.COLOR_BGR2RGB,
        )

        mp_image = mp.Image(
            image_format=mp.ImageFormat.SRGB,
            data=rgb_frame,
        )

        result = self.detector.detect(mp_image)

        faces = []

        for detection in result.detections:
            bbox = detection.bounding_box

            x1 = max(0, bbox.origin_x)
            y1 = max(0, bbox.origin_y)

            x2 = min(
                width - 1,
                bbox.origin_x + bbox.width,
            )

            y2 = min(
                height - 1,
                bbox.origin_y + bbox.height,
            )

            if x2 <= x1 or y2 <= y1:
                continue

            if (x2 - x1) < 20 or (y2 - y1) < 20:
                continue

            confidence = 0.0

            if detection.categories:
                confidence = float(
                    detection.categories[0].score
                )

            faces.append(
                {
                    "bbox": [x1, y1, x2, y2],
                    "confidence": confidence,
                }
            )

        return faces

    def close(self):
        """Release MediaPipe resources."""
        self.detector.close()