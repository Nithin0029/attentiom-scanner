import { useEffect, useState, useCallback } from "react";
import { getScannerSummary } from "../services/scannerApi";

function formatDuration(seconds) {
    if (!seconds || seconds < 0) return "0s";
    if (seconds < 60) return `${Math.round(seconds)}s`;
    const minutes = Math.floor(seconds / 60);
    const remaining = Math.round(seconds % 60);
    return `${minutes}m ${remaining}s`;
}

function formatCompletedAt(timestamp) {
    if (!timestamp) return "--";
    return new Date(timestamp * 1000).toLocaleString();
}

function SessionHistory({ isRunning }) {
    const [summary, setSummary] = useState(null);
    const [error, setError] = useState(null);
    const [loading, setLoading] = useState(true);

    const fetchSummary = useCallback(async () => {
        try {
            const data = await getScannerSummary();
            setSummary(data);
            setError(null);
        } catch (err) {
            setError(err.message || "Failed to load session history.");
        } finally {
            setLoading(false);
        }
    }, []);

    useEffect(() => {
        fetchSummary();

        if (!isRunning) return undefined;

        const interval = setInterval(fetchSummary, 5000);
        return () => clearInterval(interval);
    }, [fetchSummary, isRunning]);

    const sessions =
        summary && Array.isArray(summary.completed_sessions)
            ? summary.completed_sessions
            : [];

    return (
        <section className="session-history">
            <div className="session-history-header">
                <h2>Completed Sessions</h2>
                <button
                    type="button"
                    className="refresh-button"
                    onClick={fetchSummary}
                    disabled={loading}
                >
                    Refresh
                </button>
            </div>

            {error && <p className="history-error">{error}</p>}

            {!error && sessions.length === 0 && (
                <div className="history-empty">
                    <p>
                        No completed sessions yet. Sessions appear here once a
                        tracked person leaves the frame or the scanner stops.
                    </p>
                </div>
            )}

            {sessions.length > 0 && (
                <div className="history-table-wrapper">
                    <table className="history-table">
                        <thead>
                            <tr>
                                <th>Track ID</th>
                                <th>Score</th>
                                <th>Duration</th>
                                <th>Frames</th>
                                <th>Attentive %</th>
                                <th>Completed At</th>
                            </tr>
                        </thead>
                        <tbody>
                            {sessions
                                .slice()
                                .reverse()
                                .map((record, index) => {
                                    const session = record.session || {};
                                    const score =
                                        record.attention_score?.score;
                                    const attentivePct =
                                        session.attention_percentages
                                            ?.ATTENTIVE;

                                    return (
                                        <tr
                                            key={`${record.track_id}-${record.completed_at}-${index}`}
                                        >
                                            <td>#{record.track_id}</td>
                                            <td>
                                                {typeof score === "number"
                                                    ? score.toFixed(1)
                                                    : "--"}
                                            </td>
                                            <td>
                                                {formatDuration(
                                                    session.duration_seconds
                                                )}
                                            </td>
                                            <td>
                                                {session.total_frames ?? 0}
                                            </td>
                                            <td>
                                                {typeof attentivePct ===
                                                "number"
                                                    ? `${attentivePct.toFixed(
                                                          1
                                                      )}%`
                                                    : "--"}
                                            </td>
                                            <td>
                                                {formatCompletedAt(
                                                    record.completed_at
                                                )}
                                            </td>
                                        </tr>
                                    );
                                })}
                        </tbody>
                    </table>
                </div>
            )}
        </section>
    );
}

export default SessionHistory;
