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
        
        logger.info(f"Finding optimal clips for {duration_seconds:.1f}s audio")
        
        # Convert audio to numpy array for analysis
        import numpy as np
        from scipy.signal import find_peaks
        
        # Extract audio data
        samples = np.array(audio.get_array_of_samples())
        sample_rate = audio.frame_rate
        
        # Find speech activity and natural boundaries
        speech_boundaries = detect_speech_boundaries(samples, sample_rate)
        logger.info(f"Detected {len(speech_boundaries)} speech boundaries")
        
        # Generate candidate clips around speech boundaries
        candidate_clips = generate_candidate_clips(speech_boundaries, duration_seconds)
        logger.info(f"Generated {len(candidate_clips)} candidate clips")
        
        # Score and select the best clips
        optimal_clips = select_best_clips(candidate_clips, audio, downloads_dir, video_id)
        
        logger.info(f"Selected {len(optimal_clips)} optimal clips")
        
        # Log the timing distribution of selected clips
        if optimal_clips:
            timings = [(clip['start_time'], clip['end_time']) for clip in optimal_clips]
            logger.info(f"Selected clip timings: {timings}")
            
            # Check if clips are too clustered at the beginning
            early_clips = [clip for clip in optimal_clips if clip['start_time'] < duration_seconds * 0.3]
            if len(early_clips) > len(optimal_clips) * 0.6:  # More than 60% in first 30%
                logger.warning(f"Warning: {len(early_clips)}/{len(optimal_clips)} clips are in the first 30% of the video")
        
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
        silence_threshold = np.percentile(energy, 25)  # Bottom 25% is silence
        silence_mask = energy < silence_threshold
        
        # Find speech boundaries (transitions from speech to silence and vice versa)
        boundaries = []
        
        # Find speech-to-silence transitions (good for ending clips)
        for i in range(1, len(silence_mask)):
            if not silence_mask[i-1] and silence_mask[i]:  # Speech to silence
                time_seconds = (i * hop_length) / sample_rate
                # Only add if it's not too close to the beginning or end
                if 5 < time_seconds < (len(samples) / sample_rate - 5):
                    boundaries.append(time_seconds)
        
        # Find silence-to-speech transitions (good for starting clips)
        for i in range(1, len(silence_mask)):
            if silence_mask[i-1] and not silence_mask[i]:  # Silence to speech
                time_seconds = (i * hop_length) / sample_rate
                # Only add if it's not too close to the beginning or end
                if 5 < time_seconds < (len(samples) / sample_rate - 5):
                    boundaries.append(time_seconds)
        
        # Remove duplicate boundaries (within 1 second)
        if boundaries:
            boundaries.sort()
            filtered_boundaries = [boundaries[0]]
            for boundary in boundaries[1:]:
                if boundary - filtered_boundaries[-1] > 1.0:  # At least 1 second apart
                    filtered_boundaries.append(boundary)
            boundaries = filtered_boundaries
        
        # If we don't have enough boundaries, add some strategic ones
        if len(boundaries) < 3:
            total_duration = len(samples) / sample_rate
            # Add boundaries at 25%, 50%, and 75% of the video
            strategic_boundaries = [
                total_duration * 0.25,
                total_duration * 0.50,
                total_duration * 0.75
            ]
            for boundary in strategic_boundaries:
                if 5 < boundary < (total_duration - 5):
                    boundaries.append(boundary)
        
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
        
        # Strategy 1: Clips around detected boundaries
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
        
        # Strategy 2: Strategic sampling across the video
        # Create clips at different positions to ensure coverage
        strategic_positions = []
        
        # Early section (first 20% of video) - fewer candidates
        early_start = max(5, total_duration * 0.05)  # Start at 5% but not before 5 seconds
        early_end = min(total_duration * 0.25, total_duration - 5)
        if early_end - early_start >= 10:
            strategic_positions.extend([
                (early_start, early_start + 15),
                (early_start + 8, early_start + 23)
            ])
        
        # Middle section (25-75% of video) - more candidates
        mid_start = max(total_duration * 0.25, 10)
        mid_end = min(total_duration * 0.75, total_duration - 10)
        if mid_end - mid_start >= 10:
            strategic_positions.extend([
                (mid_start, mid_start + 15),
                (mid_start + 15, mid_start + 30),
                (mid_start + 30, mid_start + 45),
                (mid_start + 45, mid_start + 60),
                (mid_start + 60, mid_start + 75),
                (mid_start + 75, mid_start + 90)
            ])
        
        # Late section (last 25% of video) - more candidates
        late_start = max(total_duration * 0.75, total_duration - 60)
        late_end = min(total_duration - 5, total_duration)
        if late_end - late_start >= 10:
            strategic_positions.extend([
                (late_start, late_start + 15),
                (late_start + 10, late_start + 25),
                (late_start + 20, late_start + 35),
                (late_start + 30, late_start + 45)
            ])
        
        # Add strategic positions to candidates
        for start_time, end_time in strategic_positions:
            if end_time <= total_duration and end_time - start_time >= 11.0:
                candidates.append((start_time, end_time))
        
        # Strategy 3: Random sampling for diversity
        import random
        random.seed(42)  # For reproducible results
        
        for _ in range(15):  # Generate 15 random candidates (increased from 10)
            # Random start time, avoiding the very beginning and end
            # Bias towards middle and later parts of the video
            if random.random() < 0.3:  # 30% chance for early part
                start_time = random.uniform(10, total_duration * 0.3)
            elif random.random() < 0.5:  # 50% chance for middle part
                start_time = random.uniform(total_duration * 0.3, total_duration * 0.7)
            else:  # 20% chance for late part
                start_time = random.uniform(total_duration * 0.7, total_duration - 20)
            
            # Random duration between 12-18 seconds
            duration = random.uniform(12, 18)
            end_time = min(total_duration - 2, start_time + duration)
            
            if end_time - start_time >= 11.0:
                candidates.append((start_time, end_time))
        
        # Remove duplicates and sort
        candidates = list(set(candidates))
        candidates.sort(key=lambda x: x[0])
        
        # Limit to reasonable number of candidates to avoid overwhelming the system
        if len(candidates) > 50:
            # Keep the most diverse candidates
            candidates = _select_diverse_candidates(candidates, 50)
        
        return candidates
        
    except Exception as e:
        logger.error(f"Error generating candidate clips: {str(e)}")
        return []

def _select_diverse_candidates(candidates: List[tuple], max_count: int) -> List[tuple]:
    """Select diverse candidates to avoid clustering."""
    if len(candidates) <= max_count:
        return candidates
    
    # Sort by start time
    candidates.sort(key=lambda x: x[0])
    
    # Select candidates with good spacing
    selected = []
    step = len(candidates) // max_count
    
    for i in range(0, len(candidates), step):
        if len(selected) < max_count:
            selected.append(candidates[i])
    
    # Add any remaining slots with random selection
    remaining = [c for c in candidates if c not in selected]
    if remaining and len(selected) < max_count:
        import random
        random.shuffle(remaining)
        selected.extend(remaining[:max_count - len(selected)])
    
    return selected[:max_count]

def select_best_clips(candidates: List[tuple], audio: AudioSegment, downloads_dir: Path, video_id: str) -> List[Dict[str, Any]]:
    """Select the best clips based on content quality and diversity."""
    try:
        if not candidates:
            logger.info("No candidates found, using fallback segmentation")
            return fallback_to_fixed_segments(audio, downloads_dir, video_id)
        
        logger.info(f"Scoring {len(candidates)} candidate clips")
        
        # Score each candidate based on various factors
        scored_candidates = []
        for i, (start_time, end_time) in enumerate(candidates):
            score = score_clip_quality(audio, start_time, end_time)
            scored_candidates.append((start_time, end_time, score))
            logger.debug(f"Candidate {i+1}: {start_time:.1f}s - {end_time:.1f}s, score: {score:.2f}")
        
        # Sort by score and select top candidates
        scored_candidates.sort(key=lambda x: x[2], reverse=True)
        
        logger.info(f"Top 5 candidate scores: {[f'{score:.2f}' for _, _, score in scored_candidates[:5]]}")
        
        # NEW: Force diversity by selecting clips from different time zones
        video_duration = len(audio) / 1000
        logger.info(f"Video duration: {video_duration:.1f}s")
        
        # Define time zones for diversity
        time_zones = [
            (0, video_duration * 0.2),           # First 20%
            (video_duration * 0.2, video_duration * 0.4),  # 20-40%
            (video_duration * 0.4, video_duration * 0.6),  # 40-60%
            (video_duration * 0.6, video_duration * 0.8),  # 60-80%
            (video_duration * 0.8, video_duration)         # Last 20%
        ]
        
        selected_clips = []
        clips_per_zone = 2  # Try to get 2 clips per zone (10 total, but we'll limit to 8)
        
        # Select best clips from each time zone
        for zone_start, zone_end in time_zones:
            zone_candidates = [
                (start, end, score) for start, end, score in scored_candidates
                if zone_start <= start < zone_end
            ]
            
            logger.info(f"Zone {zone_start:.1f}s-{zone_end:.1f}s: {len(zone_candidates)} candidates")
            
            # Select best clips from this zone
            zone_selected = 0
            for start_time, end_time, score in zone_candidates:
                if zone_selected >= clips_per_zone:
                    break
                    
                # Check for overlaps with already selected clips
                overlaps = False
                for selected_start, selected_end, _ in selected_clips:
                    overlap_start = max(start_time, selected_start)
                    overlap_end = min(end_time, selected_end)
                    if overlap_end - overlap_start > 3.0:  # More than 3 seconds overlap
                        overlaps = True
                        break
                
                if not overlaps:
                    selected_clips.append((start_time, end_time, score))
                    logger.info(f"Selected clip from zone {zone_start:.1f}s-{zone_end:.1f}s: {start_time:.1f}s - {end_time:.1f}s, score: {score:.2f}")
                    zone_selected += 1
                    
                    # Limit total clips
                    if len(selected_clips) >= 8:
                        break
        
        # If we didn't get enough clips from zones, fill with remaining high-scoring clips
        if len(selected_clips) < 5:  # Minimum 5 clips
            logger.info(f"Only selected {len(selected_clips)} clips from zones, filling with remaining candidates")
            
            for start_time, end_time, score in scored_candidates:
                if len(selected_clips) >= 8:
                    break
                    
                # Check if this clip is already selected
                already_selected = any(
                    abs(start_time - selected_start) < 1.0 and abs(end_time - selected_end) < 1.0
                    for selected_start, selected_end, _ in selected_clips
                )
                
                if not already_selected:
                    # Check for overlaps
                    overlaps = False
                    for selected_start, selected_end, _ in selected_clips:
                        overlap_start = max(start_time, selected_start)
                        overlap_end = min(end_time, selected_end)
                        if overlap_end - overlap_start > 3.0:
                            overlaps = True
                            break
                    
                    if not overlaps:
                        selected_clips.append((start_time, end_time, score))
                        logger.info(f"Added remaining clip: {start_time:.1f}s - {end_time:.1f}s, score: {score:.2f}")
        
        logger.info(f"Selected {len(selected_clips)} clips with diversity-enforced selection")
        
        # Log the timing distribution of selected clips
        if selected_clips:
            timings = [(clip[0], clip[1]) for clip in selected_clips]
            logger.info(f"Final selected clip timings: {timings}")
            
            # Check distribution
            early_clips = [clip for clip in selected_clips if clip[0] < video_duration * 0.3]
            middle_clips = [clip for clip in selected_clips if video_duration * 0.3 <= clip[0] < video_duration * 0.7]
            late_clips = [clip for clip in selected_clips if clip[0] >= video_duration * 0.7]
            
            logger.info(f"Distribution: {len(early_clips)} early, {len(middle_clips)} middle, {len(late_clips)} late")
            
            if len(early_clips) > len(selected_clips) * 0.6:
                logger.warning(f"Warning: Still too many early clips: {len(early_clips)}/{len(selected_clips)}")
        
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
                "boundary_type": "intelligent_diverse"
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
        
        # Calculate RMS (Root Mean Square) for volume analysis
        rms = np.sqrt(np.mean(samples ** 2))
        
        # Calculate zero-crossing rate (indicates speech vs silence)
        zero_crossings = np.sum(np.diff(np.sign(samples)) != 0)
        zero_crossing_rate = zero_crossings / len(samples)
        
        # Calculate spectral centroid (brightness of sound)
        fft = np.fft.fft(samples)
        magnitude = np.abs(fft)
        frequencies = np.fft.fftfreq(len(samples), 1/clip_audio.frame_rate)
        spectral_centroid = np.sum(frequencies * magnitude) / np.sum(magnitude)
        
        # Enhanced scoring algorithm
        score = 5.0  # Base score
        
        # Volume/energy scoring (0-2 points)
        if rms > 1000:  # Good volume
            score += 1.0
        elif rms < 100:  # Too quiet
            score -= 1.0
        
        # Dynamic range scoring (0-2 points)
        if energy_variance > 1000000:  # Good dynamic range
            score += 1.0
        elif energy_variance < 100000:  # Too flat
            score -= 0.5
        
        # Speech activity scoring (0-2 points)
        if 0.01 < zero_crossing_rate < 0.1:  # Good speech range
            score += 1.0
        elif zero_crossing_rate < 0.005:  # Too much silence
            score -= 1.0
        
        # Frequency content scoring (0-1 point)
        if spectral_centroid > 1000:  # Good frequency range
            score += 0.5
        
        # Position in video scoring (0-2 points)
        # Strongly prefer clips that aren't at the very beginning or end
        video_duration = len(audio) / 1000
        clip_center = (start_time + end_time) / 2
        
        # Strong penalty for clips in the first 10% of the video
        if clip_center < video_duration * 0.1:
            score -= 2.0  # Strong penalty for very early clips
        # Moderate penalty for clips in the first 30% of the video
        elif clip_center < video_duration * 0.3:
            score -= 1.0  # Moderate penalty for early clips
        # Bonus for clips in the middle section (30-70%)
        elif video_duration * 0.3 <= clip_center <= video_duration * 0.7:
            score += 1.0  # Bonus for middle clips
        # Small penalty for clips in the last 10%
        elif clip_center > video_duration * 0.9:
            score -= 0.5  # Small penalty for very late clips
        
        # Ensure score is within bounds
        score = max(1.0, min(10.0, score))
        
        return score
        
    except Exception as e:
        logger.error(f"Error scoring clip quality: {str(e)}")
        return 5.0

def fallback_to_fixed_segments(audio: AudioSegment, downloads_dir: Path, video_id: str) -> List[Dict[str, Any]]:
    """Fallback to diverse 15-second segments if intelligent detection fails."""
    try:
        logger.info("Using fallback segmentation with diverse positioning")
        
        duration_ms = len(audio)
        duration_seconds = duration_ms / 1000
        segment_duration_ms = 15 * 1000
        
        segments = []
        segment_count = 1
        
        # Instead of sequential segments, create diverse segments across the video
        # Calculate how many segments we can fit
        max_segments = min(8, int(duration_seconds / 15))  # Limit to 8 segments max
        
        logger.info(f"Video duration: {duration_seconds:.1f}s, creating up to {max_segments} segments")
        
        if max_segments <= 0:
            # Very short video, just create one segment
            logger.info("Very short video, creating single segment")
            segment = {
                "id": f"{video_id}_segment_{segment_count}",
                "start_time": 0.0,
                "end_time": min(15.0, duration_seconds),
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
            
            segment_audio = audio[0:min(15000, duration_ms)]
            segment_audio.export(segment["audio_path"], format="mp3")
            segments.append(segment)
            return segments
        
        # Create diverse segments across the video
        import random
        random.seed(42)  # For reproducible results
        
        # Define target positions (avoiding the very beginning and end)
        target_positions = []
        
        if max_segments >= 1:
            # First segment: start around 5-10 seconds in
            pos = random.uniform(5, min(10, duration_seconds - 20))
            target_positions.append(pos)
            logger.info(f"Target position 1: {pos:.1f}s")
        
        if max_segments >= 2:
            # Second segment: around 25-35% of video
            pos = random.uniform(duration_seconds * 0.25, duration_seconds * 0.35)
            target_positions.append(pos)
            logger.info(f"Target position 2: {pos:.1f}s")
        
        if max_segments >= 3:
            # Third segment: around 45-55% of video
            pos = random.uniform(duration_seconds * 0.45, duration_seconds * 0.55)
            target_positions.append(pos)
            logger.info(f"Target position 3: {pos:.1f}s")
        
        if max_segments >= 4:
            # Fourth segment: around 65-75% of video
            pos = random.uniform(duration_seconds * 0.65, duration_seconds * 0.75)
            target_positions.append(pos)
            logger.info(f"Target position 4: {pos:.1f}s")
        
        if max_segments >= 5:
            # Fifth segment: around 80-85% of video
            pos = random.uniform(duration_seconds * 0.80, duration_seconds * 0.85)
            target_positions.append(pos)
            logger.info(f"Target position 5: {pos:.1f}s")
        
        if max_segments >= 6:
            # Sixth segment: around 15-20% of video
            pos = random.uniform(duration_seconds * 0.15, duration_seconds * 0.20)
            target_positions.append(pos)
            logger.info(f"Target position 6: {pos:.1f}s")
        
        if max_segments >= 7:
            # Seventh segment: around 90-95% of video
            pos = random.uniform(duration_seconds * 0.90, duration_seconds * 0.95)
            target_positions.append(pos)
            logger.info(f"Target position 7: {pos:.1f}s")
        
        if max_segments >= 8:
            # Eighth segment: around 40-45% of video
            pos = random.uniform(duration_seconds * 0.40, duration_seconds * 0.45)
            target_positions.append(pos)
            logger.info(f"Target position 8: {pos:.1f}s")
        
        # Create segments at these positions
        for i, start_seconds in enumerate(target_positions[:max_segments]):
            start_ms = int(start_seconds * 1000)
            end_ms = min(start_ms + segment_duration_ms, duration_ms)
            end_seconds = end_ms / 1000
            
            # Ensure we have at least 10 seconds of content
            if end_seconds - start_seconds >= 10.0:
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
                    "boundary_type": "fixed_diverse"
                }
                
                segment_audio.export(segment["audio_path"], format="mp3")
                segments.append(segment)
                logger.info(f"Created diverse segment {segment_count}: {start_seconds:.1f}s - {end_seconds:.1f}s")
                segment_count += 1
        
        # If we didn't get enough segments, add some sequential ones as backup
        if len(segments) < 3:
            logger.info(f"Only created {len(segments)} diverse segments, adding sequential backup")
            for start_ms in range(0, duration_ms, segment_duration_ms):
                if len(segments) >= 8:  # Limit total segments
                    break
                    
                end_ms = min(start_ms + segment_duration_ms, duration_ms)
                start_seconds = start_ms / 1000
                end_seconds = end_ms / 1000
                
                # Skip if this overlaps with existing segments
                overlaps = False
                for existing_segment in segments:
                    if (start_seconds < existing_segment["end_time"] and 
                        end_seconds > existing_segment["start_time"]):
                        overlaps = True
                        break
                
                if not overlaps and (end_seconds - start_seconds) >= 10.0:
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
                        "boundary_type": "fixed_sequential"
                    }
                    
                    segment_audio.export(segment["audio_path"], format="mp3")
                    segments.append(segment)
                    logger.info(f"Created sequential segment {segment_count}: {start_seconds:.1f}s - {end_seconds:.1f}s")
                    segment_count += 1
        
        logger.info(f"Fallback segmentation complete: {len(segments)} segments created")
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
