import os
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# OpenRouter model options
RECOMMENDED_MODELS = {
    "dolphin3.0-r1": "cognitivecomputations/dolphin3.0-r1-mistral-24b:free",
    "deepseek-r1": "deepseek/deepseek-r1:free",
    "qwen2.5-coder": "qwen/qwen-2.5-coder-32b-instruct:free",
    "gemini-2.0":"google/gemini-2.0-pro-exp-02-05:free"
    # Add more free models here as needed
}

# Default model if none specified
DEFAULT_MODEL = "cognitivecomputations/dolphin3.0-r1-mistral-24b:free"

def get_model_id():
    """
    Get the OpenRouter model ID from environment variables or use default.
    Users can set OPENROUTER_MODEL_ID in their .env file to use a specific model.
    """
    model_id = os.getenv("OPENROUTER_MODEL_ID")
    source = "environment variable OPENROUTER_MODEL_ID"
    
    # Check if the model ID is a shorthand reference
    if model_id in RECOMMENDED_MODELS:
        model_id = RECOMMENDED_MODELS[model_id]
        source = f"shorthand '{os.getenv('OPENROUTER_MODEL_ID')}' in environment variable"
    elif model_id is None:
        model_id = DEFAULT_MODEL
        source = "default setting (no OPENROUTER_MODEL_ID specified)"
    
    print(f"Using OpenRouter model: {model_id}")
    print(f"Model selected from: {source}")
    
    return model_id

def test_openrouter_connection():
    """Tests the OpenRouter API connection to validate the key and return a boolean result."""
    # Get required environment variables
    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        print("OPENROUTER_API_KEY is missing. Please add it to your .env file.")
        return False
    
    model_id = get_model_id()
    
    # Create test request
    try:
        print("Testing OpenRouter API connection...")
        
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}",
            "HTTP-Referer": "https://github.com/StreamCrew/StreamCrew",
            "X-Title": "StreamCrew AI Research Platform"
        }
        
        payload = {
            "model": model_id,
            "messages": [{"role": "user", "content": "Hello, OpenRouter!"}],
            "max_tokens": 10
        }
        
        response = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers=headers,
            json=payload
        )
        
        if response.status_code == 200:
            print("OpenRouter API is working!")
            response_json = response.json()
            content = response_json.get("choices", [{}])[0].get("message", {}).get("content", "")
            print(f"Response: {content}")
            return True
        else:
            print(f"Error from OpenRouter API: {response.status_code} - {response.text}")
            return False
    
    except Exception as e:
        print(f"Error testing OpenRouter API: {e}")
        return False

def get_openrouter_model():
    """Returns a configured OpenRouter model for use with the litellm library."""
    # Get required environment variables
    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        raise ValueError("OPENROUTER_API_KEY is missing. Please add it to your .env file.")
    
    # Get the model ID to use
    model_id = get_model_id()
    
    # For litellm, we don't need the openrouter/ prefix
    litellm_model = model_id
    
    return litellm_model, model_id

def list_recommended_models():
    """Prints a list of recommended models with their descriptions."""
    print("\n🤖 Recommended OpenRouter Models:")
    print("------------------------------------")
    for shortname, model_id in RECOMMENDED_MODELS.items():
        print(f"- {shortname}: {model_id}")
    print("\nTo use a specific model, set OPENROUTER_MODEL_ID in your .env file.")
    print("You can use either the full model name or one of the shorthand names above.")