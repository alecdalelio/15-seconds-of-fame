#!/usr/bin/env python3
"""
Startup script for the 15 Seconds of Fame API server.
This script starts the FastAPI server with proper configuration.
"""

import subprocess
import sys
import os

def check_dependencies():
    """Check if required dependencies are installed."""
    print("Checking dependencies...")
    
    try:
        import fastapi
        import uvicorn
        import requests
        import viral_analyzer
        print("✓ All dependencies are installed")
        return True
    except ImportError as e:
        print(f"✗ Missing dependency: {e}")
        print("Please install dependencies with: pip3 install -r requirements.txt")
        return False

def check_configuration():
    """Check if the application is properly configured."""
    print("Checking configuration...")
    
    try:
        import viral_analyzer
        
        stats = viral_analyzer.analyzer.get_usage_stats()
        if stats['enabled']:
            print("✓ OpenAI API is configured")
        else:
            print("⚠ OpenAI API not configured - will use fallback mode")
        
        return True
    except Exception as e:
        print(f"✗ Configuration error: {e}")
        return False

def start_server():
    """Start the FastAPI server."""
    print("Starting FastAPI server...")
    print("Server will be available at: http://localhost:8000")
    print("API documentation at: http://localhost:8000/docs")
    print("Press Ctrl+C to stop the server")
    print("-" * 50)
    
    try:
        # Start the server with uvicorn
        subprocess.run([
            sys.executable, "-m", "uvicorn", 
            "app:app", 
            "--host", "0.0.0.0", 
            "--port", "8000", 
            "--reload"
        ])
    except KeyboardInterrupt:
        print("\nServer stopped by user")
    except Exception as e:
        print(f"Error starting server: {e}")

def main():
    """Main startup function."""
    print("15 Seconds of Fame API Server")
    print("=" * 40)
    
    # Check dependencies
    if not check_dependencies():
        sys.exit(1)
    
    # Check configuration
    if not check_configuration():
        print("Continuing anyway...")
    
    print()
    start_server()

if __name__ == "__main__":
    main()
