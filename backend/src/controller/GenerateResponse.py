import os

import vertexai
from google.oauth2 import service_account
from src import ABS_CREDENTIAL_PATH
from src.logging.Logging import logger
from vertexai.preview.generative_models import GenerativeModel

# Set up your project details
PROJECT_ID = os.getenv("PROJECT_ID")
LOCATION = os.getenv("REGION")
RESOURCE_ID = "gemini-pro"

credentials = service_account.Credentials.from_service_account_file(ABS_CREDENTIAL_PATH)
vertexai.init(project=PROJECT_ID, location=LOCATION, credentials=credentials)


class GenerateResponse:
    def __init__(self, model="gemini-pro"):
        try:
            self.chat = self._initiate_chat_session(model)
            logger.info("Chat session successfully initiated.")
        except Exception as e:
            logger.error(f"Failed to initiate chat session: {e}")
            raise

    def generate_response(self, text):
        """Call the Gemini model to generate a description."""
        try:
            response = self._multiturn_generate_content(text)
            if response:
                generated_text = response.candidates[0].content.parts[0].text
                # logger.info(f"Response: {generated_text}")
                return generated_text
            else:
                logger.warning("No response generated by the model.")
                return None
        except Exception as e:
            logger.error(f"Error in generating response: {e}")
            return None

    def _initiate_chat_session(self, model=RESOURCE_ID):
        """Initialize the chat session。"""
        logger.info(f"Using model: {model}")
        model = GenerativeModel(model)
        return model.start_chat()

    def _multiturn_generate_content(self, user_input):
        """Generate responses from the model based on user input."""
        try:
            config = {"max_output_tokens": 2048, "temperature": 0.9, "top_p": 1}
            response = self.chat.send_message(user_input, generation_config=config)
            return response
        except Exception as e:
            logger.error(f"Error generating response: {e}")
            return None
