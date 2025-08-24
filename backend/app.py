from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any
import clipper
import scorer

app = FastAPI(title="15 Seconds of Fame API", version="1.0.0")

class ProcessRequest(BaseModel):
    youtube_url: str

class ProcessResponse(BaseModel):
    clips: List[Dict[str, Any]]
    status: str

@app.get("/")
async def root():
    return {"message": "15 Seconds of Fame API"}

@app.post("/process", response_model=ProcessResponse)
async def process_video(request: ProcessRequest):
    try:
        # Call function in clipper.py to download and split video
        video_segments = clipper.process_video(request.youtube_url)
        
        # Call function in scorer.py to score transcript segments
        scored_clips = scorer.score_segments(video_segments)
        
        return ProcessResponse(
            clips=scored_clips,
            status="success"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing video: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
