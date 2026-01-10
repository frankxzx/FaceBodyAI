# Example: CV Features + GPT-4o Interpretation

This document shows examples of how CV features are extracted and interpreted by GPT-4o.

## Example 1: Engaged Participant

### CV Features (Extracted)
```json
{
  "head_pitch": -8,
  "head_yaw": 2,
  "head_roll": -1,
  "eye_gaze": "on_screen",
  "motion_level": "medium"
}
```

### GPT-4o Analysis
```json
{
  "emotion": "focused",
  "engagement": "high",
  "confidence": "medium",
  "explanation": "Person leans forward (pitch -8°) with eyes on screen, showing active engagement. Medium motion suggests responsive participation."
}
```

### Interpretation
- **Head pitch -8°**: Leaning forward → interested/engaged
- **Eye gaze on_screen**: Maintaining attention → focused
- **Motion medium**: Not static, actively participating
- **Result**: High engagement, focused state

---

## Example 2: Nervous/Uncertain

### CV Features (Extracted)
```json
{
  "head_pitch": 5,
  "head_yaw": -12,
  "head_roll": 3,
  "eye_gaze": "away",
  "motion_level": "high"
}
```

### Audio Context
```json
{
  "audio_speaking": true,
  "audio_volume": "low"
}
```

### GPT-4o Analysis
```json
{
  "emotion": "nervous",
  "engagement": "medium",
  "confidence": "low",
  "explanation": "Person looks away (yaw -12°) while speaking softly, with high motion indicating restlessness. Suggests uncertainty or nervousness."
}
```

### Interpretation
- **Head yaw -12°**: Turned away → avoiding eye contact
- **Eye gaze away**: Not maintaining attention
- **Motion high**: Fidgeting/restlessness
- **Speaking + low volume**: Uncertain communication
- **Result**: Nervous, low confidence

---

## Example 3: Confident Speaker

### CV Features (Extracted)
```json
{
  "head_pitch": 2,
  "head_yaw": 0,
  "head_roll": 0,
  "eye_gaze": "on_screen",
  "motion_level": "low"
}
```

### Audio Context
```json
{
  "audio_speaking": true,
  "audio_volume": "medium"
}
```

### GPT-4o Analysis
```json
{
  "emotion": "confident",
  "engagement": "high",
  "confidence": "high",
  "explanation": "Person maintains steady, forward-facing posture (pitch/yaw/roll near 0°) with direct eye contact while speaking at normal volume. Shows confidence and composure."
}
```

### Interpretation
- **All angles near 0°**: Steady, centered posture
- **Eye gaze on_screen**: Direct eye contact
- **Motion low**: Calm, composed
- **Speaking + medium volume**: Clear communication
- **Result**: High confidence, composed

---

## Example 4: Distracted/Disengaged

### CV Features (Extracted)
```json
{
  "head_pitch": 15,
  "head_yaw": -20,
  "head_roll": 5,
  "eye_gaze": "away",
  "motion_level": "low"
}
```

### Audio Context
```json
{
  "audio_speaking": false,
  "audio_volume": "low"
}
```

### GPT-4o Analysis
```json
{
  "emotion": "disengaged",
  "engagement": "low",
  "confidence": "medium",
  "explanation": "Person looks away and upward (pitch +15°, yaw -20°), with minimal motion and silence. Indicates distraction or disinterest."
}
```

### Interpretation
- **Head pitch +15°**: Looking up → distracted
- **Head yaw -20°**: Looking away → disengaged
- **Eye gaze away**: Not paying attention
- **Motion low + silent**: Passive, disengaged
- **Result**: Low engagement, distracted

---

## Example 5: Active Listening

### CV Features (Extracted)
```json
{
  "head_pitch": -5,
  "head_yaw": 3,
  "head_roll": -2,
  "eye_gaze": "on_screen",
  "motion_level": "medium"
}
```

### Audio Context
```json
{
  "audio_speaking": false,
  "audio_volume": "low"
}
```

### GPT-4o Analysis
```json
{
  "emotion": "attentive",
  "engagement": "high",
  "confidence": "high",
  "explanation": "Person leans slightly forward with steady gaze, showing active listening. Medium motion suggests responsive body language (nodding, slight shifts)."
}
```

### Interpretation
- **Head pitch -5°**: Slight forward lean → attentive
- **Eye gaze on_screen**: Maintaining focus
- **Motion medium**: Responsive (nodding, etc.)
- **Silent**: Listening, not speaking
- **Result**: High engagement, active listening

---

## Key Patterns

### Engagement Indicators
✅ **High Engagement**:
- Head pitch < 0 (leaning forward)
- Eye gaze = on_screen
- Motion = medium (responsive)

❌ **Low Engagement**:
- Head pitch > 10 (looking up/away)
- Eye gaze = away
- Motion = low (passive) or high (restless)

### Confidence Indicators
✅ **High Confidence**:
- Pitch/yaw/roll near 0 (steady posture)
- Eye gaze = on_screen
- Motion = low to medium
- Speaking + normal volume

❌ **Low Confidence**:
- Yaw != 0 (turned away)
- Eye gaze = away
- Motion = high (fidgeting)
- Speaking + low volume or silent

---

## How GPT-4o Uses CV Features

1. **Factual Input**: CV features provide quantified, objective measurements
2. **Context Integration**: Combines CV data with visual analysis and audio context
3. **Pattern Recognition**: Maps measurements to behavioral states
4. **Explanation**: Provides evidence-based reasoning

**Example Reasoning**:
```
CV: pitch = -10° → "leaning forward"
CV: gaze = on_screen → "maintaining eye contact"
CV: motion = medium → "responsive body language"
Audio: speaking = false → "listening"

GPT Conclusion: "High engagement, active listening"
```

---

## Benefits of CV + GPT Architecture

1. **Quantified**: CV features are measurable and reproducible
2. **Stable**: Less sensitive to lighting/angle than pure visual analysis
3. **Explainable**: GPT can cite specific measurements
4. **Flexible**: GPT adapts interpretation to context
5. **Accurate**: Combines structured data with visual understanding
