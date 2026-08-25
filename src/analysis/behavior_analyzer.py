import time


class BehaviorAnalyzer:
    """
    Interprets temporally smoothed facial features.

    Detects:
    - Eye closure
    - Blinks
    - Prolonged eye closure
    - Looking away
    - Yawning

    This class does not calculate an engagement score.
    It converts facial signals into time-based
    behavioral states and events.
    """

    def __init__(
        self,
        eye_closed_threshold=0.20,
        eye_open_threshold=0.23,
        yawn_threshold=0.30,
        yawn_end_threshold=0.18,
        yaw_threshold=25.0,
        pitch_threshold=25.0,
        prolonged_eye_closure_seconds=1.5,
        yawn_min_duration_seconds=0.5,
        look_away_min_duration_seconds=1.0,
    ):
        self.eye_closed_threshold = eye_closed_threshold
        self.eye_open_threshold = eye_open_threshold

        self.yawn_threshold = yawn_threshold
        self.yawn_end_threshold = yawn_end_threshold

        self.yaw_threshold = yaw_threshold
        self.pitch_threshold = pitch_threshold

        self.prolonged_eye_closure_seconds = (
            prolonged_eye_closure_seconds
        )
        self.yawn_min_duration_seconds = (
            yawn_min_duration_seconds
        )
        self.look_away_min_duration_seconds = (
            look_away_min_duration_seconds
        )

        self.eyes_closed = False
        self.eye_closed_start_time = None
        self.prolonged_eye_closure_detected = False


        self.mouth_open = False
        self.mouth_open_start_time = None


        self.looking_away = False
        self.look_away_start_time = None
        self.look_away_confirmed = False

    def update(
        self,
        features,
        timestamp=None,
        raw_mar=None,
    ):
        if timestamp is None:
            timestamp = time.monotonic()

        ear = features["ear"]
        mar = features["mar"]
        yaw = features["yaw"]
        pitch = features["pitch"]

        if raw_mar is None:
            raw_mar = features.get("raw_mar", mar)

        events = []

        eye_result = self._update_eye_state(
            ear,
            timestamp,
        )

        events.extend(
            eye_result["events"]
        )

        yawn_result = self._update_yawn_state(
            mar,
            timestamp,
        )

        events.extend(
            yawn_result["events"]
        )


        look_result = self._update_look_away_state(
            yaw,
            pitch,
            timestamp,
        )

        events.extend(
            look_result["events"]
        )
        return {
            "ear": ear,
            "mar": mar,
            "yaw": yaw,
            "pitch": pitch,
            "roll": features.get("roll", 0.0),

            "eyes_closed": self.eyes_closed,

            "eye_closure_duration": (
                self._get_duration(
                    self.eye_closed_start_time,
                    timestamp,
                )
                if self.eyes_closed
                else 0.0
            ),

            "prolonged_eye_closure": (
                self.prolonged_eye_closure_detected
            ),

            "mouth_open": self.mouth_open,

            "mouth_open_duration": (
                self._get_duration(
                    self.mouth_open_start_time,
                    timestamp,
                )
                if self.mouth_open
                else 0.0
            ),

            "looking_away": self.looking_away,

            "look_away_duration": (
                self._get_duration(
                    self.look_away_start_time,
                    timestamp,
                )
                if self.looking_away
                else 0.0
            ),

            "events": events,
        }

    def _update_eye_state(
        self,
        ear,
        timestamp,
    ):
        """
        Update eye closure state.
        """

        events = []

        if (
            not self.eyes_closed
            and ear <= self.eye_closed_threshold
        ):
            self.eyes_closed = True
            self.eye_closed_start_time = timestamp
            self.prolonged_eye_closure_detected = False

            events.append(
                "eyes_closed"
            )

        elif self.eyes_closed:

            duration = self._get_duration(
                self.eye_closed_start_time,
                timestamp,
            )

            if (
                duration
                >= self.prolonged_eye_closure_seconds
                and not self.prolonged_eye_closure_detected
            ):
                self.prolonged_eye_closure_detected = True

                events.append(
                    "prolonged_eye_closure"
                )

            if ear >= self.eye_open_threshold:

                if (
                    not self.prolonged_eye_closure_detected
                ):
                    events.append(
                        "blink"
                    )

                else:
                    events.append(
                        "eyes_reopened"
                    )

                self.eyes_closed = False
                self.eye_closed_start_time = None
                self.prolonged_eye_closure_detected = False

        return {
            "events": events
        }

    def _update_yawn_state(
        self,
        mar,
        timestamp,
    ):
        """
        Update mouth and yawn state.
        """

        events = []

        if (
            not self.mouth_open
            and mar >= self.yawn_threshold
        ):
            self.mouth_open = True
            self.mouth_open_start_time = timestamp

            events.append(
                "mouth_opened"
            )

        elif self.mouth_open:

            duration = self._get_duration(
                self.mouth_open_start_time,
                timestamp,
            )

            if mar <= self.yawn_end_threshold:

                if (
                    duration
                    >= self.yawn_min_duration_seconds
                ):
                    events.append(
                        "yawn"
                    )

                self.mouth_open = False
                self.mouth_open_start_time = None

        return {
            "events": events
        }

    def _update_look_away_state(
        self,
        yaw,
        pitch,
        timestamp,
    ):
        """
        Update looking-away state.

        The 'looking_away' event is emitted only once
        after the minimum duration is crossed.
        """

        events = []

        is_away = (
            abs(yaw) >= self.yaw_threshold
            or abs(pitch) >= self.pitch_threshold
        )


        if (
            is_away
            and not self.looking_away
        ):
            self.looking_away = True
            self.look_away_start_time = timestamp
            self.look_away_confirmed = False

            events.append(
                "look_away_started"
            )

        elif (
            is_away
            and self.looking_away
        ):
            duration = self._get_duration(
                self.look_away_start_time,
                timestamp,
            )

            if (
                duration
                >= self.look_away_min_duration_seconds
                and not self.look_away_confirmed
            ):
                self.look_away_confirmed = True

                events.append(
                    "looking_away"
                )

        elif (
            not is_away
            and self.looking_away
        ):
            events.append(
                "look_away_ended"
            )

            self.looking_away = False
            self.look_away_start_time = None
            self.look_away_confirmed = False

        return {
            "events": events
        }

    @staticmethod
    def _get_duration(
        start_time,
        current_time,
    ):
        """
        Calculate elapsed duration safely.
        """

        if start_time is None:
            return 0.0

        return max(
            0.0,
            current_time - start_time,
        )

    def reset(self):
        """
        Reset all behavioral state.
        """

        self.eyes_closed = False
        self.eye_closed_start_time = None
        self.prolonged_eye_closure_detected = False

        self.mouth_open = False
        self.mouth_open_start_time = None

        self.looking_away = False
        self.look_away_start_time = None
        self.look_away_confirmed = False