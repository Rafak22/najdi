from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from server import generate_response
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
        logger.info(f"Received voice file: {file.filename}")
        
        # Create temp directory if it doesn't exist
        os.makedirs("temp", exist_ok=True)
        
        # Save the uploaded file
        temp_path = os.path.join("temp", "temp_audio.wav")
        async with aiofiles.open(temp_path, 'wb') as out_file:
            content = await file.read()
            await out_file.write(content)
        
        logger.info(f"Saved voice file to: {temp_path}")
        
        # TODO: Process voice with Whisper or speech-to-text model
        # For now, return placeholder response
        return {
            "status": "success",
            "message": "تم استلام الملف الصوتي بنجاح",
            "text": "Voice processing not implemented yet."
        }
        
    except Exception as e:
        logger.error(f"Error processing voice file: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="عذراً، صار خطأ في معالجة الملف الصوتي"
        )
    finally:
        # Clean up temp file if it exists
        if os.path.exists("temp/temp_audio.wav"):
            try:
                os.remove("temp/temp_audio.wav")
                logger.info("Cleaned up temporary audio file")
            except Exception as e:
                logger.warning(f"Could not clean up temp file: {str(e)}")

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