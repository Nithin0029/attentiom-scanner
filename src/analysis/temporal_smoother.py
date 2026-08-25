from collections import deque


class TemporalSmoother:
    """
    Smooths noisy frame-by-frame facial features using
    a moving average over a fixed-size window.

    Supported features:
    - EAR
    - MAR
    - Yaw
    - Pitch
    - Roll
    """

    def __init__(self, window_size=5):
        """
        Initialize the temporal smoothing buffers.

        Args:
            window_size: Number of recent frames used
                         to calculate the moving average.
        """

        if window_size < 1:
            raise ValueError(
                "window_size must be at least 1"
            )

        self.window_size = window_size

        self.ear_values = deque(
            maxlen=window_size
        )

        self.mar_values = deque(
            maxlen=window_size
        )

        self.yaw_values = deque(
            maxlen=window_size
        )

        self.pitch_values = deque(
            maxlen=window_size
        )

        self.roll_values = deque(
            maxlen=window_size
        )

    def update(
        self,
        ear,
        mar,
        yaw,
        pitch,
        roll,
    ):
        """
        Add new raw feature values and return
        their temporally smoothed values.
        """

        self.ear_values.append(float(ear))
        self.mar_values.append(float(mar))
        self.yaw_values.append(float(yaw))
        self.pitch_values.append(float(pitch))
        self.roll_values.append(float(roll))

        return {
            "ear": self._average(
                self.ear_values
            ),
            "mar": self._average(
                self.mar_values
            ),
            "yaw": self._average(
                self.yaw_values
            ),
            "pitch": self._average(
                self.pitch_values
            ),
            "roll": self._average(
                self.roll_values
            ),
        }

    def reset(self):
        """
        Clear all stored temporal data.

        Useful when:
        - A tracked person leaves the frame
        - A new person gets a new track ID
        - Analysis is restarted
        """

        self.ear_values.clear()
        self.mar_values.clear()
        self.yaw_values.clear()
        self.pitch_values.clear()
        self.roll_values.clear()

    def is_warmed_up(self):
        """
        Return True when the smoothing window
        contains enough frames.
        """

        return len(
            self.ear_values
        ) >= self.window_size

    @staticmethod
    def _average(values):
        """
        Calculate the average of a collection
        of numeric values.
        """

        if not values:
            return 0.0

        return sum(values) / len(values)