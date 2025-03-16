import unittest
import os
from dotenv import load_dotenv
import logging

# Configure basic logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

from models.llm import get_model

class TestLLMFallback(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        """Set up test environment variables"""
        load_dotenv()
        cls.original_mistral_key = os.getenv('MISTRAL_API_KEY')
        cls.original_openrouter_key = os.getenv('OPENROUTER_API_KEY')
        cls.original_openai_key = os.getenv('OPENAI_API_KEY')

    def setUp(self):
        """Reset environment variables before each test"""
        if self.original_mistral_key:
            os.environ['MISTRAL_API_KEY'] = self.original_mistral_key
        if self.original_openrouter_key:
            os.environ['OPENROUTER_API_KEY'] = self.original_openrouter_key
        if self.original_openai_key:
            os.environ['OPENAI_API_KEY'] = self.original_openai_key

    def test_mistral_primary(self):
        """Test Mistral API as primary choice"""
        logger.info("🧪 TEST: Testing Mistral API as primary choice")
        client, model_name = get_model(model_type="mistral", test=True)
        self.assertIsNotNone(client, "Mistral client should not be None")
        self.assertIsNotNone(model_name, "Mistral model name should not be None")
        self.assertEqual(model_name, "mistral/mistral-large-latest", "Should use mistral-large-latest model")
        logger.info("✅ TEST: Mistral primary test passed")

    def test_fallback_to_openrouter(self):
        """Test fallback to OpenRouter when Mistral fails"""
        logger.info("🧪 TEST: Testing fallback to OpenRouter")
        # Invalidate Mistral API key
        os.environ['MISTRAL_API_KEY'] = 'invalid_key'
        
        client, model_name = get_model(model_type="mistral", test=True)
        self.assertIsNotNone(client, "OpenRouter client should not be None")
        self.assertIsNotNone(model_name, "OpenRouter model name should not be None")
        self.assertEqual(model_name, "deepseek/deepseek-r1:free", "Should use default OpenRouter model")
        logger.info("✅ TEST: OpenRouter fallback test passed")

    def test_fallback_to_openai(self):
        """Test fallback to OpenAI when both Mistral and OpenRouter fail"""
        logger.info("🧪 TEST: Testing fallback to OpenAI")
        # Invalidate both Mistral and OpenRouter API keys
        os.environ['MISTRAL_API_KEY'] = 'invalid_key'
        os.environ['OPENROUTER_API_KEY'] = 'invalid_key'
        
        client, model_name = get_model(model_type="mistral", test=True)
        self.assertIsNotNone(client, "OpenAI client should not be None")
        self.assertIsNotNone(model_name, "OpenAI model name should not be None")
        self.assertEqual(model_name, "openai/gpt-3.5-turbo", "Should use default OpenAI model")
        logger.info("✅ TEST: OpenAI fallback test passed")

    def test_all_apis_fail(self):
        """Test behavior when all APIs fail"""
        logger.info("🧪 TEST: Testing all APIs failing")
        # Invalidate all API keys
        os.environ['MISTRAL_API_KEY'] = 'invalid_key'
        os.environ['OPENROUTER_API_KEY'] = 'invalid_key'
        os.environ['OPENAI_API_KEY'] = 'invalid_key'
        
        client, model_name = get_model(model_type="mistral", test=True)
        self.assertIsNone(client, "All APIs should fail")
        self.assertIsNone(model_name, "All model names should be None")
        logger.info("✅ TEST: All APIs fail test passed")

if __name__ == '__main__':
    unittest.main() 