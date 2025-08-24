# 15 Seconds of Fame - Backend

A FastAPI backend that processes YouTube videos into 15-second clips and scores them for viral potential.

## Features

- **YouTube Video Processing**: Downloads and processes YouTube videos using yt-dlp
- **Audio Segmentation**: Splits videos into 15-second audio segments
- **Transcript Generation**: Uses OpenAI Whisper to generate transcripts for each segment
- **Content Scoring**: Analyzes transcripts for engagement potential
- **REST API**: FastAPI endpoints for video processing

## Setup

### Prerequisites

- Python 3.8+
- FFmpeg (required for audio processing)

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

Process a YouTube video into scored clips.

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
      "reasoning": "High engagement potential; Contains humor"
    }
  ],
  "status": "success"
}
```

### Testing

Run the test script to verify functionality:

```bash
python test_clipper.py
```

## File Structure

```
backend/
├── app.py              # FastAPI application
├── clipper.py          # Video processing module
├── scorer.py           # Content scoring module
├── requirements.txt    # Python dependencies
├── downloads/          # Downloaded videos and segments
├── test_clipper.py     # Test script
└── README.md          # This file
```

## How It Works

1. **Video Download**: Uses yt-dlp to download YouTube videos (limited to 720p for efficiency)
2. **Audio Extraction**: Extracts audio from video files using pydub
3. **Segmentation**: Splits audio into 15-second segments
4. **Transcription**: Uses Whisper to generate transcripts for each segment
5. **Scoring**: Analyzes transcripts for engagement factors (humor, excitement, etc.)
6. **Ranking**: Returns clips sorted by engagement score

## Scoring Algorithm

The scoring system analyzes transcripts for:

- **Positive Indicators**: Humor, excitement, controversy, emotional words
- **Negative Indicators**: Filler words, silence, boring content
- **Engagement Factors**: Exclamation marks, questions, content length
- **Base Score**: 5.0 with adjustments based on content analysis

## Error Handling

The system handles various edge cases:
- Videos shorter than 15 seconds
- Failed downloads
- Audio extraction errors
- Transcription failures
- Invalid YouTube URLs

## Performance Notes

- First run will download the Whisper model (~1GB)
- Processing time depends on video length
- Audio files are stored in the `downloads/` directory
- Consider implementing cleanup for old files in production

## Development

### Adding New Scoring Factors

Edit `scorer.py` to add new scoring criteria:
- Add new keywords to `positive_words` or `negative_words`
- Modify scoring weights in `calculate_engagement_score()`
- Update reasoning logic in `generate_reasoning()`

### Improving Transcription

- Change Whisper model size in `clipper.py`:
  - `"base"` (fastest, ~1GB)
  - `"small"` (balanced, ~244MB)
  - `"medium"` (better accuracy, ~769MB)
  - `"large"` (best accuracy, ~1550MB)
