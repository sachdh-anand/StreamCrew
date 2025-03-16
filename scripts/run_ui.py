#!/usr/bin/env python3
"""
Script to run the StreamCrew UI
"""
import subprocess
import sys
from pathlib import Path

def main():
    """Run the StreamCrew UI"""
    # Get the root directory
    root_dir = Path(__file__).parent.parent
    ui_path = root_dir / "src" / "ui" / "app.py"
    
    # Run the Streamlit app
    try:
        subprocess.run([sys.executable, "-m", "streamlit", "run", str(ui_path)], check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error running the UI: {e}", file=sys.stderr)
        sys.exit(1)
    except KeyboardInterrupt:
        print("\nShutting down the UI...")
        sys.exit(0)

if __name__ == "__main__":
    main() 