from openai import OpenAI
from dotenv import load_dotenv
import base64
import os
import logging

# Load environment variables from .env file
load_dotenv()

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Get API key from environment variable
openai_key = os.getenv("OPENAI_API_KEY")
if not openai_key:
    raise ValueError("OPENAI_API_KEY not found in environment variables. Please check your .env file.")

# Initialize OpenAI client with API key from environment
client = OpenAI(api_key=openai_key)

# System prompt for Khaleeji dialect
SAUDI_PROMPT = """
أنت نكستا الخليجي، مساعد ذكي يتحدث حصريًا باللهجة الخليجية. جميع إجاباتك، بدون استثناء، لازم تكون باللهجة الخليجية فقط.

مهامك الأساسية:
1- الرد على الأسئلة والمحادثات: جاوب دومًا باللهجة الخليجية. لا تستخدم الفصحى أو لهجات غير خليجية.
2- استخدم السياق بشكل ذكي: خلك واعي للسياق وخل إجابتك واضحة وسلسة باللهجة.
3- تكلم بأسلوب بشري طبيعي: رد بعفوية وكأنك شخص حقيقي من الخليج يتكلم مع صاحبه.
4- أضف لمسة ودية وأحيانًا نكهات محلية (مثل: يبه، حبيبي، هلا وغلا، الخ).
"""

async def generate_response(message: str):
    """
    Generate a response using OpenAI's GPT-4 and convert it to speech.
    
    Args:
        message (str): The user's input message
        
    Returns:
        dict: A dictionary containing the generated text and audio in base64 format
    """
    try:
        # Prepare messages for chat
        messages = [
            {"role": "system", "content": SAUDI_PROMPT},
            {"role": "user", "content": message}
        ]

        # Generate text response
        response = client.chat.completions.create(
            model="gpt-4",
            messages=messages,
            temperature=0.7,
            max_tokens=150
        )

        generated_text = response.choices[0].message.content

        # Generate speech
        speech_response = client.audio.speech.create(
            model="tts-1",
            voice="alloy",
            input=generated_text
        )

        # Convert audio to base64
        audio_data = speech_response.read()
        audio_base64 = base64.b64encode(audio_data).decode('utf-8')

        logger.info(f"Generated response: {generated_text}")
        return {
            "text": generated_text,
            "audio_base64": audio_base64
        }

    except Exception as e:
        logger.error(f"Error generating response: {str(e)}")
        raise Exception(f"Error generating response: {str(e)}")