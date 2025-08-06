from fastapi import FastAPI, HTTPException, Request, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from server import generate_response, process_voice_message
import logging
import os
from dotenv import load_dotenv

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Try to load environment variables from .env file
try:
    load_dotenv()
    logger.info("Loaded environment variables from .env file")
except Exception as e:
    logger.warning(f"Could not load .env file: {e}. Assuming environment variables are set.")

app = FastAPI(
    title="Nexsta Khaleeji Voice API",
    description="API لمساعد ذكي يتحدث باللهجة الخليجية ويدعم الإدخال النصي والصوتي.",
    version="1.0.0",
)

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

@app.get("/")
async def root():
    """
    الصفحة الرئيسية للـ API
    """
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
    return {"status": "ok"}

@app.post("/chat")
async def chat_endpoint(request: Request):
    """
    معالجة المدخلات النصية وإنشاء رد نصي وصوتي
    """
    try:
        data = await request.json()
        message = data.get("message")
        if not message:
            raise HTTPException(status_code=400, detail="الرجاء إدخال نص الرسالة")
        
        response = await generate_response(message)
        return response
    except Exception as e:
        logger.error(f"Error in chat endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/voice")
async def handle_voice(file: UploadFile = File(...)):
    """
    معالجة المدخلات الصوتية وإنشاء رد نصي وصوتي
    """
    try:
        # Save uploaded file temporarily
        temp_path = "temp_voice.wav"
        with open(temp_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)
        
        # Process voice message
        result = await process_voice_message(temp_path)
        
        # Clean up
        if os.path.exists(temp_path):
            os.remove(temp_path)
            
        return result
    except Exception as e:
        logger.error(f"Error in voice endpoint: {str(e)}")
        if os.path.exists("temp_voice.wav"):
            os.remove("temp_voice.wav")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=False)