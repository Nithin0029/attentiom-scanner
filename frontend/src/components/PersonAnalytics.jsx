const STATE_LABELS = {
    ATTENTIVE: "Attentive",
    DISTRACTED: "Distracted",
    DROWSY: "Drowsy",
    YAWNING: "Yawning",
};

function formatDuration(seconds) {
    if (!seconds || seconds < 0) return "0s";
    if (seconds < 60) return `${Math.round(seconds)}s`;
    const minutes = Math.floor(seconds / 60);
    const remaining = Math.round(seconds % 60);
    return `${minutes}m ${remaining}s`;
}

function PersonCard({ person }) {
    const state = person.attention?.state || "ATTENTIVE";
    const score = person.attention_score?.score;
    const session = person.session || {};
    const eventCounts = session.event_counts || {};
    const recentEvents = person.attention?.events || [];

    return (
        <div className={`person-card state-${state.toLowerCase()}`}>
            <div className="person-card-header">
                <span className="person-track-id">Track #{person.track_id}</span>
                <span className={`person-state-badge state-${state.toLowerCase()}`}>
                    {STATE_LABELS[state] || state}
                </span>
            </div>

            <div className="person-score">
                <span className="person-score-value">
                    {typeof score === "number" ? Math.round(score) : "--"}
                </span>
                <span className="person-score-label">Attention Score</span>
            </div>

            <div className="person-stats">
                <div className="person-stat">
                    <span className="person-stat-label">Duration</span>
                    <span className="person-stat-value">
                        {formatDuration(session.duration_seconds)}
                    </span>
                </div>
                <div className="person-stat">
                    <span className="person-stat-label">Frames</span>
                    <span className="person-stat-value">
                        {session.total_frames ?? 0}
                    </span>
                </div>
                <div className="person-stat">
                    <span className="person-stat-label">Blinks</span>
                    <span className="person-stat-value">
                        {eventCounts.blinks ?? 0}
                    </span>
                </div>
                <div className="person-stat">
                    <span className="person-stat-label">Yawns</span>
                    <span className="person-stat-value">
                        {eventCounts.yawns ?? 0}
                    </span>
                </div>
            </div>

            {recentEvents.length > 0 && (
                <div className="person-events">
                    {recentEvents.map((event, index) => (
                        <span key={`${event}-${index}`} className="event-chip">
                            {event.replace(/_/g, " ")}
                        </span>
                    ))}
                </div>
            )}
        </div>
    );
}

function PersonAnalytics({ people = [] }) {
    if (people.length === 0) {
        return (
            <div className="person-analytics-empty">
                <p>No faces detected in the current frame.</p>
            </div>
        );
    }

    return (
        <div className="person-analytics-grid">
            {people.map((person) => (
                <PersonCard key={person.track_id} person={person} />
            ))}
        </div>
    );
}

export default PersonAnalytics;
