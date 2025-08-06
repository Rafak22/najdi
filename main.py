from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from server import generate_response, process_voice_message
import logging
import os
import aiofiles

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="نكستا الخليجي API",
    description="واجهة برمجة التطبيقات للمساعد الذكي باللهجة الخليجية",
    version="1.0.0"
)

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ChatRequest(BaseModel):
    message: str

@app.post("/chat")
async def chat_endpoint(request: ChatRequest):
    try:
        # Call the generate_response function from server.py
        response = await generate_response(request.message)
        return response
    except Exception as e:
        logger.error(f"Error in chat endpoint: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="عذراً، صار خطأ في النظام. جرب مرة ثانية بعد شوي ✨"
        )

@app.post("/voice")
async def handle_voice(file: UploadFile = File(...)):
    try:
        # Create temp directory if it doesn't exist
        os.makedirs("temp", exist_ok=True)
        temp_path = os.path.join("temp", "temp_audio.wav")
        
        # Save uploaded file
        async with aiofiles.open(temp_path, 'wb') as out_file:
            content = await file.read()
            await out_file.write(content)
        
        # Process voice message
        result = await process_voice_message(temp_path)
        
        return {
            "transcript": result["transcript"],
            "reply_text": result["reply_text"],
            "reply_audio": result["reply_audio"]
        }
        
    except Exception as e:
        logger.error(f"Error processing voice: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="عذراً، صار خطأ في معالجة الملف الصوتي"
        )
    finally:
        # Clean up temp file
        if os.path.exists(temp_path):
            os.remove(temp_path)

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "message": "نكستا الخليجي جاهز لخدمتك 💚",
        "environment": {
            "OPENAI_API_KEY": "✓ موجود" if os.environ.get("OPENAI_API_KEY") else "✗ غير موجود"
        }
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)