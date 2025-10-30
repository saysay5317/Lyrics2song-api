from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
import uuid, os, time, json

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # tighten later to your app domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

JOBS_DIR = "/mnt/data/jobs"
os.makedirs(JOBS_DIR, exist_ok=True)

@app.post("/v1/generate")
def generate(payload: dict):
    job_id = str(uuid.uuid4())
    job_path = os.path.join(JOBS_DIR, job_id)
    os.makedirs(job_path, exist_ok=True)
    json.dump(payload, open(os.path.join(job_path, "request.json"), "w"))
    open(os.path.join(job_path, "status.txt"), "w").write(str(time.time()))
    return {"job_id": job_id, "status": "queued"}

@app.get("/v1/status/{job_id}")
def status(job_id: str):
    job_path = os.path.join(JOBS_DIR, job_id)
    if not os.path.exists(job_path):
        return {"job_id": job_id, "status": "unknown"}
    t0 = float(open(os.path.join(job_path, "status.txt")).read())
    if time.time() - t0 > 8:
        final_path = os.path.join(job_path, "final.mp3")
        if not os.path.exists(final_path):
            with open(final_path, "wb") as f: f.write(b"ID3")  # tiny mp3 stub
        return {"job_id": job_id, "status": "done", "download": f"/v1/download/{job_id}"}
    return {"job_id": job_id, "status": "processing"}

@app.get("/v1/download/{job_id}")
def download(job_id: str):
    job_path = os.path.join(JOBS_DIR, job_id)
    final_path = os.path.join(job_path, "final.mp3")
    return FileResponse(final_path, media_type="audio/mpeg", filename=f"{job_id}.mp3")
