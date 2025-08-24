import audio_analyzer
import audio_analyzer
import database
import os
import uuid
import tempfile
from typing import List, Dict, Any
from pathlib import Path
import yt_dlp
from pydub import AudioSegment
import whisper
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def process_video(youtube_url: str) -> List[Dict[str, Any]]:
    """
    Download and process a YouTube video into 15-second segments with transcripts.
    
    Args:
        youtube_url (str): The YouTube URL to process
        
    Returns:
        List[Dict[str, Any]]: List of video segments with metadata
    """
    try:
        logger.info(f"Processing video: {youtube_url}")
        
        # Create downloads directory if it doesn't exist
        downloads_dir = Path("downloads")
        downloads_dir.mkdir(exist_ok=True)
        
        # Generate unique identifier for this video
        video_id = str(uuid.uuid4())
        
        # Add video to database
        database.db.add_video(video_id, youtube_url)
        
        # Download video
        video_path, video_title = download_youtube_video(youtube_url, downloads_dir, video_id)
        if not video_path:
            raise Exception("Failed to download video")
        
        # Extract audio
        audio_path = extract_audio(video_path, downloads_dir, video_id)
        if not audio_path:
            raise Exception("Failed to extract audio")
        
        # Split audio into 15-second segments
        segments = split_audio_into_segments(audio_path, downloads_dir, video_id)
        
        # Generate transcripts for each segment
        segments_with_transcripts = generate_transcripts(segments)
        
        # Add video title to each segment
        print(f"Adding video title '{video_title}' to {len(segments_with_transcripts)} segments")
        for segment in segments_with_transcripts:
            segment['video_title'] = video_title
            segment['video_url'] = youtube_url
            print(f"Segment {segment['id']} - video_title: {segment['video_title']}")
        
        logger.info(f"Successfully processed video '{video_title}' into {len(segments_with_transcripts)} segments")
        
        # Update database with clips and mark as completed
        database.db.add_clips(video_id, segments_with_transcripts)
        database.db.update_video_status(video_id, "completed")
        return segments_with_transcripts
        
    except Exception as e:
        logger.error(f"Error processing video: {str(e)}")
        # Update status to failed if video_id exists
        if 'video_id' in locals():
            database.db.update_video_status(video_id, "failed")
        raise

def download_youtube_video(url: str, downloads_dir: Path, video_id: str) -> tuple[str, str]:
    """Download YouTube video using yt-dlp and return path and title."""
    try:
        video_path = downloads_dir / f"{video_id}_video.mp4"
        
        ydl_opts = {
            'format': 'best[height<=720]',  # Limit to 720p to keep file size reasonable
            'outtmpl': str(video_path),
            'quiet': True,
        }
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            try:
                # First, extract info to get the title
                info = ydl.extract_info(url, download=False)
                video_title = info.get('title', 'Unknown Video')
                
                # Debug logging
                print(f"Extracted video title: {video_title}")
                print(f"Video info keys: {list(info.keys())}")
                
                # Then download the video
                ydl.download([url])
            except Exception as e:
                print(f"Error extracting video info: {e}")
                # Try to extract video ID from URL as fallback
                try:
                    from urllib.parse import urlparse, parse_qs
                    parsed_url = urlparse(url)
                    if 'youtube.com' in parsed_url.netloc:
                        video_id = parse_qs(parsed_url.query).get('v', [None])[0]
                        if video_id:
                            video_title = f"YouTube Video ({video_id[:8]}...)"
                        else:
                            video_title = 'Unknown Video'
                    elif 'youtu.be' in parsed_url.netloc:
                        video_id = parsed_url.path[1:]  # Remove leading slash
                        if video_id:
                            video_title = f"YouTube Video ({video_id[:8]}...)"
                        else:
                            video_title = 'Unknown Video'
                    else:
                        video_title = 'Unknown Video'
                except:
                    video_title = 'Unknown Video'
                
                # Still try to download
                ydl.download([url])
        
        if video_path.exists():
            logger.info(f"Video downloaded to: {video_path}")
            return str(video_path), video_title
        else:
            logger.error("Video file not found after download")
            return None, None
            
    except Exception as e:
        logger.error(f"Error downloading video: {str(e)}")
        return None, None

def extract_audio(video_path: str, downloads_dir: Path, video_id: str) -> str:
    """Extract audio from video file."""
    try:
        audio_path = downloads_dir / f"{video_id}_audio.mp3"
        
        # Load video and extract audio
        video = AudioSegment.from_file(video_path, format="mp4")
        audio = video.set_channels(1).set_frame_rate(16000)  # Convert to mono, 16kHz for Whisper
        
        # Export audio
        audio.export(str(audio_path), format="mp3")
        
        logger.info(f"Audio extracted to: {audio_path}")
        return str(audio_path)
        
    except Exception as e:
        logger.error(f"Error extracting audio: {str(e)}")
        return None

def split_audio_into_segments(audio_path: str, downloads_dir: Path, video_id: str) -> List[Dict[str, Any]]:
    """Split audio into 15-second segments."""
    try:
        # Load audio
        audio = AudioSegment.from_mp3(audio_path)
        duration_ms = len(audio)
        duration_seconds = duration_ms / 1000
        
        segments = []
        segment_duration_ms = 15 * 1000  # 15 seconds in milliseconds
        
        # Handle videos shorter than 15 seconds
        if duration_seconds <= 15:
            segment = {
                "id": f"{video_id}_segment_1",
                "start_time": 0,
                "end_time": duration_seconds,
                "audio_path": str(downloads_dir / f"{video_id}_segment_1.mp3"),
                "video_path": str(downloads_dir / f"{video_id}_video.mp4"),
                "transcript": "", "audio_quality_score": 5.0, "dramatic_intensity": 5.0, "speech_clarity": 5.0, "segment_coherence": 5.0, "overall_score": 5.0, "boundary_type": "fixed"
            }
            segments.append(segment)
            
            # Export the single segment
            audio.export(segment["audio_path"], format="mp3")
            return segments
        
        # Split into 15-second segments
        segment_count = 1
        for start_ms in range(0, duration_ms, segment_duration_ms):
            end_ms = min(start_ms + segment_duration_ms, duration_ms)
            start_seconds = start_ms / 1000
            end_seconds = end_ms / 1000
            
            # Extract segment
            segment_audio = audio[start_ms:end_ms]
            
            segment = {
                "id": f"{video_id}_segment_{segment_count}",
                "start_time": start_seconds,
                "end_time": end_seconds,
                "audio_path": str(downloads_dir / f"{video_id}_segment_{segment_count}.mp3"),
                "video_path": str(downloads_dir / f"{video_id}_video.mp4"),
                "transcript": "", "audio_quality_score": 5.0, "dramatic_intensity": 5.0, "speech_clarity": 5.0, "segment_coherence": 5.0, "overall_score": 5.0, "boundary_type": "fixed"
            }
            
            # Export segment
            segment_audio.export(segment["audio_path"], format="mp3")
            segments.append(segment)
            segment_count += 1
        
        logger.info(f"Split audio into {len(segments)} segments")
        return segments
        
    except Exception as e:
        logger.error(f"Error splitting audio: {str(e)}")
        return []

def generate_transcripts(segments: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Generate transcripts for each audio segment using Whisper."""
    try:
        # Load Whisper model (this will download the model on first use)
        logger.info("Loading Whisper model...")
        model = whisper.load_model("base")  # Using base model for speed, can use "small" or "medium" for better accuracy
        
        for segment in segments:
            try:
                # Transcribe the segment
                result = model.transcribe(segment["audio_path"])
                segment["transcript"] = result["text"].strip()
                logger.info(f"Generated transcript for {segment['id']}: {segment['transcript'][:50]}...")
                
            except Exception as e:
                logger.error(f"Error transcribing segment {segment['id']}: {str(e)}")
                segment["transcript"] = "[Transcription failed]"
        
        return segments
        
    except Exception as e:
        logger.error(f"Error loading Whisper model: {str(e)}")
        # Return segments with empty transcripts if Whisper fails
        for segment in segments:
            segment["transcript"] = "[Transcription unavailable]"
        return segments
