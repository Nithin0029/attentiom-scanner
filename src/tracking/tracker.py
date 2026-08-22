from dataclasses import dataclass
from math import hypot


@dataclass
class Track:
    """
    Represents one tracked face.
    """

    track_id: int
    bbox: list[int]
    confidence: float
    lost_frames: int = 0

    @property
    def center(self) -> tuple[float, float]:
        x1, y1, x2, y2 = self.bbox

        return (
            (x1 + x2) / 2.0,
            (y1 + y2) / 2.0,
        )


class FaceTracker:
    """
    Simple multi-face tracker based on nearest-center matching.

    This is intentionally simple for Phase 1.
    We can replace the tracking algorithm later without
    changing the rest of the CV pipeline.
    """

    def __init__(
        self,
        max_lost_frames: int = 10,
        max_distance: float = 150.0,
    ):
        self.max_lost_frames = max_lost_frames
        self.max_distance = max_distance

        self.next_id = 0
        self.tracks: dict[int, Track] = {}

    def update(self, detections: list[dict]) -> list[Track]:
        """
        Match current detections with existing tracks.

        Args:
            detections:
                [
                    {
                        "bbox": [x1, y1, x2, y2],
                        "confidence": 0.95
                    }
                ]

        Returns:
            Current active tracks.
        """

        if not detections:
            self._handle_missing_detections()
            return list(self.tracks.values())

        detection_centers = [
            self._get_center(detection["bbox"])
            for detection in detections
        ]

        matched_track_ids = set()
        matched_detection_indexes = set()

        # Match existing tracks to the nearest detection.
        for track_id, track in list(self.tracks.items()):

            best_index = None
            best_distance = float("inf")

            for index, center in enumerate(detection_centers):

                if index in matched_detection_indexes:
                    continue

                distance = hypot(
                    track.center[0] - center[0],
                    track.center[1] - center[1],
                )

                if distance < best_distance:
                    best_distance = distance
                    best_index = index

            if (
                best_index is not None
                and best_distance <= self.max_distance
            ):
                detection = detections[best_index]

                track.bbox = detection["bbox"]
                track.confidence = detection["confidence"]
                track.lost_frames = 0

                matched_track_ids.add(track_id)
                matched_detection_indexes.add(best_index)

        # Create new tracks for unmatched detections.
        for index, detection in enumerate(detections):

            if index in matched_detection_indexes:
                continue

            track = Track(
                track_id=self.next_id,
                bbox=detection["bbox"],
                confidence=detection["confidence"],
            )

            self.tracks[self.next_id] = track

            matched_track_ids.add(self.next_id)

            self.next_id += 1

        # Increase lost counter for unmatched existing tracks.
        for track_id, track in list(self.tracks.items()):

            if track_id not in matched_track_ids:
                track.lost_frames += 1

                if track.lost_frames > self.max_lost_frames:
                    del self.tracks[track_id]

        return list(self.tracks.values())

    def reset(self):
        """
        Remove all tracks and reset IDs.
        """

        self.tracks.clear()
        self.next_id = 0

    def _handle_missing_detections(self):
        """
        Handle a frame where no faces were detected.
        """

        for track_id, track in list(self.tracks.items()):

            track.lost_frames += 1

            if track.lost_frames > self.max_lost_frames:
                del self.tracks[track_id]

    @staticmethod
    def _get_center(
        bbox: list[int],
    ) -> tuple[float, float]:

        x1, y1, x2, y2 = bbox

        return (
            (x1 + x2) / 2.0,
            (y1 + y2) / 2.0,
        )