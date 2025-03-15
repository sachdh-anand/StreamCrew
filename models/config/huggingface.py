import os
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# List of recommended open-source models
RECOMMENDED_MODELS = {
    # Smaller models that work well with free tier
    "tiny-llama": "TinyLlama/TinyLlama-1.1B-Chat-v1.0",  # Only 1.1B parameters
    "flan-t5-small": "google/flan-t5-small",  # Smaller version (80M parameters)
    "flan-t5-base": "google/flan-t5-base",  # Medium size (250M parameters)
    "phi-2": "microsoft/phi-2",  # 2.7B efficient model
    "gemma-2b": "google/gemma-2b-it",  # Google's 2B instruction-tuned model
    "bloomz-1b7": "bigscience/bloomz-1b7",  # 1.7B multilingual model
    "distilgpt2": "distilgpt2",  # Lightweight GPT-2 (82M parameters)
    "opt-350m": "facebook/opt-350m",  # Meta's 350M parameter model
    
    # These models might work but could be close to the limit
    "mistral-7b-instruct": "mistralai/Mistral-7B-Instruct-v0.1",  # High quality but larger
    "zephyr-7b": "HuggingFaceH4/zephyr-7b-beta"  # High quality but larger
}

# Default model if none specified
DEFAULT_MODEL = "mistralai/Mistral-7B-Instruct-v0.2"

# Get model ID from environment or use default
def get_model_id():
    """
    Get the Hugging Face model ID from environment variables or use default.
    Users can set HF_MODEL_ID in their .env file to use a specific model.
    """
    model_id = os.getenv("HF_MODEL_ID")
    source = "environment variable HF_MODEL_ID"
    
    # Check if the model ID is a shorthand reference
    if model_id in RECOMMENDED_MODELS:
        model_id = RECOMMENDED_MODELS[model_id]
        source = f"shorthand '{os.getenv('HF_MODEL_ID')}' in environment variable"
    elif model_id is None:
        model_id = DEFAULT_MODEL
        source = "default setting (no HF_MODEL_ID specified)"
    
    print(f"ℹ️ Using Hugging Face model: {model_id}")
    print(f"ℹ️ Model selected from: {source}")
    
    return model_id

def test_huggingface_connection(model_id=None):
    """
    Tests the Hugging Face API connection with the specified model.
    
    Args:
        model_id: Optional model ID to test. If None, uses the value from get_model_id()
    
    Returns:
        bool: True if connection successful, False otherwise
    """
    # Get API key
    api_key = os.getenv("HUGGINGFACE_API_KEY")
    if not api_key:
        print("❌ HUGGINGFACE_API_KEY is missing.")
        return False
    
    # Get model ID
    if model_id is None:
        model_id = get_model_id()
    
    print(f"🔄 Testing Hugging Face connection with model: {model_id}")
    
    # API endpoint for Hugging Face Inference API
    API_URL = f"https://api-inference.huggingface.co/models/{model_id}"

    # Headers with API key
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    # Test prompt
    data = {
        "inputs": "Write a short greeting introducing yourself as an AI assistant.",
        "parameters": {
            "max_length": 100,
            "temperature": 0.7,
            "top_p": 0.9
        }
    }

    try:
        response = requests.post(API_URL, headers=headers, json=data)
        
        if response.status_code == 200:
            print("✅ Hugging Face API is working!")
            print("Response:", response.json()[0]['generated_text'])
            return True
        else:
            print(f"❌ Error: API returned status code {response.status_code}")
            print(f"Response: {response.text}")
            return False

    except Exception as e:
        print(f"❌ Error reaching Hugging Face API: {e}")
        return False

def get_huggingface_model(model_id=None):
    """
    Returns a configured Hugging Face model instance for use with CrewAI.
    
    Args:
        model_id: Optional model ID to use. If None, uses the value from get_model_id()
    
    Returns:
        tuple: (client, model_name)
    """
    # Get API key
    api_key = os.getenv("HUGGINGFACE_API_KEY")
    if not api_key:
        raise ValueError("❌ HUGGINGFACE_API_KEY is missing. Please add it to your .env file.")
    
    # Get model ID
    if model_id is None:
        model_id = get_model_id()
    
    # Format for CrewAI compatibility
    model = f"huggingface/{model_id}"

    # Create a simple client to pass along with the model
    class HuggingFaceClient:
        def __init__(self, api_key):
            self.api_key = api_key
            self.base_url = "https://api-inference.huggingface.co/models"
            
        def get_model_url(self, model_id):
            return f"{self.base_url}/{model_id}"
    
    client = HuggingFaceClient(api_key)
    return client, model

def list_recommended_models():
    """Prints a list of recommended models with their IDs."""
    print("\n🤗 Recommended Hugging Face Models:")
    print("------------------------------------")
    for shortname, model_id in RECOMMENDED_MODELS.items():
        print(f"- {shortname}: {model_id}")
    print("\nTo use a specific model, set HF_MODEL_ID in your .env file.")
    print("You can use either the full model ID or one of the shorthand names above.")