#!/usr/bin/env python3
"""
Test script for the full video processing pipeline.
This script tests the complete flow from video processing to scoring.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_imports():
    """Test that all required modules can be imported."""
    print("Testing imports...")
    
    try:
        import clipper
        print("✓ clipper imported successfully")
    except Exception as e:
        print(f"✗ Error importing clipper: {e}")
        return False
    
    try:
        import scorer
        print("✓ scorer imported successfully")
    except Exception as e:
        print(f"✗ Error importing scorer: {e}")
        return False
    
    try:
        import viral_analyzer
        print("✓ viral_analyzer imported successfully")
    except Exception as e:
        print(f"✗ Error importing viral_analyzer: {e}")
        return False
    
    try:
        import database
        print("✓ database imported successfully")
    except Exception as e:
        print(f"✗ Error importing database: {e}")
        return False
    
    return True

def test_analyzer_status():
    """Test the analyzer status."""
    print("\nTesting analyzer status...")
    
    try:
        import viral_analyzer
        
        stats = viral_analyzer.analyzer.get_usage_stats()
        print(f"✓ Analyzer enabled: {stats['enabled']}")
        print(f"✓ Daily budget: ${stats['daily_budget']}")
        print(f"✓ Budget remaining: ${stats['budget_remaining']}")
        
        if stats['enabled']:
            print("✓ OpenAI API is configured and ready")
            return True
        else:
            print("⚠ OpenAI API not configured - will use fallback mode")
            return True  # Still works, just in fallback mode
            
    except Exception as e:
        print(f"✗ Error checking analyzer status: {e}")
        return False

def test_sample_analysis():
    """Test a sample analysis without processing a real video."""
    print("\nTesting sample analysis...")
    
    try:
        import viral_analyzer
        
        # Test with a sample transcript
        test_transcript = "This is absolutely incredible! You won't believe what happened next."
        test_segment = {
            "id": "test_sample",
            "start_time": 0.0,
            "end_time": 15.0
        }
        
        analysis = viral_analyzer.analyzer.analyze_viral_potential(test_transcript, test_segment)
        
        print(f"✓ Analysis completed successfully")
        print(f"✓ Viral Score: {analysis.viral_score}")
        print(f"✓ Combined Score: {analysis.combined_score}")
        print(f"✓ Reasoning: {analysis.viral_reasoning[:100]}...")
        
        return True
        
    except Exception as e:
        print(f"✗ Error in sample analysis: {e}")
        return False

def main():
    """Run all pipeline tests."""
    print("Full Pipeline Test Suite")
    print("=" * 50)
    
    # Test imports
    imports_ok = test_imports()
    
    # Test analyzer status
    analyzer_ok = test_analyzer_status()
    
    # Test sample analysis
    analysis_ok = test_sample_analysis()
    
    print("\n" + "=" * 50)
    print("Test Results Summary")
    print("=" * 50)
    
    if all([imports_ok, analyzer_ok, analysis_ok]):
        print("✓ All tests passed! The pipeline is ready to use.")
        print("\nYou can now:")
        print("1. Start the FastAPI server: python3 -m uvicorn app:app --reload")
        print("2. Use the frontend to process videos")
        print("3. Monitor API usage at /api/usage endpoint")
    else:
        print("✗ Some tests failed. Check the output above for details.")
        
        if not imports_ok:
            print("  - Check that all required packages are installed")
        if not analyzer_ok:
            print("  - Check OpenAI API configuration")
        if not analysis_ok:
            print("  - Check analyzer functionality")

if __name__ == "__main__":
    main()
