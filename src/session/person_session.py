class PersonSession:
    def __init__(self, track_id, start_time):
        self.track_id = track_id
        self.start_time = start_time
        self.last_seen_time = start_time

        self.total_frames = 0

        self.attentive_frames = 0
        self.distracted_frames = 0
        self.drowsy_frames = 0
        self.yawning_frames = 0

        self.total_blinks = 0
        self.total_yawns = 0
        self.total_prolonged_eye_closures = 0
        self.total_look_away_events = 0

        self.event_history = []

    def update(self, timestamp, attention, behavior):
        self.last_seen_time = timestamp
        self.total_frames += 1

        state = attention.get("state", "ATTENTIVE")
        events = behavior.get("events", [])

        if state == "ATTENTIVE":
            self.attentive_frames += 1

        elif state == "DISTRACTED":
            self.distracted_frames += 1

        elif state == "DROWSY":
            self.drowsy_frames += 1

        elif state == "YAWNING":
            self.yawning_frames += 1

        for event in events:
            self.event_history.append(
                {
                    "event": event,
                    "timestamp": timestamp,
                }
            )

            if event == "blink":
                self.total_blinks += 1

            elif event == "yawn":
                self.total_yawns += 1

            elif event == "prolonged_eye_closure":
                self.total_prolonged_eye_closures += 1

            elif event == "looking_away":
                self.total_look_away_events += 1

    def get_duration(self, timestamp=None):
        if timestamp is None:
            timestamp = self.last_seen_time

        return max(0.0, timestamp - self.start_time)

    def get_summary(self, timestamp=None):
        duration = self.get_duration(timestamp)

        if self.total_frames == 0:
            attentive_percentage = 0.0
            distracted_percentage = 0.0
            drowsy_percentage = 0.0
            yawning_percentage = 0.0
        else:
            attentive_percentage = (
                self.attentive_frames / self.total_frames
            ) * 100

            distracted_percentage = (
                self.distracted_frames / self.total_frames
            ) * 100

            drowsy_percentage = (
                self.drowsy_frames / self.total_frames
            ) * 100

            yawning_percentage = (
                self.yawning_frames / self.total_frames
            ) * 100

        return {
            "track_id": self.track_id,
            "start_time": self.start_time,
            "last_seen_time": self.last_seen_time,
            "duration_seconds": duration,
            "total_frames": self.total_frames,
            "attention_frames": {
                "ATTENTIVE": self.attentive_frames,
                "DISTRACTED": self.distracted_frames,
                "DROWSY": self.drowsy_frames,
                "YAWNING": self.yawning_frames,
            },
            "attention_percentages": {
                "ATTENTIVE": attentive_percentage,
                "DISTRACTED": distracted_percentage,
                "DROWSY": drowsy_percentage,
                "YAWNING": yawning_percentage,
            },
            "event_counts": {
                "blinks": self.total_blinks,
                "yawns": self.total_yawns,
                "prolonged_eye_closures": (
                    self.total_prolonged_eye_closures
                ),
                "look_away_events": (
                    self.total_look_away_events
                ),
            },
            "event_history": self.event_history.copy(),
        }