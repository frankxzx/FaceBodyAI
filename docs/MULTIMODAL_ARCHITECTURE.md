# Multimodal Behavior Analysis Architecture

## Overview

This document describes the **Fast Chain + Slow Chain** architecture for near real-time multimodal behavioral analysis.

**Goal**: Analyze human behavior (expression, body language, tone) with **near real-time (1–3 seconds)** feedback, not millisecond-level real-time.

---

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                         Frontend (Vue.js)                        │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌────────────────────┐          ┌────────────────────┐        │
│  │   FAST CHAIN       │          │   SLOW CHAIN        │        │
│  │   (~100ms)         │          │   (~3-5 seconds)    │        │
│  ├────────────────────┤          ├────────────────────┤        │
│  │ • Motion Detection │          │ • Image Capture     │        │
│  │   (Frame Diff)     │          │ • Audio Metadata    │        │
│  │ • Audio Detection  │          │ • API Call          │        │
│  │   (Volume/VAD)     │          │                     │        │
│  ├────────────────────┤          └─────────┬──────────┘        │
│  │ Output:            │                    │                    │
│  │ • Activity Status  │                    │ HTTP POST          │
│  │ • Motion Level     │                    ▼                    │
│  │ • Speaking Status  │          ┌─────────────────────────┐   │
│  └────────────────────┘          │  Backend (FastAPI)       │   │
│           │                      │                          │   │
│           │                      │ ┌─────────────────────┐ │   │
│           ▼                      │ │  CV Feature Extract │ │   │
│  ┌────────────────────┐          │ │  (MediaPipe)        │ │   │
│  │ Visual Indicators  │          │ ├─────────────────────┤ │   │
│  │ • Activity Light   │          │ │ • Head Pitch/Yaw    │ │   │
│  │ • Motion Bar       │          │ │ • Eye Gaze          │ │   │
│  │ • Speaking Icon    │          │ │ • Motion Level      │ │   │
│  └────────────────────┘          │ └─────────┬───────────┘ │   │
│                                  │           │             │   │
│                                  │           ▼             │   │
│                                  │ ┌─────────────────────┐ │   │
│                                  │ │ GPT-4o Multimodal   │ │   │
│                                  │ │ (Azure OpenAI)      │ │   │
│                                  │ ├─────────────────────┤ │   │
│                                  │ │ Input:              │ │   │
│                                  │ │ • Image (base64)    │ │   │
│                                  │ │ • CV Features (JSON)│ │   │
│                                  │ │ • Audio Metadata    │ │   │
│                                  │ ├─────────────────────┤ │   │
│                                  │ │ Output:             │ │   │
│                                  │ │ • Emotion           │ │   │
│                                  │ │ • Engagement        │ │   │
│                                  │ │ • Confidence        │ │   │
│                                  │ │ • Explanation       │ │   │
│                                  │ └─────────────────────┘ │   │
│                                  └─────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
```

---

## Fast Chain (Client-Side, ~100ms)

### Purpose
Make the system **feel real-time** with instant feedback.

### Technology
Pure frontend JavaScript (no network, no AI).

### What It Does

1. **Motion Detection** (Frame Diff)
   - Compares consecutive video frames
   - Calculates pixel differences
   - Classifies as: `low`, `medium`, `high`

2. **Audio Detection** (Volume/VAD)
   - Uses Web Audio API
   - Analyzes frequency data
   - Detects speaking vs. silent

### Output Format

```json
{
  "activity": "active | idle",
  "motion": "low | medium | high",
  "speaking": true | false
}
```

### Use Cases
- Real-time UI indicators (activity lights, motion bars)
- Instant user feedback
- System "aliveness" perception
- **NOT for behavioral analysis**

---

## Slow Chain (Server-Side, ~3-5 seconds)

### Purpose
Provide **meaningful behavioral insights** with AI analysis.

### Technology
- **CV Features**: MediaPipe (FaceMesh)
- **AI Analysis**: Azure OpenAI GPT-4o (Multimodal)

### Pipeline

#### 1. CV Feature Extraction (Backend)

Extracts quantified measurements from video frames:

```json
{
  "head_pitch": -12,  // degrees (negative = down, positive = up)
  "head_yaw": 5,      // degrees (negative = left, positive = right)
  "head_roll": 3,     // degrees (head tilt)
  "eye_gaze": "on_screen | away | unknown",
  "motion_level": "low | medium | high"
}
```

**Implementation**:
- Uses MediaPipe FaceMesh for landmark detection
- Calculates head pose from facial landmarks
- Estimates eye gaze from head orientation
- Detects motion via frame comparison

#### 2. GPT-4o Analysis

**Input**:
- Image (base64 encoded)
- CV features (structured JSON)
- Audio metadata (speaking status, volume)

**Prompt Strategy**:
```
CV features provide quantified facts:
- head_pitch = -12° → user is leaning forward
- eye_gaze = on_screen → maintaining attention
- motion = medium → engaged, not static

GPT-4o interprets these facts + visual cues to determine:
- Emotional state
- Engagement level
- Confidence level
- Behavioral explanation
```

**Output**:
```json
{
  "emotion": "slightly nervous",
  "engagement": "high",
  "confidence": "medium",
  "explanation": "Leans forward, maintains eye contact, but shows slight tension in posture.",
  "cv_features": { /* raw CV data */ }
}
```

---

## Why This Architecture?

### Fast Chain Benefits
✅ **Instant feedback** - UI feels responsive
✅ **No latency** - Runs locally in browser
✅ **No cost** - No API calls
✅ **Reliable** - Works offline

### Slow Chain Benefits
✅ **Accurate analysis** - AI-powered insights
✅ **Explainable** - CV features + GPT explanation
✅ **Stable** - Structured, quantified data
✅ **Valuable** - Meaningful behavioral insights

### Why Not "True Real-Time"?
- Azure OpenAI is HTTP-based (not streaming)
- LLM inference takes 1-3 seconds
- **Near real-time (3-5s) is acceptable** for behavioral analysis
- Fast chain provides perceived real-time responsiveness

---

## CV Features: Design Philosophy

> **CV's role is NOT to make conclusions, but to:**
> **Convert continuous, unstable video into stable, quantified signals for GPT**

### Minimal CV Feature Set (POC)

For proof-of-concept, we extract:
1. **Head Pose** (pitch, yaw, roll)
2. **Eye Gaze** (on_screen, away)
3. **Motion Level** (low, medium, high)

### How GPT Interprets CV Features

GPT treats CV features as a **fact table**:
- `pitch < -10` → "leaning forward" (engagement)
- `gaze = on_screen` → "maintaining attention"
- `motion = medium` → "active participation"

Combined with visual analysis, GPT produces behavioral insights.

---

## Implementation Details

### Backend (FastAPI)

**File**: `backend/cv_features.py`
- `CVFeatureExtractor` class
- MediaPipe FaceMesh integration
- Head pose estimation
- Motion detection via frame diff

**File**: `backend/main.py`
- `/api/frame` endpoint
- Accepts image + audio metadata
- Returns behavioral analysis

### Frontend (Vue.js)

**File**: `frontend/src/App.vue`
- Fast chain: Motion + audio detection (100ms interval)
- Slow chain: Image capture + API call (4s interval)
- Visual indicators for fast chain
- Results display for slow chain

---

## API Specification

### POST `/api/frame`

**Request**:
```
Content-Type: multipart/form-data

file: <image/jpeg>
audio_speaking: "true" | "false"
audio_volume: "low" | "medium" | "high"
```

**Response**:
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

---

## POC Success Criteria

1. ✅ **Fast chain feels real-time** (< 100ms updates)
2. ✅ **Slow chain provides insights** (emotion, engagement, confidence)
3. ✅ **GPT distinguishes states** (confident vs. nervous vs. distracted)
4. ✅ **Explanations are credible** (users "nod in agreement")
5. ✅ **UI feels responsive** (fast chain + slow chain separation)

---

## One-Line Summary

> **Fast chain makes the system "alive",**
> **Slow chain (CV + GPT) makes it "smart and stable".**

---

## Future Enhancements

- [ ] Audio analysis (not just metadata)
- [ ] Temporal patterns (behavior over time)
- [ ] Multi-person analysis
- [ ] Custom behavioral models
- [ ] Real-time streaming (WebSocket)
- [ ] Facial expression micro-analysis
- [ ] Voice tone analysis

---

## References

- [MediaPipe FaceMesh](https://google.github.io/mediapipe/solutions/face_mesh.html)
- [Azure OpenAI Vision](https://learn.microsoft.com/en-us/azure/ai-services/openai/how-to/gpt-with-vision)
- [Web Audio API](https://developer.mozilla.org/en-US/docs/Web/API/Web_Audio_API)
