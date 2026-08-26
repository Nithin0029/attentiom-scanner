function formatDuration(seconds) {
    if (!seconds || seconds < 0) return "0s";
    if (seconds < 60) return `${Math.round(seconds)}s`;
    const minutes = Math.floor(seconds / 60);
    const remaining = Math.round(seconds % 60);
    return `${minutes}m ${remaining}s`;
}

function FinalSummary({ summary }) {
    const analytics = summary && summary.analytics;
    const sessions =
        summary && Array.isArray(summary.completed_sessions)
            ? summary.completed_sessions
            : [];

    if (!analytics || analytics.total_sessions === 0) {
        return (
            <div className="final-summary-empty">
                <h2>Scan Complete</h2>
                <p>No sessions were recorded during this scan.</p>
            </div>
        );
    }

    const pct = analytics.overall_attention_percentages || {};
    const events = analytics.total_events || {};
    const distribution = analytics.score_distribution || {};
    const engagement = analytics.engagement || {};

    return (
        <div className="final-summary">
            <h2>Scan Complete — Final Summary</h2>

            <div className="summary-highlight-grid">
                <div className="summary-highlight">
                    <span className="summary-highlight-value">
                        {analytics.average_attention_score.toFixed(1)}
                    </span>
                    <span className="summary-highlight-label">
                        Average Attention Score
                    </span>
                </div>
                <div className="summary-highlight">
                    <span className="summary-highlight-value">
                        {analytics.total_sessions}
                    </span>
                    <span className="summary-highlight-label">
                        Total Sessions
                    </span>
                </div>
                <div className="summary-highlight">
                    <span className="summary-highlight-value">
                        {formatDuration(analytics.total_duration_seconds)}
                    </span>
                    <span className="summary-highlight-label">
                        Total Duration
                    </span>
                </div>
                <div className="summary-highlight">
                    <span className="summary-highlight-value">
                        {analytics.total_frames}
                    </span>
                    <span className="summary-highlight-label">
                        Total Frames
                    </span>
                </div>
            </div>

            <div className="summary-section-grid">
                <div className="summary-panel">
                    <h3>Attention Breakdown</h3>
                    <div className="pct-bars">
                        {["ATTENTIVE", "DISTRACTED", "DROWSY", "YAWNING"].map(
                            (key) => (
                                <div className="pct-row" key={key}>
                                    <span className="pct-row-label">
                                        {key}
                                    </span>
                                    <div className="pct-track">
                                        <div
                                            className={`pct-fill state-${key.toLowerCase()}`}
                                            style={{
                                                width: `${pct[key] || 0}%`,
                                            }}
                                        />
                                    </div>
                                    <span className="pct-row-value">
                                        {(pct[key] || 0).toFixed(1)}%
                                    </span>
                                </div>
                            )
                        )}
                    </div>
                </div>

                <div className="summary-panel">
                    <h3>Score Distribution</h3>
                    <div className="dist-row">
                        <span>High</span>
                        <span>{distribution.HIGH ?? 0}</span>
                    </div>
                    <div className="dist-row">
                        <span>Moderate</span>
                        <span>{distribution.MODERATE ?? 0}</span>
                    </div>
                    <div className="dist-row">
                        <span>Low</span>
                        <span>{distribution.LOW ?? 0}</span>
                    </div>

                    <h3 className="summary-panel-subheading">
                        Behavioral Events
                    </h3>
                    <div className="dist-row">
                        <span>Blinks</span>
                        <span>{events.blinks ?? 0}</span>
                    </div>
                    <div className="dist-row">
                        <span>Yawns</span>
                        <span>{events.yawns ?? 0}</span>
                    </div>
                    <div className="dist-row">
                        <span>Prolonged Eye Closures</span>
                        <span>{events.prolonged_eye_closures ?? 0}</span>
                    </div>
                    <div className="dist-row">
                        <span>Look-away Events</span>
                        <span>{events.look_away_events ?? 0}</span>
                    </div>
                </div>

                <div className="summary-panel">
                    <h3>Best / Worst Session</h3>
                    {analytics.best_session ? (
                        <div className="best-worst-row good">
                            <span>Best: Track #{analytics.best_session.track_id}</span>
                            <span>{analytics.best_session.score.toFixed(1)}</span>
                        </div>
                    ) : (
                        <p className="muted">No data.</p>
                    )}
                    {analytics.worst_session ? (
                        <div className="best-worst-row bad">
                            <span>
                                Worst: Track #{analytics.worst_session.track_id}
                            </span>
                            <span>{analytics.worst_session.score.toFixed(1)}</span>
                        </div>
                    ) : (
                        <p className="muted">No data.</p>
                    )}

                    <h3 className="summary-panel-subheading">Engagement</h3>
                    <div className="dist-row">
                        <span>Attentive Sessions</span>
                        <span>{engagement.attentive_sessions ?? 0}</span>
                    </div>
                    <div className="dist-row">
                        <span>With Distraction</span>
                        <span>{engagement.sessions_with_distraction ?? 0}</span>
                    </div>
                    <div className="dist-row">
                        <span>With Drowsiness</span>
                        <span>{engagement.sessions_with_drowsiness ?? 0}</span>
                    </div>
                </div>
            </div>

            {sessions.length > 0 && (
                <div className="summary-panel">
                    <h3>Per-Session Breakdown</h3>
                    <div className="history-table-wrapper">
                        <table className="history-table">
                            <thead>
                                <tr>
                                    <th>Track ID</th>
                                    <th>Score</th>
                                    <th>Duration</th>
                                    <th>Attentive %</th>
                                    <th>Distracted %</th>
                                    <th>Drowsy %</th>
                                </tr>
                            </thead>
                            <tbody>
                                {sessions.map((record, index) => {
                                    const session = record.session || {};
                                    const percentages =
                                        session.attention_percentages || {};
                                    const score = record.attention_score?.score;

                                    return (
                                        <tr
                                            key={`${record.track_id}-${index}`}
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
                                                {(
                                                    percentages.ATTENTIVE || 0
                                                ).toFixed(1)}
                                                %
                                            </td>
                                            <td>
                                                {(
                                                    percentages.DISTRACTED || 0
                                                ).toFixed(1)}
                                                %
                                            </td>
                                            <td>
                                                {(
                                                    percentages.DROWSY || 0
                                                ).toFixed(1)}
                                                %
                                            </td>
                                        </tr>
                                    );
                                })}
                            </tbody>
                        </table>
                    </div>
                </div>
            )}
        </div>
    );
}

export default FinalSummary;
