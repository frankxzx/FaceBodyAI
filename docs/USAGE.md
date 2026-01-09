# Usage Examples

## Basic Usage

### 1. Starting the Application

**Terminal 1 - Backend:**
```bash
cd backend
source venv/bin/activate
python main.py
```

**Terminal 2 - Frontend:**
```bash
cd frontend
npm run dev
```

### 2. Using the Web Interface

1. Open browser to `http://localhost:5173`
2. Click "Start Camera" - browser will request camera permission
3. Grant camera access
4. Position yourself in front of the camera
5. Click "Start Analysis"
6. Analysis results will update every 5 seconds

### 3. Understanding the Results

The system analyzes each frame and returns:

**Emotion Categories:**
- happy
- sad
- neutral
- surprised
- angry
- fearful
- disgusted

**Body Language Descriptions:**
- relaxed
- tense
- open
- closed
- confident
- nervous
- engaged
- withdrawn

## Advanced Usage

### Custom Analysis Interval

To change the capture interval from 5 seconds to another value, edit `frontend/src/App.vue`:

```javascript
// Change 5000 to your desired interval in milliseconds
captureInterval = setInterval(() => {
  analyzeFrame()
}, 5000)  // Change this value
```

### API Integration

#### Using cURL

```bash
# Test with an image file
curl -X POST http://localhost:8000/api/frame \
  -H "Content-Type: multipart/form-data" \
  -F "file=@/path/to/image.jpg"
```

#### Using Python

```python
import requests
import time

def analyze_webcam_frames():
    """Continuously capture and analyze webcam frames"""
    import cv2
    
    cap = cv2.VideoCapture(0)
    
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        
        # Encode frame as JPEG
        _, buffer = cv2.imencode('.jpg', frame)
        
        # Send to API
        files = {'file': ('frame.jpg', buffer.tobytes(), 'image/jpeg')}
        response = requests.post('http://localhost:8000/api/frame', files=files)
        
        if response.status_code == 200:
            result = response.json()
            print(f"Emotion: {result['emotion']}, Body Language: {result['body_language']}")
        
        # Wait 5 seconds
        time.sleep(5)
    
    cap.release()

# Run
analyze_webcam_frames()
```

#### Using JavaScript (Browser)

```javascript
// Capture from video element
async function captureAndAnalyze(videoElement) {
  const canvas = document.createElement('canvas');
  canvas.width = videoElement.videoWidth;
  canvas.height = videoElement.videoHeight;
  
  const ctx = canvas.getContext('2d');
  ctx.drawImage(videoElement, 0, 0);
  
  // Convert to blob
  const blob = await new Promise(resolve => 
    canvas.toBlob(resolve, 'image/jpeg', 0.8)
  );
  
  // Send to API
  const formData = new FormData();
  formData.append('file', blob, 'frame.jpg');
  
  const response = await fetch('http://localhost:8000/api/frame', {
    method: 'POST',
    body: formData
  });
  
  const result = await response.json();
  console.log(result);
  
  return result;
}

// Set up periodic capture
const video = document.querySelector('video');
setInterval(() => captureAndAnalyze(video), 5000);
```

### Batch Processing

Process multiple images at once:

```python
import requests
import os
from concurrent.futures import ThreadPoolExecutor

def analyze_image(image_path):
    with open(image_path, 'rb') as f:
        files = {'file': (os.path.basename(image_path), f, 'image/jpeg')}
        response = requests.post('http://localhost:8000/api/frame', files=files)
        return response.json()

# Process all images in a directory
image_dir = '/path/to/images'
image_files = [os.path.join(image_dir, f) for f in os.listdir(image_dir) 
               if f.endswith(('.jpg', '.jpeg', '.png'))]

# Process in parallel
with ThreadPoolExecutor(max_workers=4) as executor:
    results = list(executor.map(analyze_image, image_files))

for img, result in zip(image_files, results):
    print(f"{img}: {result['emotion']} / {result['body_language']}")
```

## Use Cases

### 1. Mental Health Monitoring

Monitor emotional states over time for mental health insights:

```python
import requests
import json
from datetime import datetime

def log_emotion(result):
    """Log emotion data with timestamp"""
    log_entry = {
        'timestamp': datetime.now().isoformat(),
        'emotion': result['emotion'],
        'body_language': result['body_language'],
        'confidence': result['confidence']
    }
    
    with open('emotion_log.json', 'a') as f:
        f.write(json.dumps(log_entry) + '\n')
```

### 2. Video Conferencing Enhancement

Analyze participant engagement during video calls:

```javascript
class MeetingAnalyzer {
  constructor(videoElement) {
    this.video = videoElement;
    this.emotions = [];
  }
  
  async analyze() {
    const result = await captureAndAnalyze(this.video);
    this.emotions.push({
      timestamp: Date.now(),
      ...result
    });
    return result;
  }
  
  getEngagementScore() {
    // Calculate based on positive emotions and open body language
    const positive = ['happy', 'confident', 'engaged'];
    const engaged = this.emotions.filter(e => 
      positive.includes(e.emotion) || positive.includes(e.body_language)
    );
    return (engaged.length / this.emotions.length) * 100;
  }
}
```

### 3. Customer Service Training

Analyze customer service representative interactions:

```python
def analyze_service_interaction(video_path):
    """Analyze a recorded customer service interaction"""
    import cv2
    
    cap = cv2.VideoCapture(video_path)
    fps = cap.get(cv2.CAP_PROP_FPS)
    frame_interval = int(fps * 5)  # Every 5 seconds
    
    results = []
    frame_count = 0
    
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        
        if frame_count % frame_interval == 0:
            _, buffer = cv2.imencode('.jpg', frame)
            files = {'file': ('frame.jpg', buffer.tobytes(), 'image/jpeg')}
            
            response = requests.post('http://localhost:8000/api/frame', files=files)
            if response.status_code == 200:
                result = response.json()
                results.append({
                    'time': frame_count / fps,
                    **result
                })
        
        frame_count += 1
    
    cap.release()
    return results
```

## Customization

### Modify Analysis Prompt

Edit `backend/main.py` to customize the Azure OpenAI analysis prompt:

```python
# In the analyze_frame function
response = client.chat.completions.create(
    model=AZURE_OPENAI_DEPLOYMENT,
    messages=[
        {
            "role": "system",
            "content": "Your custom system prompt here"
        },
        # ... rest of the configuration
    ]
)
```

### Custom UI Themes

Edit `frontend/src/style.css` to change the appearance:

```css
/* Change gradient colors */
body {
  background: linear-gradient(135deg, #your-color-1 0%, #your-color-2 100%);
}

/* Change button colors */
button {
  background: #your-button-color;
}
```

### Add Data Export

Save analysis results to a file:

```javascript
// Add to App.vue
const exportResults = () => {
  const data = JSON.stringify(allResults, null, 2);
  const blob = new Blob([data], { type: 'application/json' });
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = 'analysis-results.json';
  a.click();
}
```

## Performance Tips

1. **Reduce Analysis Frequency**: Increase the interval to reduce API calls
2. **Lower Image Quality**: Reduce JPEG quality in the `toBlob` call
3. **Resize Images**: Scale down video frames before sending
4. **Batch Processing**: Queue frames and send in batches
5. **Cache Results**: Store recent analysis to avoid redundant API calls

## Troubleshooting

### High API Costs

- Increase the capture interval (e.g., 10 or 15 seconds)
- Implement smart capture (only when motion detected)
- Use local preprocessing to filter out similar frames

### Slow Performance

- Check network latency to Azure OpenAI
- Reduce image resolution
- Enable HTTP/2 for faster requests
- Consider edge caching for common patterns

### Inaccurate Results

- Ensure good lighting conditions
- Position camera at eye level
- Avoid extreme angles or distances
- Test with various backgrounds
- Consider fine-tuning the analysis prompt
