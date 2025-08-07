from openai import OpenAI
from dotenv import load_dotenv
import base64
import os
import logging
import openai_whisper as whisper

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

try:
    # Try to load from .env file first (for local development)
    load_dotenv()
    logger.info("✅ Loaded environment variables from .env file")
except Exception as e:
    logger.warning(f"⚠️ Could not load .env file: {e}. Assuming Railway env vars are used.")

# Get API key from environment variable
openai_key = os.environ.get("OPENAI_API_KEY")
if not openai_key:
    logger.error("❌ OPENAI_API_KEY not found in environment variables")
    raise ValueError(
        "OPENAI_API_KEY not found. Please set it in Railway environment variables "
        "or in .env file for local development"
    )

# Initialize OpenAI client with API key from environment
client = OpenAI(api_key=openai_key)
logger.info("✅ Initialized OpenAI client")

# Load Whisper model for voice transcription
logger.info("🎙️ Loading Whisper model...")
whisper_model = whisper.load_model("base")
logger.info("✅ Whisper model loaded successfully")

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
    Generate a response using OpenAI's GPT-4 and convert it to speech.
    
    Args:
        message (str): The user's input message
        
    Returns:
        dict: A dictionary containing the generated text and audio in base64 format
    """
    try:
        logger.info(f"🤖 Generating response for message: {message}")
        
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
        logger.info(f"✅ Generated text response: {generated_text}")

        # Generate speech
        logger.info("🔊 Converting text to speech...")
        speech_response = client.audio.speech.create(
            model="tts-1",
            voice="alloy",
            input=generated_text
        )

        # Convert audio to base64
        audio_data = speech_response.read()
        audio_base64 = base64.b64encode(audio_data).decode('utf-8')
        logger.info("✅ Audio conversion complete")

        return {
            "text": generated_text,
            "audio_base64": audio_base64
        }

    except Exception as e:
        logger.error(f"❌ Error generating response: {str(e)}")
        raise Exception(f"Error generating response: {str(e)}")

async def process_voice_message(audio_file_path: str):
    """
    Process a voice message: transcribe it, generate a response, and convert response to speech.
    
    Args:
        audio_file_path (str): Path to the audio file
        
    Returns:
        dict: A dictionary containing the transcript, reply text, and reply audio
    """
    try:
        logger.info(f"🎙️ Processing voice file: {audio_file_path}")
        
        # Transcribe audio using Whisper
        logger.info("🔍 Transcribing audio...")
        result = whisper_model.transcribe(audio_file_path)
        transcript = result["text"]
        logger.info(f"✅ Transcribed text: {transcript}")

        # Generate response
        logger.info("🤖 Generating response...")
        response = await generate_response(transcript)
        logger.info("✅ Response generated successfully")
        
        return {
            "transcript": transcript,
            "reply_text": response["text"],
            "reply_audio": response["audio_base64"]
        }

    except Exception as e:
        logger.error(f"❌ Error processing voice message: {str(e)}")
        raise Exception(f"Error processing voice message: {str(e)}")