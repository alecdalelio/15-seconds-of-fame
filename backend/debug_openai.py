#!/usr/bin/env python3
"""
Debug script for OpenAI API issues.
This script helps diagnose problems with the OpenAI API configuration.
"""

import os
import sys
from dotenv import load_dotenv

def check_env_file():
    """Check if .env file exists and has the right content."""
    print("=== Environment File Check ===")
    
    env_path = ".env"
    if os.path.exists(env_path):
        print(f"✓ .env file found at: {os.path.abspath(env_path)}")
        
        with open(env_path, 'r') as f:
            content = f.read().strip()
            lines = content.split('\n')
            
        api_key_line = None
        for line in lines:
            if line.startswith('OPENAI_API_KEY='):
                api_key_line = line
                break
        
        if api_key_line:
            key_value = api_key_line.split('=', 1)[1]
            if key_value and key_value != 'your_api_key_here':
                print(f"✓ OPENAI_API_KEY found: {key_value[:10]}...")
                return True
            else:
                print("✗ OPENAI_API_KEY is empty or placeholder")
                return False
        else:
            print("✗ OPENAI_API_KEY not found in .env file")
            return False
    else:
        print(f"✗ .env file not found at: {os.path.abspath(env_path)}")
        return False

def check_env_loading():
    """Check if environment variables are loaded correctly."""
    print("\n=== Environment Loading Check ===")
    
    # Load environment variables
    load_dotenv()
    
    api_key = os.getenv("OPENAI_API_KEY")
    if api_key:
        print(f"✓ OPENAI_API_KEY loaded: {api_key[:10]}...")
        return True
    else:
        print("✗ OPENAI_API_KEY not loaded from environment")
        return False

def check_analyzer():
    """Check if the analyzer can be imported and initialized."""
    print("\n=== Analyzer Check ===")
    
    try:
        import viral_analyzer
        print("✓ openai_analyzer imported successfully")
        
        analyzer = openai_analyzer.analyzer
        print(f"✓ Analyzer initialized: enabled={analyzer.enabled}")
        
        if analyzer.enabled:
            print("✓ API key detected by analyzer")
            return True
        else:
            print("✗ API key not detected by analyzer")
            return False
            
    except Exception as e:
        print(f"✗ Error importing analyzer: {e}")
        return False

def main():
    """Run all diagnostic checks."""
    print("OpenAI API Diagnostic Tool")
    print("=" * 40)
    
    env_file_ok = check_env_file()
    env_loaded_ok = check_env_loading()
    analyzer_ok = check_analyzer()
    
    print("\n=== Summary ===")
    if all([env_file_ok, env_loaded_ok, analyzer_ok]):
        print("✓ All checks passed! OpenAI API should be working.")
    else:
        print("✗ Some checks failed. See details above.")
        
        if not env_file_ok:
            print("  - Create a .env file with your OPENAI_API_KEY")
        if not env_loaded_ok:
            print("  - Check that python-dotenv is installed")
        if not analyzer_ok:
            print("  - Check analyzer initialization")

if __name__ == "__main__":
    main()
