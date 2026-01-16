import base64
import json
import logging
import os
from typing import Optional

from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from openai import AzureOpenAI
from pydantic import BaseModel

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
AZURE_OPENAI_AUDIO_DEPLOYMENT = os.getenv("AZURE_OPENAI_AUDIO_DEPLOYMENT", "gpt-4o-audio-preview")

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

class AudioAnalysisResponse(BaseModel):
    emotional_state: str
    tone: str
    confidence: str
    reasoning: str
    notable_vocal_cues: str
    original_voice: Optional[str] = None

@app.get("/")
async def root():
    return {
        "message": "FaceBodyAI API is running",
        "endpoints": {
            "/api/frame": "POST - Analyze video frame for emotions and body language",
            "/api/audio": "POST - Analyze audio for emotional state, tone, confidence, and vocal cues"
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

@app.post("/api/audio", response_model=AudioAnalysisResponse)
async def analyze_audio(file: UploadFile = File(...)):
    """
    Analyze an audio file for emotional state, tone, confidence, and vocal cues.
    
    Args:
        file: Audio file (webm, mp3, wav, etc.)
        
    Returns:
        JSON with emotional_state, tone, confidence, reasoning, notable_vocal_cues, and original_voice analysis
    """
    try:
        # Validate file type
        if not file.content_type or not file.content_type.startswith("audio/"):
            raise HTTPException(status_code=400, detail="File must be an audio file")
        
        # Read audio data
        audio_data = await file.read()
        
        # Check if Azure OpenAI client is configured
        if not client:
            logger.warning("Azure OpenAI not configured, returning mock response")
            return AudioAnalysisResponse(
                emotional_state="neutral",
                tone="calm",
                confidence="medium",
                reasoning="Azure OpenAI API not configured. Set AZURE_OPENAI_ENDPOINT and AZURE_OPENAI_API_KEY environment variables.",
                notable_vocal_cues="N/A",
                original_voice="N/A"
            )
        
        # Encode audio to base64
        base64_audio = base64.b64encode(audio_data).decode('utf-8')
        
        # Determine audio format from content type using dictionary mapping
        audio_format_mapping = {
            "webm": "webm",
            "mp3": "mp3",
            "wav": "wav",
            "ogg": "ogg",
            "mp4": "mp4"
        }
        
        # Default to wav if no match found
        audio_format = "wav"
        for format_key, format_value in audio_format_mapping.items():
            if format_key in file.content_type.lower():
                audio_format = format_value
                break
        
        logger.info(f"Detected audio format: {audio_format} from content type: {file.content_type}")
        
        # Call Azure OpenAI Audio API
        response = client.chat.completions.create(
            model=AZURE_OPENAI_AUDIO_DEPLOYMENT,
            modalities=["text"],
            messages=[
                {
                    "role": "system",
                    "content": "You are an expert at analyzing human voice and speech patterns. Provide detailed, accurate analysis of emotional state, tone, confidence level, and notable vocal characteristics."
                },
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": """Analyze this audio recording and provide:
1. emotional_state: The primary emotional state conveyed (e.g., happy, sad, neutral, anxious, excited, calm, stressed)
2. tone: The tone of voice (e.g., warm, cold, professional, casual, assertive, hesitant)
3. confidence: Level of confidence in speech (high/medium/low)
4. reasoning: Brief explanation of your analysis
5. notable_vocal_cues: Any notable vocal characteristics (e.g., pitch variations, speech rate, pauses, vocal tremors, clarity)
6. original_voice: Description of the voice characteristics (e.g., deep, high-pitched, soft, loud)

Respond in JSON format with these exact keys: emotional_state, tone, confidence, reasoning, notable_vocal_cues, original_voice"""
                        },
                        {
                            "type": "input_audio",
                            "input_audio": {
                                "data": base64_audio,
                                "format": audio_format
                            }
                        }
                    ]
                }
            ],
            max_tokens=500,
            temperature=0.3
        )
        
        # Parse the response
        analysis_text = response.choices[0].message.content
        logger.info(f"Azure OpenAI audio response: {analysis_text}")
        
        # Try to parse as JSON
        try:
            # Try to extract JSON from response
            start_idx = analysis_text.find('{')
            end_idx = analysis_text.rfind('}') + 1
            if start_idx != -1 and end_idx > start_idx:
                json_str = analysis_text[start_idx:end_idx]
                analysis_json = json.loads(json_str)
                return AudioAnalysisResponse(
                    emotional_state=analysis_json.get("emotional_state", "unknown"),
                    tone=analysis_json.get("tone", "unknown"),
                    confidence=analysis_json.get("confidence", "medium"),
                    reasoning=analysis_json.get("reasoning", ""),
                    notable_vocal_cues=analysis_json.get("notable_vocal_cues", ""),
                    original_voice=analysis_json.get("original_voice", "")
                )
        except json.JSONDecodeError:
            pass
        
        # Fallback: return text as reasoning
        return AudioAnalysisResponse(
            emotional_state="unknown",
            tone="unknown",
            confidence="medium",
            reasoning=analysis_text,
            notable_vocal_cues="Unable to parse structured response",
            original_voice=""
        )
        
    except Exception as e:
        logger.error(f"Error analyzing audio: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error analyzing audio: {str(e)}")

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
