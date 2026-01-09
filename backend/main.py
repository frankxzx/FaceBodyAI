from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os
import base64
from openai import AzureOpenAI
from typing import Optional
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="FaceBodyAI API", version="1.0.0")

# Configure CORS to allow requests from frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Azure OpenAI configuration
AZURE_OPENAI_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT", "")
AZURE_OPENAI_API_KEY = os.getenv("AZURE_OPENAI_API_KEY", "")
AZURE_OPENAI_DEPLOYMENT = os.getenv("AZURE_OPENAI_DEPLOYMENT", "gpt-4-vision")
AZURE_OPENAI_API_VERSION = os.getenv("AZURE_OPENAI_API_VERSION", "2024-02-15-preview")

# Initialize Azure OpenAI client
client = None
if AZURE_OPENAI_ENDPOINT and AZURE_OPENAI_API_KEY:
    client = AzureOpenAI(
        azure_endpoint=AZURE_OPENAI_ENDPOINT,
        api_key=AZURE_OPENAI_API_KEY,
        api_version=AZURE_OPENAI_API_VERSION
    )

class AnalysisResponse(BaseModel):
    emotion: str
    body_language: str
    details: Optional[str] = None
    confidence: Optional[str] = None

@app.get("/")
async def root():
    return {
        "message": "FaceBodyAI API is running",
        "endpoints": {
            "/api/frame": "POST - Analyze video frame for emotions and body language"
        }
    }

@app.post("/api/frame", response_model=AnalysisResponse)
async def analyze_frame(file: UploadFile = File(...)):
    """
    Analyze a video frame (JPEG image) for emotions and body language.
    
    Args:
        file: JPEG image file from video capture
        
    Returns:
        JSON with emotion and body_language analysis
    """
    try:
        # Validate file type
        if not file.content_type or not file.content_type.startswith("image/"):
            raise HTTPException(status_code=400, detail="File must be an image")
        
        # Read image data
        image_data = await file.read()
        
        # Check if Azure OpenAI client is configured
        if not client:
            logger.warning("Azure OpenAI not configured, returning mock response")
            return AnalysisResponse(
                emotion="neutral",
                body_language="relaxed",
                details="Azure OpenAI API not configured. Set AZURE_OPENAI_ENDPOINT and AZURE_OPENAI_API_KEY environment variables.",
                confidence="N/A"
            )
        
        # Encode image to base64
        base64_image = base64.b64encode(image_data).decode('utf-8')
        
        # Call Azure OpenAI Vision API
        response = client.chat.completions.create(
            model=AZURE_OPENAI_DEPLOYMENT,
            messages=[
                {
                    "role": "system",
                    "content": "You are an expert at analyzing human emotions and body language from images. Provide concise, accurate analysis."
                },
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": """Analyze this image and provide:
1. The primary emotion displayed (e.g., happy, sad, neutral, surprised, angry, fearful, disgusted)
2. Body language description (e.g., relaxed, tense, open, closed, confident, nervous)

Respond in JSON format with keys: emotion, body_language, details (brief description), confidence (high/medium/low)"""
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{base64_image}"
                            }
                        }
                    ]
                }
            ],
            max_tokens=300,
            temperature=0.3
        )
        
        # Parse the response
        analysis_text = response.choices[0].message.content
        logger.info(f"Azure OpenAI response: {analysis_text}")
        
        # Try to parse as JSON, fallback to text parsing
        import json
        try:
            # Try to extract JSON from response
            start_idx = analysis_text.find('{')
            end_idx = analysis_text.rfind('}') + 1
            if start_idx != -1 and end_idx > start_idx:
                json_str = analysis_text[start_idx:end_idx]
                analysis_json = json.loads(json_str)
                return AnalysisResponse(
                    emotion=analysis_json.get("emotion", "unknown"),
                    body_language=analysis_json.get("body_language", "unknown"),
                    details=analysis_json.get("details", ""),
                    confidence=analysis_json.get("confidence", "medium")
                )
        except json.JSONDecodeError:
            pass
        
        # Fallback: parse text response
        lines = analysis_text.lower().split('\n')
        emotion = "neutral"
        body_language = "relaxed"
        
        for line in lines:
            if 'emotion' in line:
                words = line.split(':')
                if len(words) > 1:
                    emotion = words[1].strip().split(',')[0].strip()
            elif 'body language' in line or 'body_language' in line:
                words = line.split(':')
                if len(words) > 1:
                    body_language = words[1].strip().split(',')[0].strip()
        
        return AnalysisResponse(
            emotion=emotion,
            body_language=body_language,
            details=analysis_text,
            confidence="medium"
        )
        
    except Exception as e:
        logger.error(f"Error analyzing frame: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error analyzing frame: {str(e)}")

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "azure_openai_configured": client is not None
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
