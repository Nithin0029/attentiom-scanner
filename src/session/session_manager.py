import time

from src.session.person_session import PersonSession


class SessionManager:
    def __init__(self):
        self.sessions = {}

    def update_person(
        self,
        track_id,
        attention,
        behavior,
        timestamp=None,
    ):
        if timestamp is None:
            timestamp = time.time()

        if track_id not in self.sessions:
            self.sessions[track_id] = PersonSession(
                track_id=track_id,
                start_time=timestamp,
            )

        session = self.sessions[track_id]

        session.update(
            timestamp=timestamp,
            attention=attention,
            behavior=behavior,
        )

        return session.get_summary(timestamp)

    def get_session(
        self,
        track_id,
        timestamp=None,
    ):
        session = self.sessions.get(track_id)

        if session is None:
            return None

        return session.get_summary(timestamp)

    def get_active_track_ids(self):
        return sorted(self.sessions.keys())

    def get_all_sessions(
        self,
        timestamp=None,
    ):
        return {
            track_id: session.get_summary(timestamp)
            for track_id, session in self.sessions.items()
        }

    def remove_session(
        self,
        track_id,
        timestamp=None,
    ):
        session = self.sessions.pop(
            track_id,
            None,
        )

        if session is None:
            return None

        return session.get_summary(timestamp)

    def reset(self):
        self.sessions.clear()