from pathlib import Path

import cv2
import mediapipe as mp


class FaceLandmarker:
    """
    Extracts facial landmarks using the modern
    MediaPipe Tasks FaceLandmarker API.
    """

    def __init__(
        self,
        model_path: str | None = None,
        num_faces: int = 8,
    ):
        if model_path is None:
            project_root = Path(__file__).resolve().parents[2]

            model_path = (
                project_root
                / "models"
                / "face_landmarker.task"
            )

        self.model_path = Path(model_path)

        if not self.model_path.exists():
            raise FileNotFoundError(
                f"Face landmarker model not found: "
                f"{self.model_path}"
            )

        base_options = mp.tasks.BaseOptions(
            model_asset_path=str(self.model_path)
        )

        options = mp.tasks.vision.FaceLandmarkerOptions(
            base_options=base_options,
            running_mode=mp.tasks.vision.RunningMode.IMAGE,
            num_faces=num_faces,
            output_face_blendshapes=False,
            output_facial_transformation_matrixes=True,
        )

        self.landmarker = (
            mp.tasks.vision.FaceLandmarker
            .create_from_options(options)
        )

    def detect(self, frame):
        """
        Detect facial landmarks.

        Args:
            frame: BGR OpenCV frame.

        Returns:
            MediaPipe FaceLandmarkerResult
        """

        if frame is None:
            raise ValueError("Frame cannot be None")

        if len(frame.shape) != 3:
            raise ValueError(
                "Expected a color image frame"
            )

        rgb_frame = cv2.cvtColor(
            frame,
            cv2.COLOR_BGR2RGB,
        )

        mp_image = mp.Image(
            image_format=mp.ImageFormat.SRGB,
            data=rgb_frame,
        )

        return self.landmarker.detect(mp_image)

    def close(self):
        """Release MediaPipe resources."""
        self.landmarker.close()