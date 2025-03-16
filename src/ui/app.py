import streamlit as st
import subprocess
import time
from pathlib import Path
import sys
from os.path import dirname, abspath, join

# Add the src directory to Python path
root_dir = dirname(dirname(dirname(abspath(__file__))))
sys.path.append(root_dir)

from src.config.settings import (
    APP_NAME,
    APP_VERSION,
    DEFAULT_RESEARCH_TOPIC,
    RESEARCH_SUMMARY_FILE,
    KEYNOTE_SPEECH_FILE
)

# Set page configuration
st.set_page_config(
    page_title=f"{APP_NAME} - Quantum Computing Research",
    page_icon="🔬",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main {
        padding: 2rem;
        background-color: #0e1117;
    }
    .stTextInput > div > div > input {
        background-color: #262730;
        color: #ffffff;
        border: 1px solid #4a4a4a;
    }
    .output-container {
        background-color: #1e2129;
        padding: 1.5rem;
        border-radius: 10px;
        border: 1px solid #2d3139;
        margin: 1rem 0;
        min-height: 400px;
        overflow-y: auto;
    }
    .header-text {
        background: linear-gradient(90deg, #3a7bd5, #00d2ff);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 2.5rem;
        font-weight: bold;
        margin-bottom: 2rem;
        text-align: center;
    }
    .subheader {
        color: #00d2ff;
        font-size: 1.5rem;
        font-weight: 600;
        margin-bottom: 1rem;
    }
    .research-input {
        margin-bottom: 2rem;
    }
    .stButton > button {
        background: linear-gradient(90deg, #3a7bd5, #00d2ff);
        color: white;
        border: none;
        padding: 0.5rem 2rem;
        border-radius: 5px;
        font-weight: 600;
        width: 100%;
        transition: all 0.3s ease;
    }
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(0, 210, 255, 0.2);
    }
    .content-text {
        color: #e0e0e0;
        line-height: 1.6;
    }
    .status-message {
        text-align: center;
        padding: 1rem;
        border-radius: 5px;
        margin: 1rem 0;
        background-color: #2d3139;
        color: #00d2ff;
    }
    .loading-spinner {
        display: flex;
        justify-content: center;
        margin: 2rem 0;
    }
</style>
""", unsafe_allow_html=True)

# Header
st.markdown(f'<p class="header-text">🔬 {APP_NAME} Research Hub</p>', unsafe_allow_html=True)

# Research Input Section
st.markdown('<p class="subheader">Research Focus</p>', unsafe_allow_html=True)
research_topic = st.text_input(
    "Research on",
    value=DEFAULT_RESEARCH_TOPIC,
    disabled=True,
    key="research_topic"
)

# Function to read and format the output files
def read_output_file(file_path: Path) -> str:
    try:
        return file_path.read_text(encoding='utf-8')
    except FileNotFoundError:
        return ""
    except Exception as e:
        return f"Error reading file: {str(e)}"

# Function to run the research agent
def run_research_agent():
    try:
        agent_path = join(dirname(dirname(abspath(__file__))), "agents", "agent.py")
        process = subprocess.Popen(
            ["python", agent_path],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            cwd=root_dir  # Set working directory to project root
        )
        return process
    except Exception as e:
        st.error(f"Error running research agent: {str(e)}")
        return None

# Run Research Button
if st.button("🚀 Run Research Agent", help="Click to start the research process"):
    # Initialize progress
    progress_placeholder = st.empty()
    progress_bar = progress_placeholder.progress(0)
    
    # Start the research process
    process = run_research_agent()
    if process:
        with st.spinner('Running research agent...'):
            # Simulate progress while the process is running
            for i in range(100):
                time.sleep(0.1)  # Adjust the sleep time based on your needs
                progress_bar.progress(i + 1)
                
                # Check if process has finished
                if process.poll() is not None:
                    break
            
            # Wait for process to complete
            stdout, stderr = process.communicate()
            
            if process.returncode == 0:
                st.success("Research completed successfully!")
            else:
                st.error(f"Error during research: {stderr}")
        
        # Clear progress bar
        progress_placeholder.empty()

# Create two columns for the output
col1, col2 = st.columns(2)

# Display outputs in columns
with col1:
    st.markdown('<p class="subheader">Research Summary</p>', unsafe_allow_html=True)
    with st.container():
        st.markdown('<div class="output-container">', unsafe_allow_html=True)
        research_content = read_output_file(RESEARCH_SUMMARY_FILE)
        if research_content:
            st.markdown(f'<div class="content-text">{research_content}</div>', unsafe_allow_html=True)
        else:
            st.info("Run the research agent to generate the summary.")
        st.markdown('</div>', unsafe_allow_html=True)

with col2:
    st.markdown('<p class="subheader">Keynote Speech</p>', unsafe_allow_html=True)
    with st.container():
        st.markdown('<div class="output-container">', unsafe_allow_html=True)
        keynote_content = read_output_file(KEYNOTE_SPEECH_FILE)
        if keynote_content:
            st.markdown(f'<div class="content-text">{keynote_content}</div>', unsafe_allow_html=True)
        else:
            st.info("Run the research agent to generate the keynote speech.")
        st.markdown('</div>', unsafe_allow_html=True)

# Footer
st.markdown(f"""
<div style="text-align: center; margin-top: 2rem; padding: 1rem; background-color: #1e2129; border-radius: 10px; border: 1px solid #2d3139;">
    <p style="color: #00d2ff; margin-bottom: 0;">Powered by {APP_NAME} v{APP_VERSION}</p>
</div>
""", unsafe_allow_html=True) 