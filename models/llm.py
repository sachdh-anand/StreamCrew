import os
from dotenv import load_dotenv
import logging

# Configure basic logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Import config functions
from models.config.mistral import get_mistral_model, test_mistral_connection
from models.config.openrouterai import get_openrouter_model, test_openrouter_connection
from models.config.openai import get_openai_model, test_openai_connection

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
        logger.info("🤖 LLM: Attempting to use Mistral API")
        try:
            if test:
                test_result = test_mistral_connection()
                if test_result:
                    logger.info("✅ LLM: Mistral connection test passed")
                    return get_mistral_model()
                else:
                    logger.warning("⚠️ LLM: Mistral connection test failed")
                    logger.info("🔄 LLM: Falling back to OpenRouter")
                    return get_model("openrouter", test=True)
            return get_mistral_model()
        except Exception as e:
            logger.warning(f"⚠️ LLM: Mistral initialization failed: {str(e)}")
            return get_model("openrouter", test=True)
    
    # Try OpenRouter (either as primary choice or fallback)
    elif model_type == "openrouter":
        logger.info("🤖 LLM: Attempting to use OpenRouter API")
        try:
            if test:
                test_result = test_openrouter_connection()
                if test_result:
                    logger.info("✅ LLM: OpenRouter connection test passed")
                    return get_openrouter_model()
                else:
                    logger.warning("⚠️ LLM: OpenRouter connection test failed")
                    logger.info("🔄 LLM: Falling back to OpenAI")
                    return get_model("openai", test=True)
            return get_openrouter_model()
        except Exception as e:
            logger.warning(f"⚠️ LLM: OpenRouter initialization failed: {str(e)}")
            return get_model("openai", test=True)
    
    # Try OpenAI (either as primary choice or final fallback)
    elif model_type == "openai":
        logger.info("🤖 LLM: Attempting to use OpenAI API")
        try:
            if test:
                test_result = test_openai_connection()
                if test_result:
                    logger.info("✅ LLM: OpenAI connection test passed")
                    return get_openai_model()
                else:
                    logger.warning("⚠️ LLM: OpenAI connection test failed")
                    logger.error("❌ LLM: All API attempts failed")
                    return None, None
            return get_openai_model()
        except Exception as e:
            logger.warning(f"⚠️ LLM: OpenAI initialization failed: {str(e)}")
            return None, None
    
    else:
        logger.error(f"❌ LLM: Unsupported model type: {model_type}")
        raise ValueError(f"Unsupported model type: {model_type}")