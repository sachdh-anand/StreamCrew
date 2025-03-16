import os
from dotenv import load_dotenv
import logging

# Configure basic logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Import config functions
from src.models.config.mistral import get_mistral_model, test_mistral_connection
from src.models.config.openrouterai import get_openrouter_model, test_openrouter_connection
from src.models.config.openai import get_openai_model, test_openai_connection

# Load environment variables
load_dotenv()

def get_model(model_type="mistral", test=False):
    """
    Returns the configured LLM model based on user selection with fallback logic:
    Mistral -> OpenRouter -> OpenAI
    
    Parameters:
    - model_type: Type of model to use (mistral, openai, openrouter)
    - test: If True, run a connection test before returning the model
    
    Returns:
    - (client, model_name): Tuple containing the client instance and model name
    """
    # Try Mistral first (either as primary choice or fallback)
    if model_type == "mistral":
        logger.info("LLM: Attempting to use Mistral API")
        try:
            if test:
                test_result = test_mistral_connection()
                if test_result:
                    logger.info("LLM: Mistral connection test passed")
                else:
                    logger.warning("LLM: Mistral connection test failed. Falling back to OpenRouter.")
                    return get_model("openrouter", test)
            return get_mistral_model()
        except Exception as e:
            logger.error(f"LLM: Error initializing Mistral: {str(e)}")
            logger.warning("LLM: Falling back to OpenRouter...")
            return get_model("openrouter", test)
    
    # Try OpenRouter second (either as primary choice or fallback)
    if model_type == "openrouter":
        logger.info("LLM: Attempting to use OpenRouter API")
        try:
            if test:
                test_result = test_openrouter_connection()
                if test_result:
                    logger.info("LLM: OpenRouter connection test passed")
                else:
                    logger.warning("LLM: OpenRouter connection test failed. Falling back to OpenAI.")
                    return get_model("openai", test)
            return get_openrouter_model()
        except Exception as e:
            logger.error(f"LLM: Error initializing OpenRouter: {str(e)}")
            logger.warning("LLM: Falling back to OpenAI...")
            return get_model("openai", test)
    
    # Try OpenAI last (either as primary choice or final fallback)
    if model_type == "openai":
        logger.info("LLM: Attempting to use OpenAI API")
        try:
            if test:
                test_result = test_openai_connection()
                if test_result:
                    logger.info("LLM: OpenAI connection test passed")
                else:
                    logger.error("LLM: All API connection tests failed.")
                    return None, None
            return get_openai_model()
        except Exception as e:
            logger.error(f"LLM: Error initializing OpenAI: {str(e)}")
            logger.error("LLM: All fallback options failed.")
            return None, None
    
    # Unknown model type
    logger.error(f"LLM: Unknown model type: {model_type}")
    return None, None