import sys
from pathlib import Path
from os.path import dirname, abspath, join

# Add the src directory to Python path
root_dir = dirname(dirname(dirname(abspath(__file__))))
sys.path.append(root_dir)

from crewai import Crew, Task, Agent
import os
from dotenv import load_dotenv
from src.models.llm import get_model
from src.utils.logger import get_logger
from src.config.settings import OUTPUTS_DIR, RESEARCH_SUMMARY_FILE, KEYNOTE_SPEECH_FILE

# Initialize logger
logger = get_logger(__name__)

# Load environment variables
load_dotenv()

# Try to import SerperDevTool, use a placeholder if not available
try:
    from crewai_tools import SerperDevTool
    search = SerperDevTool()
    logger.info("Successfully imported SerperDevTool")
except ImportError:
    logger.warning("SerperDevTool not available - using empty tools list")
    search = None

# Validate required environment variables
required_vars = ["SERPER_API_KEY"]
missing_vars = [var for var in required_vars if not os.getenv(var)]
if missing_vars:
    raise ValueError(f"Missing required environment variables: {', '.join(missing_vars)}")

# Get the LLM with fallback logic
model_name, _ = get_model(model_type="mistral", test=True)
if model_name is None:
    raise ValueError("Failed to initialize any LLM. Please check your API keys and try again.")

logger.info(f"Using model: {model_name}")

# Create the researcher agent with tools if available
tools = [search] if search else []

# Create the researcher agent
researcher = Agent(
    model_name=model_name,  # Using model name directly
    role="Senior AI Researcher",
    goal="Find promising research in the field of quantum computing.",
    backstory="You are a veteran quantum computing researcher with a background in modern physics.",
    allow_delegation=False,
    tools=tools,
    verbose=False,
)

# Create research task
research_task = Task(
    description="Research and analyze recent quantum computing breakthroughs and their AI applications.",
    expected_output="A detailed bullet point summary on each of the topics. Each bullet point should cover the topic, background and why the innovation is useful.",
    output_file=str(RESEARCH_SUMMARY_FILE),
    agent=researcher,
)

# Create the writer agent
writer = Agent(
    model_name=model_name,  # Using model name directly
    role="Senior Speech Writer",
    goal="Write engaging and witty keynote speeches from provided research.",
    backstory="You are a veteran quantum computing writer with a background in modern physics.",
    allow_delegation=False,
    verbose=False,
)

# Create writing task
keynote_task = Task(
    description="Create a compelling keynote speech about quantum computing innovations and their impact on AI.",
    expected_output="A detailed keynote speech with an intro, body and conclusion.",
    output_file=str(KEYNOTE_SPEECH_FILE),
    agent=writer,
)

def run_crew():
    """Run the CrewAI workflow"""
    try:
        # Create outputs directory if it doesn't exist
        OUTPUTS_DIR.mkdir(exist_ok=True)
        
        # Initialize and run the crew
        crew = Crew(
            agents=[researcher, writer],
            tasks=[research_task, keynote_task],
            verbose=0
        )
        
        logger.info("Starting CrewAI workflow...")
        result = crew.kickoff()
        logger.info("CrewAI workflow completed successfully")
        return result
        
    except Exception as e:
        logger.error(f"Error running CrewAI workflow: {str(e)}")
        raise

if __name__ == "__main__":
    print(run_crew())
