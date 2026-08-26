import { useEffect, useRef, useState, useCallback } from "react";
import { sendFrame } from "../services/scannerApi";

function CameraFeed({
    isRunning,
    onFrameResult,
    onError,
    intervalMs = 1000,
}) {
    const videoRef = useRef(null);
    const canvasRef = useRef(null);
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
            {!cameraActive && isRunning && (
                <div className="camera-loading-overlay">
                    <p>Initializing camera feed...</p>
                </div>
            )}
        </div>
    );
}

export default CameraFeed;
