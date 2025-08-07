from fastapi import FastAPI, HTTPException, Request, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from server import generate_response, process_voice_message
import logging
import os
from dotenv import load_dotenv

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load .env file if present (for local dev)
try:
    load_dotenv()
    logger.info("✅ Loaded environment variables from .env file")
except Exception as e:
    logger.warning(f"⚠️ Could not load .env file: {e}")

# Initialize FastAPI
app = FastAPI(
    title="Nexsta Khaleeji Voice API",
    description="API لمساعد ذكي يتحدث باللهجة الخليجية ويدعم الإدخال النصي والصوتي.",
    version="1.0.0",
)

# Allow frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ✅ Log health check requests
@app.middleware("http")
async def log_health_requests(request: Request, call_next):
    if request.url.path in ["/ping", "/health"]:
        logger.info(f"[HealthCheck] {request.method} {request.url.path}")
    response = await call_next(request)
    return response

# ✅ Root route
@app.get("/")
async def root():
    logger.info("✅ / root endpoint was called.")
    return {
        "message": "🚀 Nexsta Khaleeji Voice API is up and running!",
        "version": "1.0.0",
        "endpoints": {
            "/chat": "للمحادثة النصية",
            "/voice": "لمعالجة المدخلات الصوتية",
            "/health": "للتحقق من حالة الخدمة",
            "/ping": "فحص سريع للتأكد من التشغيل"
        }
    }

# ✅ Lightweight /ping route
@app.get("/ping")
async def ping():
    logger.info("✅ /ping endpoint was called.")
    return {"status": "pong"}

# ✅ Simplified /health route (no DB)
@app.get("/health")
async def health_check():
    logger.info("✅ /health endpoint was called.")
    return {
        "status": "healthy",
        "note": "No DB check required"
    }

# 📨 Text chat endpoint
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

# 🎙️ Voice input endpoint
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

# ✅ Entry point with 5-second delay for Railway
if __name__ == "__main__":
    import uvicorn
    import time

    logger.info("🚀 Starting app from __main__")
    logger.info("⏳ Waiting 5 seconds before starting to ensure readiness...")
    time.sleep(5)

    port = int(os.getenv("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port)
