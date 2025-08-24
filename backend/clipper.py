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
import ffmpeg
import numpy as np
from scipy.signal import find_peaks

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def process_video(youtube_url: str) -> List[Dict[str, Any]]:
    """
    Download and process a YouTube video into 15-second segments with transcripts and video clips.
    
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
        
        # Generate video clips for each segment
        segments_with_clips = generate_video_clips(segments, video_path, downloads_dir)
        
        # Generate transcripts for each segment
        segments_with_transcripts = generate_transcripts(segments_with_clips)
        
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
    """Intelligently split audio into optimal 15-second segments based on content analysis."""
    try:
        # Load audio
        audio = AudioSegment.from_mp3(audio_path)
        duration_ms = len(audio)
        duration_seconds = duration_ms / 1000
        
        # Handle videos shorter than 15 seconds
        if duration_seconds <= 15:
            segment = {
                "id": f"{video_id}_segment_1",
                "start_time": 0,
                "end_time": duration_seconds,
                "audio_path": str(downloads_dir / f"{video_id}_segment_1.mp3"),
                "video_path": str(downloads_dir / f"{video_id}_video.mp4"),
                "video_clip_path": str(downloads_dir / f"{video_id}_segment_1.mp4"),
                "transcript": "", "audio_quality_score": 5.0, "dramatic_intensity": 5.0, "speech_clarity": 5.0, "segment_coherence": 5.0, "overall_score": 5.0, "boundary_type": "natural"
            }
            segments.append(segment)
            
            # Export the single segment
            audio.export(segment["audio_path"], format="mp3")
            return segments
        
        # Use intelligent segmentation to find optimal 15-second clips
        segments = find_optimal_clips(audio, downloads_dir, video_id)
        
        logger.info(f"Intelligently split audio into {len(segments)} optimal segments")
        return segments
        
    except Exception as e:
        logger.error(f"Error splitting audio: {str(e)}")
        return []

def find_optimal_clips(audio: AudioSegment, downloads_dir: Path, video_id: str) -> List[Dict[str, Any]]:
    """Find optimal 15-second clips using content analysis and speech detection."""
    try:
        duration_ms = len(audio)
        duration_seconds = duration_ms / 1000
        
        # Convert audio to numpy array for analysis
        import numpy as np
        from scipy.signal import find_peaks
        
        # Extract audio data
        samples = np.array(audio.get_array_of_samples())
        sample_rate = audio.frame_rate
        
        # Find speech activity and natural boundaries
        speech_boundaries = detect_speech_boundaries(samples, sample_rate)
        
        # Generate candidate clips around speech boundaries
        candidate_clips = generate_candidate_clips(speech_boundaries, duration_seconds)
        
        # Score and select the best clips
        optimal_clips = select_best_clips(candidate_clips, audio, downloads_dir, video_id)
        
        return optimal_clips
        
    except Exception as e:
        logger.error(f"Error in intelligent clip detection: {str(e)}")
        # Fallback to fixed intervals if intelligent detection fails
        return fallback_to_fixed_segments(audio, downloads_dir, video_id)

def detect_speech_boundaries(samples: np.ndarray, sample_rate: int) -> List[float]:
    """Detect natural speech boundaries using energy and silence detection."""
    try:
        # Calculate energy over time
        frame_length = int(0.025 * sample_rate)  # 25ms frames
        hop_length = int(0.010 * sample_rate)    # 10ms hop
        
        energy = []
        for i in range(0, len(samples) - frame_length, hop_length):
            frame = samples[i:i + frame_length]
            energy.append(np.sum(frame ** 2))
        
        energy = np.array(energy)
        
        # Find silence periods (low energy)
        silence_threshold = np.percentile(energy, 30)  # Bottom 30% is silence
        silence_mask = energy < silence_threshold
        
        # Find speech boundaries (transitions from silence to speech)
        boundaries = []
        for i in range(1, len(silence_mask)):
            if not silence_mask[i-1] and silence_mask[i]:  # Speech to silence
                time_seconds = (i * hop_length) / sample_rate
                boundaries.append(time_seconds)
        
        return boundaries
        
    except Exception as e:
        logger.error(f"Error detecting speech boundaries: {str(e)}")
        return []

def generate_candidate_clips(boundaries: List[float], total_duration: float) -> List[tuple]:
    """Generate candidate clips around natural boundaries with varied lengths."""
    try:
        candidates = []
        
        # Add boundaries at start and end
        all_boundaries = [0.0] + boundaries + [total_duration]
        
        for i, boundary in enumerate(all_boundaries):
            # Try different start times around this boundary
            for offset in [-3, -2, -1, 0, 1, 2, 3]:  # Try 3 seconds before/after boundary
                start_time = max(0, boundary + offset)
                
                # Try different durations: 12-18 seconds for variety
                for target_duration in [12.0, 13.0, 14.0, 15.0, 16.0, 17.0, 18.0]:
                    end_time = min(total_duration, start_time + target_duration)
                    
                    # Only add if we get a reasonable duration
                    if end_time - start_time >= 11.0:  # At least 11 seconds
                        candidates.append((start_time, end_time))
        
        # Remove duplicates and sort
        candidates = list(set(candidates))
        candidates.sort(key=lambda x: x[0])
        
        return candidates
        
    except Exception as e:
        logger.error(f"Error generating candidate clips: {str(e)}")
        return []

def select_best_clips(candidates: List[tuple], audio: AudioSegment, downloads_dir: Path, video_id: str) -> List[Dict[str, Any]]:
    """Select the best clips based on content quality and diversity."""
    try:
        if not candidates:
            return fallback_to_fixed_segments(audio, downloads_dir, video_id)
        
        # Score each candidate based on various factors
        scored_candidates = []
        for start_time, end_time in candidates:
            score = score_clip_quality(audio, start_time, end_time)
            scored_candidates.append((start_time, end_time, score))
        
        # Sort by score and select top candidates
        scored_candidates.sort(key=lambda x: x[2], reverse=True)
        
        # Select top clips, ensuring they don't overlap too much
        selected_clips = []
        for start_time, end_time, score in scored_candidates:
            # Check if this clip overlaps significantly with already selected clips
            overlaps = False
            for selected_start, selected_end, _ in selected_clips:
                overlap_start = max(start_time, selected_start)
                overlap_end = min(end_time, selected_end)
                if overlap_end - overlap_start > 3.0:  # More than 3 seconds overlap
                    overlaps = True
                    break
            
            if not overlaps:
                selected_clips.append((start_time, end_time, score))
                
                # Limit to reasonable number of clips
                if len(selected_clips) >= 8:
                    break
        
        # Convert to segment format
        segments = []
        for i, (start_time, end_time, score) in enumerate(selected_clips):
            segment = {
                "id": f"{video_id}_segment_{i+1}",
                "start_time": start_time,
                "end_time": end_time,
                "audio_path": str(downloads_dir / f"{video_id}_segment_{i+1}.mp3"),
                "video_path": str(downloads_dir / f"{video_id}_video.mp4"),
                "video_clip_path": str(downloads_dir / f"{video_id}_segment_{i+1}.mp4"),
                "transcript": "",
                "audio_quality_score": score,
                "dramatic_intensity": 5.0,
                "speech_clarity": 5.0,
                "segment_coherence": 5.0,
                "overall_score": 5.0,
                "boundary_type": "intelligent"
            }
            
            # Extract and export the audio segment
            start_ms = int(start_time * 1000)
            end_ms = int(end_time * 1000)
            segment_audio = audio[start_ms:end_ms]
            segment_audio.export(segment["audio_path"], format="mp3")
            
            segments.append(segment)
        
        return segments
        
    except Exception as e:
        logger.error(f"Error selecting best clips: {str(e)}")
        return fallback_to_fixed_segments(audio, downloads_dir, video_id)

def score_clip_quality(audio: AudioSegment, start_time: float, end_time: float) -> float:
    """Score a clip based on audio quality and content factors."""
    try:
        start_ms = int(start_time * 1000)
        end_ms = int(end_time * 1000)
        clip_audio = audio[start_ms:end_ms]
        
        # Convert to numpy for analysis
        samples = np.array(clip_audio.get_array_of_samples())
        
        # Calculate various quality metrics
        energy = np.mean(samples ** 2)
        energy_variance = np.var(samples ** 2)
        
        # Higher energy and variance = more dynamic content
        quality_score = min(10.0, (energy / 1000000) + (energy_variance / 1000000))
        
        return quality_score
        
    except Exception as e:
        logger.error(f"Error scoring clip quality: {str(e)}")
        return 5.0

def fallback_to_fixed_segments(audio: AudioSegment, downloads_dir: Path, video_id: str) -> List[Dict[str, Any]]:
    """Fallback to fixed 15-second segments if intelligent detection fails."""
    try:
        duration_ms = len(audio)
        segment_duration_ms = 15 * 1000
        
        segments = []
        segment_count = 1
        
        for start_ms in range(0, duration_ms, segment_duration_ms):
            end_ms = min(start_ms + segment_duration_ms, duration_ms)
            start_seconds = start_ms / 1000
            end_seconds = end_ms / 1000
            
            segment_audio = audio[start_ms:end_ms]
            
            segment = {
                "id": f"{video_id}_segment_{segment_count}",
                "start_time": start_seconds,
                "end_time": end_seconds,
                "audio_path": str(downloads_dir / f"{video_id}_segment_{segment_count}.mp3"),
                "video_path": str(downloads_dir / f"{video_id}_video.mp4"),
                "video_clip_path": str(downloads_dir / f"{video_id}_segment_{segment_count}.mp4"),
                "transcript": "",
                "audio_quality_score": 5.0,
                "dramatic_intensity": 5.0,
                "speech_clarity": 5.0,
                "segment_coherence": 5.0,
                "overall_score": 5.0,
                "boundary_type": "fixed"
            }
            
            segment_audio.export(segment["audio_path"], format="mp3")
            segments.append(segment)
            segment_count += 1
        
        return segments
        
    except Exception as e:
        logger.error(f"Error in fallback segmentation: {str(e)}")
        return []

def generate_video_clips(segments: List[Dict[str, Any]], source_video_path: str, downloads_dir: Path) -> List[Dict[str, Any]]:
    """Generate 15-second video clips for each segment using FFmpeg."""
    try:
        logger.info(f"Generating video clips for {len(segments)} segments")
        
        for segment in segments:
            try:
                start_time = segment["start_time"]
                end_time = segment["end_time"]
                clip_path = segment["video_clip_path"]
                
                # Use FFmpeg to extract the video segment
                (
                    ffmpeg
                    .input(source_video_path, ss=start_time, t=end_time - start_time)
                    .output(clip_path, 
                           vcodec='libx264',  # H.264 codec for compatibility
                           acodec='aac',      # AAC audio codec
                           preset='fast',     # Faster encoding
                           crf=23,            # Good quality/size balance
                           movflags='+faststart'  # Optimize for web streaming
                    )
                    .overwrite_output()
                    .run(quiet=True, capture_stdout=True, capture_stderr=True)
                )
                
                logger.info(f"Generated video clip: {clip_path}")
                
            except Exception as e:
                logger.error(f"Error generating video clip for segment {segment['id']}: {str(e)}")
                # Set clip path to None if generation fails
                segment["video_clip_path"] = None
        
        return segments
        
    except Exception as e:
        logger.error(f"Error in video clip generation: {str(e)}")
        return segments

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
