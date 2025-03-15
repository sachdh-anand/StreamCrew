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
    
    print(f"ℹ️ Using OpenRouter model: {model_id}")
    print(f"ℹ️ Model selected from: {source}")
    
    return model_id

def test_openrouter_connection(model_id=None):
    """
    Tests the OpenRouter API connection with the specified model.
    
    Args:
        model_id: Optional model ID to test. If None, uses the value from get_model_id()
    
    Returns:
        bool: True if connection successful, False otherwise
    """
    # Get API key
    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        print("❌ OPENROUTER_API_KEY is missing.")
        return False
    
    # Get model ID
    if model_id is None:
        model_id = get_model_id()
    
    print(f"🔄 Testing OpenRouter connection with model: {model_id}")
    
    # API endpoint for OpenRouter
    API_URL = "https://openrouter.ai/api/v1/chat/completions"

    # Headers with API key
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    # Test prompt
    data = {
        "model": model_id,
        "messages": [{"role": "user", "content": "Hello, please introduce yourself in one sentence."}],
        "max_tokens": 100,
        "temperature": 0.7
    }

    try:
        response = requests.post(API_URL, headers=headers, json=data)
        
        if response.status_code == 200:
            result = response.json()
            print("✅ OpenRouter API is working!")
            print("Response:", result["choices"][0]["message"]["content"])
            return True
        else:
            print(f"❌ Error: API returned status code {response.status_code}")
            print(f"Response: {response.text}")
            return False

    except Exception as e:
        print(f"❌ Error reaching OpenRouter API: {e}")
        return False

def get_openrouter_model(model_id=None):
    """
    Returns a configured OpenRouter model instance for use with CrewAI.
    
    Args:
        model_id: Optional model ID to use. If None, uses the value from get_model_id()
    
    Returns:
        tuple: (client, model_name)
    """
    # Get API key
    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        raise ValueError("❌ OPENROUTER_API_KEY is missing. Please add it to your .env file.")
    
    # Get model ID
    if model_id is None:
        model_id = get_model_id()
    
    # Format for CrewAI compatibility
    model = model_id

    # Create a simple client to pass along with the model
    class OpenRouterClient:
        def __init__(self, api_key):
            self.api_key = api_key
            self.base_url = "https://openrouter.ai/api/v1"
    
    client = OpenRouterClient(api_key)
    return client, model

def list_recommended_models():
    """Prints a list of recommended models with their descriptions."""
    print("\n🤖 Recommended OpenRouter Models:")
    print("------------------------------------")
    for shortname, model_id in RECOMMENDED_MODELS.items():
        print(f"- {shortname}: {model_id}")
    print("\nTo use a specific model, set OPENROUTER_MODEL_ID in your .env file.")
    print("You can use either the full model name or one of the shorthand names above.")