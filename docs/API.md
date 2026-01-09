# API Documentation

## Base URL
- Development: `http://localhost:8000`

## Endpoints

### 1. Root Endpoint

**GET** `/`

Returns API information and available endpoints.

**Response**
```json
{
  "message": "FaceBodyAI API is running",
  "endpoints": {
    "/api/frame": "POST - Analyze video frame for emotions and body language"
  }
}
```

### 2. Health Check

**GET** `/health`

Check API health and Azure OpenAI configuration status.

**Response**
```json
{
  "status": "healthy",
  "azure_openai_configured": true
}
```

### 3. Analyze Frame

**POST** `/api/frame`

Analyze a video frame (JPEG image) for emotions and body language using Azure OpenAI Vision API.

**Request**
- Method: `POST`
- Content-Type: `multipart/form-data`
- Body Parameters:
  - `file` (required): Image file (JPEG, PNG)

**cURL Example**
```bash
curl -X POST \
  http://localhost:8000/api/frame \
  -H 'Content-Type: multipart/form-data' \
  -F 'file=@/path/to/image.jpg'
```

**Success Response (200 OK)**
```json
{
  "emotion": "happy",
  "body_language": "relaxed",
  "details": "The person appears cheerful with an open, welcoming posture. Arms are relaxed at sides.",
  "confidence": "high"
}
```

**Fields:**
- `emotion` (string): Primary emotion detected (e.g., happy, sad, neutral, surprised, angry, fearful, disgusted)
- `body_language` (string): Body language description (e.g., relaxed, tense, open, closed, confident, nervous)
- `details` (string): Detailed description of the analysis
- `confidence` (string): Confidence level of the analysis (high, medium, low, N/A)

**Error Response (400 Bad Request)**
```json
{
  "detail": "File must be an image"
}
```

**Error Response (500 Internal Server Error)**
```json
{
  "detail": "Error analyzing frame: [error message]"
}
```

## Error Codes

| Status Code | Description |
|-------------|-------------|
| 200 | Success |
| 400 | Bad Request - Invalid input |
| 500 | Internal Server Error |

## Rate Limiting

Currently, there is no rate limiting implemented. In production, consider implementing rate limiting to prevent API abuse.

## Azure OpenAI Configuration

The API requires Azure OpenAI credentials to be configured via environment variables:

```bash
AZURE_OPENAI_ENDPOINT=https://your-resource-name.openai.azure.com/
AZURE_OPENAI_API_KEY=your-api-key-here
AZURE_OPENAI_DEPLOYMENT=gpt-4-vision
AZURE_OPENAI_API_VERSION=2024-02-15-preview
```

If not configured, the API will return mock responses for testing purposes.

## Interactive API Documentation

FastAPI automatically generates interactive API documentation:

- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`

## CORS Configuration

CORS is currently configured to allow all origins (`*`) for development purposes. In production, update the `allow_origins` parameter in `main.py` to specify exact allowed origins.

## Example Integration (JavaScript)

```javascript
async function analyzeFrame(imageBlob) {
  const formData = new FormData();
  formData.append('file', imageBlob, 'frame.jpg');
  
  const response = await fetch('http://localhost:8000/api/frame', {
    method: 'POST',
    body: formData
  });
  
  if (!response.ok) {
    throw new Error(`HTTP error! status: ${response.status}`);
  }
  
  const result = await response.json();
  console.log('Emotion:', result.emotion);
  console.log('Body Language:', result.body_language);
  console.log('Details:', result.details);
  console.log('Confidence:', result.confidence);
  
  return result;
}
```

## Example Integration (Python)

```python
import requests

def analyze_frame(image_path):
    url = 'http://localhost:8000/api/frame'
    
    with open(image_path, 'rb') as f:
        files = {'file': ('image.jpg', f, 'image/jpeg')}
        response = requests.post(url, files=files)
    
    if response.status_code == 200:
        result = response.json()
        print(f"Emotion: {result['emotion']}")
        print(f"Body Language: {result['body_language']}")
        print(f"Details: {result['details']}")
        print(f"Confidence: {result['confidence']}")
        return result
    else:
        print(f"Error: {response.status_code} - {response.text}")
        return None

# Usage
analyze_frame('/path/to/image.jpg')
```
