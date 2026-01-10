#!/bin/bash
# Quick Demo Script for FaceBodyAI Multimodal Behavior Analysis

echo "╔════════════════════════════════════════════════════════════════╗"
echo "║  FaceBodyAI - Multimodal Behavior Analysis POC Demo           ║"
echo "║  Fast Chain + Slow Chain Architecture                         ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""

# Check if in correct directory
if [ ! -f "README.md" ]; then
    echo "❌ Error: Please run this script from the FaceBodyAI root directory"
    exit 1
fi

echo "📋 Pre-flight Checks..."
echo ""

# Check Python
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
    echo "✅ Python: $PYTHON_VERSION"
else
    echo "❌ Python 3 not found"
    exit 1
fi

# Check Node
if command -v node &> /dev/null; then
    NODE_VERSION=$(node --version)
    echo "✅ Node.js: $NODE_VERSION"
else
    echo "❌ Node.js not found"
    exit 1
fi

# Check npm
if command -v npm &> /dev/null; then
    NPM_VERSION=$(npm --version)
    echo "✅ npm: $NPM_VERSION"
else
    echo "❌ npm not found"
    exit 1
fi

echo ""
echo "🔧 Setup Steps..."
echo ""

# Backend setup
echo "1️⃣  Setting up Backend..."
cd backend

if [ ! -d "venv" ]; then
    echo "   Creating virtual environment..."
    python3 -m venv venv
fi

echo "   Activating virtual environment..."
source venv/bin/activate || . venv/Scripts/activate

echo "   Installing dependencies..."
pip install -q -r requirements.txt

echo "   ✅ Backend setup complete!"
echo ""

# Test CV features
echo "2️⃣  Testing CV Feature Extraction..."
python test_cv_features.py 2>&1 | grep -E "(✅|EXTRACTED CV FEATURES|Head Pitch|Head Yaw|Eye Gaze|Motion Level|All tests passed)"
echo ""

cd ..

# Frontend setup
echo "3️⃣  Setting up Frontend..."
cd frontend

if [ ! -d "node_modules" ]; then
    echo "   Installing dependencies..."
    npm install --silent
fi

echo "   Building frontend..."
npm run build --silent 2>&1 | tail -3

echo "   ✅ Frontend setup complete!"
echo ""

cd ..

echo "╔════════════════════════════════════════════════════════════════╗"
echo "║  Setup Complete! Ready to Run                                 ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""

echo "🚀 To start the application:"
echo ""
echo "   Terminal 1 - Backend:"
echo "   $ cd backend"
echo "   $ source venv/bin/activate  # or . venv/Scripts/activate on Windows"
echo "   $ python main.py"
echo ""
echo "   Terminal 2 - Frontend:"
echo "   $ cd frontend"
echo "   $ npm run dev"
echo ""
echo "   Then open: http://localhost:5173"
echo ""

echo "📖 Features:"
echo "   ⚡ Fast Chain (~100ms)  - Real-time motion & audio detection"
echo "   🧠 Slow Chain (~3-5s)   - CV features + GPT-4o behavioral analysis"
echo ""

echo "📚 Documentation:"
echo "   • IMPLEMENTATION_SUMMARY.md      - Complete overview"
echo "   • docs/MULTIMODAL_ARCHITECTURE.md - Architecture details"
echo "   • docs/CV_FEATURES_EXAMPLES.md   - Feature interpretation examples"
echo ""

echo "⚙️  Configuration (Optional):"
echo "   To enable GPT-4o analysis:"
echo "   $ cd backend"
echo "   $ cp .env.example .env"
echo "   $ # Edit .env with your Azure OpenAI credentials"
echo ""

echo "✨ Demo complete! Happy analyzing! 🎉"
