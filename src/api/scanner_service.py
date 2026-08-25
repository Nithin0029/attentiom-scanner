import threading
from typing import Any, Dict, List, Optional

import numpy as np

from src.pipeline.realtime_pipeline import RealtimePipeline


class ScannerService:
    """
    Manages the lifecycle of the realtime attention scanner for the API.
    """

    def __init__(self) -> None:
        self._pipeline: Optional[RealtimePipeline] = None
        self._is_running = False
        self._lock = threading.Lock()

        # IMPORTANT:
        # These preserve finalized data after pipeline.close() and after
        # the scanner has stopped.
        self._last_completed_sessions: List[Dict[str, Any]] = []
        self._last_analytics: Optional[Dict[str, Any]] = None

    def start(self) -> Dict[str, Any]:
        """
        Start a new scanner session.
        """

        with self._lock:
            if self._is_running:
                return {
                    "success": False,
                    "status": "running",
                    "message": "Scanner is already running.",
                }

            # Starting a new scan should clear results from the previous scan.
            self._last_completed_sessions = []
            self._last_analytics = None

            self._pipeline = RealtimePipeline()
            self._is_running = True

            return {
                "success": True,
                "status": "running",
                "message": "Scanner started successfully.",
            }

    def process_frame(self, frame: np.ndarray) -> Dict[str, Any]:
        """
        Process one decoded OpenCV frame.
        """

        with self._lock:
            if not self._is_running or self._pipeline is None:
                raise RuntimeError("Scanner is not running.")

            return self._pipeline.process_frame(frame)

    def get_status(self) -> Dict[str, Any]:
        """
        Return the current scanner status.
        """

        with self._lock:
            completed_sessions_count = len(self._last_completed_sessions)

            if self._pipeline is not None:
                completed_sessions_count = len(
                    self._pipeline.get_completed_sessions()
                )

            return {
                "status": "running" if self._is_running else "stopped",
                "running": self._is_running,
                "completed_sessions": completed_sessions_count,
            }

    def stop(self) -> Dict[str, Any]:
        """
        Stop the scanner and finalize all active sessions.

        IMPORTANT:
        Results are captured immediately after pipeline.close() so they
        remain available through get_summary() after the pipeline is stopped.
        """

        with self._lock:
            if self._pipeline is None:
                return {
                    "success": False,
                    "status": "stopped",
                    "message": "Scanner is not running.",
                }

            try:
                # 1. Finalize active sessions.
                self._pipeline.close()

                # 2. CRITICAL FIX:
                # Capture completed history AFTER close() finalizes active
                # sessions and BEFORE the pipeline reference is discarded.
                self._last_completed_sessions = (
                    self._pipeline.get_completed_sessions()
                )

                # 3. Capture final analytics from the completed history.
                self._last_analytics = (
                    self._pipeline.get_session_analytics()
                )

            finally:
                self._is_running = False

                # We can safely discard the pipeline because final data has
                # already been preserved above.
                self._pipeline = None

            return {
                "success": True,
                "status": "stopped",
                "message": "Scanner stopped and active sessions finalized.",
            }

    def get_summary(self) -> Dict[str, Any]:
        """
        Return the latest scanner summary.

        While running, return live completed history/analytics.
        After stopping, return the preserved final snapshot.
        """

        with self._lock:
            if self._pipeline is not None:
                return {
                    "completed_sessions": (
                        self._pipeline.get_completed_sessions()
                    ),
                    "analytics": (
                        self._pipeline.get_session_analytics()
                    ),
                }

            return {
                "completed_sessions": self._last_completed_sessions,
                "analytics": self._last_analytics,
            }