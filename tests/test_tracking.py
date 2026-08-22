import cv2

from src.core.face_detector import FaceDetector
from src.tracking.tracker import FaceTracker


def main():
    detector = FaceDetector()
    tracker = FaceTracker()

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

        detections = detector.detect(frame)

        tracks = tracker.update(detections)

        for track in tracks:

            x1, y1, x2, y2 = track.bbox

            cv2.rectangle(
                frame,
                (x1, y1),
                (x2, y2),
                (0, 255, 0),
                2,
            )

            label = (
                f"Student {track.track_id}"
                f" | {track.confidence:.2f}"
            )

            cv2.putText(
                frame,
                label,
                (x1, max(20, y1 - 10)),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.6,
                (0, 255, 0),
                2,
            )

        cv2.putText(
            frame,
            f"Students detected: {len(tracks)}",
            (10, 30),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.8,
            (255, 255, 255),
            2,
        )

        cv2.imshow(
            "Face Detection + Tracking",
            frame,
        )

        if cv2.waitKey(1) & 0xFF == 27:
            break

    camera.release()
    detector.close()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()