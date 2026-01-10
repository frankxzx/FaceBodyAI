# FaceBodyAI

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Node 18+](https://img.shields.io/badge/node-18+-green.svg)](https://nodejs.org/)
[![Vue 3](https://img.shields.io/badge/vue-3-brightgreen.svg)](https://vuejs.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.109-009688.svg)](https://fastapi.tiangolo.com/)

**Near real-time multimodal behavioral analysis using Fast Chain + Slow Chain architecture.**

Analyzes human behavior (emotions, engagement, body language) with computer vision features and Azure OpenAI GPT-4o.

## 🎯 Features

### Fast Chain (~100ms) - Instant Feedback
- **Motion Detection**: Real-time frame difference analysis
- **Audio Detection**: Voice activity detection (VAD) and volume monitoring
- **Visual Indicators**: Activity lights, motion levels, speaking status
- **Pure Frontend**: No network latency, works offline

### Slow Chain (~3-5 seconds) - AI Insights
- **CV Feature Extraction**: Head pose (pitch/yaw/roll), eye gaze, motion level using MediaPipe
- **Multimodal AI Analysis**: GPT-4o interprets CV features + visual cues + audio context
- **Behavioral Insights**: Emotion, engagement level, confidence, and explanations
- **Quantified & Stable**: CV features provide reliable data for AI interpretation

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    FAST CHAIN (Frontend, ~100ms)                 │
│  Motion Detection + Audio Detection → Visual Indicators          │
└─────────────────────────────────────────────────────────────────┘
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                   SLOW CHAIN (Backend, ~3-5s)                    │
│  Image → CV Features (MediaPipe) → GPT-4o → Behavioral Analysis  │
└─────────────────────────────────────────────────────────────────┘
```

**See [Multimodal Architecture Documentation](docs/MULTIMODAL_ARCHITECTURE.md) for detailed design.**

## 📋 Prerequisites

- **Node.js** 18+ and npm
- **Python** 3.8+
- **Azure OpenAI** account with GPT-4 Vision deployment
- Modern web browser with camera and microphone access

## 🚀 Quick Start

**New to the project?** Check out our [Quick Start Guide](docs/QUICKSTART.md) for step-by-step instructions!

## 🚀 Setup Instructions

### Backend Setup (FastAPI)

1. Navigate to the backend directory:
   ```bash
   cd backend
   ```

2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Configure Azure OpenAI credentials:
   ```bash
   cp .env.example .env
   ```
   
   Edit `.env` and add your Azure OpenAI credentials:
   ```
   AZURE_OPENAI_ENDPOINT=https://your-resource-name.openai.azure.com/
   AZURE_OPENAI_API_KEY=your-api-key-here
   AZURE_OPENAI_DEPLOYMENT=gpt-4-vision
   AZURE_OPENAI_API_VERSION=2024-02-15-preview
   ```

5. Run the backend server:
   ```bash
   python main.py
   ```
   
   The API will be available at `http://localhost:8000`
   - API docs: `http://localhost:8000/docs`
   - Health check: `http://localhost:8000/health`

### Frontend Setup (Vue)

1. Navigate to the frontend directory:
   ```bash
   cd frontend
   ```

2. Install dependencies:
   ```bash
   npm install
   ```

3. Run the development server:
   ```bash
   npm run dev
   ```
   
   The app will be available at `http://localhost:5173`

## 📖 Usage

1. **Start both servers** (backend on port 8000, frontend on port 5173)

2. **Open the frontend** in your browser at `http://localhost:5173`

3. **Click "Start Camera"** to grant camera and microphone access

4. **Watch the Fast Chain indicators** - See real-time activity, motion, and speaking status

5. **Click "Start Analysis"** to begin slow chain behavioral analysis

6. **View results** - The app will:
   - **Fast Chain**: Update activity indicators every ~100ms (motion, audio)
   - **Slow Chain**: Analyze frame + CV features every 4 seconds with GPT-4o
   - Display emotion, engagement, confidence, and behavioral explanation
   - Show extracted CV features (head pose, eye gaze, motion)

## 🔧 API Endpoints

### `POST /api/frame`

Analyze a video frame for behavioral insights (Slow Chain endpoint).

**Request:**
- Method: `POST`
- Content-Type: `multipart/form-data`
- Body: 
  - `file`: Image file (JPEG)
  - `audio_speaking`: "true" or "false" (optional)
  - `audio_volume`: "low", "medium", or "high" (optional)

**Response:**
```json
{
  "emotion": "focused",
  "engagement": "high",
  "confidence": "medium",
  "explanation": "Person maintains forward gaze with slight head tilt, indicating active listening.",
  "cv_features": {
    "head_pitch": -8,
    "head_yaw": 2,
    "head_roll": -3,
    "eye_gaze": "on_screen",
    "motion_level": "medium"
  }
}
```

### `GET /health`

Check API health and Azure OpenAI configuration status.

**Response:**
```json
{
  "status": "healthy",
  "azure_openai_configured": true
}
```

## 🛠️ Development

### Backend Development

The backend uses:
- **FastAPI**: Modern, fast web framework for building APIs
- **MediaPipe**: Computer vision for facial landmark detection
- **OpenCV**: Image processing for motion detection
- **OpenAI Python SDK**: For Azure OpenAI integration
- **Uvicorn**: ASGI server for running FastAPI

To run in development mode with auto-reload:
```bash
cd backend
uvicorn main:app --reload --port 8000
```

### Frontend Development

The frontend uses:
- **Vue 3**: Progressive JavaScript framework with Composition API
- **Web Audio API**: For real-time audio analysis (fast chain)
- **Canvas API**: For frame difference motion detection (fast chain)
- **Vite**: Next-generation frontend tooling
- **Axios**: HTTP client for API requests

To build for production:
```bash
cd frontend
npm run build
```

## 📚 Documentation

- [Multimodal Architecture](docs/MULTIMODAL_ARCHITECTURE.md) - Detailed architecture documentation
- [Quick Start Guide](docs/QUICKSTART.md) - Step-by-step setup instructions
- [API Documentation](docs/API.md) - API reference
- [Usage Guide](docs/USAGE.md) - User guide

## 🔒 Security Notes

- The `.env` file containing API keys is gitignored and should never be committed
- In production, configure CORS to only allow specific origins
- Consider implementing rate limiting on the API endpoint
- Store Azure OpenAI credentials securely (use Azure Key Vault in production)
- **Security Updates**: All dependencies are up-to-date with latest security patches
  - FastAPI 0.109.1 (patched ReDoS vulnerability)
  - python-multipart 0.0.18 (patched DoS and ReDoS vulnerabilities)

## 📝 Environment Variables

### Backend (.env)

| Variable | Description | Example |
|----------|-------------|---------|
| `AZURE_OPENAI_ENDPOINT` | Your Azure OpenAI endpoint URL | `https://your-resource.openai.azure.com/` |
| `AZURE_OPENAI_API_KEY` | Your Azure OpenAI API key | `abc123...` |
| `AZURE_OPENAI_DEPLOYMENT` | Your GPT-4 Vision deployment name | `gpt-4-vision` |
| `AZURE_OPENAI_API_VERSION` | API version to use | `2024-02-15-preview` |

## 🧪 Testing Without Azure OpenAI

The backend includes a fallback mode. If Azure OpenAI credentials are not configured, it will return mock responses, allowing you to test the frontend integration without a real API connection.

## 📦 Project Structure

```
FaceBodyAI/
├── backend/
│   ├── main.py              # FastAPI application
│   ├── requirements.txt     # Python dependencies
│   ├── .env.example        # Environment variables template
│   └── .gitignore
├── frontend/
│   ├── src/
│   │   ├── App.vue         # Main Vue component
│   │   ├── main.js         # Vue app entry point
│   │   └── style.css       # Global styles
│   ├── index.html          # HTML template
│   ├── vite.config.js      # Vite configuration
│   ├── package.json        # Node dependencies
│   └── .gitignore
└── README.md               # This file
```

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📄 License

This project is open source and available under the MIT License.