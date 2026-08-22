import cv2

from src.core.face_landmarker import FaceLandmarker
from src.core.feature_extractor import FeatureExtractor


def main():
    landmarker = FaceLandmarker()
    extractor = FeatureExtractor()

    camera = cv2.VideoCapture(
        0,
        cv2.CAP_DSHOW,
    )

    if not camera.isOpened():
        print("ERROR: Could not open camera.")
        landmarker.close()
        return

    print("Head pose test started.")
    print("Press ESC to exit.")

    while True:
        success, frame = camera.read()

        if not success:
            break

        frame_height, frame_width = frame.shape[:2]

        result = landmarker.detect(frame)

        for face_landmarks in result.face_landmarks:

            pose = extractor.calculate_head_pose(
                face_landmarks,
                frame_width,
                frame_height,
            )

            yaw = pose["yaw"]
            pitch = pose["pitch"]
            roll = pose["roll"]

            cv2.putText(
                frame,
                f"Yaw: {yaw:.1f}",
                (10, 40),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.8,
                (255, 255, 255),
                2,
            )

            cv2.putText(
                frame,
                f"Pitch: {pitch:.1f}",
                (10, 80),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.8,
                (255, 255, 255),
                2,
            )

            cv2.putText(
                frame,
                f"Roll: {roll:.1f}",
                (10, 120),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.8,
                (255, 255, 255),
                2,
            )

        cv2.imshow(
            "Head Pose Test",
            frame,
        )

        if cv2.waitKey(1) & 0xFF == 27:
            break

    camera.release()
    landmarker.close()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()