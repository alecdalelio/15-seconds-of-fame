import sqlite3
import os
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)

class VideoDatabase:
    def __init__(self, db_path: str = "videos.db"):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Initialize the database with required tables."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Videos table - stores metadata about processed videos
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS videos (
                    id TEXT PRIMARY KEY,
                    youtube_url TEXT NOT NULL,
                    title TEXT,
                    duration REAL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    processed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    status TEXT DEFAULT 'processing',
                    file_path TEXT,
                    cleanup_after TIMESTAMP
                )
            ''')
            
            # Clips table - stores metadata about individual clips
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS clips (
                    id TEXT PRIMARY KEY,
                    video_id TEXT,
                    segment_id TEXT,
                    start_time REAL,
                    end_time REAL,
                    transcript TEXT,
                    score REAL,
                    reasoning TEXT,
                    audio_path TEXT,
                    video_path TEXT,
                    video_clip_path TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    audio_quality_score REAL DEFAULT 5.0,
                    dramatic_intensity REAL DEFAULT 5.0,
                    speech_clarity REAL DEFAULT 5.0,
                    segment_coherence REAL DEFAULT 5.0,
                    overall_score REAL DEFAULT 5.0,
                    boundary_type TEXT DEFAULT 'unknown',
                    viral_score REAL DEFAULT 5.0,
                    emotional_intensity REAL DEFAULT 5.0,
                    controversy_level REAL DEFAULT 5.0,
                    relatability REAL DEFAULT 5.0,
                    educational_value REAL DEFAULT 5.0,
                    entertainment_factor REAL DEFAULT 5.0,
                    viral_reasoning TEXT DEFAULT '',
                    combined_score REAL DEFAULT 5.0,
                    api_usage_tokens INTEGER DEFAULT 0,
                    api_usage_cost REAL DEFAULT 0.0
                )
            ''')
            
            conn.commit()
    
    def add_video(self, video_id: str, youtube_url: str, title: str = None, duration: float = None, file_path: str = None) -> bool:
        """Add a new video to the database."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO videos (id, youtube_url, title, duration, file_path, cleanup_after)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (
                    video_id, 
                    youtube_url, 
                    title, 
                    duration, 
                    file_path,
                    datetime.now() + timedelta(hours=24)  # Clean up after 24 hours
                ))
                conn.commit()
                logger.info(f"Added video {video_id} to database")
                return True
        except Exception as e:
            logger.error(f"Error adding video to database: {e}")
            return False
    
    def add_clips(self, video_id: str, clips: List[Dict[str, Any]]) -> bool:
        """Add clips for a video to the database."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                for clip in clips:
                    cursor.execute('''
                        INSERT INTO clips (
                            id, video_id, segment_id, start_time, end_time, transcript, 
                            score, reasoning, audio_path, video_path, video_clip_path,
                            audio_quality_score, dramatic_intensity, speech_clarity, 
                            segment_coherence, overall_score, boundary_type,
                            viral_score, emotional_intensity, controversy_level, 
                            relatability, educational_value, entertainment_factor,
                            viral_reasoning, combined_score, api_usage_tokens, api_usage_cost
                        )
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (
                        clip['id'],
                        video_id,
                        clip.get('segment_id', clip['id']),
                        clip['start_time'],
                        clip['end_time'],
                        clip.get('transcript', ''),
                        clip.get('score', 0.0),
                        clip.get('reasoning', ''),
                        clip.get('audio_path', ''),
                        clip.get('video_path', ''),
                        clip.get('video_clip_path', ''),
                        clip.get('audio_quality_score', 5.0),
                        clip.get('dramatic_intensity', 5.0),
                        clip.get('speech_clarity', 5.0),
                        clip.get('segment_coherence', 5.0),
                        clip.get('overall_score', 5.0),
                        clip.get('boundary_type', 'unknown'),
                        clip.get('viral_score', 5.0),
                        clip.get('emotional_intensity', 5.0),
                        clip.get('controversy_level', 5.0),
                        clip.get('relatability', 5.0),
                        clip.get('educational_value', 5.0),
                        clip.get('entertainment_factor', 5.0),
                        clip.get('viral_reasoning', ''),
                        clip.get('combined_score', 5.0),
                        clip.get('api_usage_tokens', 0),
                        clip.get('api_usage_cost', 0.0)
                    ))
                conn.commit()
                logger.info(f"Added {len(clips)} clips for video {video_id}")
                return True
        except Exception as e:
            logger.error(f"Error adding clips to database: {e}")
            return False
    
    def get_video_clips(self, video_id: str) -> List[Dict[str, Any]]:
        """Get all clips for a video."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT * FROM clips WHERE video_id = ? ORDER BY start_time
                ''', (video_id,))
                clips = [dict(row) for row in cursor.fetchall()]
                return clips
        except Exception as e:
            logger.error(f"Error getting clips from database: {e}")
            return []
    
    def update_video_status(self, video_id: str, status: str) -> bool:
        """Update the status of a video."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    UPDATE videos SET status = ?, processed_at = CURRENT_TIMESTAMP
                    WHERE id = ?
                ''', (status, video_id))
                conn.commit()
                return True
        except Exception as e:
            logger.error(f"Error updating video status: {e}")
            return False
    
    def cleanup_old_files(self, max_age_hours: int = 24) -> int:
        """Clean up old video and audio files."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Get videos that are older than max_age_hours
                cutoff_time = datetime.now() - timedelta(hours=max_age_hours)
                cursor.execute('''
                    SELECT id, file_path FROM videos 
                    WHERE created_at < ? AND status = 'completed'
                ''', (cutoff_time,))
                
                old_videos = cursor.fetchall()
                deleted_count = 0
                
                for video_id, file_path in old_videos:
                    # Delete video file
                    if file_path and os.path.exists(file_path):
                        try:
                            os.remove(file_path)
                            logger.info(f"Deleted video file: {file_path}")
                            deleted_count += 1
                        except Exception as e:
                            logger.error(f"Error deleting video file {file_path}: {e}")
                    
                    # Delete associated audio files
                    downloads_dir = Path("downloads")
                    if downloads_dir.exists():
                        # Delete main audio file
                        audio_file = downloads_dir / f"{video_id}_audio.mp3"
                        if audio_file.exists():
                            try:
                                audio_file.unlink()
                                logger.info(f"Deleted audio file: {audio_file}")
                                deleted_count += 1
                            except Exception as e:
                                logger.error(f"Error deleting audio file {audio_file}: {e}")
                        
                        # Delete segment files
                        for segment_file in downloads_dir.glob(f"{video_id}_segment_*.mp3"):
                            try:
                                segment_file.unlink()
                                logger.info(f"Deleted segment file: {segment_file}")
                                deleted_count += 1
                            except Exception as e:
                                logger.error(f"Error deleting segment file {segment_file}: {e}")
                
                # Delete database records for old videos
                cursor.execute('''
                    DELETE FROM clips WHERE video_id IN (
                        SELECT id FROM videos WHERE created_at < ? AND status = 'completed'
                    )
                ''', (cutoff_time,))
                
                cursor.execute('''
                    DELETE FROM videos WHERE created_at < ? AND status = 'completed'
                ''', (cutoff_time,))
                
                conn.commit()
                logger.info(f"Cleanup completed: {deleted_count} files deleted")
                return deleted_count
                
        except Exception as e:
            logger.error(f"Error during cleanup: {e}")
            return 0
    
    def get_video_info(self, video_id: str) -> Optional[Dict[str, Any]]:
        """Get video information."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT * FROM videos WHERE id = ?
                ''', (video_id,))
                row = cursor.fetchone()
                return dict(row) if row else None
        except Exception as e:
            logger.error(f"Error getting video info: {e}")
            return None

# Global database instance
db = VideoDatabase()
