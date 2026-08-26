function StatusCards({ backendStatus, isRunning }) {
    return (
        <div className="status-group">
            <div className="status-card">
                <span className="status-label">BACKEND</span>
                <span className={`status-value ${backendStatus}`}>
                    {backendStatus === "connected"
                        ? "CONNECTED"
                        : backendStatus === "offline"
                        ? "OFFLINE"
                        : "CHECKING"}
                </span>
            </div>

            <div className="status-card">
                <span className="status-label">SCANNER</span>
                <span
                    className={`status-value ${
                        isRunning ? "running" : "stopped"
                    }`}
                >
                    {isRunning ? "RUNNING" : "STOPPED"}
                </span>
            </div>
        </div>
    );
}

export default StatusCards;
