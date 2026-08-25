import cv2

from src.core.face_landmarker import FaceLandmarker


def main():
    landmarker = FaceLandmarker()

    camera = cv2.VideoCapture(
        0,
        cv2.CAP_DSHOW,
    )

    if not camera.isOpened():
        print("ERROR: Could not open camera.")
        landmarker.close()
        return

    print("Camera started.")
    print("Press ESC to exit.")

    while True:
        success, frame = camera.read()

        if not success:
            print("ERROR: Failed to read frame.")
            break

        result = landmarker.detect(frame)

        face_count = len(
            result.face_landmarks
        )

        cv2.putText(
            frame,
            f"Faces with landmarks: {face_count}",
            (10, 30),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.8,
            (255, 255, 255),
            2,
        )

        height, width = frame.shape[:2]

        for face_landmarks in result.face_landmarks:

            for landmark in face_landmarks:

                x = int(landmark.x * width)
                y = int(landmark.y * height)

                if (
                    0 <= x < width
                    and 0 <= y < height
                ):
                    cv2.circle(
                        frame,
                        (x, y),
                        1,
                        (0, 255, 0),
                        -1,
                    )

        cv2.imshow(
            "Face Landmarks Test",
            frame,
        )

        if cv2.waitKey(1) & 0xFF == 27:
            break

    camera.release()
    landmarker.close()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()