<template>
  <div>
    <h1>FaceBodyAI - Real-time Emotion & Body Language Analysis</h1>
    
    <div class="container">
      <div class="info-box">
        <h4>How it works:</h4>
        <p>📹 Camera captures video in real-time</p>
        <p>⏱️ Frame is sent to AI every 5 seconds for analysis</p>
        <p>🤖 Azure OpenAI Vision analyzes emotions and body language</p>
        <p>📊 Results are displayed below in real-time</p>
      </div>

      <div class="video-section">
        <div class="video-container">
          <h2>Live Video Feed</h2>
          <video ref="videoElement" autoplay playsinline></video>
          <canvas ref="canvasElement"></canvas>
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

      <div v-if="latestAnalysis" class="results-section">
        <h2>Latest Analysis Results</h2>
        <div class="results-grid">
          <div class="result-card">
            <h3>Emotion</h3>
            <div class="value">{{ latestAnalysis.emotion }}</div>
          </div>
          
          <div class="result-card">
            <h3>Body Language</h3>
            <div class="value">{{ latestAnalysis.body_language }}</div>
          </div>
          
          <div class="result-card" v-if="latestAnalysis.confidence">
            <h3>Confidence</h3>
            <div class="value">{{ latestAnalysis.confidence }}</div>
          </div>
        </div>
        
        <div v-if="latestAnalysis.details" style="margin-top: 20px; padding: 20px; background: #f8f9fa; border-radius: 10px;">
          <h3 style="margin-bottom: 10px;">Analysis Details</h3>
          <p style="color: #555; line-height: 1.6;">{{ latestAnalysis.details }}</p>
        </div>
      </div>

      <div v-if="isAnalyzing && !latestAnalysis" class="loading">
        <p>🔄 Analyzing frame... Please wait</p>
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
    
    let mediaStream = null
    let captureInterval = null
    
    const statusClass = computed(() => {
      if (isAnalyzing.value) return 'active'
      if (statusMessage.value.includes('Error')) return 'error'
      return 'idle'
    })

    // Start camera stream
    const startCamera = async () => {
      try {
        statusMessage.value = 'Requesting camera access...'
        
        const constraints = {
          video: {
            width: { ideal: 1280 },
            height: { ideal: 720 },
            facingMode: 'user'
          },
          audio: false
        }
        
        mediaStream = await navigator.mediaDevices.getUserMedia(constraints)
        videoElement.value.srcObject = mediaStream
        isStreaming.value = true
        statusMessage.value = 'Camera started. Ready to analyze!'
        
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
      isStreaming.value = false
      stopAnalysis()
      statusMessage.value = 'Camera stopped'
    }

    // Capture frame from video and convert to JPEG
    const captureFrame = () => {
      const video = videoElement.value
      const canvas = canvasElement.value
      
      if (!video || !canvas) return null
      
      // Set canvas dimensions to match video
      canvas.width = video.videoWidth
      canvas.height = video.videoHeight
      
      // Draw current video frame to canvas
      const ctx = canvas.getContext('2d')
      ctx.drawImage(video, 0, 0, canvas.width, canvas.height)
      
      // Convert canvas to blob (JPEG)
      return new Promise((resolve) => {
        canvas.toBlob((blob) => {
          // Also create a URL for display
          lastFrameUrl.value = canvas.toDataURL('image/jpeg', 0.8)
          resolve(blob)
        }, 'image/jpeg', 0.8)
      })
    }

    // Send frame to backend for analysis
    const analyzeFrame = async () => {
      try {
        statusMessage.value = '📸 Capturing frame...'
        const frameBlob = await captureFrame()
        
        if (!frameBlob) {
          statusMessage.value = 'Error: Could not capture frame'
          return
        }

        statusMessage.value = '🔄 Analyzing with Azure OpenAI Vision...'
        
        // Create FormData and append the image
        const formData = new FormData()
        formData.append('file', frameBlob, 'frame.jpg')
        
        // Send to backend API
        const response = await axios.post('/api/frame', formData, {
          headers: {
            'Content-Type': 'multipart/form-data'
          }
        })
        
        latestAnalysis.value = response.data
        statusMessage.value = '✅ Analysis complete! Next capture in 5 seconds...'
        
      } catch (error) {
        console.error('Error analyzing frame:', error)
        statusMessage.value = `Error analyzing frame: ${error.response?.data?.detail || error.message}`
      }
    }

    // Start periodic frame analysis
    const startAnalysis = () => {
      if (!isStreaming.value) {
        statusMessage.value = 'Please start camera first'
        return
      }
      
      isAnalyzing.value = true
      statusMessage.value = 'Analysis started! Capturing every 5 seconds...'
      
      // Capture first frame immediately
      analyzeFrame()
      
      // Then capture every 5 seconds
      captureInterval = setInterval(() => {
        analyzeFrame()
      }, 5000)
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
</style>
