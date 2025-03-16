import sys
from pathlib import Path
from os.path import dirname, abspath, join
import argparse
import os
import warnings

# Filter out specific deprecation warnings from dependencies
warnings.filterwarnings("ignore", category=DeprecationWarning, module="pkg_resources")
warnings.filterwarnings("ignore", category=DeprecationWarning, module="pydantic")
warnings.filterwarnings("ignore", category=UserWarning, module="pydantic")
# Also filter out warnings from crewai_tools validators
warnings.filterwarnings("ignore", category=DeprecationWarning, module="crewai_tools")

# Add the src directory to Python path
root_dir = dirname(dirname(dirname(abspath(__file__))))
sys.path.append(root_dir)

from crewai import Crew, Task, Agent
from dotenv import load_dotenv, find_dotenv
from src.models.llm import get_model
from src.utils.logger import get_logger
from src.config.settings import OUTPUTS_DIR, DEFAULT_RESEARCH_TOPIC

# Initialize logger
logger = get_logger(__name__)

# Enhanced env loading - check multiple locations
dotenv_paths = [
    Path(root_dir) / '.env',
    Path(root_dir) / '.env.local',
    Path(root_dir) / 'src' / '.env',
    Path.cwd() / '.env'
]

logger.info(f"Project root directory: {root_dir}")
logger.info(f"Current working directory: {Path.cwd()}")

# Log all potential .env paths we're checking
for p in dotenv_paths:
    if p.exists():
        logger.info(f"Found .env file at: {p}")
        dotenv_path = str(p)
        break
else:
    logger.warning("No .env file found in any of the expected locations")
    dotenv_path = None

# Load environment variables with detailed logging
if dotenv_path:
    logger.info(f"Loading environment from: {dotenv_path}")
    load_dotenv(dotenv_path=dotenv_path, verbose=True)
else:
    logger.info("Attempting to load environment variables from default locations")
    load_dotenv()

# Parse command line arguments for dynamic topics
def parse_args():
    parser = argparse.ArgumentParser(description="Run research on a specific topic")
    parser.add_argument("topic", nargs="?", default=DEFAULT_RESEARCH_TOPIC, 
                        help="The research topic to analyze")
    return parser.parse_args()

# Log environment variable status - safely show prefix of key
serper_key = os.getenv("SERPER_API_KEY")
if serper_key:
    masked_key = serper_key[:4] + "..." + serper_key[-4:] if len(serper_key) > 8 else "***"
    logger.info(f"SERPER_API_KEY found in environment: {masked_key}")
else:
    logger.error("SERPER_API_KEY not found in environment variables")

# Try to import SerperDevTool with more detailed error handling
try:
    logger.info("Attempting to import SerperDevTool...")
    from crewai_tools import SerperDevTool
    logger.info("Successfully imported SerperDevTool class")
    
    try:
        logger.info("Initializing SerperDevTool instance...")
        
        # Print packages installed to help with debugging
        import pkg_resources
        installed_packages = pkg_resources.working_set
        installed_packages_list = sorted(["%s==%s" % (i.key, i.version) for i in installed_packages])
        logger.info(f"Installed packages: {[p for p in installed_packages_list if 'crew' in p.lower()]}")
        
        search = SerperDevTool()
        logger.info(f"Successfully initialized SerperDevTool with API key: {masked_key}")
    except Exception as e:
        logger.error(f"Error initializing SerperDevTool instance: {str(e)}")
        import traceback
        logger.error(f"Detailed error: {traceback.format_exc()}")
        search = None
except ImportError as e:
    logger.error(f"ImportError when importing SerperDevTool: {str(e)}")
    logger.error(f"Python path: {sys.path}")
    search = None
except Exception as e:
    logger.error(f"Unexpected error when importing SerperDevTool: {str(e)}")
    import traceback
    logger.error(f"Detailed error: {traceback.format_exc()}")
    search = None

# Validate required environment variables
required_vars = ["SERPER_API_KEY"]
missing_vars = [var for var in required_vars if not os.getenv(var)]
if missing_vars:
    logger.error(f"Missing required environment variables: {', '.join(missing_vars)}")
else:
    logger.info("All required environment variables found")

# Get the LLM with fallback logic
model_name, _ = get_model(model_type="mistral", test=True)
if model_name is None:
    raise ValueError("Failed to initialize any LLM. Please check your API keys and try again.")

logger.info(f"Using model: {model_name}")

def create_output_paths(topic):
    """Generate output file paths based on the topic"""
    # Create a safe filename from the topic
    safe_topic = "".join(c if c.isalnum() or c in [' ', '_', '-'] else '_' for c in topic.lower())
    safe_topic = safe_topic.replace(' ', '_')[:50]  # Limit length, replace spaces
    
    # Create the file paths
    research_file = OUTPUTS_DIR / f"{safe_topic}_research_summary.txt"
    keynote_file = OUTPUTS_DIR / f"{safe_topic}_keynote_speech.txt"
    
    return research_file, keynote_file

def run_crew(topic=DEFAULT_RESEARCH_TOPIC):
    """Run the CrewAI workflow for the given topic"""
    try:
        # Create outputs directory if it doesn't exist
        OUTPUTS_DIR.mkdir(exist_ok=True)
        
        # Generate output file paths based on the topic
        research_file, keynote_file = create_output_paths(topic)
        
        # Create the researcher agent with tools if available
        tools = [search] if search else []
        logger.info(f"Tools available to researcher: {[tool.__class__.__name__ for tool in tools]}")
        
        # Create the researcher agent
        researcher = Agent(
            model_name=model_name,
            role="Senior Researcher",
            goal=f"Find promising research in the field of {topic}.",
            backstory="You are a veteran researcher with deep expertise in the requested topic.",
            allow_delegation=False,
            tools=tools,
            verbose=False,
        )
        logger.info(f"Created researcher agent with {len(tools)} tools")
        
        # Add a custom log wrapper around SerperDevTool to monitor usage
        if search:
            try:
                # Try using _run method first (new API)
                if hasattr(search, '_run'):
                    original_execute = search._run
                    
                    def execute_with_logging(*args, **kwargs):
                        # Try to find query in different possible locations
                        if 'search_query' in kwargs:
                            query = kwargs.get('search_query')
                        elif 'query' in kwargs:
                            query = kwargs.get('query')
                        elif len(args) > 0 and isinstance(args[0], dict) and 'query' in args[0]:
                            query = args[0]['query']
                        elif 'input' in kwargs:
                            query = kwargs.get('input')
                        else:
                            # Inspect all args and kwargs for debugging
                            query = f"unknown (args={str(args)[:50]}..., kwargs_keys={list(kwargs.keys())})"
                        
                        logger.info(f"Executing Serper search with query: {query}")
                        result = original_execute(*args, **kwargs)
                        
                        # Log count of results
                        organic_results = result.get('organic', [])
                        logger.info(f"Serper search completed with {len(organic_results)} organic results")
                        
                        # Log titles and links
                        if organic_results:
                            logger.info("Search results:")
                            for i, res in enumerate(organic_results[:10], 1):
                                title = res.get('title', 'No title')
                                link = res.get('link', 'No link')
                                logger.info(f"  {i}. {title} - {link}")
                        
                        return result
                    
                    search._run = execute_with_logging
                    logger.info("Successfully wrapped SerperDevTool._run with logging")
                # Fallback to execute method
                elif hasattr(search, 'execute'):
                    original_execute = search.execute
                    
                    def execute_with_logging(*args, **kwargs):
                        # Try to find query in different possible locations
                        if 'search_query' in kwargs:
                            query = kwargs.get('search_query')
                        elif 'query' in kwargs:
                            query = kwargs.get('query')
                        elif len(args) > 0 and isinstance(args[0], dict) and 'query' in args[0]:
                            query = args[0]['query']
                        elif 'input' in kwargs:
                            query = kwargs.get('input')
                        else:
                            # Inspect all args and kwargs for debugging
                            query = f"unknown (args={str(args)[:50]}..., kwargs_keys={list(kwargs.keys())})"
                        
                        logger.info(f"Executing Serper search with query: {query}")
                        result = original_execute(*args, **kwargs)
                        
                        # Log count of results
                        organic_results = result.get('organic', [])
                        logger.info(f"Serper search completed with {len(organic_results)} organic results")
                        
                        # Log titles and links
                        if organic_results:
                            logger.info("Search results:")
                            for i, res in enumerate(organic_results[:10], 1):
                                title = res.get('title', 'No title')
                                link = res.get('link', 'No link')
                                logger.info(f"  {i}. {title} - {link}")
                        
                        return result
                    
                    search.execute = execute_with_logging
                    logger.info("Successfully wrapped SerperDevTool.execute with logging")
                else:
                    logger.warning("Could not wrap SerperDevTool methods - API may have changed")
            except Exception as e:
                logger.warning(f"Error setting up SerperDevTool logging wrapper: {str(e)}")
        
        # Create research task
        research_task = Task(
            description=f"Research and analyze: {topic}",
            expected_output="A detailed bullet point summary on each of the topics. Each bullet point should cover the topic, background and why the innovation is useful.",
            output_file=str(research_file),
            agent=researcher,
        )
        
        # Create the writer agent
        writer = Agent(
            model_name=model_name,
            role="Senior Speech Writer",
            goal=f"Write engaging and witty keynote speeches about {topic} from provided research.",
            backstory="You are a veteran writer with a background in creating compelling narratives from technical content.",
            allow_delegation=False,
            verbose=False,
        )
        
        # Create writing task
        keynote_task = Task(
            description=f"Create a compelling keynote speech about {topic}.",
            expected_output="A detailed keynote speech with an intro, body and conclusion.",
            output_file=str(keynote_file),
            agent=writer,
            context=[research_task]
        )
        
        # Initialize and run the crew
        crew = Crew(
            agents=[researcher, writer],
            tasks=[research_task, keynote_task],
            verbose=0
        )
        
        logger.info(f"Starting CrewAI workflow for topic: {topic}")
        result = crew.kickoff()
        logger.info("CrewAI workflow completed successfully")
        return result
        
    except Exception as e:
        logger.error(f"Error running CrewAI workflow: {str(e)}")
        raise

if __name__ == "__main__":
    args = parse_args()
    print(run_crew(args.topic))
