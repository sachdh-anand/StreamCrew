import os
from dotenv import load_dotenv
import litellm

# Load environment variables
load_dotenv()

def test_mistral_connection():
    """Tests the Mistral API connection and returns the result."""
    api_key = os.getenv("MISTRAL_API_KEY")
    if not api_key:
        print("❌ MISTRAL_API_KEY is missing.")
        return False

    # Initialize litellm for testing
    try:
        print("🔄 Testing Mistral API connection...")
        response = litellm.completion(
            model="mistral/mistral-large-latest",
            messages=[{"role": "user", "content": "Hello, Mistral!"}],
            api_key=api_key
        )

        print("✅ Mistral API is working!")
        print("Response:", response.choices[0].message.content)
        return True

    except Exception as e:
        print("❌ Error reaching Mistral API:", e)
        return False

def get_mistral_model():
    """Returns a configured Mistral AI model instance using litellm."""
    api_key = os.getenv("MISTRAL_API_KEY")
    if not api_key:
        raise ValueError("❌ MISTRAL_API_KEY is missing. Please add it to your .env file.")

    # Set the API key for litellm
    os.environ["MISTRAL_API_KEY"] = api_key
    
    # Return the model name in litellm format
    model = "mistral/mistral-large-latest"
    return model, model