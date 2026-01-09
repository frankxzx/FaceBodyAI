# Quick Start Guide

This guide will help you get FaceBodyAI up and running in minutes.

## Prerequisites

Before you begin, ensure you have:
- [ ] Node.js 18+ installed
- [ ] Python 3.8+ installed
- [ ] An Azure OpenAI account with GPT-4 Vision deployment
- [ ] A webcam or camera connected to your computer

## Option 1: Manual Setup (Recommended for Development)

### Step 1: Clone the Repository

```bash
git clone https://github.com/frankxzx/FaceBodyAI.git
cd FaceBodyAI
```

### Step 2: Set Up the Backend

```bash
# Navigate to backend directory
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment variables
cp .env.example .env
# Edit .env and add your Azure OpenAI credentials
```

Edit the `.env` file:
```env
AZURE_OPENAI_ENDPOINT=https://your-resource-name.openai.azure.com/
AZURE_OPENAI_API_KEY=your-api-key-here
AZURE_OPENAI_DEPLOYMENT=gpt-4-vision
AZURE_OPENAI_API_VERSION=2024-02-15-preview
```

```bash
# Start the backend server
python main.py
```

The backend should now be running at `http://localhost:8000`

### Step 3: Set Up the Frontend

Open a new terminal window:

```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install

# Start the development server
npm run dev
```

The frontend should now be running at `http://localhost:5173`

### Step 4: Use the Application

1. Open your browser and navigate to `http://localhost:5173`
2. Click **"Start Camera"** to grant camera access
3. Click **"Start Analysis"** to begin capturing and analyzing frames
4. View the real-time emotion and body language analysis results

## Option 2: Docker Setup (Recommended for Production)

### Step 1: Prerequisites

Ensure Docker and Docker Compose are installed:
```bash
docker --version
docker-compose --version
```

### Step 2: Configure Environment

```bash
# Create .env file in the root directory
cp backend/.env.example .env
# Edit .env and add your Azure OpenAI credentials
```

### Step 3: Start Services

```bash
# Build and start all services
docker-compose up --build

# Or run in detached mode
docker-compose up -d --build
```

### Step 4: Access the Application

- Frontend: `http://localhost:5173`
- Backend API: `http://localhost:8000`
- API Documentation: `http://localhost:8000/docs`

### Stop Services

```bash
docker-compose down
```

## Testing Without Azure OpenAI

If you want to test the application without configuring Azure OpenAI:

1. Skip the `.env` configuration
2. The backend will return mock responses
3. You can still test the complete flow from video capture to result display

## Troubleshooting

### Camera Access Issues

- **Browser doesn't ask for camera permission**: Ensure you're accessing via HTTPS or localhost
- **Permission denied**: Check browser settings to allow camera access
- **No camera found**: Ensure your webcam is connected and not being used by another application

### Backend Issues

- **Module not found**: Ensure you activated the virtual environment
- **Port 8000 already in use**: Stop any other services using port 8000
- **Azure OpenAI errors**: Verify your credentials and deployment name

### Frontend Issues

- **npm install fails**: Try clearing npm cache: `npm cache clean --force`
- **Port 5173 already in use**: Stop any other Vite dev servers or change the port in `vite.config.js`
- **CORS errors**: Ensure backend is running and CORS is properly configured

## Next Steps

- Read the [API Documentation](docs/API.md) for integration details
- Customize the UI in `frontend/src/App.vue`
- Adjust analysis frequency by changing the interval in `App.vue` (currently 5 seconds)
- Configure production settings for deployment

## Getting Azure OpenAI Access

1. Sign up for an Azure account at https://azure.microsoft.com
2. Create an Azure OpenAI resource
3. Deploy a GPT-4 Vision model
4. Get your endpoint and API key from the Azure portal
5. Update your `.env` file with these credentials

## Support

For issues or questions:
- Check the [README.md](README.md) for detailed information
- Review the [API Documentation](docs/API.md)
- Open an issue on GitHub
