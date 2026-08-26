function formatTime(timestamp) {
    if (!timestamp) return "--:--:--";
    return new Date(timestamp * 1000).toLocaleTimeString();
}

function LiveMetrics({ result, activeSessionCount, completedSessionCount }) {
    const peopleCount =
        result && Array.isArray(result.people) ? result.people.length : 0;

    return (
        <div className="live-metrics-bar">
            <div className="metric-badge">
                <span className="metric-dot active"></span>
                <span>Processing: Active</span>
            </div>

            <div className="metric-badge">
                <span>
                    People Detected: <strong>{peopleCount}</strong>
                </span>
            </div>

            <div className="metric-badge">
                <span>
                    Active Sessions: <strong>{activeSessionCount}</strong>
                </span>
            </div>

            <div className="metric-badge">
                <span>
                    Completed Sessions:{" "}
                    <strong>{completedSessionCount}</strong>
                </span>
            </div>

            <div className="metric-badge">
                <span>Last Frame: {formatTime(result && result.timestamp)}</span>
            </div>
        </div>
    );
}

export default LiveMetrics;
