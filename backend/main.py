from fastapi import FastAPI, File, UploadFile, HTTPException, Form
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os
import base64
from openai import AzureOpenAI
from typing import Optional, Dict
import logging
from cv_features import CVFeatureExtractor

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

# Initialize CV Feature Extractor
cv_extractor = CVFeatureExtractor()

class AnalysisResponse(BaseModel):
    emotion: str
    body_language: str
    details: Optional[str] = None
    confidence: Optional[str] = None
    engagement: Optional[str] = None
    explanation: Optional[str] = None
    cv_features: Optional[Dict] = None

@app.get("/")
async def root():
    return {
        "message": "FaceBodyAI API is running",
        "endpoints": {
            "/api/frame": "POST - Analyze video frame for emotions and body language"
        }
    }

@app.post("/api/frame", response_model=AnalysisResponse)
async def analyze_frame(
    file: UploadFile = File(...),
    audio_speaking: Optional[str] = Form(None),
    audio_volume: Optional[str] = Form(None)
):
    """
    Analyze a video frame (JPEG image) for emotions and body language.
    Implements the "Slow Chain" with CV features + GPT-4o multimodal analysis.
    
    Args:
        file: JPEG image file from video capture
        audio_speaking: Optional "true"/"false" indicating if user is speaking
        audio_volume: Optional "low"/"medium"/"high" audio volume level
        
    Returns:
        JSON with emotion, engagement, confidence, and explanation
    """
    try:
        # Validate file type
        if not file.content_type or not file.content_type.startswith("image/"):
            raise HTTPException(status_code=400, detail="File must be an image")
        
        # Read image data
        image_data = await file.read()
        
        # Extract CV features
        logger.info("Extracting CV features...")
        cv_features = cv_extractor.extract_features(image_data)
        logger.info(f"CV features extracted: {cv_features}")
        
        # Check if Azure OpenAI client is configured
        if not client:
            logger.warning("Azure OpenAI not configured, returning mock response")
            return AnalysisResponse(
                emotion="neutral",
                body_language="relaxed",
                engagement="medium",
                confidence="medium",
                details="Azure OpenAI API not configured. Set AZURE_OPENAI_ENDPOINT and AZURE_OPENAI_API_KEY environment variables.",
                explanation="Mock response - Azure OpenAI not configured",
                cv_features=cv_features
            )
        
        # Encode image to base64
        base64_image = base64.b64encode(image_data).decode('utf-8')
        
        # Build audio context for prompt
        audio_context = ""
        if audio_speaking:
            is_speaking = audio_speaking.lower() == "true"
            audio_context = f"\n- Audio: User is {'speaking' if is_speaking else 'silent'}"
            if audio_volume and is_speaking:
                audio_context += f" (volume: {audio_volume})"
        
        # Create enhanced prompt with CV features
        prompt_text = f"""Analyze this person's behavioral state using the image and the following CV features:

CV Features (quantified measurements):
- Head pitch: {cv_features['head_pitch']}° (negative=looking down, positive=looking up)
- Head yaw: {cv_features['head_yaw']}° (negative=turned left, positive=turned right)
- Head roll: {cv_features['head_roll']}° (head tilt)
- Eye gaze: {cv_features['eye_gaze']} (on_screen/away/unknown)
- Motion level: {cv_features['motion_level']} (low/medium/high){audio_context}

Based on the image AND these CV features, provide a structured behavioral analysis:

1. **Emotion**: Primary emotional state (e.g., neutral, happy, nervous, focused, confused)
2. **Engagement**: Level of engagement (high/medium/low)
3. **Confidence**: Confidence level (high/medium/low)
4. **Explanation**: Brief explanation (1-2 sentences) of what the CV features + visual cues reveal about their behavioral state

Respond in JSON format with keys: emotion, engagement, confidence, explanation"""
        
        # Call Azure OpenAI Vision API
        response = client.chat.completions.create(
            model=AZURE_OPENAI_DEPLOYMENT,
            messages=[
                {
                    "role": "system",
                    "content": "You are an expert at multimodal behavioral analysis. You interpret computer vision features and visual cues to understand human emotional and engagement states. Your analysis is evidence-based and concise."
                },
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": prompt_text
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
            max_tokens=400,
            temperature=0.3
        )
        
        # Parse the response
        analysis_text = response.choices[0].message.content
        logger.info(f"Azure OpenAI response: {analysis_text}")
        
        # Try to parse as JSON
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
                    body_language=cv_features['motion_level'],  # Use motion as body language indicator
                    engagement=analysis_json.get("engagement", "medium"),
                    confidence=analysis_json.get("confidence", "medium"),
                    explanation=analysis_json.get("explanation", ""),
                    details=analysis_text,
                    cv_features=cv_features
                )
        except json.JSONDecodeError:
            pass
        
        # Fallback: parse text response
        lines = analysis_text.lower().split('\n')
        emotion = "neutral"
        engagement = "medium"
        confidence_level = "medium"
        
        for line in lines:
            if 'emotion' in line and ':' in line:
                words = line.split(':')
                if len(words) > 1:
                    emotion = words[1].strip().split(',')[0].strip()
            elif 'engagement' in line and ':' in line:
                words = line.split(':')
                if len(words) > 1:
                    engagement = words[1].strip().split(',')[0].strip()
            elif 'confidence' in line and ':' in line:
                words = line.split(':')
                if len(words) > 1:
                    confidence_level = words[1].strip().split(',')[0].strip()
        
        return AnalysisResponse(
            emotion=emotion,
            body_language=cv_features['motion_level'],
            engagement=engagement,
            confidence=confidence_level,
            explanation=analysis_text,
            details=analysis_text,
            cv_features=cv_features
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
