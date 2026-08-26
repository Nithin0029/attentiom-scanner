function ScannerControls({
    message,
    loading,
    isRunning,
    onStart,
    onStop,
}) {
    return (
        <section className="control-panel">
            <div className="message">
                <span className="message-label">SYSTEM STATUS</span>
                <p>{message}</p>
            </div>

            <div className="controls">
                <button
                    className="start-button"
                    onClick={onStart}
                    disabled={loading || isRunning}
                >
                    {loading && !isRunning ? "Starting..." : "Start Scanner"}
                </button>

                <button
                    className="stop-button"
                    onClick={onStop}
                    disabled={loading || !isRunning}
                >
                    {loading && isRunning ? "Stopping..." : "Stop Scanner"}
                </button>
            </div>
        </section>
    );
}

export default ScannerControls;
