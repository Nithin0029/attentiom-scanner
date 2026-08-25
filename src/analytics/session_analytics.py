import copy
from typing import Any, Dict, List, Optional, Union

from src.reporting.session_report import SessionReport
from src.scoring.attention_score import AttentionScore
from src.session.session_history import SessionHistory


class SessionAnalytics:
    """
    Reusable analytics component operating on completed session history records.
    Produces dashboard-ready aggregate statistics, frame-weighted attention percentages,
    score distributions, best/worst session tracking, and engagement metrics.
    """

    def __init__(self, session_report: Optional[SessionReport] = None):
        self.session_report = session_report or SessionReport()
        self.attention_score = AttentionScore()

    def _unpack_record(
        self, record: Dict[str, Any]
    ) -> tuple[Dict[str, Any], Dict[str, Any]]:
        """
        Unpacks session summary dict and attention score dict from a history record or summary.
        """
        if "session" in record and isinstance(record["session"], dict):
            summary = record["session"]
            score_dict = record.get("attention_score")
        else:
            summary = record
            score_dict = None

        if score_dict is None:
            score_dict = self.attention_score.calculate(summary)

        return summary, score_dict

    def analyze_history(
        self, history: Union[SessionHistory, List[Dict[str, Any]]]
    ) -> Dict[str, Any]:
        """
        Analyzes completed session history records and returns aggregate dashboard statistics.
        Does not mutate the input history records.
        """
        if isinstance(history, SessionHistory):
            records = history.get_all_sessions()
        elif isinstance(history, list):
            records = copy.deepcopy(history)
        else:
            records = []

        total_sessions = len(records)

        if total_sessions == 0:
            return {
                "total_sessions": 0,
                "total_duration_seconds": 0.0,
                "total_frames": 0,
                "average_attention_score": 0.0,
                "best_session": None,
                "worst_session": None,
                "overall_attention_percentages": {
                    "ATTENTIVE": 0.0,
                    "DISTRACTED": 0.0,
                    "DROWSY": 0.0,
                    "YAWNING": 0.0,
                },
                "total_events": {
                    "blinks": 0,
                    "yawns": 0,
                    "prolonged_eye_closures": 0,
                    "look_away_events": 0,
                },
                "score_distribution": {
                    "HIGH": 0,
                    "MODERATE": 0,
                    "LOW": 0,
                },
                "engagement": {
                    "attentive_sessions": 0,
                    "sessions_with_distraction": 0,
                    "sessions_with_drowsiness": 0,
                    "sessions_with_yawning": 0,
                },
            }

        total_duration = 0.0
        total_frames = 0

        score_sum = 0.0
        best_session_info = None
        worst_session_info = None
        best_score = -1.0
        worst_score = 101.0

        total_attentive_frames = 0
        total_distracted_frames = 0
        total_drowsy_frames = 0
        total_yawning_frames = 0

        blinks = 0
        yawns = 0
        prolonged_eye_closures = 0
        look_away_events = 0

        high_count = 0
        moderate_count = 0
        low_count = 0

        attentive_sessions_count = 0
        distraction_sessions_count = 0
        drowsiness_sessions_count = 0
        yawning_sessions_count = 0

        for rec in records:
            summary, score_dict = self._unpack_record(rec)

            track_id = rec.get("track_id", summary.get("track_id", 0))
            duration = summary.get("duration_seconds", 0.0)
            frames = summary.get("total_frames", 0)
            score = score_dict.get("score", 0.0)

            total_duration += duration
            total_frames += frames
            score_sum += score

            if score > best_score:
                best_score = score
                best_session_info = {
                    "track_id": track_id,
                    "score": round(score, 2),
                    "duration_seconds": round(duration, 2),
                }

            if score < worst_score:
                worst_score = score
                worst_session_info = {
                    "track_id": track_id,
                    "score": round(score, 2),
                    "duration_seconds": round(duration, 2),
                }

            att_frames = summary.get("attention_frames", {}).get("ATTENTIVE", 0)
            dis_frames = summary.get("attention_frames", {}).get("DISTRACTED", 0)
            dro_frames = summary.get("attention_frames", {}).get("DROWSY", 0)
            yawn_frames = summary.get("attention_frames", {}).get("YAWNING", 0)

            total_attentive_frames += att_frames
            total_distracted_frames += dis_frames
            total_drowsy_frames += dro_frames
            total_yawning_frames += yawn_frames

            evts = summary.get("event_counts", {})
            blinks += evts.get("blinks", 0)
            yawns += evts.get("yawns", 0)
            prolonged_eye_closures += evts.get("prolonged_eye_closures", 0)
            look_away_events += evts.get("look_away_events", 0)

            rating = self.session_report._determine_rating(score)
            if rating == "HIGH":
                high_count += 1
            elif rating == "MODERATE":
                moderate_count += 1
            elif rating == "LOW":
                low_count += 1

            if frames > 0 and att_frames > max(dis_frames, dro_frames, yawn_frames):
                attentive_sessions_count += 1

            if dis_frames > 0:
                distraction_sessions_count += 1
            if dro_frames > 0:
                drowsiness_sessions_count += 1
            if yawn_frames > 0:
                yawning_sessions_count += 1

        if total_frames > 0:
            overall_pcts = {
                "ATTENTIVE": round((total_attentive_frames / total_frames) * 100, 2),
                "DISTRACTED": round((total_distracted_frames / total_frames) * 100, 2),
                "DROWSY": round((total_drowsy_frames / total_frames) * 100, 2),
                "YAWNING": round((total_yawning_frames / total_frames) * 100, 2),
            }
        else:
            overall_pcts = {
                "ATTENTIVE": 0.0,
                "DISTRACTED": 0.0,
                "DROWSY": 0.0,
                "YAWNING": 0.0,
            }

        avg_score = score_sum / total_sessions if total_sessions > 0 else 0.0

        return {
            "total_sessions": total_sessions,
            "total_duration_seconds": round(total_duration, 2),
            "total_frames": total_frames,
            "average_attention_score": round(avg_score, 2),
            "best_session": best_session_info,
            "worst_session": worst_session_info,
            "overall_attention_percentages": overall_pcts,
            "total_events": {
                "blinks": blinks,
                "yawns": yawns,
                "prolonged_eye_closures": prolonged_eye_closures,
                "look_away_events": look_away_events,
            },
            "score_distribution": {
                "HIGH": high_count,
                "MODERATE": moderate_count,
                "LOW": low_count,
            },
            "engagement": {
                "attentive_sessions": attentive_sessions_count,
                "sessions_with_distraction": distraction_sessions_count,
                "sessions_with_drowsiness": drowsiness_sessions_count,
                "sessions_with_yawning": yawning_sessions_count,
            },
        }
