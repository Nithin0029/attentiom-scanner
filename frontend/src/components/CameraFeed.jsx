import { useEffect, useRef, useState, useCallback } from "react";
import { sendFrame } from "../services/scannerApi";

const STATE_COLORS = {
    ATTENTIVE: "#22c55e",
    DISTRACTED: "#f59e0b",
    DROWSY: "#ef4444",
    YAWNING: "#a855f7",
};

function CameraFeed({
    isRunning,
    onFrameResult,
    onError,
    people = [],
    intervalMs = 1000,
}) {
    const videoRef = useRef(null);
    const canvasRef = useRef(null);
    const overlayRef = useRef(null);
    const streamRef = useRef(null);
    const intervalRef = useRef(null);
    const isSendingRef = useRef(false);
    const consecutiveErrorsRef = useRef(0);
    const [cameraActive, setCameraActive] = useState(false);

    const stopCamera = useCallback(() => {
        if (intervalRef.current) {
            clearInterval(intervalRef.current);
            intervalRef.current = null;
        }
        if (streamRef.current) {
            streamRef.current.getTracks().forEach((track) => track.stop());
            streamRef.current = null;
        }
        if (videoRef.current) {
            videoRef.current.srcObject = null;
        }
        isSendingRef.current = false;
        setCameraActive(false);
    }, []);

    const captureAndSendFrame = useCallback(async () => {
        if (isSendingRef.current) {
            return;
        }

        const video = videoRef.current;
        const canvas = canvasRef.current;

        if (!video || !canvas) return;
        if (
            video.paused ||
            video.ended ||
            video.videoWidth === 0 ||
            video.videoHeight === 0
        ) {
            return;
        }

        isSendingRef.current = true;

        try {
            canvas.width = video.videoWidth;
            canvas.height = video.videoHeight;
            const ctx = canvas.getContext("2d");
            if (!ctx) {
                isSendingRef.current = false;
                return;
            }

            ctx.drawImage(video, 0, 0, video.videoWidth, video.videoHeight);

            canvas.toBlob(
                async (blob) => {
                    if (!blob) {
                        isSendingRef.current = false;
                        return;
                    }
                    try {
                        const data = await sendFrame(blob);
                        consecutiveErrorsRef.current = 0;
                        if (data && data.result) {
                            onFrameResult(data.result);
                        }
                    } catch (err) {
                        consecutiveErrorsRef.current += 1;
                        if (
                            consecutiveErrorsRef.current === 1 ||
                            consecutiveErrorsRef.current % 5 === 0
                        ) {
                            onError(`Frame upload notice: ${err.message}`);
                        }
                    } finally {
                        isSendingRef.current = false;
                    }
                },
                "image/jpeg",
                0.85
            );
        } catch (err) {
            isSendingRef.current = false;
        }
    }, [onFrameResult, onError]);

    useEffect(() => {
        if (!isRunning) {
            stopCamera();
            return;
        }

        let isMounted = true;

        async function initCamera() {
            try {
                const stream = await navigator.mediaDevices.getUserMedia({
                    video: { width: { ideal: 640 }, height: { ideal: 480 } },
                    audio: false,
                });

                if (!isMounted) {
                    stream.getTracks().forEach((t) => t.stop());
                    return;
                }

                streamRef.current = stream;
                if (videoRef.current) {
                    videoRef.current.srcObject = stream;
                }
                setCameraActive(true);

                intervalRef.current = setInterval(
                    captureAndSendFrame,
                    intervalMs
                );
            } catch (err) {
                if (isMounted) {
                    const errorMsg =
                        err.name === "NotAllowedError" ||
                        err.name === "PermissionDeniedError"
                            ? "Camera permission denied. Please allow access."
                            : err.name === "NotFoundError" ||
                              err.name === "DevicesNotFoundError"
                            ? "No camera device found."
                            : `Camera error: ${err.message}`;
                    onError(errorMsg);
                }
            }
        }

        initCamera();

        return () => {
            isMounted = false;
            stopCamera();
        };
    }, [isRunning, intervalMs, stopCamera, captureAndSendFrame, onError]);

    // Draw bounding boxes for each detected/tracked person on top of the
    // live video, scaled from native frame resolution to display size.
    useEffect(() => {
        const video = videoRef.current;
        const overlay = overlayRef.current;

        if (!video || !overlay) return;

        const displayWidth = video.clientWidth;
        const displayHeight = video.clientHeight;

        if (!displayWidth || !displayHeight) return;

        overlay.width = displayWidth;
        overlay.height = displayHeight;

        const ctx = overlay.getContext("2d");
        if (!ctx) return;

        ctx.clearRect(0, 0, displayWidth, displayHeight);

        if (
            !cameraActive ||
            !video.videoWidth ||
            !video.videoHeight ||
            people.length === 0
        ) {
            return;
        }

        const scaleX = displayWidth / video.videoWidth;
        const scaleY = displayHeight / video.videoHeight;

        people.forEach((person) => {
            const bbox = person.bbox;
            if (!bbox || bbox.length !== 4) return;

            const [x1, y1, x2, y2] = bbox;
            const state =
                (person.attention && person.attention.state) || "ATTENTIVE";
            const color = STATE_COLORS[state] || STATE_COLORS.ATTENTIVE;

            const drawX = x1 * scaleX;
            const drawY = y1 * scaleY;
            const drawW = (x2 - x1) * scaleX;
            const drawH = (y2 - y1) * scaleY;

            ctx.strokeStyle = color;
            ctx.lineWidth = 2;
            ctx.strokeRect(drawX, drawY, drawW, drawH);

            const score =
                person.attention_score && person.attention_score.score;
            const label =
                `#${person.track_id} ${state}` +
                (typeof score === "number" ? ` · ${Math.round(score)}` : "");

            ctx.font = "600 12px Inter, system-ui, sans-serif";
            const textWidth = ctx.measureText(label).width;

            ctx.fillStyle = color;
            ctx.fillRect(drawX, Math.max(0, drawY - 20), textWidth + 12, 20);

            ctx.fillStyle = "#0b0f16";
            ctx.fillText(label, drawX + 6, Math.max(14, drawY - 6));
        });
    }, [people, cameraActive]);

    return (
        <div className="camera-feed-container">
            <video
                ref={videoRef}
                autoPlay
                playsInline
                muted
                className="camera-video"
            />
            <canvas ref={canvasRef} style={{ display: "none" }} />
            <canvas ref={overlayRef} className="camera-overlay" />
            {!cameraActive && isRunning && (
                <div className="camera-loading-overlay">
                    <p>Initializing camera feed...</p>
                </div>
            )}
        </div>
    );
}

export default CameraFeed;
