from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from server import generate_response
from dotenv import load_dotenv
import logging
import os

# Load environment variables
load_dotenv()

# Verify OpenAI API key is present
if not os.getenv("OPENAI_API_KEY"):
    raise ValueError("OPENAI_API_KEY not found in environment variables. Please check your .env file.")

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

@app.get("/health")
async def health_check():
    return {"status": "healthy", "message": "نكستا الخليجي جاهز لخدمتك 💚"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)