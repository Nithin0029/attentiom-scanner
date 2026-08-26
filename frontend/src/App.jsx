import { useState, useCallback } from "react";
import { startScanner, stopScanner } from "./services/scannerApi";
import CameraFeed from "./components/CameraFeed";

function App() {
    const [scannerStatus, setScannerStatus] = useState("stopped");
    const [backendStatus, setBackendStatus] = useState("unknown");
    const [message, setMessage] = useState(
        "Ready to start attention monitoring."
    );
    const [loading, setLoading] = useState(false);
    const [latestResult, setLatestResult] = useState(null);

    const handleStart = async () => {
        setLoading(true);
        setMessage("Starting scanner...");

        try {
            const data = await startScanner();

            setScannerStatus("running");
            setBackendStatus("connected");
            setMessage(
                data.message || "Scanner started successfully."
            );
        } catch (error) {
            setBackendStatus("offline");
            setMessage(
                error.message || "Could not connect to the backend."
            );
        } finally {
            setLoading(false);
        }
    };

    const handleStop = async () => {
        setLoading(true);
        setMessage("Stopping scanner...");
        setScannerStatus("stopped");

        try {
            const data = await stopScanner();

            setBackendStatus("connected");
            setMessage(
                data.message || "Scanner stopped successfully."
            );
            setLatestResult(null);
        } catch (error) {
            setBackendStatus("offline");
            setMessage(
                error.message || "Could not connect to the backend."
            );
        } finally {
            setLoading(false);
        }
    };

    const handleFrameResult = useCallback((result) => {
        setLatestResult(result);
    }, []);

    const handleCameraError = useCallback((errorMsg) => {
        setMessage(errorMsg);
    }, []);

    const isRunning = scannerStatus === "running";
    const peopleCount =
        latestResult && Array.isArray(latestResult.people)
            ? latestResult.people.length
            : 0;

    return (
        <main className="app">
            <section className="dashboard">
                <header className="header">
                    <div>
                        <p className="eyebrow">
                            AI-POWERED MONITORING
                        </p>

                        <h1>Attention Scanner</h1>

                        <p className="subtitle">
                            Real-time engagement and behavior analysis
                        </p>
                    </div>

                    <div className="status-group">
                        <div className="status-card">
                            <span className="status-label">
                                BACKEND
                            </span>

                            <span
                                className={`status-value ${backendStatus}`}
                            >
                                {backendStatus === "connected"
                                    ? "CONNECTED"
                                    : backendStatus === "offline"
                                    ? "OFFLINE"
                                    : "UNKNOWN"}
                            </span>
                        </div>

                        <div className="status-card">
                            <span className="status-label">
                                SCANNER
                            </span>

                            <span
                                className={`status-value ${
                                    isRunning ? "running" : "stopped"
                                }`}
                            >
                                {isRunning ? "RUNNING" : "STOPPED"}
                            </span>
                        </div>
                    </div>
                </header>

                <section className="scanner-area">
                    {isRunning ? (
                        <div className="scanner-active-view">
                            <CameraFeed
                                isRunning={isRunning}
                                onFrameResult={handleFrameResult}
                                onError={handleCameraError}
                            />
                            <div className="live-metrics-overlay">
                                <div className="metric-badge">
                                    <span className="metric-dot active"></span>
                                    <span>Processing: Active</span>
                                </div>
                                <div className="metric-badge">
                                    <span>People Detected: {peopleCount}</span>
                                </div>
                            </div>
                        </div>
                    ) : (
                        <div className="scanner-placeholder">
                            <div className="scanner-icon">
                                <span className="icon-pulse"></span>
                            </div>

                            <h2>Scanner Ready</h2>

                            <p>
                                Start the scanner to begin live monitoring.
                            </p>
                        </div>
                    )}
                </section>

                <section className="control-panel">
                    <div className="message">
                        <span className="message-label">
                            SYSTEM STATUS
                        </span>

                        <p>{message}</p>
                    </div>

                    <div className="controls">
                        <button
                            className="start-button"
                            onClick={handleStart}
                            disabled={loading || isRunning}
                        >
                            {loading && !isRunning
                                ? "Starting..."
                                : "Start Scanner"}
                        </button>

                        <button
                            className="stop-button"
                            onClick={handleStop}
                            disabled={loading || !isRunning}
                        >
                            {loading && isRunning
                                ? "Stopping..."
                                : "Stop Scanner"}
                        </button>
                    </div>
                </section>
            </section>
        </main>
    );
}

export default App;