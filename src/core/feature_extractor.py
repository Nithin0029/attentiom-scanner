import math

import cv2
import numpy as np


class FeatureExtractor:
    """
    Extracts measurable facial features from MediaPipe
    Face Landmarker landmarks.

    Current features:
    - Eye Aspect Ratio (EAR)
    - Mouth Aspect Ratio (MAR)
    - Head Pose (Yaw, Pitch, Roll)
    """

    LEFT_EYE = [33, 160, 158, 133, 153, 144]
    RIGHT_EYE = [362, 385, 387, 263, 373, 380]

    MOUTH_LEFT = 61
    MOUTH_RIGHT = 291
    UPPER_LIP = 13
    LOWER_LIP = 14

    NOSE_TIP = 1
    CHIN = 152
    LEFT_EYE_OUTER = 33
    RIGHT_EYE_OUTER = 263
    MOUTH_LEFT_CORNER = 61
    MOUTH_RIGHT_CORNER = 291


    def calculate_ear(self, landmarks, eye_indices):
        """
        Calculate Eye Aspect Ratio (EAR).

        Higher EAR -> eye is more open.
        Lower EAR  -> eye is more closed.
        """

        p1, p2, p3, p4, p5, p6 = [
            landmarks[index]
            for index in eye_indices
        ]

        vertical_1 = self._distance(p2, p6)
        vertical_2 = self._distance(p3, p5)

        horizontal = self._distance(p1, p4)

        if horizontal == 0:
            return 0.0

        return (
            vertical_1 + vertical_2
        ) / (2.0 * horizontal)

    def extract_ear(self, landmarks):
        """
        Calculate left EAR, right EAR and average EAR.
        """

        left_ear = self.calculate_ear(
            landmarks,
            self.LEFT_EYE,
        )

        right_ear = self.calculate_ear(
            landmarks,
            self.RIGHT_EYE,
        )

        average_ear = (
            left_ear + right_ear
        ) / 2.0

        return {
            "left_ear": left_ear,
            "right_ear": right_ear,
            "average_ear": average_ear,
        }



    def calculate_mar(self, landmarks):
        """
        Calculate Mouth Aspect Ratio (MAR).

        MAR = vertical mouth opening / horizontal mouth width

        Higher MAR -> mouth is more open.
        Lower MAR  -> mouth is more closed.
        """

        mouth_left = landmarks[self.MOUTH_LEFT]
        mouth_right = landmarks[self.MOUTH_RIGHT]

        upper_lip = landmarks[self.UPPER_LIP]
        lower_lip = landmarks[self.LOWER_LIP]

        horizontal = self._distance(
            mouth_left,
            mouth_right,
        )

        vertical = self._distance(
            upper_lip,
            lower_lip,
        )

        if horizontal == 0:
            return 0.0

        return vertical / horizontal

    def extract_mouth_features(self, landmarks):
        """
        Extract mouth-related features.
        """

        mar = self.calculate_mar(landmarks)

        return {
            "mar": mar,
        }



    def calculate_head_pose(
        self,
        landmarks,
        frame_width,
        frame_height,
    ):
        """
        Estimate head pose using MediaPipe facial landmarks
        and OpenCV solvePnP.

        Returns:
            {
                "yaw": float,
                "pitch": float,
                "roll": float
            }
        """



        image_points = np.array(
            [
                self._landmark_to_pixel(
                    landmarks[self.NOSE_TIP],
                    frame_width,
                    frame_height,
                ),

                self._landmark_to_pixel(
                    landmarks[self.CHIN],
                    frame_width,
                    frame_height,
                ),

                self._landmark_to_pixel(
                    landmarks[self.LEFT_EYE_OUTER],
                    frame_width,
                    frame_height,
                ),

                self._landmark_to_pixel(
                    landmarks[self.RIGHT_EYE_OUTER],
                    frame_width,
                    frame_height,
                ),

                self._landmark_to_pixel(
                    landmarks[self.MOUTH_LEFT_CORNER],
                    frame_width,
                    frame_height,
                ),

                self._landmark_to_pixel(
                    landmarks[self.MOUTH_RIGHT_CORNER],
                    frame_width,
                    frame_height,
                ),
            ],
            dtype=np.float64,
        )



        model_points = np.array(
            [
                (0.0, 0.0, 0.0),             # Nose tip
                (0.0, -330.0, -65.0),        # Chin
                (-225.0, 170.0, -135.0),     # Left eye outer
                (225.0, 170.0, -135.0),      # Right eye outer
                (-150.0, -150.0, -125.0),    # Left mouth corner
                (150.0, -150.0, -125.0),     # Right mouth corner
            ],
            dtype=np.float64,
        )


        focal_length = float(frame_width)

        camera_matrix = np.array(
            [
                [
                    focal_length,
                    0,
                    frame_width / 2,
                ],
                [
                    0,
                    focal_length,
                    frame_height / 2,
                ],
                [
                    0,
                    0,
                    1,
                ],
            ],
            dtype=np.float64,
        )

  
        distortion_coefficients = np.zeros(
            (4, 1),
            dtype=np.float64,
        )


        success, rotation_vector, translation_vector = (
            cv2.solvePnP(
                model_points,
                image_points,
                camera_matrix,
                distortion_coefficients,
                flags=cv2.SOLVEPNP_ITERATIVE,
            )
        )

        if not success:
            return {
                "yaw": 0.0,
                "pitch": 0.0,
                "roll": 0.0,
            }

      
        rotation_matrix, _ = cv2.Rodrigues(
            rotation_vector
        )

  
        angles, _, _, _, _, _ = cv2.RQDecomp3x3(
            rotation_matrix
        )


 

        pitch = self._normalize_angle(
            float(angles[0])
        )

        yaw = self._normalize_angle(
            float(angles[1])
        )

        roll = self._normalize_angle(
            float(angles[2])
        )

        return {
            "yaw": yaw,
            "pitch": pitch,
            "roll": roll,
        }

    @staticmethod
    def _normalize_angle(angle):
        """
        Normalize an angle to approximately
        the range -90 to 90 degrees.

        OpenCV can return equivalent Euler angle
        representations such as 176 degrees instead
        of approximately -4 degrees.
        """

        if angle > 90:
            angle -= 180

        elif angle < -90:
            angle += 180

        return angle

    @staticmethod
    def _landmark_to_pixel(
        landmark,
        frame_width,
        frame_height,
    ):
        """
        Convert normalized MediaPipe landmark coordinates
        to image pixel coordinates.
        """

        return (
            landmark.x * frame_width,
            landmark.y * frame_height,
        )

    @staticmethod
    def _distance(point_a, point_b):
        """
        Calculate Euclidean distance between
        two MediaPipe landmarks.
        """

        return math.sqrt(
            (point_a.x - point_b.x) ** 2
            + (point_a.y - point_b.y) ** 2
            + (point_a.z - point_b.z) ** 2
        )