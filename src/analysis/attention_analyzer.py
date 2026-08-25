class AttentionAnalyzer:
    def analyze(self, behavior):
        events = behavior.get("events", [])

        if behavior.get("prolonged_eye_closure", False):
            return {
                "state": "DROWSY",
                "reason": "prolonged_eye_closure",
                "events": events,
            }

        if behavior.get("looking_away", False):
            return {
                "state": "DISTRACTED",
                "reason": "looking_away",
                "events": events,
            }

        if "yawn" in events:
            return {
                "state": "YAWNING",
                "reason": "yawn_detected",
                "events": events,
            }

        return {
            "state": "ATTENTIVE",
            "reason": "normal_behavior",
            "events": events,
        }