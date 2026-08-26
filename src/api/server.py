from __future__ import annotations

import cv2
import numpy as np

from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware

from src.api.scanner_service import ScannerService


app = FastAPI(
    title="Attention Scanner API",
    description="Web API for the real-time attention scanner.",
    version="1.0.0",
)

allowed_origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)



scanner_service = ScannerService()


@app.get("/health")
def health():
    """
    Basic API health check.
    """

    return {
        "status": "ok",
        "message": "Attention Scanner API is running.",
    }


@app.post("/api/scanner/start")
def start_scanner():
    """
    Start the realtime scanner pipeline.
    """

    try:
        return scanner_service.start()

    except FileNotFoundError as error:
        raise HTTPException(
            status_code=500,
            detail=f"Required model file was not found: {error}",
        )

    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to start scanner: {error}",
        )


@app.get("/api/scanner/status")
def scanner_status():
    """
    Get the current scanner status.
    """

    return scanner_service.get_status()


@app.post("/api/scanner/frame")
async def process_frame(
    file: UploadFile = File(...)
):
    """
    Receive and process one image frame from the frontend.
    """

    if not scanner_service.get_status()["running"]:
        raise HTTPException(
            status_code=400,
            detail="Scanner is not running. Call /api/scanner/start first.",
        )

    try:
        image_bytes = await file.read()

        if not image_bytes:
            raise HTTPException(
                status_code=400,
                detail="Uploaded image is empty.",
            )

        image_array = np.frombuffer(
            image_bytes,
            dtype=np.uint8,
        )

        frame = cv2.imdecode(
            image_array,
            cv2.IMREAD_COLOR,
        )

        if frame is None:
            raise HTTPException(
                status_code=400,
                detail="Uploaded file is not a valid image.",
            )

        result = scanner_service.process_frame(frame)

        return {
            "success": True,
            "result": result,
        }

    except HTTPException:
        raise

    except RuntimeError as error:
        raise HTTPException(
            status_code=400,
            detail=str(error),
        )

    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail=f"Frame processing failed: {error}",
        )


@app.post("/api/scanner/stop")
def stop_scanner():
    """
    Stop the scanner and finalize all active sessions.
    """

    try:
        return scanner_service.stop()

    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to stop scanner: {error}",
        )


@app.get("/api/scanner/summary")
def scanner_summary():
    """
    Return completed sessions and aggregate analytics.
    """

    try:
        return scanner_service.get_summary()

    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get scanner summary: {error}",
        )