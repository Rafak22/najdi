from openai import OpenAI
from dotenv import load_dotenv
import os
import logging
import edge_tts

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

# Using OpenAI Whisper API for transcription (no local model required)

# System prompt for Khaleeji dialect
SAUDI_PROMPT = """
أنت نيكستا الخليجي، مساعد ذكي يتحدث حصريًا باللهجة الخليجية. جميع إجاباتك، بدون استثناء، لازم تكون باللهجة الخليجية فقط.

مهامك الأساسية:
1- الرد على الأسئلة والمحادثات: جاوب دومًا باللهجة الخليجية. لا تستخدم الفصحى أو لهجات غير خليجية.
2- استخدم السياق بشكل ذكي: خلك واعي للسياق وخل إجابتك واضحة وسلسة باللهجة.
3- تكلم بأسلوب بشري طبيعي: رد بعفوية وكأنك شخص حقيقي من الخليج يتكلم مع صاحبه.
4- أضف لمسة ودية وأحيانًا نكهات محلية (مثل: يبه، حبيبي، هلا وغلا، الخ).
"""

async def synthesize_speech_edge(
    text: str,
    *,
    voice_name: str = "ar-SA-HamedNeural",
    rate: str = "0%",
    pitch: str = "0%",
) -> bytes:
    """
    Convert text to speech using edge-tts (no API key) and return MP3 bytes.

    - Default voice is "ar-SA-HamedNeural".
    - You can change to "ar-SA-ZariyahNeural" or "ar-SA-SamiNeural" easily via the voice_name argument.
    - Supports rate and pitch adjustments.
    """
    communicate = edge_tts.Communicate(text=text, voice=voice_name, rate=rate, pitch=pitch)
    audio_bytes = bytearray()
    async for chunk in communicate.stream():
        if chunk["type"] == "audio":
            audio_bytes.extend(chunk["data"])
    return bytes(audio_bytes)


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
            max_tokens=150,
        )

        generated_text = response.choices[0].message.content

        # Generate speech via edge-tts
        audio_mp3_bytes = await synthesize_speech_edge(generated_text)

        logger.info(f"Generated response text: {generated_text}")
        return {
            "text": generated_text,
            "audio_bytes": audio_mp3_bytes,
        }

    except Exception as e:
        logger.error(f"Error generating response: {str(e)}")
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
        # Transcribe audio using OpenAI Whisper API
        with open(audio_file_path, "rb") as audio_file:
            transcription = client.audio.transcriptions.create(
                model="whisper-1",
                file=audio_file,
            )
        transcript = transcription.text
        logger.info(f"Transcribed text: {transcript}")

        # Generate response
        response = await generate_response(transcript)

        return {
            "transcript": transcript,
            "reply_text": response["text"],
            "reply_audio": response["audio_bytes"],  # raw MP3 bytes
        }

    except Exception as e:
        logger.error(f"Error processing voice message: {str(e)}")
        raise Exception(f"Error processing voice message: {str(e)}")