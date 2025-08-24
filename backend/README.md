# 15 Seconds of Fame - Backend

A FastAPI backend that processes YouTube videos into 15-second clips and scores them for viral potential.

## Features

- **YouTube Video Processing**: Downloads and processes YouTube videos using yt-dlp
- **Audio Segmentation**: Splits videos into 15-second audio segments
- **Video Clip Generation**: Creates actual 15-second video clips optimized for social media
- **Transcript Generation**: Uses OpenAI Whisper to generate transcripts for each segment
- **Content Scoring**: Analyzes transcripts for engagement potential
- **REST API**: FastAPI endpoints for video processing and file serving

## Setup

### Prerequisites

- Python 3.8+
- FFmpeg (required for audio and video processing)

### Install FFmpeg

**macOS:**
```bash
brew install ffmpeg
```

**Ubuntu/Debian:**
```bash
sudo apt update
sudo apt install ffmpeg
```

**Windows:**
Download from https://ffmpeg.org/download.html

### Install Python Dependencies

```bash
cd backend
pip install -r requirements.txt
```

## Usage

### Start the Server

```bash
python app.py
```

Or with uvicorn:
```bash
uvicorn app:app --reload
```

The API will be available at `http://localhost:8000`

### API Endpoints

#### POST `/process`

Process a YouTube video into scored clips with both audio and video files.

**Request:**
```json
{
  "youtube_url": "https://www.youtube.com/watch?v=example"
}
```

**Response:**
```json
{
  "clips": [
    {
      "id": "clip_uuid_segment_1",
      "segment_id": "uuid_segment_1",
      "score": 8.5,
      "start_time": 0.0,
      "end_time": 15.0,
      "transcript": "This is the transcript text...",
      "audio_path": "downloads/uuid_segment_1.mp3",
      "video_path": "downloads/uuid_video.mp4",
      "video_clip_path": "downloads/uuid_segment_1.mp4",
      "reasoning": "High engagement potential; Contains humor"
    }
  ],
  "status": "success"
}
```

#### GET `/audio/{clip_id}`

Serve audio files for clips.

#### GET `/video/{clip_id}`

Serve video clip files (new endpoint).

#### GET `/videos/{video_id}`

Get information about a processed video.

#### POST `/cleanup`

Clean up old files (admin endpoint).

#### GET `/api/usage`

Get OpenAI API usage statistics.

#### POST `/api/reset-usage`

Reset daily API usage counters.

### Video Clip Features

The backend now generates actual 15-second video clips that are:

- **Optimized for social media**: Uses H.264/AAC codecs with faststart for web compatibility
- **Ready for sharing**: Can be directly uploaded to TikTok, LinkedIn, Instagram Reels, etc.
- **High quality**: Balanced quality/size ratio (CRF 23)
- **Fast encoding**: Uses 'fast' preset for quicker processing

### Testing

Run the test script to verify video clip functionality:

```bash
python test_video_clips.py
```

## File Structure

```
backend/
├── app.py              # FastAPI application
├── clipper.py          # Video processing module (now with video clips)
├── scorer.py           # Content scoring module
├── database.py         # Database operations
├── requirements.txt    # Python dependencies
├── test_video_clips.py # Video clip testing script
└── downloads/          # Generated audio and video files
```

## Video Processing Pipeline

1. **Download**: YouTube video downloaded using yt-dlp
2. **Audio Extraction**: Audio extracted for transcription
3. **Segmentation**: Video split into 15-second segments
4. **Video Clip Generation**: FFmpeg creates individual video clips
5. **Transcription**: Whisper generates transcripts
6. **Scoring**: AI analyzes content for viral potential
7. **Storage**: All files stored in downloads directory

## Frontend Integration

The frontend now supports:
- Video clip preview with HTML5 video player
- Download buttons for both audio and video files
- Enhanced clip cards with video controls
