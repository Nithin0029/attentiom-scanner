class AttentionScore:
    def __init__(
        self,
        distracted_weight=0.5,
        drowsy_weight=1.0,
        yawning_weight=0.75,
    ):
        self.distracted_weight = distracted_weight
        self.drowsy_weight = drowsy_weight
        self.yawning_weight = yawning_weight

    def calculate(self, session_summary):
        if not session_summary:
            session_summary = {}

        percentages = session_summary.get("attention_percentages", {})

        attentive = percentages.get("ATTENTIVE", 0.0)
        distracted = percentages.get("DISTRACTED", 0.0)
        drowsy = percentages.get("DROWSY", 0.0)
        yawning = percentages.get("YAWNING", 0.0)

        penalty = (
            distracted * self.distracted_weight
            + drowsy * self.drowsy_weight
            + yawning * self.yawning_weight
        )

        score = 100.0 - penalty
        score = max(0.0, min(100.0, score))

        return {
            "score": round(score, 2),
            "attentive_percentage": round(attentive, 2),
            "distracted_percentage": round(distracted, 2),
            "drowsy_percentage": round(drowsy, 2),
            "yawning_percentage": round(yawning, 2),
        }
