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
            max_tokens=400,
        )

        generated_text = response.choices[0].message.content
        logger.info(f"Generated response text: {generated_text}")
        return generated_text

    except Exception as e:
        logger.error(f"Error generating response: {str(e)}")
        raise Exception(f"Error generating response: {str(e)}")
    