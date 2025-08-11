from openai import OpenAI
from dotenv import load_dotenv
import os
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

try:
    # Try to load from .env file first (for local development)
    load_dotenv()
except Exception as e:
    logger.warning(f"Could not load .env file: {e}")

# Get API key from environment variable
openai_key = os.environ.get("OPENAI_API_KEY")
if not openai_key:
    logger.error("OPENAI_API_KEY not found in environment variables")
    raise ValueError(
        "OPENAI_API_KEY not found. Please set it in Railway environment variables "
        "or in .env file for local development"
    )

# Initialize OpenAI client with API key from environment
client = OpenAI(api_key=openai_key)

## Text-only chat; voice transcription and TTS removed

# System prompt for Khaleeji dialect
SAUDI_PROMPT = """
أنت نيكستا الخليجي، مساعد ذكي يتحدث حصريًا باللهجة الخليجية. جميع إجاباتك، بدون استثناء، لازم تكون باللهجة الخليجية فقط.

مهامك الأساسية:
1- الرد على الأسئلة والمحادثات: جاوب دومًا باللهجة الخليجية. لا تستخدم الفصحى أو لهجات غير خليجية.
2- استخدم السياق بشكل ذكي: خلك واعي للسياق وخل إجابتك واضحة وسلسة باللهجة.
3- تكلم بأسلوب بشري طبيعي: رد بعفوية وكأنك شخص حقيقي من الخليج يتكلم مع صاحبه.
4- أضف لمسة ودية وأحيانًا نكهات محلية (مثل: يبه، حبيبي، هلا وغلا، الخ).
"""

async def generate_response(message: str):
    """
    Generate a response using OpenAI's GPT-4.
    
    Args:
        message (str): The user's input message
        
    Returns:
        str: The generated text
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
            max_tokens=150,
        )

        generated_text = response.choices[0].message.content
        logger.info(f"Generated response text: {generated_text}")
        return generated_text

    except Exception as e:
        logger.error(f"Error generating response: {str(e)}")
        raise Exception(f"Error generating response: {str(e)}")
    