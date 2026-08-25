import copy
import time


class SessionHistory:
    def __init__(self):
        self.history = []

    def add_completed_session(
        self,
        track_id,
        session_summary,
        attention_score,
        completed_at=None,
    ):
        if completed_at is None:
            completed_at = time.time()

        record = {
            "track_id": track_id,
            "session": copy.deepcopy(session_summary),
            "attention_score": copy.deepcopy(attention_score),
            "completed_at": completed_at,
        }

        self.history.append(record)

        return copy.deepcopy(record)

    def get_all_sessions(self):
        return copy.deepcopy(self.history)

    def get_latest_session(self):
        if not self.history:
            return None

        return copy.deepcopy(self.history[-1])

    def get_sessions_by_track_id(self, track_id):
        filtered = [
            item for item in self.history if item["track_id"] == track_id
        ]
        return copy.deepcopy(filtered)

    def clear(self):
        self.history.clear()

    def __len__(self):
        return len(self.history)
