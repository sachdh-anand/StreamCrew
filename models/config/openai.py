import os
import requests
import json
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# OpenAI model options
RECOMMENDED_MODELS = {
    "gpt-3.5-turbo": "gpt-3.5-turbo",           # Good balance of capability and cost
    "gpt-3.5-turbo-16k": "gpt-3.5-turbo-16k",   # Extended context version
    "gpt-4": "gpt-4",                           # Most capable model
    "gpt-4-turbo": "gpt-4-turbo-preview",       # Newest version of GPT-4
    "gpt-4-vision": "gpt-4-vision-preview",     # Vision-capable model
    "gpt-4-32k": "gpt-4-32k",                   # Extended context GPT-4
}

# Default model if none specified
DEFAULT_MODEL = "gpt-3.5-turbo"

def get_model_id():
    """
    Get the OpenAI model ID from environment variables or use default.
    Users can set OPENAI_MODEL_ID in their .env file to use a specific model.
    """
    model_id = os.getenv("OPENAI_MODEL_ID")
    source = "environment variable OPENAI_MODEL_ID"
    
    # Check if the model ID is a shorthand reference
    if model_id in RECOMMENDED_MODELS:
        model_id = RECOMMENDED_MODELS[model_id]
        source = f"shorthand '{os.getenv('OPENAI_MODEL_ID')}' in environment variable"
    elif model_id is None:
        model_id = DEFAULT_MODEL
        source = "default setting (no OPENAI_MODEL_ID specified)"
    
    print(f"ℹ️ Using OpenAI model: {model_id}")
    print(f"ℹ️ Model selected from: {source}")
    
    return model_id

def test_openai_connection(model_id=None):
    """
    Tests the OpenAI API connection with the specified model.
    
    Args:
        model_id: Optional model ID to test. If None, uses the value from get_model_id()
    
    Returns:
        bool: True if connection successful, False otherwise
    """
    # Get API key
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("❌ OPENAI_API_KEY is missing.")
        return False
    
    # Get model ID
    if model_id is None:
        model_id = get_model_id()
    
    print(f"🔄 Testing OpenAI connection with model: {model_id}")
    
    # API endpoint for OpenAI
    API_URL = "https://api.openai.com/v1/chat/completions"

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
            print("✅ OpenAI API is working!")
            print("Response:", result["choices"][0]["message"]["content"])
            return True
        else:
            print(f"❌ Error: API returned status code {response.status_code}")
            print(f"Response: {response.text}")
            return False

    except Exception as e:
        print(f"❌ Error reaching OpenAI API: {e}")
        return False

def get_openai_model(model_id=None):
    """
    Returns a configured OpenAI model instance for use with CrewAI.
    
    Args:
        model_id: Optional model ID to use. If None, uses the value from get_model_id()
    
    Returns:
        tuple: (client, model_name)
    """
    # Get API key
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("❌ OPENAI_API_KEY is missing. Please add it to your .env file.")
    
    # Get model ID
    if model_id is None:
        model_id = get_model_id()
    
    # Format for CrewAI compatibility
    model = f"openai/{model_id}"

    # Create a simple client to pass along with the model
    class OpenAIClient:
        def __init__(self, api_key):
            self.api_key = api_key
            self.base_url = "https://api.openai.com/v1"
    
    client = OpenAIClient(api_key)
    return client, model

def list_recommended_models():
    """Prints a list of recommended models with their descriptions."""
    print("\n🤖 Recommended OpenAI Models:")
    print("------------------------------------")
    for shortname, model_id in RECOMMENDED_MODELS.items():
        print(f"- {shortname}: {model_id}")
    print("\nTo use a specific model, set OPENAI_MODEL_ID in your .env file.")
    print("You can use either the full model name or one of the shorthand names above.")
    print("\nNote: Different models have different pricing. Check OpenAI's website for current rates.")