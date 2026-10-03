import uuid
import time
import io
from fastapi import FastAPI, UploadFile, File, Form
from pydantic import BaseModel
import av
from PIL import Image

app = FastAPI(title="Cloud Comparison Benchmark Service")

class DocInput(BaseModel):
    title: str
    body: str

@app.get("/")
def health():
    return {"status": "ok", "service": "comparison-benchmark"}

@app.post("/docs")
def insert_doc(doc: DocInput):
    doc_id = str(uuid.uuid4())
    title_upper = doc.title.upper()
    summary = doc.title[:12] + "..." if len(doc.title) > 12 else doc.title
    return {
        "id": doc_id,
        "title_upper": title_upper,
        "summary": summary
    }

@app.post("/clip")
async def insert_clip(clip: UploadFile = File(...), title: str = Form(...)):
    clip_id = str(uuid.uuid4())
    content = await clip.read()
    
    # Process video using PyAV
    container = av.open(io.BytesIO(content))
    duration = float(container.duration / av.time_base) if container.duration else 0.0
    
    # Extract frame at ~0.5s or first frame
    frame_image = None
    stream = container.streams.video[0]
    container.seek(500000, stream=stream)  # Seek 0.5s in microseconds
    for frame in container.decode(video=0):
        frame_image = frame.to_image()
        break
    
    if frame_image is None:
        container.seek(0)
        for frame in container.decode(video=0):
            frame_image = frame.to_image()
            break
            
    # Generate thumbnail
    w, h = 320, 180
    if frame_image:
        thumb = frame_image.resize((w, h))
    
    return {
        "id": clip_id,
        "title": title,
        "duration": round(duration, 2),
        "thumb": [w, h]
    }
