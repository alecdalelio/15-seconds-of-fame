from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import List, Dict, Any
import clipper
import scorer
import database
import viral_analyzer
import os
from datetime import datetime

app = FastAPI(title="15 Seconds of Fame API", version="1.0.0")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],  # Frontend URLs
    allow_credentials=True,
    allow_methods=["*"],  # Allow all methods
    allow_headers=["*"],  # Allow all headers
)

# Mount static files for serving audio files
app.mount("/downloads", StaticFiles(directory="downloads"), name="downloads")

class ProcessRequest(BaseModel):
    youtube_url: str

class ProcessResponse(BaseModel):
    clips: List[Dict[str, Any]]
    status: str

@app.get("/")
async def root():
    return {"message": "15 Seconds of Fame API"}

@app.get("/audio/{clip_id}")
async def get_audio(clip_id: str):
    """Serve audio files for clips."""
    try:
        # Look for the audio file in the downloads directory
        downloads_dir = "downloads"
        audio_file = None
        
        # Search for files that match the clip_id pattern
        for filename in os.listdir(downloads_dir):
            if filename.startswith(clip_id.replace("clip_", "")) and filename.endswith(".mp3"):
                audio_file = os.path.join(downloads_dir, filename)
                break
        
        if audio_file and os.path.exists(audio_file):
            return FileResponse(audio_file, media_type="audio/mpeg")
        else:
            raise HTTPException(status_code=404, detail="Audio file not found")
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error serving audio: {str(e)}")

@app.get("/video/{clip_id}")
async def get_video_clip(clip_id: str):
    """Serve video clip files."""
    try:
        # Look for the video clip file in the downloads directory
        downloads_dir = "downloads"
        video_file = None
        
        # Search for files that match the clip_id pattern
        for filename in os.listdir(downloads_dir):
            if filename.startswith(clip_id.replace("clip_", "")) and filename.endswith(".mp4"):
                video_file = os.path.join(downloads_dir, filename)
                break
        
        if video_file and os.path.exists(video_file):
            return FileResponse(video_file, media_type="video/mp4")
        else:
            raise HTTPException(status_code=404, detail="Video clip file not found")
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error serving video clip: {str(e)}")

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

@app.post("/cleanup")
async def cleanup_old_files():
    """Clean up old files (admin endpoint)."""
    try:
        deleted_count = database.db.cleanup_old_files()
        return {"message": f"Cleanup completed. {deleted_count} files deleted."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error during cleanup: {str(e)}")

@app.get("/videos/{video_id}")
async def get_video_info(video_id: str):
    """Get information about a processed video."""
    try:
        video_info = database.db.get_video_info(video_id)
        if not video_info:
            raise HTTPException(status_code=404, detail="Video not found")
        
        clips = database.db.get_video_clips(video_id)
        return {
            "video": video_info,
            "clips": clips
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting video info: {str(e)}")

@app.get("/api/usage")
async def get_api_usage():
    """Get OpenAI API usage statistics."""
    try:
        usage_stats = openai_analyzer.analyzer.get_usage_stats()
        return usage_stats
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting usage stats: {str(e)}")

@app.post("/api/reset-usage")
async def reset_api_usage():
    """Reset daily API usage counters."""
    try:
        openai_analyzer.analyzer.reset_daily_usage()
        return {"message": "Daily usage counters reset successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error resetting usage: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
