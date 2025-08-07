from fastapi import FastAPI, HTTPException, Request, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from server import generate_response, process_voice_message
import logging
import os
from dotenv import load_dotenv

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load .env variables (optional for Railway, useful locally)
try:
    load_dotenv()
    logger.info("✅ Loaded environment variables from .env file")
except Exception as e:
    logger.warning(f"⚠️ Could not load .env file: {e}. Assuming Railway env vars are used.")

# Initialize FastAPI
app = FastAPI(
    title="Nexsta Khaleeji Voice API",
    description="API لمساعد ذكي يتحدث باللهجة الخليجية ويدعم الإدخال النصي والصوتي.",
    version="1.0.0",
)

# Allow all origins (for frontend use)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routes

@app.get("/")
async def root():
    return {
        "message": "مرحباً بك في Nexsta Khaleeji Voice API",
        "version": "1.0.0",
        "endpoints": {
            "/chat": "للمحادثة النصية",
            "/voice": "لمعالجة المدخلات الصوتية",
            "/health": "للتحقق من حالة الخدمة"
        }
    }

@app.get("/health")
def health_check():
    logger.info("✅ /health endpoint was called.")
    return {"status": "ok"}

@app.post("/chat")
async def chat_endpoint(request: Request):
    try:
        data = await request.json()
        message = data.get("message")
        if not message:
            raise HTTPException(status_code=400, detail="الرجاء إدخال نص الرسالة")
        
        logger.info(f"📩 Received text message: {message}")
        response = await generate_response(message)
        return response
    except Exception as e:
        logger.error(f"❌ Error in /chat: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/voice")
async def handle_voice(file: UploadFile = File(...)):
    try:
        temp_path = "temp_voice.wav"
        with open(temp_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)

        logger.info(f"🎙️ Received voice file: {file.filename}")
        result = await process_voice_message(temp_path)

        os.remove(temp_path)
        return result

    except Exception as e:
        logger.error(f"❌ Error in /voice: {str(e)}")
        if os.path.exists("temp_voice.wav"):
            os.remove("temp_voice.wav")
        raise HTTPException(status_code=500, detail=str(e))

# ENTRYPOINT
if __name__ == "__main__":
    import uvicorn
    logger.info("🚀 Starting app from __main__")
    port = int(os.getenv("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port)
