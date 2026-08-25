import time

from src.core.face_detector import FaceDetector
from src.core.face_landmarker import FaceLandmarker
from src.core.feature_extractor import FeatureExtractor
from src.tracking.tracker import FaceTracker
from src.analysis.analysis_manager import AnalysisManager
from src.analysis.attention_analyzer import AttentionAnalyzer
from src.session.session_manager import SessionManager
from src.session.session_history import SessionHistory
from src.scoring.attention_score import AttentionScore
from src.analytics.session_analytics import SessionAnalytics


class RealtimePipeline:
    def __init__(
        self,
        smoothing_window_size=5,
        behavior_config=None,
        tracker_max_lost_frames=180,
        tracker_max_distance=180.0,
        crop_padding=20,
    ):
        self.face_detector = FaceDetector()

        self.face_tracker = FaceTracker(
            max_lost_frames=tracker_max_lost_frames,
            max_distance=tracker_max_distance,
            lost_track_distance_multiplier=3.0,
        )

        self.face_landmarker = FaceLandmarker(
            num_faces=1
        )

        self.feature_extractor = FeatureExtractor()

        self.analysis_manager = AnalysisManager(
            window_size=smoothing_window_size,
            behavior_config=behavior_config,
        )

        self.attention_analyzer = AttentionAnalyzer()

        self.session_manager = SessionManager()

        self.session_history = SessionHistory()

        self.attention_score = AttentionScore()

        # Aggregates completed session analytics
        self.session_analytics = SessionAnalytics()

        self.crop_padding = crop_padding
        self._is_closed = False

    def process_frame(
        self,
        frame,
        timestamp=None,
    ):
        if frame is None:
            raise ValueError("Frame cannot be None")

        if timestamp is None:
            timestamp = time.time()


        detections = self.face_detector.detect(frame)


        tracks = self.face_tracker.update(detections)

        visible_tracks = [
            track
            for track in tracks
            if track.lost_frames == 0
        ]

        visible_track_ids = {
            track.track_id
            for track in visible_tracks
        }


        managed_analysis_ids = set(
            self.analysis_manager.get_active_track_ids()
        )

        removed_analysis_ids = (
            managed_analysis_ids - visible_track_ids
        )

        for track_id in removed_analysis_ids:
            self.analysis_manager.remove_track(track_id)

        active_session_ids = set(
            self.session_manager.get_active_track_ids()
        )

        removed_session_ids = (
            active_session_ids - visible_track_ids
        )

        for track_id in removed_session_ids:
            session_summary = (
                self.session_manager.get_session(
                    track_id=track_id,
                    timestamp=timestamp,
                )
            )

            if session_summary is not None:
                final_score = (
                    self.attention_score.calculate(
                        session_summary
                    )
                )

                self.session_history.add_completed_session(
                    track_id=track_id,
                    session_summary=session_summary,
                    attention_score=final_score,
                    completed_at=timestamp,
                )

            self.session_manager.remove_session(
                track_id=track_id,
                timestamp=timestamp,
            )


        people = []

        for track in visible_tracks:

            face_crop, crop_info = self._crop_face(
                frame,
                track.bbox,
            )

            if face_crop is None:
                continue

            landmark_result = (
                self.face_landmarker.detect(
                    face_crop
                )
            )

            if not landmark_result.face_landmarks:
                continue

            landmarks = (
                landmark_result.face_landmarks[0]
            )


            ear_features = (
                self.feature_extractor.extract_ear(
                    landmarks
                )
            )


            mouth_features = (
                self.feature_extractor.extract_mouth_features(
                    landmarks
                )
            )


            crop_height, crop_width = (
                face_crop.shape[:2]
            )

            head_pose = (
                self.feature_extractor.calculate_head_pose(
                    landmarks,
                    crop_width,
                    crop_height,
                )
            )


            raw_features = {
                "ear": ear_features["average_ear"],
                "mar": mouth_features["mar"],
                "yaw": head_pose["yaw"],
                "pitch": head_pose["pitch"],
                "roll": head_pose["roll"],
            }


            analysis = (
                self.analysis_manager.update_features(
                    track_id=track.track_id,
                    ear=raw_features["ear"],
                    mar=raw_features["mar"],
                    yaw=raw_features["yaw"],
                    pitch=raw_features["pitch"],
                    roll=raw_features["roll"],
                    timestamp=timestamp,
                )
            )

            behavior = analysis["behavior"]


            attention = (
                self.attention_analyzer.analyze(
                    behavior
                )
            )


            session_summary = (
                self.session_manager.update_person(
                    track_id=track.track_id,
                    attention=attention,
                    behavior=behavior,
                    timestamp=timestamp,
                )
            )

            score_result = (
                self.attention_score.calculate(
                    session_summary
                )
            )


            people.append(
                {
                    "track_id": track.track_id,
                    "bbox": track.bbox,
                    "confidence": track.confidence,
                    "crop_info": crop_info,
                    "features": raw_features,
                    "analysis": analysis,
                    "attention": attention,
                    "session": session_summary,
                    "attention_score": score_result,
                }
            )


        return {
            "timestamp": timestamp,
            "detections": detections,
            "people": people,

            "active_sessions": (
                self.session_manager.get_all_sessions(
                    timestamp
                )
            ),

            "completed_sessions": (
                self.session_history.get_all_sessions()
            ),
        }

    def _crop_face(
        self,
        frame,
        bbox,
    ):
        frame_height, frame_width = frame.shape[:2]

        x1, y1, x2, y2 = bbox

        x1 = max(
            0,
            int(x1 - self.crop_padding),
        )

        y1 = max(
            0,
            int(y1 - self.crop_padding),
        )

        x2 = min(
            frame_width,
            int(x2 + self.crop_padding),
        )

        y2 = min(
            frame_height,
            int(y2 + self.crop_padding),
        )

        if x2 <= x1 or y2 <= y1:
            return None, None

        face_crop = frame[
            y1:y2,
            x1:x2,
        ]

        if face_crop.size == 0:
            return None, None

        return (
            face_crop,
            {
                "x1": x1,
                "y1": y1,
                "x2": x2,
                "y2": y2,
            },
        )

    def get_session(
        self,
        track_id,
        timestamp=None,
    ):
        return self.session_manager.get_session(
            track_id=track_id,
            timestamp=timestamp,
        )

    def get_all_active_sessions(
        self,
        timestamp=None,
    ):
        return self.session_manager.get_all_sessions(
            timestamp=timestamp,
        )

    def get_completed_sessions(self):
        return self.session_history.get_all_sessions()

    def get_latest_completed_session(self):
        return self.session_history.get_latest_session()

    def clear_session_history(self):
        self.session_history.clear()

    def get_session_analytics(self):
        return self.session_analytics.analyze_history(
            self.session_history.get_all_sessions()
        )

    def reset(self):
        self.face_tracker.reset()

        self.analysis_manager.reset()

        self.session_manager.reset()

        self.session_history.clear()

    def close(self):
        if self._is_closed:
            return
        self._is_closed = True
        timestamp = time.time()

        active_track_ids = (
            self.session_manager.get_active_track_ids()
        )

        for track_id in active_track_ids:
            session_summary = (
                self.session_manager.get_session(
                    track_id=track_id,
                    timestamp=timestamp,
                )
            )

            if session_summary is not None:
                final_score = (
                    self.attention_score.calculate(
                        session_summary
                    )
                )

                self.session_history.add_completed_session(
                    track_id=track_id,
                    session_summary=session_summary,
                    attention_score=final_score,
                    completed_at=timestamp,
                )

            self.session_manager.remove_session(
                track_id=track_id,
                timestamp=timestamp,
            )

        self.face_detector.close()
        self.face_landmarker.close()