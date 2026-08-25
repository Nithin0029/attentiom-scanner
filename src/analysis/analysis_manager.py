from src.analysis.temporal_smoother import TemporalSmoother
from src.analysis.behavior_analyzer import BehaviorAnalyzer
from src.analysis.attention_analyzer import AttentionAnalyzer


class AnalysisManager:
    def __init__(
        self,
        window_size=5,
        behavior_config=None,
    ):
        self.window_size = window_size
        self.behavior_config = behavior_config or {}
        self.track_states = {}

    def update_features(
        self,
        track_id,
        ear,
        mar,
        yaw,
        pitch,
        roll,
        timestamp=None,
    ):
        if track_id not in self.track_states:
            self._create_track_state(track_id)

        track_state = self.track_states[track_id]

        smoother = track_state["smoother"]
        behavior_analyzer = track_state["behavior_analyzer"]
        attention_analyzer = track_state["attention_analyzer"]

        smoothed_features = smoother.update(
            ear=ear,
            mar=mar,
            yaw=yaw,
            pitch=pitch,
            roll=roll,
        )

        behavior = behavior_analyzer.update(
            features=smoothed_features,
            timestamp=timestamp,
            raw_mar=mar,
        )

        attention = attention_analyzer.analyze(behavior)

        return {
            "track_id": track_id,
            "is_warmed_up": smoother.is_warmed_up(),
            "smoothed_features": smoothed_features,
            "behavior": behavior,
            "attention": attention,
        }

    def is_warmed_up(self, track_id):
        if track_id not in self.track_states:
            return False

        return self.track_states[track_id]["smoother"].is_warmed_up()

    def remove_track(self, track_id):
        if track_id in self.track_states:
            del self.track_states[track_id]

    def get_active_track_ids(self):
        return list(self.track_states.keys())

    def reset(self):
        self.track_states.clear()

    def _create_track_state(self, track_id):
        self.track_states[track_id] = {
            "smoother": TemporalSmoother(
                window_size=self.window_size
            ),
            "behavior_analyzer": BehaviorAnalyzer(
                **self.behavior_config
            ),
            "attention_analyzer": AttentionAnalyzer(),
        }