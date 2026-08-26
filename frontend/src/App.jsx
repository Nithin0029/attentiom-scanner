import { useState, useCallback, useEffect, useRef } from "react";
import {
    startScanner,
    stopScanner,
    getHealth,
    getScannerStatus,
    getScannerSummary,
} from "./services/scannerApi";

import Header from "./components/Header";
import StatusCards from "./components/StatusCards";
import ScannerControls from "./components/ScannerControls";
import CameraFeed from "./components/CameraFeed";
import LiveMetrics from "./components/LiveMetrics";
import PersonAnalytics from "./components/PersonAnalytics";
import SessionHistory from "./components/SessionHistory";
import FinalSummary from "./components/FinalSummary";

function App() {
    const [activeTab, setActiveTab] = useState("monitor");
    const [scannerStatus, setScannerStatus] = useState("stopped");
    const [backendStatus, setBackendStatus] = useState("checking");
    const [message, setMessage] = useState(
        "Ready to start attention monitoring."
    );
    const [loading, setLoading] = useState(false);
    const [latestResult, setLatestResult] = useState(null);
    const [finalSummary, setFinalSummary] = useState(null);

    const isRunning = scannerStatus === "running";
    const startInFlightRef = useRef(false);
    const stopInFlightRef = useRef(false);

    // On load, verify backend reachability and sync with any scanner
    // session that may already be running on the server.
    useEffect(() => {
        let cancelled = false;

        async function checkBackend() {
            try {
                await getHealth();
                const status = await getScannerStatus();

                if (cancelled) return;

                setBackendStatus("connected");

                if (status.running) {
                    setScannerStatus("running");
                    setMessage("Reconnected to an already-running scanner.");
                }
            } catch (error) {
                if (!cancelled) {
                    setBackendStatus("offline");
                }
            }
        }

        checkBackend();

        const interval = setInterval(checkBackend, 15000);

        return () => {
            cancelled = true;
            clearInterval(interval);
        };
    }, []);

    const handleStart = async () => {
        if (startInFlightRef.current || isRunning) return;
        startInFlightRef.current = true;

        setLoading(true);
        setMessage("Starting scanner...");
        setFinalSummary(null);
        setLatestResult(null);

        try {
            const data = await startScanner();

            setScannerStatus("running");
            setBackendStatus("connected");
            setMessage(data.message || "Scanner started successfully.");
        } catch (error) {
            setBackendStatus("offline");
            setMessage(error.message || "Could not connect to the backend.");
        } finally {
            setLoading(false);
            startInFlightRef.current = false;
        }
    };

    const handleStop = async () => {
        if (stopInFlightRef.current || !isRunning) return;
        stopInFlightRef.current = true;

        setLoading(true);
        setMessage("Stopping scanner...");
        // Immediately flip the running flag so CameraFeed tears down the
        // camera stream and stops sending frames right away.
        setScannerStatus("stopped");

        try {
            const data = await stopScanner();

            setBackendStatus("connected");
            setMessage(data.message || "Scanner stopped successfully.");

            const summary = await getScannerSummary();
            setFinalSummary(summary);
        } catch (error) {
            setBackendStatus("offline");
            setMessage(error.message || "Could not connect to the backend.");
        } finally {
            setLoading(false);
            setLatestResult(null);
            stopInFlightRef.current = false;
        }
    };

    const handleFrameResult = useCallback((result) => {
        setLatestResult(result);
    }, []);

    const handleCameraError = useCallback((errorMsg) => {
        setMessage(errorMsg);
    }, []);

    const people =
        latestResult && Array.isArray(latestResult.people)
            ? latestResult.people
            : [];

    const activeSessionCount = latestResult
        ? Object.keys(latestResult.active_sessions || {}).length
        : 0;

    const completedSessionCount = latestResult
        ? (latestResult.completed_sessions || []).length
        : 0;

    return (
        <main className="app">
            <section className="dashboard">
                <Header activeTab={activeTab} onTabChange={setActiveTab}>
                    <StatusCards
                        backendStatus={backendStatus}
                        isRunning={isRunning}
                    />
                </Header>

                {activeTab === "monitor" ? (
                    <section className="scanner-area">
                        {isRunning ? (
                            <div className="scanner-active-view">
                                <CameraFeed
                                    isRunning={isRunning}
                                    onFrameResult={handleFrameResult}
                                    onError={handleCameraError}
                                    people={people}
                                />

                                <LiveMetrics
                                    result={latestResult}
                                    activeSessionCount={activeSessionCount}
                                    completedSessionCount={
                                        completedSessionCount
                                    }
                                />

                                <PersonAnalytics people={people} />
                            </div>
                        ) : finalSummary ? (
                            <FinalSummary summary={finalSummary} />
                        ) : (
                            <div className="scanner-placeholder">
                                <div className="scanner-icon">
                                    <span className="icon-pulse"></span>
                                </div>

                                <h2>Scanner Ready</h2>

                                <p>
                                    Start the scanner to begin live
                                    monitoring.
                                </p>
                            </div>
                        )}
                    </section>
                ) : (
                    <SessionHistory isRunning={isRunning} />
                )}

                <ScannerControls
                    message={message}
                    loading={loading}
                    isRunning={isRunning}
                    onStart={handleStart}
                    onStop={handleStop}
                />
            </section>
        </main>
    );
}

export default App;
