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

    print("EAR test started.")
    print("Press ESC to exit.")

    while True:
        success, frame = camera.read()

        if not success:
            break

        result = landmarker.detect(frame)

        for face_landmarks in result.face_landmarks:

            features = extractor.extract_ear(
                face_landmarks
            )

            left_ear = features["left_ear"]
            right_ear = features["right_ear"]
            average_ear = features["average_ear"]

            cv2.putText(
                frame,
                f"Left EAR: {left_ear:.3f}",
                (10, 30),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.7,
                (255, 255, 255),
                2,
            )

            cv2.putText(
                frame,
                f"Right EAR: {right_ear:.3f}",
                (10, 60),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.7,
                (255, 255, 255),
                2,
            )

            cv2.putText(
                frame,
                f"Average EAR: {average_ear:.3f}",
                (10, 90),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.7,
                (255, 255, 255),
                2,
            )

        cv2.imshow(
            "EAR Test",
            frame,
        )

        if cv2.waitKey(1) & 0xFF == 27:
            break

    camera.release()
    landmarker.close()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()