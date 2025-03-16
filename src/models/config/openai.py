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
    
    print(f"Using OpenAI model: {model_id}")
    print(f"Model selected from: {source}")
    
    return model_id

def test_openai_connection():
    """Tests the OpenAI API connection to validate the key and return a boolean result."""
    # Get required environment variable
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("OPENAI_API_KEY is missing. Please add it to your .env file.")
        return False
        
    model_id = get_model_id()
    
    # Create test request
    try:
        print("Testing OpenAI API connection...")
        
        # Test with the Chat Completions API
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}"
        }
        
        payload = {
            "model": model_id,
            "messages": [{"role": "user", "content": "Hello, OpenAI!"}],
            "max_tokens": 10
        }
        
        response = requests.post(
            "https://api.openai.com/v1/chat/completions",
            headers=headers,
            data=json.dumps(payload)
        )
        
        if response.status_code == 200:
            print("OpenAI API is working!")
            response_json = response.json()
            content = response_json.get("choices", [{}])[0].get("message", {}).get("content", "")
            print(f"Response: {content}")
            return True
        else:
            print(f"Error from OpenAI API: {response.status_code} - {response.text}")
            return False
            
    except Exception as e:
        print(f"Error testing OpenAI API: {e}")
        return False

def get_openai_model():
    """Returns a configured OpenAI model for use with the litellm library."""
    # Get required environment variable
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("OPENAI_API_KEY is missing. Please add it to your .env file.")
    
    # Get the model ID to use
    model_id = get_model_id()
    
    # For litellm, return model name with appropriate prefix
    litellm_model = f"openai/{model_id}"
    
    return litellm_model, model_id

def list_recommended_models():
    """Prints a list of recommended models with their descriptions."""
    print("\n🤖 Recommended OpenAI Models:")
    print("------------------------------------")
    for shortname, model_id in RECOMMENDED_MODELS.items():
        print(f"- {shortname}: {model_id}")
    print("\nTo use a specific model, set OPENAI_MODEL_ID in your .env file.")
    print("You can use either the full model name or one of the shorthand names above.")
    print("\nNote: Different models have different pricing. Check OpenAI's website for current rates.")