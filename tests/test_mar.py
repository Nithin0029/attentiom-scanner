import cv2

from src.core.face_landmarker import FaceLandmarker
from src.core.feature_extractor import FeatureExtractor


def main():
    landmarker = FaceLandmarker()
    extractor = FeatureExtractor()

    camera = cv2.VideoCapture(0, cv2.CAP_DSHOW)

    if not camera.isOpened():
        print("ERROR: Could not open camera.")
        landmarker.close()
        return

    print("MAR test started.")
    print("Press ESC to exit.")

    while True:
        success, frame = camera.read()

        if not success:
            break

        result = landmarker.detect(frame)

        for face_landmarks in result.face_landmarks:

            features = extractor.extract_mouth_features(
                face_landmarks
            )

            mar = features["mar"]

            cv2.putText(
                frame,
                f"MAR: {mar:.3f}",
                (10, 40),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.9,
                (255, 255, 255),
                2,
            )

        cv2.imshow(
            "MAR Test",
            frame,
        )

        if cv2.waitKey(1) & 0xFF == 27:
            break

    camera.release()
    landmarker.close()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()