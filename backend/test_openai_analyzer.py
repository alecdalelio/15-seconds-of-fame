#!/usr/bin/env python3
"""
Test script for OpenAI analyzer functionality.
This script tests the viral analysis features without requiring an actual API key.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from viral_analyzer import analyzer, ViralAnalysis

def test_fallback_analysis():
    """Test the fallback analysis when no API key is available."""
    print("Testing fallback analysis...")
    
    # Test with a sample transcript
    test_transcript = "This is an amazing moment that will blow your mind! The incredible story of how one person changed everything."
    test_segment = {
        "id": "test_1",
        "start_time": 0.0,
        "end_time": 15.0
    }
    
    # Analyze the transcript
    analysis = analyzer.analyze_viral_potential(test_transcript, test_segment)
    
    print(f"Viral Score: {analysis.viral_score}")
    print(f"Emotional Intensity: {analysis.emotional_intensity}")
    print(f"Controversy Level: {analysis.controversy_level}")
    print(f"Relatability: {analysis.relatability}")
    print(f"Educational Value: {analysis.educational_value}")
    print(f"Entertainment Factor: {analysis.entertainment_factor}")
    print(f"Combined Score: {analysis.combined_score}")
    print(f"Viral Reasoning: {analysis.viral_reasoning}")
    print()
    
    return analysis

def test_empty_transcript():
    """Test analysis with empty transcript."""
    print("Testing empty transcript...")
    
    analysis = analyzer.analyze_viral_potential("", {})
    
    print(f"Viral Score: {analysis.viral_score}")
    print(f"Combined Score: {analysis.combined_score}")
    print(f"Viral Reasoning: {analysis.viral_reasoning}")
    print()
    
    return analysis

def test_usage_stats():
    """Test usage statistics."""
    print("Testing usage statistics...")
    
    stats = analyzer.get_usage_stats()
    
    print(f"Enabled: {stats['enabled']}")
    print(f"Daily Budget: ${stats['daily_budget']}")
    print(f"Budget Remaining: ${stats['budget_remaining']}")
    print(f"Budget Percentage: {stats['budget_percentage']}%")
    print(f"Requests Made: {stats['daily_usage']['requests_made']}")
    print(f"Total Cost: ${stats['daily_usage']['total_cost']}")
    print()

def test_api_connection():
    """Test if the API connection is working."""
    print("Testing API connection...")
    
    if analyzer.test_api_connection():
        print("✓ API connection successful!")
    else:
        print("✗ API connection failed!")
    print()

def test_scorer_integration():
    """Test integration with the enhanced scorer."""
    print("Testing scorer integration...")
    
    try:
        import scorer
        
        # Create test segments
        test_segments = [
            {
                "id": "1",
                "start_time": 0.0,
                "end_time": 15.0,
                "transcript": "This is absolutely incredible! You won't believe what happened next.",
                "audio_path": "test_audio_1.mp3",
                "video_path": "test_video_1.mp4"
            },
            {
                "id": "2", 
                "start_time": 15.0,
                "end_time": 30.0,
                "transcript": "The boring details of the process continued for several minutes.",
                "audio_path": "test_audio_2.mp3",
                "video_path": "test_video_2.mp4"
            }
        ]
        
        # Score the segments
        scored_clips = scorer.score_segments(test_segments)
        
        print(f"Scored {len(scored_clips)} clips:")
        for i, clip in enumerate(scored_clips):
            print(f"  Clip {i+1}:")
            print(f"    Score: {clip['score']}")
            print(f"    Combined Score: {clip['combined_score']}")
            print(f"    Viral Score: {clip['viral_score']}")
            print(f"    Reasoning: {clip['reasoning'][:100]}...")
            print()
        
        return scored_clips
        
    except ImportError as e:
        print(f"Error importing scorer: {e}")
        return None

def main():
    """Run all tests."""
    print("=" * 50)
    print("OpenAI Analyzer Test Suite")
    print("=" * 50)
    print()
    
    # Test fallback analysis
    test_fallback_analysis()
    
    # Test empty transcript
    test_empty_transcript()
    
    # Test usage stats
    test_usage_stats()
    
    # Test API connection
    test_api_connection()
    
    # Test scorer integration
    test_scorer_integration()
    
    print("=" * 50)
    print("All tests completed successfully!")
    print("=" * 50)
    print()
    
    # Check if API key is actually working
    stats = analyzer.get_usage_stats()
    if stats['enabled'] and stats['daily_usage']['requests_made'] > 0:
        print("✓ OpenAI API is working correctly!")
        print(f"✓ Made {stats['daily_usage']['requests_made']} API calls")
        print(f"✓ Total cost: ${stats['daily_usage']['total_cost']}")
    else:
        print("⚠ OpenAI API key not found or not working.")
        print("To test with real OpenAI analysis, add your API key to the .env file.")

if __name__ == "__main__":
    main()
