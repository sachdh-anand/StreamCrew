import streamlit as st
import subprocess
import time
from pathlib import Path
import sys
from os.path import dirname, abspath, join
import warnings
import os

# Filter out specific deprecation warnings from dependencies
warnings.filterwarnings("ignore", category=DeprecationWarning, module="pkg_resources")
warnings.filterwarnings("ignore", category=DeprecationWarning, module="pydantic")
warnings.filterwarnings("ignore", category=UserWarning, module="pydantic")
warnings.filterwarnings("ignore", category=DeprecationWarning, module="crewai_tools")

# Add the src directory to Python path
root_dir = dirname(dirname(dirname(abspath(__file__))))
sys.path.append(root_dir)

from src.config.settings import (
    APP_NAME,
    APP_VERSION,
    DEFAULT_RESEARCH_TOPIC,
    OUTPUTS_DIR
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
        padding: 1rem 2rem;
        background-color: #0e1117;
        background-image: linear-gradient(to bottom, rgba(13, 17, 23, 0.9), rgba(13, 17, 23, 1)), 
                          url("https://images.unsplash.com/photo-1635070041078-e363dbe005cb?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&auto=format&fit=crop&w=2070&q=80");
        background-size: cover;
        background-attachment: fixed;
    }
    .stTextInput > div > div > input {
        background-color: #1e2330;
        color: #ffffff;
        border: 1px solid #4a4a4a;
        border-radius: 8px;
        padding: 10px 14px;
        font-size: 1rem;
    }
    .output-container {
        background-color: rgba(30, 33, 41, 0.7);
        padding: 1.8rem;
        border-radius: 16px;
        border: 1px solid #3a4149;
        margin: 1.5rem 0;
        min-height: 20px;
        overflow-y: auto;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.2);
        backdrop-filter: blur(8px);
        -webkit-backdrop-filter: blur(8px);
        transition: all 0.4s ease;
    }
    .output-container:hover {
        box-shadow: 0 12px 36px rgba(0, 210, 255, 0.15);
        border-color: #4d5d6c;
        background-color: rgba(30, 33, 41, 0.8);
    }
    .header-text {
        background: linear-gradient(90deg, #0088ff, #00e1ff, #0088ff);
        background-size: 200% auto;
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 4rem;
        font-weight: 800;
        margin-bottom: 1rem;
        text-align: center;
        animation: gradient 10s ease infinite;
        letter-spacing: -1px;
        padding: 0.5rem 0;
        text-shadow: 0 0 30px rgba(0, 210, 255, 0.5);
    }
    @keyframes gradient {
        0% {background-position: 0% 50%;}
        50% {background-position: 100% 50%;}
        100% {background-position: 0% 50%;}
    }
    .subheader {
        color: #00d2ff;
        font-size: 1.8rem;
        font-weight: 600;
        margin-bottom: 1.5rem;
        text-shadow: 0 0 10px rgba(0, 210, 255, 0.3);
        position: relative;
        display: inline-block;
    }
    .subheader:after {
        content: '';
        position: absolute;
        width: 100%;
        height: 3px;
        bottom: -8px;
        left: 0;
        background: linear-gradient(90deg, #0088ff, #00e1ff);
        border-radius: 10px;
    }
    .research-input {
        margin-bottom: 2.5rem;
    }
    .stButton > button {
        background: linear-gradient(90deg, #0066cc, #00a3cc);
        color: white;
        border: none;
        padding: 0.9rem 2.5rem;
        border-radius: 10px;
        font-weight: 600;
        width: 100%;
        transition: all 0.3s ease;
        box-shadow: 0 4px 20px rgba(0, 130, 220, 0.3);
        text-transform: uppercase;
        letter-spacing: 1.5px;
        font-size: 1.1rem;
    }
    .stButton > button:hover {
        transform: translateY(-3px);
        box-shadow: 0 6px 30px rgba(0, 210, 255, 0.4);
        background: linear-gradient(90deg, #0077e6, #00bfff);
    }
    .stButton > button:active {
        transform: translateY(1px);
        box-shadow: 0 2px 10px rgba(0, 130, 220, 0.2);
    }
    .content-text {
        color: #e6e6e6;
        line-height: 1.8;
        font-size: 1.05rem;
    }
    .status-message {
        text-align: center;
        padding: 1.2rem;
        border-radius: 12px;
        margin: 1.5rem 0;
        background-color: rgba(45, 49, 57, 0.7);
        color: #00d2ff;
        border-left: 3px solid #00d2ff;
        backdrop-filter: blur(4px);
        -webkit-backdrop-filter: blur(4px);
    }
    .loading-spinner {
        display: flex;
        justify-content: center;
        margin: 2.5rem 0;
    }
    .stAlert {
        background-color: rgba(45, 55, 72, 0.7) !important;
        color: #e2e8f0 !important;
        border-radius: 12px !important;
        border: 1px solid #3a4149 !important;
        padding: 1.2rem !important;
        backdrop-filter: blur(4px) !important;
        -webkit-backdrop-filter: blur(4px) !important;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1) !important;
    }
    .stAlert > div {
        color: #e2e8f0 !important;
    }
    .timestamp {
        color: #00d2ff;
        font-size: 0.9rem;
        margin-bottom: 1.2rem;
        opacity: 0.9;
        font-style: italic;
    }
    .footer {
        text-align: center; 
        margin-top: 3rem; 
        padding: 1.5rem; 
        background-color: rgba(30, 33, 41, 0.7); 
        border-radius: 16px; 
        border: 1px solid #3a4149;
        opacity: 0.9;
        transition: opacity 0.3s ease;
        backdrop-filter: blur(4px);
        -webkit-backdrop-filter: blur(4px);
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
    }
    .footer:hover {
        opacity: 1;
        border-color: #4d5d6c;
    }
    .app-container {
        max-width: 1400px;
        margin: 0 auto;
        padding: 0 1rem;
    }
    /* Success Message Styling */
    .success-container {
        background-color: rgba(22, 57, 41, 0.7);
        border-left: 4px solid #00cc88;
        border-radius: 8px;
        padding: 1rem 1.5rem;
        margin: 1rem 0;
        box-shadow: 0 4px 12px rgba(0, 204, 136, 0.2);
        backdrop-filter: blur(4px);
        -webkit-backdrop-filter: blur(4px);
    }
    .stMarkdown p {
        font-size: 1.05rem;
        line-height: 1.8;
    }
    h1, h2, h3 {
        color: #e6e6e6;
        margin-top: 1.5rem;
        margin-bottom: 1rem;
    }
    h1 {
        font-size: 2.2rem;
        font-weight: 700;
    }
    h2 {
        font-size: 1.8rem;
        font-weight: 600;
    }
    h3 {
        font-size: 1.5rem;
        font-weight: 600;
    }
    strong {
        color: #ffffff;
        font-weight: 600;
    }
    ul, ol {
        margin-left: 1.5rem;
        margin-bottom: 1.5rem;
    }
    li {
        margin-bottom: 0.5rem;
    }
    blockquote {
        border-left: 3px solid #00d2ff;
        padding-left: 1rem;
        color: #c0c0c0;
        font-style: italic;
        margin: 1.5rem 0;
    }
</style>
""", unsafe_allow_html=True)

# App container for better layout
st.markdown('<div class="app-container">', unsafe_allow_html=True)

# Header
st.markdown(f'<p class="header-text">🔬 {APP_NAME} Research Hub</p>', unsafe_allow_html=True)

# Initialize session state to track when the agent was last run and topics
if 'last_run_time' not in st.session_state:
    st.session_state.last_run_time = None
    st.session_state.files_mod_time = {}
    st.session_state.last_topic = None
    st.session_state.input_value = DEFAULT_RESEARCH_TOPIC  # Track the input value
    st.session_state.input_clicked = False  # Track if input field has been clicked
    st.session_state.first_load = True  # Track if this is the first load

# Research Input Section
st.markdown('<p class="subheader">🔍 Research Focus</p>', unsafe_allow_html=True)

# Handle input changes with a callback
def on_text_change():
    if st.session_state.first_load:
        st.session_state.first_load = False
    # Save the current input value to session state
    st.session_state.input_value = st.session_state.research_topic

# Display the text input with the value from session state
research_topic = st.text_input(
    "Research on",
    value=st.session_state.input_value,
    key="research_topic",
    placeholder="Enter a research topic...",
    on_change=on_text_change
)

# Function to create the same output paths that the agent uses
def create_output_paths(topic):
    """Generate output file paths based on the topic - matches agent.py logic"""
    # Create a safe filename from the topic
    safe_topic = "".join(c if c.isalnum() or c in [' ', '_', '-'] else '_' for c in topic.lower())
    safe_topic = safe_topic.replace(' ', '_')[:50]  # Limit length, replace spaces
    
    # Create the file paths
    research_file = OUTPUTS_DIR / f"{safe_topic}_research_summary.txt"
    keynote_file = OUTPUTS_DIR / f"{safe_topic}_keynote_speech.txt"
    
    return research_file, keynote_file

# Function to read and format the output files
def read_output_file(file_path: Path) -> str:
    try:
        return file_path.read_text(encoding='utf-8')
    except FileNotFoundError:
        return ""
    except Exception as e:
        return f"Error reading file: {str(e)}"

# Function to check if files were modified after the last run
def was_file_modified_after_last_run(file_path: Path) -> bool:
    if not file_path.exists():
        return False
    
    # If we just ran the agent in this session, always show the content
    if st.session_state.last_run_time is not None:
        return True
    
    # Otherwise, use modification time logic for previous sessions
    mod_time = file_path.stat().st_mtime
    if file_path not in st.session_state.files_mod_time:
        st.session_state.files_mod_time[file_path] = mod_time
        return False
    
    # Check if file was modified since we loaded the app
    if mod_time > st.session_state.files_mod_time[file_path]:
        st.session_state.files_mod_time[file_path] = mod_time
        return True
    
    return False

# Function to run the research agent
def run_research_agent(topic: str):
    try:
        agent_path = join(dirname(dirname(abspath(__file__))), "agents", "agent.py")
        # Use the virtual environment's Python interpreter
        venv_python = join(root_dir, "venv", "Scripts", "python.exe")
        
        # Set environment variables to suppress warnings
        env = os.environ.copy()
        env["PYTHONWARNINGS"] = "ignore::DeprecationWarning:pkg_resources,ignore::DeprecationWarning:pydantic,ignore::UserWarning:pydantic,ignore::DeprecationWarning:crewai_tools"
        
        # Pass the topic as a command line argument
        process = subprocess.Popen(
            [venv_python, agent_path, topic],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            cwd=root_dir,  # Set working directory to project root
            env=env  # Pass the modified environment variables
        )
        return process
    except Exception as e:
        st.error(f"Error running research agent: {str(e)}")
        return None

# Run Research Button
if st.button("🚀 Run Research Agent", help="Click to start the research process"):
    # Validate the topic and save to session state
    if not research_topic or research_topic.strip() == "":
        st.error("Please enter a research topic.")
    else:
        # Update both topic values in session state
        st.session_state.last_topic = research_topic
        st.session_state.input_value = research_topic
        
        # Initialize progress
        progress_placeholder = st.empty()
        progress_bar = progress_placeholder.progress(0)
        
        # Start the research process with the topic
        process = run_research_agent(research_topic)
        if process:
            with st.spinner(f'🔎 Researching "{research_topic}"...'):
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
                    # Record when the run completed
                    st.session_state.last_run_time = time.time()
                    st.markdown(f'<div class="success-container">Research on "{research_topic}" completed successfully!</div>', unsafe_allow_html=True)
                else:
                    st.error(f"Error during research: {stderr}")
            
            # Clear progress bar
            progress_placeholder.empty()

# Create two columns for the output
col1, col2 = st.columns(2)

# Get the topic to use for file paths - either the last run topic or the current input
display_topic = st.session_state.last_topic if st.session_state.last_topic else research_topic

# Get the dynamic file paths based on the topic
research_file, keynote_file = create_output_paths(display_topic)

# Display outputs in columns
with col1:
    st.markdown('<p class="subheader">📊 Research Summary</p>', unsafe_allow_html=True)
    with st.container():
        st.markdown('<div class="output-container">', unsafe_allow_html=True)
        research_content = read_output_file(research_file)
        
        if research_content:
            # Check if the file was modified after the last run
            if st.session_state.last_run_time and was_file_modified_after_last_run(research_file):
                timestamp = time.strftime("%Y-%m-%d %H:%M:%S", 
                                         time.localtime(research_file.stat().st_mtime))
                st.markdown(f'<p class="timestamp">Generated: {timestamp}</p>', 
                           unsafe_allow_html=True)
                st.markdown(research_content)
            else:
                # Don't show previous content with info message
                st.info("Run the research agent to generate the summary.")
        else:
            st.info("Run the research agent to generate the summary.")
        st.markdown('</div>', unsafe_allow_html=True)

with col2:
    st.markdown('<p class="subheader">🎤 Keynote Speech</p>', unsafe_allow_html=True)
    with st.container():
        st.markdown('<div class="output-container">', unsafe_allow_html=True)
        keynote_content = read_output_file(keynote_file)
        
        if keynote_content:
            # Check if the file was modified after the last run
            if st.session_state.last_run_time and was_file_modified_after_last_run(keynote_file):
                timestamp = time.strftime("%Y-%m-%d %H:%M:%S", 
                                         time.localtime(keynote_file.stat().st_mtime))
                st.markdown(f'<p class="timestamp">Generated: {timestamp}</p>', 
                           unsafe_allow_html=True)
                st.markdown(keynote_content)
            else:
                # Don't show previous content with info message
                st.info("Run the research agent to generate the keynote speech.")
        else:
            st.info("Run the research agent to generate the keynote speech.")
        st.markdown('</div>', unsafe_allow_html=True)

# Footer
st.markdown(f"""
<div class="footer">
    <p style="color: #00d2ff; margin-bottom: 0;">Powered by {APP_NAME} v{APP_VERSION}</p>
</div>
""", unsafe_allow_html=True)

# Close the app container div
st.markdown('</div>', unsafe_allow_html=True) 