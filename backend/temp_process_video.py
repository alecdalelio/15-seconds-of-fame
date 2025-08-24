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
        database.db.add_video(video_id, youtube_url, status="processing")
        
        # Download video
        video_path = download_youtube_video(youtube_url, downloads_dir, video_id)
        if not video_path:
            database.db.update_video_status(video_id, "failed")
            raise Exception("Failed to download video")
        
        # Extract audio
        audio_path = extract_audio(video_path, downloads_dir, video_id)
        if not audio_path:
            database.db.update_video_status(video_id, "failed")
            raise Exception("Failed to extract audio")
        
        # Split audio into 15-second segments
        segments = split_audio_into_segments(audio_path, downloads_dir, video_id)
        
        # Generate transcripts for each segment
        segments_with_transcripts = generate_transcripts(segments)
        
        # Update database with clips and mark as completed
        database.db.add_clips(video_id, segments_with_transcripts)
        database.db.update_video_status(video_id, "completed")
        
        logger.info(f"Successfully processed video into {len(segments_with_transcripts)} segments")
        return segments_with_transcripts
        
    except Exception as e:
        # Update status to failed if video_id exists
        if 'video_id' in locals():
            database.db.update_video_status(video_id, "failed")
        logger.error(f"Error processing video: {str(e)}")
        raise
