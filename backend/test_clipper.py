#!/usr/bin/env python3
"""
Test script for the video processing functionality.
"""

import clipper
import json

def test_video_processing():
    """Test the video processing with a short YouTube video."""
    
    # Use a short test video (Rick Roll - 3:33 minutes)
    test_url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
    
    print("Testing video processing...")
    print(f"URL: {test_url}")
    print("-" * 50)
    
    try:
        # Process the video
        segments = clipper.process_video(test_url)
        
        print(f"Successfully processed video into {len(segments)} segments")
        print("\nSegments:")
        
        for i, segment in enumerate(segments, 1):
            print(f"\nSegment {i}:")
            print(f"  ID: {segment['id']}")
            print(f"  Time: {segment['start_time']:.1f}s - {segment['end_time']:.1f}s")
            print(f"  Transcript: {segment['transcript'][:100]}...")
            print(f"  Audio: {segment['audio_path']}")
        
        # Save results to JSON for inspection
        with open("test_results.json", "w") as f:
            json.dump(segments, f, indent=2)
        
        print(f"\nResults saved to test_results.json")
        
    except Exception as e:
        print(f"Error: {str(e)}")
        return False
    
    return True

if __name__ == "__main__":
    test_video_processing()
