<template>
  <div>
    <h1>FaceBodyAI - Multimodal Behavioral Analysis</h1>
    
    <div class="container">
      <div class="info-box">
        <h4>Architecture: Fast Chain + Slow Chain</h4>
        <p>⚡ <strong>Fast Chain (~100ms)</strong>: Local motion & audio detection for instant feedback</p>
        <p>🧠 <strong>Slow Chain (~3-5s)</strong>: CV features + GPT-4o for behavioral insights</p>
        <p>🎯 Near real-time multimodal behavioral analysis</p>
      </div>

      <!-- Fast Chain Status Indicators -->
      <div v-if="isStreaming" class="fast-chain-section">
        <h3>⚡ Fast Chain (Live Status)</h3>
        <div class="fast-chain-indicators">
          <div class="indicator" :class="fastChainStatus.activity">
            <div class="indicator-light"></div>
            <span>{{ fastChainStatus.activity === 'active' ? '🟢 Active' : '🔵 Idle' }}</span>
          </div>
          <div class="indicator">
            <div class="indicator-light" :class="'motion-' + fastChainStatus.motion"></div>
            <span>Motion: {{ fastChainStatus.motion }}</span>
          </div>
          <div class="indicator">
            <div class="indicator-light" :class="fastChainStatus.speaking ? 'speaking' : ''"></div>
            <span>{{ fastChainStatus.speaking ? '🎤 Speaking' : '🔇 Silent' }}</span>
          </div>
        </div>
      </div>

      <div class="video-section">
        <div class="video-container">
          <h2>Live Video Feed</h2>
          <video ref="videoElement" autoplay playsinline></video>
          <canvas ref="canvasElement" style="display: none;"></canvas>
        </div>
        
        <div class="video-container">
          <h2>Latest Captured Frame</h2>
          <img v-if="lastFrameUrl" :src="lastFrameUrl" style="width: 100%; border-radius: 10px;" alt="Latest frame" />
          <div v-else style="width: 100%; aspect-ratio: 4/3; background: #f0f0f0; border-radius: 10px; display: flex; align-items: center; justify-content: center; color: #999;">
            No frame captured yet
          </div>
        </div>
      </div>

      <div class="controls">
        <button @click="startCamera" :disabled="isStreaming">Start Camera</button>
        <button @click="stopCamera" :disabled="!isStreaming">Stop Camera</button>
        <button @click="startAnalysis" :disabled="!isStreaming || isAnalyzing">Start Analysis</button>
        <button @click="stopAnalysis" :disabled="!isAnalyzing">Stop Analysis</button>
      </div>

      <div class="status" :class="statusClass">
        {{ statusMessage }}
      </div>

      <!-- Slow Chain Results -->
      <div v-if="latestAnalysis" class="results-section">
        <h2>🧠 Slow Chain Analysis Results</h2>
        
        <div class="results-grid">
          <div class="result-card">
            <h3>😊 Emotion</h3>
            <div class="value">{{ latestAnalysis.emotion }}</div>
          </div>
          
          <div class="result-card" v-if="latestAnalysis.engagement">
            <h3>🎯 Engagement</h3>
            <div class="value">{{ latestAnalysis.engagement }}</div>
          </div>
          
          <div class="result-card" v-if="latestAnalysis.confidence">
            <h3>💪 Confidence</h3>
            <div class="value">{{ latestAnalysis.confidence }}</div>
          </div>
        </div>
        
        <div v-if="latestAnalysis.explanation" class="explanation-box">
          <h3>📝 Behavioral Insight</h3>
          <p>{{ latestAnalysis.explanation }}</p>
        </div>

        <div v-if="latestAnalysis.cv_features" class="cv-features-box">
          <h3>📊 CV Features (Quantified)</h3>
          <div class="cv-features-grid">
            <div class="cv-feature">
              <span class="label">Head Pitch:</span>
              <span class="value">{{ latestAnalysis.cv_features.head_pitch }}°</span>
            </div>
            <div class="cv-feature">
              <span class="label">Head Yaw:</span>
              <span class="value">{{ latestAnalysis.cv_features.head_yaw }}°</span>
            </div>
            <div class="cv-feature">
              <span class="label">Head Roll:</span>
              <span class="value">{{ latestAnalysis.cv_features.head_roll }}°</span>
            </div>
            <div class="cv-feature">
              <span class="label">Eye Gaze:</span>
              <span class="value">{{ latestAnalysis.cv_features.eye_gaze }}</span>
            </div>
            <div class="cv-feature">
              <span class="label">Motion Level:</span>
              <span class="value">{{ latestAnalysis.cv_features.motion_level }}</span>
            </div>
          </div>
        </div>
      </div>

      <div v-if="isAnalyzing && !latestAnalysis" class="loading">
        <p>🔄 Running slow chain analysis... Please wait</p>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed, onUnmounted } from 'vue'
import axios from 'axios'

export default {
  name: 'App',
  setup() {
    const videoElement = ref(null)
    const canvasElement = ref(null)
    const isStreaming = ref(false)
    const isAnalyzing = ref(false)
    const latestAnalysis = ref(null)
    const statusMessage = ref('Click "Start Camera" to begin')
    const lastFrameUrl = ref(null)
    
    // Fast chain status
    const fastChainStatus = ref({
      activity: 'idle',
      motion: 'low',
      speaking: false
    })
    
    let mediaStream = null
    let captureInterval = null
    let fastChainInterval = null
    let audioContext = null
    let analyser = null
    let previousFrame = null
    
    const statusClass = computed(() => {
      if (isAnalyzing.value) return 'active'
      if (statusMessage.value.includes('Error')) return 'error'
      return 'idle'
    })

    // Fast Chain: Motion Detection (frame diff)
    const detectMotion = () => {
      const video = videoElement.value
      const canvas = canvasElement.value
      
      if (!video || !canvas || video.videoWidth === 0) return 'low'
      
      canvas.width = video.videoWidth
      canvas.height = video.videoHeight
      
      const ctx = canvas.getContext('2d')
      ctx.drawImage(video, 0, 0, canvas.width, canvas.height)
      
      const currentFrame = ctx.getImageData(0, 0, canvas.width, canvas.height)
      
      if (!previousFrame) {
        previousFrame = currentFrame
        return 'low'
      }
      
      // Calculate frame difference
      let diff = 0
      const pixels = currentFrame.data.length / 4
      
      for (let i = 0; i < currentFrame.data.length; i += 4) {
        const rDiff = Math.abs(currentFrame.data[i] - previousFrame.data[i])
        const gDiff = Math.abs(currentFrame.data[i + 1] - previousFrame.data[i + 1])
        const bDiff = Math.abs(currentFrame.data[i + 2] - previousFrame.data[i + 2])
        
        if (rDiff + gDiff + bDiff > 50) {
          diff++
        }
      }
      
      previousFrame = currentFrame
      
      const motionPercent = (diff / pixels) * 100
      
      if (motionPercent < 1) return 'low'
      if (motionPercent < 5) return 'medium'
      return 'high'
    }

    // Fast Chain: Audio Detection (volume/VAD)
    const detectAudio = () => {
      if (!analyser) return { speaking: false, volume: 'low' }
      
      const dataArray = new Uint8Array(analyser.frequencyBinCount)
      analyser.getByteFrequencyData(dataArray)
      
      // Calculate average volume
      const average = dataArray.reduce((a, b) => a + b) / dataArray.length
      
      const speaking = average > 20
      let volume = 'low'
      if (average > 40) volume = 'high'
      else if (average > 20) volume = 'medium'
      
      return { speaking, volume }
    }

    // Fast Chain: Update status every ~100ms
    const runFastChain = () => {
      if (!isStreaming.value) return
      
      const motion = detectMotion()
      const audio = detectAudio()
      
      fastChainStatus.value = {
        activity: (motion !== 'low' || audio.speaking) ? 'active' : 'idle',
        motion: motion,
        speaking: audio.speaking
      }
    }

    // Start camera stream with audio
    const startCamera = async () => {
      try {
        statusMessage.value = 'Requesting camera and microphone access...'
        
        const constraints = {
          video: {
            width: { ideal: 1280 },
            height: { ideal: 720 },
            facingMode: 'user'
          },
          audio: true
        }
        
        mediaStream = await navigator.mediaDevices.getUserMedia(constraints)
        videoElement.value.srcObject = mediaStream
        
        // Setup audio analysis
        audioContext = new (window.AudioContext || window.webkitAudioContext)()
        const source = audioContext.createMediaStreamSource(mediaStream)
        analyser = audioContext.createAnalyser()
        analyser.fftSize = 256
        source.connect(analyser)
        
        isStreaming.value = true
        statusMessage.value = 'Camera started. Ready to analyze!'
        
        // Start fast chain
        fastChainInterval = setInterval(runFastChain, 100)
        
      } catch (error) {
        console.error('Error accessing camera:', error)
        statusMessage.value = `Error accessing camera: ${error.message}`
      }
    }

    // Stop camera stream
    const stopCamera = () => {
      if (mediaStream) {
        mediaStream.getTracks().forEach(track => track.stop())
        mediaStream = null
      }
      if (videoElement.value) {
        videoElement.value.srcObject = null
      }
      if (audioContext) {
        audioContext.close()
        audioContext = null
      }
      if (fastChainInterval) {
        clearInterval(fastChainInterval)
        fastChainInterval = null
      }
      isStreaming.value = false
      stopAnalysis()
      statusMessage.value = 'Camera stopped'
      fastChainStatus.value = {
        activity: 'idle',
        motion: 'low',
        speaking: false
      }
    }

    // Capture frame from video and convert to JPEG
    const captureFrame = () => {
      const video = videoElement.value
      const canvas = canvasElement.value
      
      if (!video || !canvas) return null
      
      canvas.width = video.videoWidth
      canvas.height = video.videoHeight
      
      const ctx = canvas.getContext('2d')
      ctx.drawImage(video, 0, 0, canvas.width, canvas.height)
      
      return new Promise((resolve) => {
        canvas.toBlob((blob) => {
          lastFrameUrl.value = canvas.toDataURL('image/jpeg', 0.8)
          resolve(blob)
        }, 'image/jpeg', 0.8)
      })
    }

    // Slow Chain: Send frame + audio context to backend
    const analyzeFrame = async () => {
      try {
        statusMessage.value = '📸 Capturing frame for slow chain analysis...'
        const frameBlob = await captureFrame()
        
        if (!frameBlob) {
          statusMessage.value = 'Error: Could not capture frame'
          return
        }

        statusMessage.value = '🔄 Running slow chain (CV + GPT-4o)...'
        
        // Get current audio status from fast chain
        const audio = detectAudio()
        
        // Create FormData and append the image + audio metadata
        const formData = new FormData()
        formData.append('file', frameBlob, 'frame.jpg')
        formData.append('audio_speaking', audio.speaking.toString())
        formData.append('audio_volume', audio.speaking ? 'medium' : 'low')
        
        // Send to backend API
        const response = await axios.post('/api/frame', formData, {
          headers: {
            'Content-Type': 'multipart/form-data'
          }
        })
        
        latestAnalysis.value = response.data
        statusMessage.value = '✅ Slow chain analysis complete! Next in 3-5 seconds...'
        
      } catch (error) {
        console.error('Error analyzing frame:', error)
        statusMessage.value = `Error analyzing frame: ${error.response?.data?.detail || error.message}`
      }
    }

    // Start periodic frame analysis (slow chain every 3-5 seconds)
    const startAnalysis = () => {
      if (!isStreaming.value) {
        statusMessage.value = 'Please start camera first'
        return
      }
      
      isAnalyzing.value = true
      statusMessage.value = 'Analysis started! Slow chain runs every 4 seconds...'
      
      // Capture first frame immediately
      analyzeFrame()
      
      // Then capture every 4 seconds (configurable between 3-5s)
      captureInterval = setInterval(() => {
        analyzeFrame()
      }, 4000)
    }

    // Stop periodic frame analysis
    const stopAnalysis = () => {
      if (captureInterval) {
        clearInterval(captureInterval)
        captureInterval = null
      }
      isAnalyzing.value = false
      if (isStreaming.value) {
        statusMessage.value = 'Analysis stopped. Camera still active.'
      }
    }

    // Cleanup on component unmount
    onUnmounted(() => {
      stopCamera()
    })

    return {
      videoElement,
      canvasElement,
      isStreaming,
      isAnalyzing,
      latestAnalysis,
      statusMessage,
      statusClass,
      lastFrameUrl,
      fastChainStatus,
      startCamera,
      stopCamera,
      startAnalysis,
      stopAnalysis
    }
  }
}
</script>

<style scoped>
h2 {
  margin-bottom: 15px;
  color: #333;
  font-size: 1.2rem;
}

.fast-chain-section {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  padding: 20px;
  border-radius: 10px;
  margin-bottom: 20px;
}

.fast-chain-section h3 {
  margin: 0 0 15px 0;
  font-size: 1.3rem;
}

.fast-chain-indicators {
  display: flex;
  gap: 20px;
  flex-wrap: wrap;
}

.indicator {
  display: flex;
  align-items: center;
  gap: 10px;
  background: rgba(255, 255, 255, 0.2);
  padding: 10px 15px;
  border-radius: 8px;
  backdrop-filter: blur(10px);
}

.indicator-light {
  width: 12px;
  height: 12px;
  border-radius: 50%;
  background: #cbd5e0;
  transition: all 0.3s ease;
}

.indicator.active .indicator-light {
  background: #48bb78;
  box-shadow: 0 0 10px #48bb78;
}

.indicator-light.motion-low {
  background: #cbd5e0;
}

.indicator-light.motion-medium {
  background: #f6ad55;
  box-shadow: 0 0 8px #f6ad55;
}

.indicator-light.motion-high {
  background: #fc8181;
  box-shadow: 0 0 10px #fc8181;
}

.indicator-light.speaking {
  background: #4299e1;
  box-shadow: 0 0 10px #4299e1;
  animation: pulse 1s infinite;
}

@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.5; }
}

.explanation-box {
  margin-top: 20px;
  padding: 20px;
  background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
  color: white;
  border-radius: 10px;
}

.explanation-box h3 {
  margin: 0 0 10px 0;
  font-size: 1.1rem;
}

.explanation-box p {
  margin: 0;
  line-height: 1.6;
  font-size: 1rem;
}

.cv-features-box {
  margin-top: 20px;
  padding: 20px;
  background: #f8f9fa;
  border-radius: 10px;
  border: 2px solid #e2e8f0;
}

.cv-features-box h3 {
  margin: 0 0 15px 0;
  color: #2d3748;
}

.cv-features-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 10px;
}

.cv-feature {
  display: flex;
  justify-content: space-between;
  padding: 10px;
  background: white;
  border-radius: 6px;
  border: 1px solid #e2e8f0;
}

.cv-feature .label {
  font-weight: 600;
  color: #4a5568;
}

.cv-feature .value {
  color: #2d3748;
  font-family: 'Courier New', monospace;
}
</style>

