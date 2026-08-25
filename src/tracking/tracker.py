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

    @property
    def width(self) -> float:
        return abs(self.bbox[2] - self.bbox[0])

    @property
    def height(self) -> float:
        return abs(self.bbox[3] - self.bbox[1])


class FaceTracker:
    """
    Multi-face tracker using nearest-center matching.

    Recently lost tracks are given a larger matching
    distance so a person can briefly leave the frame
    and return without immediately receiving a new ID.
    """

    def __init__(
        self,
        max_lost_frames: int = 60,
        max_distance: float = 150.0,
        lost_track_distance_multiplier: float = 3.0,
    ):
        self.max_lost_frames = max_lost_frames
        self.max_distance = max_distance
        self.lost_track_distance_multiplier = (
            lost_track_distance_multiplier
        )

        self.next_id = 0
        self.tracks: dict[int, Track] = {}

    def update(
        self,
        detections: list[dict],
    ) -> list[Track]:
        """
        Match current detections with existing tracks.

        Active tracks use normal matching distance.

        Recently lost tracks use a larger matching
        distance to improve short-term ID persistence.
        """

        if not detections:
            self._handle_missing_detections()
            return list(self.tracks.values())

        detection_centers = [
            self._get_center(
                detection["bbox"]
            )
            for detection in detections
        ]

        matched_track_ids = set()
        matched_detection_indexes = set()


        sorted_tracks = sorted(
            self.tracks.items(),
            key=lambda item: item[1].lost_frames,
        )

        for track_id, track in sorted_tracks:

            best_index = None
            best_score = float("inf")

            allowed_distance = (
                self._get_allowed_distance(track)
            )

            for index, detection in enumerate(
                detections
            ):
                if index in matched_detection_indexes:
                    continue

                center = detection_centers[index]

                distance = hypot(
                    track.center[0] - center[0],
                    track.center[1] - center[1],
                )

                if distance > allowed_distance:
                    continue

                size_penalty = (
                    self._calculate_size_penalty(
                        track.bbox,
                        detection["bbox"],
                    )
                )

                score = (
                    distance
                    + size_penalty * 50.0
                )

                if score < best_score:
                    best_score = score
                    best_index = index

            if best_index is None:
                continue

            detection = detections[best_index]

            track.bbox = list(
                detection["bbox"]
            )

            track.confidence = (
                detection["confidence"]
            )

            track.lost_frames = 0

            matched_track_ids.add(track_id)

            matched_detection_indexes.add(
                best_index
            )


        for index, detection in enumerate(
            detections
        ):
            if index in matched_detection_indexes:
                continue

            track = Track(
                track_id=self.next_id,
                bbox=list(detection["bbox"]),
                confidence=(
                    detection["confidence"]
                ),
            )

            self.tracks[
                self.next_id
            ] = track

            matched_track_ids.add(
                self.next_id
            )

            self.next_id += 1


        for track_id, track in list(
            self.tracks.items()
        ):
            if track_id in matched_track_ids:
                continue

            track.lost_frames += 1

            if (
                track.lost_frames
                > self.max_lost_frames
            ):
                del self.tracks[track_id]

        return list(
            self.tracks.values()
        )

    def reset(self):
        """
        Remove all tracks and reset IDs.
        """

        self.tracks.clear()
        self.next_id = 0

    def _handle_missing_detections(self):
        """
        Handle a frame where no faces are detected.
        """

        for track_id, track in list(
            self.tracks.items()
        ):
            track.lost_frames += 1

            if (
                track.lost_frames
                > self.max_lost_frames
            ):
                del self.tracks[track_id]

    def _get_allowed_distance(
        self,
        track: Track,
    ) -> float:
        """
        Calculate matching distance.

        A currently visible track uses max_distance.

        A recently lost track gets a progressively larger
        search area, allowing short disappearances without
        immediately losing the ID.
        """

        if track.lost_frames == 0:
            return self.max_distance

        lost_ratio = min(
            track.lost_frames
            / self.max_lost_frames,
            1.0,
        )

        distance_multiplier = (
            1.0
            + (
                self.lost_track_distance_multiplier
                - 1.0
            )
            * lost_ratio
        )

        return (
            self.max_distance
            * distance_multiplier
        )

    @staticmethod
    def _calculate_size_penalty(
        old_bbox: list[int],
        new_bbox: list[int],
    ) -> float:
        """
        Return a penalty based on how different the
        bounding-box sizes are.

        0.0 means very similar sizes.
        Higher values mean greater difference.
        """

        old_width = max(
            1.0,
            abs(old_bbox[2] - old_bbox[0]),
        )

        old_height = max(
            1.0,
            abs(old_bbox[3] - old_bbox[1]),
        )

        new_width = max(
            1.0,
            abs(new_bbox[2] - new_bbox[0]),
        )

        new_height = max(
            1.0,
            abs(new_bbox[3] - new_bbox[1]),
        )

        width_ratio = abs(
            old_width - new_width
        ) / old_width

        height_ratio = abs(
            old_height - new_height
        ) / old_height

        return (
            width_ratio + height_ratio
        )

    @staticmethod
    def _get_center(
        bbox: list[int],
    ) -> tuple[float, float]:

        x1, y1, x2, y2 = bbox

        return (
            (x1 + x2) / 2.0,
            (y1 + y2) / 2.0,
        )