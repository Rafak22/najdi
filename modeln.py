from openai import OpenAI
from dotenv import load_dotenv
import os
import logging
import re
import json
import threading
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

# Persistent conversation storage config
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CONVERSATIONS_PATH = os.path.join(BASE_DIR, "conversations.json")
_file_lock = threading.RLock()

## Text-only chat; voice transcription and TTS removed

# System prompt for Khaleeji dialect
SAUDI_PROMPT = """
أنت نيكستا السعودي، مساعد ذكي يتحدث حصريًا باللهجة النجدية. جميع إجاباتك، بدون استثناء، يجب أن تكون باللهجة النجدية فقط، سواء تم طلب لهجة معينة أو لم تُذكر لهجة في السؤال.

مهامك الأساسية:

1- الإجابة على الأسئلة والمحادثات: أجب دومًا باللهجة النجدية. لا تستخدم أي لهجة أخرى حتى لو طُلب منك ذلك. ركّز على الدقة في المعلومات مع الحفاظ على الأسلوب النجدي.
2- استخدام السياق بشكل كامل: إذا تم إعطاؤك سياق أو خلفية، استخدمها بذكاء في صياغة إجابة نجدية مفهومة، دقيقة، ومناسبة للسياق.
3- التواصل بأسلوب بشري طبيعي: تكلّم بأسلوب عفوي وكأنك شخص حقيقي من نجد. استخدم تعبيرات محلية، نبرة ودّية، ولغة محادثة واضحة ومألوفة لأهل نجد.
4- احرص على أن تكون إجاباتك كاملة ومفصلة، ولا تختصر أو تتوقف قبل إتمام الفكرة، حتى لو كان السؤال قصير.
5- أدخل دائمًا كلمات نجدية أصيلة ومشهورة في كل رد، حتى لو لم يطلبها المستخدم، واجعلها متناسقة مع الجملة.
6- إذا كانت الإجابة قصة أو سالفة، اجعلها تحتوي على بداية، وسط، ونهاية واضحة، مع تعبيرات تحاكي أسلوب السوالف النجدي.
7- عند الشرح أو إعطاء أمثلة، استخدم أسلوب يخلط بين الطرافة والعفوية بدون فقدان وضوح المعنى.
8- حافظ على استمرارية النبرة النجدية في جميع الردود، وتجنب إدخال أي مفردة فصحى أو لهجة أخرى إلا إذا كانت جزء من شرح لمعناها النجدي.
9- لا تستخدم أي علامات توقف تدل على انقطاع النص أو نهاية غير مكتملة. إذا اضطررت للاختصار، أكمل حتى نهاية جملة كاملة.
10- اختم كل رد بالعلامة <END>، ولا تضع هذه العلامة إلا بعد إتمام الفكرة أو القصة.

"""

def _trim_to_last_sentence(text: str) -> str:
    """
    Trim the text to the last complete sentence.
    Avoids returning incomplete words if model cuts off.
    """
    match = re.search(r'(.+[\.\!\؟\!؟؛…])[^\.\!\؟\!؟؛…]*$', text, flags=re.S)
    return match.group(1).strip() if match else text.strip()

# ===== Persistent history helpers =====
def load_history() -> dict:
    """Load conversations JSON as a dict. Ensure a "default" list exists."""
    with _file_lock:
        try:
            with open(CONVERSATIONS_PATH, "r", encoding="utf-8") as f:
                data = json.load(f)
                if not isinstance(data, dict):
                    data = {"default": []}
        except FileNotFoundError:
            data = {"default": []}
            # Initialize file immediately
            try:
                with open(CONVERSATIONS_PATH, "w", encoding="utf-8") as f:
                    json.dump(data, f, ensure_ascii=False, indent=2)
            except Exception as e:
                logger.warning(f"Could not initialize conversations.json: {e}")
        except json.JSONDecodeError:
            logger.warning("conversations.json is corrupted; reinitializing.")
            data = {"default": []}
            try:
                with open(CONVERSATIONS_PATH, "w", encoding="utf-8") as f:
                    json.dump(data, f, ensure_ascii=False, indent=2)
            except Exception as e:
                logger.warning(f"Could not rewrite corrupted conversations.json: {e}")

        # Enforce schema
        if "default" not in data or not isinstance(data.get("default"), list):
            data["default"] = []
        return data


def save_history(history: dict) -> None:
    """Write the dictionary back to the JSON file safely."""
    with _file_lock:
        try:
            with open(CONVERSATIONS_PATH, "w", encoding="utf-8") as f:
                json.dump(history, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"Failed to save conversations.json: {e}")
            raise


def get_history() -> list:
    """Return the list of messages for the default conversation."""
    history = load_history()
    return history.get("default", [])


def remember_turn(user_msg: str, assistant_msg: str) -> None:
    """Append both user and assistant messages to the default conversation and persist."""
    with _file_lock:
        history = load_history()
        messages = history.setdefault("default", [])
        messages.append({"role": "user", "content": user_msg})
        messages.append({"role": "assistant", "content": assistant_msg})
        save_history(history)


def build_messages(user_msg: str) -> list:
    """Build the message list: system prompt + past history + current user message."""
    messages = [{"role": "system", "content": SAUDI_PROMPT}]
    past = get_history()
    # Only include valid past messages
    for m in past:
        if isinstance(m, dict) and "role" in m and "content" in m:
            messages.append({"role": m["role"], "content": m["content"]})
    messages.append({"role": "user", "content": user_msg})
    return messages

async def generate_response(message: str):
    """
    Generate a response using OpenAI's GPT-4.
    
    Args:
        message (str): The user's input message
        
    Returns:
        str: The generated text
    """
    try:
        # Prepare messages with persistent history (default conversation)
        messages = build_messages(message)

        # Generate text response
        response = client.chat.completions.create(
            model="gpt-4",
            messages=messages,
            temperature=0.7,
            max_tokens=400,
        )

        generated_text = response.choices[0].message.content
        # Remove the <END> marker from the final output before returning it
        # We keep <END> in the system prompt so the model knows when to stop,
        # but we strip it out here so it doesn't appear in the chat.
        if "<END>" in generated_text:
            generated_text = generated_text.split("<END>")[0].strip()
        
        # Ensure we return only complete sentences if the model cut off
        generated_text = _trim_to_last_sentence(generated_text)

        # Persist the turn (after stripping <END>)
        try:
            remember_turn(message, generated_text)
        except Exception as e:
            logger.error(f"Failed to remember turn: {e}")

        logger.info(f"Generated response text: {generated_text}")
        return generated_text

    except Exception as e:
        logger.error(f"Error generating response: {str(e)}")
        raise Exception(f"Error generating response: {str(e)}")
    