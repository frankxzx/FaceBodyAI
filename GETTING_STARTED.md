# Getting Started Guide

Welcome to the **FaceBodyAI Multimodal Behavior Analysis POC**! 

This guide will help you get started with the new Fast Chain + Slow Chain architecture.

---

## 🎯 What's New

This implementation adds:

1. **Fast Chain** (~100ms): Real-time motion and audio detection for instant feedback
2. **Slow Chain** (~3-5s): AI-powered behavioral analysis using CV features + GPT-4o
3. **CV Features**: Head pose, eye gaze, and motion level extraction with MediaPipe
4. **Enhanced UI**: Separate visual indicators for fast chain and slow chain results

---

## 🚀 Quick Start (3 Steps)

### Step 1: Setup Backend

```bash
cd backend

# Create virtual environment (first time only)
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Test CV features (optional)
python test_cv_features.py
```

### Step 2: Setup Frontend

```bash
cd frontend

# Install dependencies (first time only)
npm install

# Build to verify (optional)
npm run build
```

### Step 3: Run the Application

**Terminal 1 - Backend:**
```bash
cd backend
source venv/bin/activate  # On Windows: venv\Scripts\activate
python main.py
# Server runs on http://localhost:8000
```

**Terminal 2 - Frontend:**
```bash
cd frontend
npm run dev
# App runs on http://localhost:5173
```

**Open in Browser:**
```
http://localhost:5173
```

---

## 🎮 Using the Application

### 1. Grant Permissions
- Click **"Start Camera"**
- Allow camera and microphone access when prompted

### 2. Watch Fast Chain (Instant Feedback)
Once camera is started, you'll see:
- 🟢 **Activity Status**: Active/Idle based on motion + speaking
- 📊 **Motion Level**: Low/Medium/High from frame differences
- 🎤 **Speaking Status**: Speaking/Silent from audio detection

These update **every ~100ms** for instant feedback!

### 3. Start Slow Chain Analysis
- Click **"Start Analysis"**
- The slow chain runs **every 4 seconds**:
  1. Captures video frame
  2. Extracts CV features (head pose, eye gaze, motion)
  3. Sends to backend with audio metadata
  4. GPT-4o analyzes behavior
  5. Returns insights

### 4. View Results
You'll see:
- 😊 **Emotion**: e.g., "focused", "nervous", "confident"
- 🎯 **Engagement**: High/Medium/Low
- 💪 **Confidence**: High/Medium/Low
- 📝 **Explanation**: Why the system reached these conclusions
- 📊 **CV Features**: Head pitch/yaw/roll, eye gaze, motion level

---

## ⚙️ Configuration (Optional)

### Enable Full GPT-4o Analysis

By default, the system works in **mock mode** (no Azure OpenAI required).

To enable real GPT-4o analysis:

1. **Copy environment template:**
   ```bash
   cd backend
   cp .env.example .env
   ```

2. **Edit `.env` file:**
   ```
   AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
   AZURE_OPENAI_API_KEY=your-api-key-here
   AZURE_OPENAI_DEPLOYMENT=gpt-4-vision
   AZURE_OPENAI_API_VERSION=2024-02-15-preview
   ```

3. **Restart backend:**
   ```bash
   python main.py
   ```

---

## 📖 Understanding the Output

### Fast Chain Example
```
⚡ Fast Chain (Live Status)
🟢 Active     Motion: medium     🎤 Speaking
```

**Meaning:**
- System is "alive" and responsive
- Medium motion detected (moving, gesturing)
- User is currently speaking

### Slow Chain Example
```json
{
  "emotion": "focused",
  "engagement": "high",
  "confidence": "medium",
  "explanation": "Person leans forward (pitch -8°) with eyes on screen, showing active engagement.",
  "cv_features": {
    "head_pitch": -8,
    "head_yaw": 2,
    "head_roll": -1,
    "eye_gaze": "on_screen",
    "motion_level": "medium"
  }
}
```

**Meaning:**
- **Emotion**: Current emotional state (focused)
- **Engagement**: Level of attention (high)
- **Confidence**: Self-assurance level (medium)
- **Explanation**: Evidence-based reasoning
- **CV Features**: Quantified measurements supporting the analysis

---

## 🔍 CV Features Explained

### Head Pose
- **Pitch** (up/down): 
  - Negative = looking down/forward lean
  - Positive = looking up
  - Example: -8° = leaning forward (engaged)

- **Yaw** (left/right):
  - Negative = turned left
  - Positive = turned right
  - Example: 2° = mostly facing forward

- **Roll** (tilt):
  - Negative = tilted left
  - Positive = tilted right
  - Example: -1° = nearly straight

### Eye Gaze
- **on_screen**: Looking at camera/screen (engaged)
- **away**: Looking elsewhere (distracted)
- **unknown**: Cannot determine

### Motion Level
- **low**: Minimal movement (calm/passive)
- **medium**: Normal movement (active/responsive)
- **high**: Excessive movement (restless/fidgeting)

---

## 🧪 Testing Without Azure OpenAI

The system works in **mock mode** without Azure OpenAI:

- ✅ Fast chain works fully (local processing)
- ✅ CV features are extracted correctly
- ✅ Backend returns mock behavioral insights
- ⚠️ GPT-4o analysis is simulated (not real AI)

This is perfect for:
- Development and testing
- UI/UX validation
- CV feature verification
- Demo purposes

---

## 🐛 Troubleshooting

### Backend Issues

**Problem**: `ModuleNotFoundError: No module named 'mediapipe'`
```bash
cd backend
source venv/bin/activate
pip install -r requirements.txt
```

**Problem**: `Port 8000 already in use`
```bash
# Find and kill the process using port 8000
lsof -ti:8000 | xargs kill -9
# Or change port in main.py
```

### Frontend Issues

**Problem**: `npm install` fails
```bash
cd frontend
rm -rf node_modules package-lock.json
npm install
```

**Problem**: `CORS error` in browser console
- Make sure backend is running on port 8000
- Check backend CORS configuration in `main.py`

### Camera/Microphone Issues

**Problem**: "Permission denied" for camera/microphone
- Check browser permissions
- Try HTTPS or localhost (required by some browsers)
- On Chrome: chrome://settings/content/camera

**Problem**: Fast chain indicators not updating
- Check browser console for errors
- Ensure camera is actually streaming
- Try refreshing the page

---

## 📚 Additional Resources

- **Architecture Details**: `docs/MULTIMODAL_ARCHITECTURE.md`
- **CV Feature Examples**: `docs/CV_FEATURES_EXAMPLES.md`
- **Implementation Summary**: `IMPLEMENTATION_SUMMARY.md`
- **API Documentation**: `docs/API.md`

---

## 🎓 Learn More

### Fast Chain vs Slow Chain

**Fast Chain** makes the system feel real-time:
- Updates every 100ms
- Pure frontend (no latency)
- Motion + audio detection
- Visual feedback

**Slow Chain** makes the system smart:
- Updates every 3-5 seconds
- Backend processing + AI
- CV features + GPT-4o
- Behavioral insights

### Why CV Features?

CV features convert unstable video into **stable, quantified signals**:

```
Video (unstable) → CV Features (stable) → GPT-4o (interpretation)
```

Instead of:
```
Video (unstable) → GPT-4o (must guess)
```

This makes the analysis:
- More stable
- More explainable
- More accurate
- More cost-effective

---

## ✨ Next Steps

1. ✅ Run the demo (`./demo.sh` or follow Quick Start)
2. ✅ Test fast chain responsiveness
3. ✅ Observe CV features in action
4. ⏳ Configure Azure OpenAI for real AI analysis
5. ⏳ Test different scenarios (engaged, distracted, nervous, etc.)
6. ⏳ Customize for your use case

---

## 🆘 Need Help?

- Check documentation in `docs/` folder
- Review `IMPLEMENTATION_SUMMARY.md`
- See examples in `docs/CV_FEATURES_EXAMPLES.md`
- Check backend test: `python backend/test_cv_features.py`

---

## 🎉 Ready to Go!

You now have a complete multimodal behavior analysis system with:
- ⚡ Fast chain for instant feedback
- 🧠 Slow chain for AI insights
- 📊 CV features for stable analysis
- 🎨 Beautiful, responsive UI

**Start the servers and see it in action!** 🚀
