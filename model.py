import torch
from unsloth import FastLanguageModel
from transformers import TextStreamer


model, tokenizer = FastLanguageModel.from_pretrained(
    model_name = "AhmedEladl/Najdi-Llama3.1-8B-Instruct",
    max_seq_length = 4096,
    dtype = None, # Autodetects from the model's config
    load_in_4bit = True, # Or False if you want to load in 16-bit
)

user_query = "السلام عليكم كيف حالك؟"

saudi_prompt = """
أنت نيكستا السعودي، مساعد ذكي يتحدث حصريًا باللهجة النجدية. جميع إجاباتك، بدون استثناء، يجب أن تكون باللهجة النجدية فقط، سواء تم طلب لهجة معينة أو لم تُذكر لهجة في السؤال.

مهامك الأساسية:

1- الإجابة على الأسئلة والمحادثات: أجب دومًا باللهجة النجدية. لا تستخدم أي لهجة أخرى حتى لو طُلب منك ذلك. ركّز على الدقة في المعلومات مع الحفاظ على الأسلوب النجدي.

2- استخدام السياق بشكل كامل: إذا تم إعطاؤك سياق أو خلفية، استخدمها بذكاء في صياغة إجابة نجدية مفهومة، دقيقة، ومناسبة للسياق.

3- التواصل بأسلوب بشري طبيعي: تكلّم بأسلوب عفوي وكأنك شخص حقيقي من نجد. استخدم تعبيرات محلية، نبرة ودّية، ولغة محادثة واضحة ومألوفة لأهل نجد.

تذكير: لا تستخدم اللغة الفصحى أو أي لهجات عربية أخرى. اللهجة النجدية فقط في كل مخرجاتك.
"""

messages = [
    {"role": "system", "content": saudi_prompt},
    {"role": "user", "content": "وين نجد"},
]

# The device can be 'cuda' or 'cpu'
device = "cuda" if torch.cuda.is_available() else "cpu"
inputs = tokenizer.apply_chat_template(
    messages, tokenize = True, add_generation_prompt = True, return_tensors = "pt",
).to(device)

text_streamer = TextStreamer(tokenizer, skip_prompt = True)
_ = model.generate(
    input_ids = inputs,
    streamer = text_streamer,
    max_new_tokens = 128,
    use_cache = True,
    pad_token_id=tokenizer.eos_token_id,
    eos_token_id=tokenizer.eos_token_id,
    do_sample=True,
    temperature=0.3,
    top_p=0.85,
    no_repeat_ngram_size=3,
)
