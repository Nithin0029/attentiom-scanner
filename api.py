from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import subprocess
import os
import json
import signal
import time
from typing import Optional
from pydantic import BaseModel

# FastAPI app
app = FastAPI(title="Attention - Python API Wrapper")

# CORS: allow frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

ROOT = os.path.dirname(os.path.abspath(__file__))
PIPELINE_SCRIPT = os.path.join(ROOT, "realtime_pipeline.py")
OUTPUT_JSON = os.path.join(ROOT, "output.json")
REPORT_JSON = os.path.join(ROOT, "session_report.json")

pipeline_proc: Optional[subprocess.Popen] = None

class RegisterPayload(BaseModel):
    student_id: str
    name: Optional[str] = None
    meta: Optional[dict] = None

@app.get("/health")
def health():
    return {"status": "ok", "time": time.time()}

@app.get("/status")
def status():
    running = pipeline_proc is not None and pipeline_proc.poll() is None
    return {"running": running}

@app.post("/start-session")
def start_session():
    global pipeline_proc

    if pipeline_proc is not None and pipeline_proc.poll() is None:
        return {"status": "already_running"}

    if not os.path.exists(PIPELINE_SCRIPT):
        raise HTTPException(status_code=500, detail="Pipeline script not found")

    python_exe = os.sys.executable

    pipeline_proc = subprocess.Popen(
        [python_exe, PIPELINE_SCRIPT],
        stdout=open(os.path.join(ROOT, "pipeline_stdout.log"), "a"),
        stderr=open(os.path.join(ROOT, "pipeline_stderr.log"), "a"),
    )

    return {"status": "started", "pid": pipeline_proc.pid}

@app.post("/stop-session")
def stop_session():
    global pipeline_proc

    if pipeline_proc is None or pipeline_proc.poll() is not None:
        pipeline_proc = None
        return {"status": "not_running"}

    try:
        pipeline_proc.send_signal(signal.SIGINT)
        pipeline_proc.wait(timeout=5)
    except:
        try:
            pipeline_proc.kill()
        except:
            pass

    pid = pipeline_proc.pid
    pipeline_proc = None

    return {"status": "stopped", "pid": pid}

@app.get("/engagement")
def engagement():
    if not os.path.exists(OUTPUT_JSON):
        raise HTTPException(status_code=404, detail="output.json not found")
    
    with open(OUTPUT_JSON, "r") as f:
        return json.load(f)

@app.get("/report")
def report():
    if not os.path.exists(REPORT_JSON):
        raise HTTPException(status_code=404, detail="session_report.json not found")
    
    with open(REPORT_JSON, "r") as f:
        return json.load(f)

@app.post("/register")
def register_student(payload: RegisterPayload):
    reg_file = os.path.join(ROOT, "pending_registration.json")

    with open(reg_file, "w") as f:
        json.dump(payload.dict(), f, indent=2)

    return {"status": "saved", "file": reg_file}
