from crewai import Crew, Task, Agent
from crewai_tools import SerperDevTool
from dotenv import load_dotenv
import os
from models.llm import get_model
from utils.logger import get_logger

# Initialize logger
logger = get_logger(__name__)

# Load environment variables
load_dotenv()

# Validate required environment variables
required_vars = ["SERPER_API_KEY"]
missing_vars = [var for var in required_vars if not os.getenv(var)]
if missing_vars:
    raise ValueError(f"Missing required environment variables: {', '.join(missing_vars)}")

# Get the LLM with fallback logic
model_name, _ = get_model(model_type="mistral", test=True)
if model_name is None:
    raise ValueError("Failed to initialize any LLM. Please check your API keys and try again.")

logger.info(f"🤖 Using model: {model_name}")

# Tools
search = SerperDevTool()

# Create the researcher agent
researcher = Agent(
    model_name=model_name,  # Using model name directly
    role="Senior AI Researcher",
    goal="Find promising research in the field of quantum computing.",
    backstory="You are a veteran quantum computing researcher with a background in modern physics.",
    allow_delegation=False,
    tools=[search],
    verbose=1,
)

# Create research task
research_task = Task(
    description="Research and analyze recent quantum computing breakthroughs and their AI applications.",
    expected_output="A detailed bullet point summary on each of the topics. Each bullet point should cover the topic, background and why the innovation is useful.",
    output_file="outputs/quantum_computing_research_summary.txt",
    agent=researcher,
)

# Create the writer agent
writer = Agent(
    model_name=model_name,  # Using model name directly
    role="Senior Speech Writer",
    goal="Write engaging and witty keynote speeches from provided research.",
    backstory="You are a veteran quantum computing writer with a background in modern physics.",
    allow_delegation=False,
    verbose=1,
)

# Create writing task
keynote_task = Task(
    description="Create a compelling keynote speech about quantum computing innovations and their impact on AI.",
    expected_output="A detailed keynote speech with an intro, body and conclusion.",
    output_file="outputs/quantum_computing_keynote_speech.txt",
    agent=writer,
)

def run_crew():
    """Run the CrewAI workflow"""
    try:
        # Create outputs directory if it doesn't exist
        os.makedirs("outputs", exist_ok=True)
        
        # Initialize and run the crew
        crew = Crew(
            agents=[researcher, writer],
            tasks=[research_task, keynote_task],
            verbose=1
        )
        
        logger.info("🚀 Starting CrewAI workflow...")
        result = crew.kickoff()
        logger.info("✅ CrewAI workflow completed successfully")
        return result
        
    except Exception as e:
        logger.error(f"❌ Error running CrewAI workflow: {str(e)}")
        raise

if __name__ == "__main__":
    print(run_crew())
