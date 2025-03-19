#!/usr/bin/env python
"""
Script to run the KeynoteGenie UI
"""
import sys
from pathlib import Path
import subprocess

def main():
    """Run the KeynoteGenie UI"""
    # Get the root directory
    root_dir = Path(__file__).parent.parent.resolve()
    
    # Run streamlit
    streamlit_path = root_dir / "src" / "ui" / "app.py"
    subprocess.run([sys.executable, "-m", "streamlit", "run", str(streamlit_path)])

if __name__ == "__main__":
    main() 