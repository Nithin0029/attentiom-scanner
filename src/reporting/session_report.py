import csv
import json
import os
from typing import Any, Dict, List, Optional, Union

from src.scoring.attention_score import AttentionScore
from src.session.session_history import SessionHistory


class SessionReport:
    """
    Generates clean reports for individual attention sessions and multi-session history summaries.
    Supports dictionary output, formatted plain-text, JSON export, and CSV export.
    """

    def __init__(self, attention_score_calculator: Optional[AttentionScore] = None):
        self.attention_score_calculator = (
            attention_score_calculator or AttentionScore()
        )

    def _determine_rating(self, score: float) -> str:
        if score >= 75.0:
            return "HIGH"
        elif score >= 50.0:
            return "MODERATE"
        else:
            return "LOW"

    def _unpack_session_input(
        self,
        session: Dict[str, Any],
        attention_score: Optional[Dict[str, Any]] = None,
    ) -> tuple[Dict[str, Any], Dict[str, Any]]:
        """
        Extracts session_summary dict and attention_score dict from input formats.
        """
        if "session" in session and isinstance(session["session"], dict):
            summary = session["session"]
            score = attention_score or session.get("attention_score")
        else:
            summary = session
            score = attention_score

        if score is None:
            score = self.attention_score_calculator.calculate(summary)

        return summary, score

    def generate_session_report(
        self,
        session: Dict[str, Any],
        attention_score: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Generates a clean report dictionary for a single session.
        """
        if not session:
            session = {}

        summary, score_dict = self._unpack_session_input(session, attention_score)

        track_id = session.get("track_id", summary.get("track_id", 0))
        start_time = summary.get("start_time", 0.0)
        last_seen_time = summary.get("last_seen_time", 0.0)
        duration_seconds = summary.get("duration_seconds", 0.0)
        total_frames = summary.get("total_frames", 0)

        attention_frames = summary.get(
            "attention_frames",
            {
                "ATTENTIVE": 0,
                "DISTRACTED": 0,
                "DROWSY": 0,
                "YAWNING": 0,
            },
        )

        attention_percentages = summary.get(
            "attention_percentages",
            {
                "ATTENTIVE": 0.0,
                "DISTRACTED": 0.0,
                "DROWSY": 0.0,
                "YAWNING": 0.0,
            },
        )

        event_counts = summary.get(
            "event_counts",
            {
                "blinks": 0,
                "yawns": 0,
                "prolonged_eye_closures": 0,
                "look_away_events": 0,
            },
        )

        event_history = summary.get("event_history", [])

        score_val = score_dict.get("score", 0.0)
        rating = self._determine_rating(score_val)

        report = {
            "track_id": track_id,
            "start_time": start_time,
            "last_seen_time": last_seen_time,
            "duration_seconds": round(duration_seconds, 2),
            "total_frames": total_frames,
            "attention_score": score_val,
            "rating": rating,
            "score_breakdown": score_dict,
            "attention_frames": attention_frames.copy(),
            "attention_percentages": {
                k: round(v, 2) for k, v in attention_percentages.items()
            },
            "event_counts": event_counts.copy(),
            "event_history": event_history.copy(),
        }

        report["text_summary"] = self.format_session_text(report)
        return report

    def generate_history_report(
        self,
        history: Union[SessionHistory, List[Dict[str, Any]]],
    ) -> Dict[str, Any]:
        """
        Generates an aggregate report dictionary for session history.
        'history' can be a SessionHistory instance or a list of session records.
        """
        if isinstance(history, SessionHistory):
            records = history.get_all_sessions()
        elif isinstance(history, list):
            records = history
        else:
            records = []

        session_reports = [
            self.generate_session_report(rec) for rec in records
        ]

        total_sessions = len(session_reports)
        total_duration = sum(r["duration_seconds"] for r in session_reports)
        total_frames = sum(r["total_frames"] for r in session_reports)

        if total_sessions > 0:
            avg_score = sum(r["attention_score"] for r in session_reports) / total_sessions
        else:
            avg_score = 0.0

        overall_attentive_frames = sum(r["attention_frames"].get("ATTENTIVE", 0) for r in session_reports)
        overall_distracted_frames = sum(r["attention_frames"].get("DISTRACTED", 0) for r in session_reports)
        overall_drowsy_frames = sum(r["attention_frames"].get("DROWSY", 0) for r in session_reports)
        overall_yawning_frames = sum(r["attention_frames"].get("YAWNING", 0) for r in session_reports)

        if total_frames > 0:
            overall_percentages = {
                "ATTENTIVE": round((overall_attentive_frames / total_frames) * 100, 2),
                "DISTRACTED": round((overall_distracted_frames / total_frames) * 100, 2),
                "DROWSY": round((overall_drowsy_frames / total_frames) * 100, 2),
                "YAWNING": round((overall_yawning_frames / total_frames) * 100, 2),
            }
        else:
            overall_percentages = {
                "ATTENTIVE": 0.0,
                "DISTRACTED": 0.0,
                "DROWSY": 0.0,
                "YAWNING": 0.0,
            }

        total_event_counts = {
            "blinks": sum(r["event_counts"].get("blinks", 0) for r in session_reports),
            "yawns": sum(r["event_counts"].get("yawns", 0) for r in session_reports),
            "prolonged_eye_closures": sum(r["event_counts"].get("prolonged_eye_closures", 0) for r in session_reports),
            "look_away_events": sum(r["event_counts"].get("look_away_events", 0) for r in session_reports),
        }

        overall_rating = self._determine_rating(avg_score)

        history_report = {
            "total_sessions": total_sessions,
            "total_duration_seconds": round(total_duration, 2),
            "total_frames": total_frames,
            "average_attention_score": round(avg_score, 2),
            "overall_rating": overall_rating,
            "overall_attention_percentages": overall_percentages,
            "total_event_counts": total_event_counts,
            "sessions": session_reports,
        }

        history_report["text_summary"] = self.format_history_text(history_report)
        return history_report

    def format_session_text(self, report: Dict[str, Any]) -> str:
        """
        Formats a single session report dictionary into a readable plain-text report.
        """
        track_id = report.get("track_id", 0)
        duration = report.get("duration_seconds", 0.0)
        total_frames = report.get("total_frames", 0)
        score = report.get("attention_score", 0.0)
        rating = report.get("rating", "N/A")

        percentages = report.get("attention_percentages", {})
        events = report.get("event_counts", {})

        lines = [
            "==================================================",
            f"SESSION REPORT (Track ID: {track_id})",
            "==================================================",
            f"Duration:         {duration:.2f}s",
            f"Total Frames:     {total_frames}",
            f"Attention Score:  {score:.2f} / 100 ({rating})",
            "",
            "Attention State Breakdown:",
            f"  - Attentive:   {percentages.get('ATTENTIVE', 0.0):6.2f}%",
            f"  - Distracted:  {percentages.get('DISTRACTED', 0.0):6.2f}%",
            f"  - Drowsy:      {percentages.get('DROWSY', 0.0):6.2f}%",
            f"  - Yawning:     {percentages.get('YAWNING', 0.0):6.2f}%",
            "",
            "Detected Events:",
            f"  - Blinks:                 {events.get('blinks', 0)}",
            f"  - Yawns:                  {events.get('yawns', 0)}",
            f"  - Prolonged Eye Closures: {events.get('prolonged_eye_closures', 0)}",
            f"  - Look Away Events:       {events.get('look_away_events', 0)}",
            "==================================================",
        ]
        return "\n".join(lines)

    def format_history_text(self, report: Dict[str, Any]) -> str:
        """
        Formats a history report dictionary into a readable plain-text summary report.
        """
        total_sessions = report.get("total_sessions", 0)
        total_duration = report.get("total_duration_seconds", 0.0)
        total_frames = report.get("total_frames", 0)
        avg_score = report.get("average_attention_score", 0.0)
        overall_rating = report.get("overall_rating", "N/A")

        overall_percentages = report.get("overall_attention_percentages", {})
        total_events = report.get("total_event_counts", {})

        lines = [
            "==================================================",
            "SESSION HISTORY SUMMARY REPORT",
            "==================================================",
            f"Total Sessions:            {total_sessions}",
            f"Total Cumulative Duration: {total_duration:.2f}s",
            f"Total Cumulative Frames:   {total_frames}",
            f"Average Attention Score:   {avg_score:.2f} / 100 ({overall_rating})",
            "",
            "Overall Attention Breakdown:",
            f"  - Attentive:   {overall_percentages.get('ATTENTIVE', 0.0):6.2f}%",
            f"  - Distracted:  {overall_percentages.get('DISTRACTED', 0.0):6.2f}%",
            f"  - Drowsy:      {overall_percentages.get('DROWSY', 0.0):6.2f}%",
            f"  - Yawning:     {overall_percentages.get('YAWNING', 0.0):6.2f}%",
            "",
            "Total Event Totals:",
            f"  - Blinks:                 {total_events.get('blinks', 0)}",
            f"  - Yawns:                  {total_events.get('yawns', 0)}",
            f"  - Prolonged Eye Closures: {total_events.get('prolonged_eye_closures', 0)}",
            f"  - Look Away Events:       {total_events.get('look_away_events', 0)}",
            "==================================================",
        ]
        return "\n".join(lines)

    def export_json(
        self,
        report_data: Dict[str, Any],
        filepath: Optional[str] = None,
        indent: int = 2,
    ) -> str:
        """
        Exports report dictionary to JSON string.
        If filepath is provided, writes the JSON to disk.
        """
        json_str = json.dumps(report_data, indent=indent)

        if filepath:
            parent_dir = os.path.dirname(os.path.abspath(filepath))
            if parent_dir and not os.path.exists(parent_dir):
                os.makedirs(parent_dir, exist_ok=True)

            with open(filepath, "w", encoding="utf-8") as f:
                f.write(json_str)

        return json_str

    def export_csv(
        self,
        history: Union[SessionHistory, List[Dict[str, Any]]],
        filepath: str,
    ) -> str:
        """
        Exports session history data to a CSV file.
        Returns the absolute filepath of the generated CSV file.
        """
        if isinstance(history, SessionHistory):
            records = history.get_all_sessions()
        elif isinstance(history, list):
            records = history
        else:
            records = []

        parent_dir = os.path.dirname(os.path.abspath(filepath))
        if parent_dir and not os.path.exists(parent_dir):
            os.makedirs(parent_dir, exist_ok=True)

        fieldnames = [
            "track_id",
            "start_time",
            "last_seen_time",
            "duration_seconds",
            "total_frames",
            "attention_score",
            "rating",
            "attentive_percentage",
            "distracted_percentage",
            "drowsy_percentage",
            "yawning_percentage",
            "blinks",
            "yawns",
            "prolonged_eye_closures",
            "look_away_events",
        ]

        with open(filepath, "w", newline="", encoding="utf-8") as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()

            for rec in records:
                single_report = self.generate_session_report(rec)
                pcts = single_report.get("attention_percentages", {})
                evts = single_report.get("event_counts", {})

                row = {
                    "track_id": single_report.get("track_id"),
                    "start_time": single_report.get("start_time"),
                    "last_seen_time": single_report.get("last_seen_time"),
                    "duration_seconds": single_report.get("duration_seconds"),
                    "total_frames": single_report.get("total_frames"),
                    "attention_score": single_report.get("attention_score"),
                    "rating": single_report.get("rating"),
                    "attentive_percentage": pcts.get("ATTENTIVE", 0.0),
                    "distracted_percentage": pcts.get("DISTRACTED", 0.0),
                    "drowsy_percentage": pcts.get("DROWSY", 0.0),
                    "yawning_percentage": pcts.get("YAWNING", 0.0),
                    "blinks": evts.get("blinks", 0),
                    "yawns": evts.get("yawns", 0),
                    "prolonged_eye_closures": evts.get("prolonged_eye_closures", 0),
                    "look_away_events": evts.get("look_away_events", 0),
                }
                writer.writerow(row)

        return os.path.abspath(filepath)

    def format_final_summary_text(
        self,
        analytics: Dict[str, Any],
        session_reports: List[Dict[str, Any]],
    ) -> str:
        """
        Formats overall analytics and individual session reports into a complete plain-text final summary.
        """
        total_sessions = analytics.get("total_sessions", 0)

        if total_sessions == 0:
            lines = [
                "============================================================",
                "FINAL ATTENTION SCAN SUMMARY",
                "============================================================",
                "No completed person sessions were recorded.",
                "============================================================",
            ]
            return "\n".join(lines)

        duration = analytics.get("total_duration_seconds", 0.0)
        frames = analytics.get("total_frames", 0)
        avg_score = analytics.get("average_attention_score", 0.0)

        pcts = analytics.get("overall_attention_percentages", {})
        distrib = analytics.get("score_distribution", {})
        events = analytics.get("total_events", {})

        best = analytics.get("best_session")
        worst = analytics.get("worst_session")

        best_str = (
            f"  Track ID: {best['track_id']}\n  Score:    {best['score']:.2f}\n  Duration: {best['duration_seconds']:.1f}s"
            if best
            else "  N/A"
        )
        worst_str = (
            f"  Track ID: {worst['track_id']}\n  Score:    {worst['score']:.2f}\n  Duration: {worst['duration_seconds']:.1f}s"
            if worst
            else "  N/A"
        )

        lines = [
            "============================================================",
            "FINAL ATTENTION SCAN SUMMARY",
            "============================================================",
            f"Completed Sessions:     {total_sessions}",
            f"Total Duration:         {duration:.1f}s",
            f"Total Frames:           {frames}",
            f"Average Attention Score: {avg_score:.2f}",
            "",
            "Overall Attention:",
            f"  ATTENTIVE:  {pcts.get('ATTENTIVE', 0.0):6.2f}%",
            f"  DISTRACTED: {pcts.get('DISTRACTED', 0.0):6.2f}%",
            f"  DROWSY:     {pcts.get('DROWSY', 0.0):6.2f}%",
            f"  YAWNING:    {pcts.get('YAWNING', 0.0):6.2f}%",
            "",
            "Score Distribution:",
            f"  HIGH:     {distrib.get('HIGH', 0)}",
            f"  MODERATE: {distrib.get('MODERATE', 0)}",
            f"  LOW:      {distrib.get('LOW', 0)}",
            "",
            "Total Events:",
            f"  Blinks:                 {events.get('blinks', 0)}",
            f"  Yawns:                  {events.get('yawns', 0)}",
            f"  Prolonged Eye Closures: {events.get('prolonged_eye_closures', 0)}",
            f"  Look Away Events:       {events.get('look_away_events', 0)}",
            "",
            "Best Session:",
            best_str,
            "",
            "Worst Session:",
            worst_str,
            "",
            "============================================================",
            "INDIVIDUAL SESSION RESULTS",
            "============================================================",
        ]

        for i, single_rep in enumerate(session_reports, 1):
            t_id = single_rep.get("track_id")
            dur = single_rep.get("duration_seconds", 0.0)
            sc = single_rep.get("attention_score", 0.0)
            rat = single_rep.get("rating", "N/A")
            spcts = single_rep.get("attention_percentages", {})
            sevts = single_rep.get("event_counts", {})

            lines.extend(
                [
                    "",
                    f"SESSION {i}",
                    f"Track ID:        {t_id}",
                    f"Duration:        {dur:.1f}s",
                    f"Attention Score: {sc:.2f}",
                    f"Rating:          {rat}",
                    "",
                    "Attention:",
                    f"  ATTENTIVE:  {spcts.get('ATTENTIVE', 0.0):6.2f}%",
                    f"  DISTRACTED: {spcts.get('DISTRACTED', 0.0):6.2f}%",
                    f"  DROWSY:     {spcts.get('DROWSY', 0.0):6.2f}%",
                    f"  YAWNING:    {spcts.get('YAWNING', 0.0):6.2f}%",
                    "",
                    "Events:",
                    f"  Blinks:                 {sevts.get('blinks', 0)}",
                    f"  Yawns:                  {sevts.get('yawns', 0)}",
                    f"  Prolonged Eye Closures: {sevts.get('prolonged_eye_closures', 0)}",
                    f"  Look Away Events:       {sevts.get('look_away_events', 0)}",
                ]
            )

        lines.append("============================================================")
        return "\n".join(lines)

    def prompt_and_export_reports(
        self,
        history_records: List[Dict[str, Any]],
        analytics: Dict[str, Any],
        default_choice: Optional[str] = None,
    ) -> List[str]:
        """
        Prompts user to export JSON/CSV reports (or uses default_choice).
        Returns a list of created file paths.
        """
        if not history_records:
            print("\nNo completed person sessions were recorded. Skipping report export.")
            return []

        if default_choice is None:
            print()
            print("Export reports?")
            print("  [J] JSON")
            print("  [C] CSV")
            print("  [B] Both")
            print("  [N] No")
            try:
                choice = input("Select an option (J/C/B/N): ").strip().upper()
            except (EOFError, RuntimeError):
                choice = "N"
        else:
            choice = default_choice.strip().upper()

        if choice not in ("J", "C", "B"):
            print("No reports exported.")
            return []

        from datetime import datetime

        os.makedirs("reports", exist_ok=True)
        timestamp_str = datetime.now().strftime("%Y%m%d_%H%M%S")

        exported_files = []

        if choice in ("J", "B"):
            history_report = self.generate_history_report(history_records)
            history_report["analytics"] = analytics
            json_filename = os.path.join("reports", f"attention_report_{timestamp_str}.json")
            self.export_json(history_report, json_filename)
            exported_files.append(json_filename)
            print(f"Exported JSON report to: {json_filename}")

        if choice in ("C", "B"):
            csv_filename = os.path.join("reports", f"attention_report_{timestamp_str}.csv")
            self.export_csv(history_records, csv_filename)
            exported_files.append(csv_filename)
            print(f"Exported CSV report to: {csv_filename}")

        return exported_files

