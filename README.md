# FaceBodyAI

Real-time emotion and body language analysis using Vue.js frontend, FastAPI backend, and Azure OpenAI Vision API.

## 🎯 Features

- **Real-time Video Capture**: Uses browser's `getUserMedia()` API to access webcam
- **Automatic Frame Analysis**: Captures and analyzes video frames every 5 seconds
- **AI-Powered Analysis**: Leverages Azure OpenAI Vision (GPT-4 Vision) for emotion and body language detection
- **Modern UI**: Clean, responsive Vue 3 interface with real-time results display
- **RESTful API**: FastAPI backend with automatic OpenAPI documentation

## 🏗️ Architecture

```
┌─────────────────┐         ┌─────────────────┐         ┌──────────────────┐
│   Vue Frontend  │────────▶│  FastAPI Backend│────────▶│ Azure OpenAI     │
│  (Port 5173)    │  JPEG   │   (Port 8000)   │  Base64 │ Vision API       │
│                 │◀────────│                 │◀────────│                  │
│ - getUserMedia()│  JSON   │ - /api/frame    │  JSON   │ - GPT-4 Vision   │
│ - Canvas        │         │ - CORS enabled  │         │ - Multimodal AI  │
│ - 5s interval   │         │                 │         │                  │
└─────────────────┘         └─────────────────┘         └──────────────────┘
```

## 📋 Prerequisites

- **Node.js** 18+ and npm
- **Python** 3.8+
- **Azure OpenAI** account with GPT-4 Vision deployment
- Modern web browser with camera access

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

3. **Click "Start Camera"** to grant camera access

4. **Click "Start Analysis"** to begin automatic frame capture and analysis

5. **View results** - The app will:
   - Capture a frame from your video every 5 seconds
   - Send it to the backend API
   - Display emotion and body language analysis in real-time

## 🔧 API Endpoints

### `POST /api/frame`

Analyze a video frame for emotions and body language.

**Request:**
- Method: `POST`
- Content-Type: `multipart/form-data`
- Body: Image file (JPEG)

**Response:**
```json
{
  "emotion": "happy",
  "body_language": "relaxed",
  "details": "Person appears cheerful with open posture",
  "confidence": "high"
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
- **Vite**: Next-generation frontend tooling
- **Axios**: HTTP client for API requests

To build for production:
```bash
cd frontend
npm run build
```

## 🔒 Security Notes

- The `.env` file containing API keys is gitignored and should never be committed
- In production, configure CORS to only allow specific origins
- Consider implementing rate limiting on the API endpoint
- Store Azure OpenAI credentials securely (use Azure Key Vault in production)

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