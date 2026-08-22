import cv2

from src.core.face_detector import FaceDetector


def main():
    detector = FaceDetector()

    camera = cv2.VideoCapture(0, cv2.CAP_DSHOW)

    if not camera.isOpened():
        print("ERROR: Could not open camera.")
        detector.close()
        return

    print("Camera started.")
    print("Press ESC to exit.")

    while True:
        success, frame = camera.read()

        if not success:
            print("ERROR: Failed to read frame.")
            break

        faces = detector.detect(frame)

        for index, face in enumerate(faces):
            x1, y1, x2, y2 = face["bbox"]
            confidence = face["confidence"]

            cv2.rectangle(
                frame,
                (x1, y1),
                (x2, y2),
                (0, 255, 0),
                2,
            )

            cv2.putText(
                frame,
                f"Face {index} | {confidence:.2f}",
                (x1, max(20, y1 - 10)),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.6,
                (0, 255, 0),
                2,
            )

        cv2.putText(
            frame,
            f"Faces detected: {len(faces)}",
            (10, 30),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.8,
            (255, 255, 255),
            2,
        )

        cv2.imshow("Face Detector Test", frame)

        if cv2.waitKey(1) & 0xFF == 27:
            break

    camera.release()
    detector.close()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()