"""
Configuration settings for the StreamCrew application.
"""
import os
from pathlib import Path

# Base directories
ROOT_DIR = Path(__file__).parent.parent.parent
SRC_DIR = ROOT_DIR / "src"
OUTPUTS_DIR = ROOT_DIR / "outputs"
LOGS_DIR = ROOT_DIR / "logs"

# Ensure directories exist
OUTPUTS_DIR.mkdir(exist_ok=True)
LOGS_DIR.mkdir(exist_ok=True)

# File paths
RESEARCH_SUMMARY_FILE = OUTPUTS_DIR / "quantum_computing_research_summary.txt"
KEYNOTE_SPEECH_FILE = OUTPUTS_DIR / "quantum_computing_keynote_speech.txt"

# Application settings
APP_NAME = "StreamCrew"
APP_VERSION = "0.1.0"
DEFAULT_RESEARCH_TOPIC = "Research and analyze recent quantum computing breakthroughs and their AI applications" 