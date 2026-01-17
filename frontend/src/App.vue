<template>
  <div>
    <h1>FaceBodyAI - Real-time Emotion & Body Language Analysis</h1>
    
    <div class="container">
      <div class="info-box">
        <h4>How it works:</h4>
        <p>📹 Camera captures video in real-time</p>
        <p>⏱️ Frame is sent to AI every 5 seconds for analysis</p>
        <p>🤖 Azure OpenAI Vision analyzes emotions and body language</p>
        <p>🎤 Audio is recorded and analyzed by GPT-4o Audio</p>
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

      <div class="controls" style="margin-top: 20px;">
        <h3 style="margin-bottom: 10px;">🎤 Audio Analysis</h3>
        <button @click="startAudioRecording" :disabled="isRecording">Start Recording</button>
        <button @click="stopAudioRecording" :disabled="!isRecording">Stop Recording & Analyze</button>
        <span v-if="isRecording" style="color: red; margin-left: 10px;">● Recording...</span>
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

      <div v-if="latestAudioAnalysis" class="results-section" style="margin-top: 30px;">
        <h2>Latest Audio Analysis Results</h2>
        <div class="results-grid">
          <div class="result-card">
            <h3>Emotional State</h3>
            <div class="value">{{ latestAudioAnalysis.emotional_state }}</div>
          </div>
          
          <div class="result-card">
            <h3>Tone</h3>
            <div class="value">{{ latestAudioAnalysis.tone }}</div>
          </div>
          
          <div class="result-card">
            <h3>Confidence</h3>
            <div class="value">{{ latestAudioAnalysis.confidence }}</div>
          </div>
          
          <div class="result-card">
            <h3>Original Voice</h3>
            <div class="value">{{ latestAudioAnalysis.original_voice || 'N/A' }}</div>
          </div>
        </div>
        
        <div v-if="latestAudioAnalysis.reasoning" style="margin-top: 20px; padding: 20px; background: #f8f9fa; border-radius: 10px;">
          <h3 style="margin-bottom: 10px;">Reasoning</h3>
          <p style="color: #555; line-height: 1.6;">{{ latestAudioAnalysis.reasoning }}</p>
        </div>

        <div v-if="latestAudioAnalysis.notable_vocal_cues" style="margin-top: 20px; padding: 20px; background: #fff3cd; border-radius: 10px;">
          <h3 style="margin-bottom: 10px;">Notable Vocal Cues</h3>
          <p style="color: #856404; line-height: 1.6;">{{ latestAudioAnalysis.notable_vocal_cues }}</p>
        </div>
      </div>

      <div v-if="isAnalyzingAudio" class="loading">
        <p>🔄 Analyzing audio... Please wait</p>
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
    
    // Audio recording state
    const isRecording = ref(false)
    const isAnalyzingAudio = ref(false)
    const latestAudioAnalysis = ref(null)
    let mediaRecorder = null
    let audioChunks = []
    let audioMimeType = 'audio/webm'  // Will be set based on browser support
    
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

    // Start audio recording
    const startAudioRecording = async () => {
      try {
        statusMessage.value = 'Requesting microphone access...'
        
        const stream = await navigator.mediaDevices.getUserMedia({ 
          audio: {
            echoCancellation: true,
            noiseSuppression: true,
            sampleRate: 44100
          } 
        })
        
        // Azure OpenAI Audio API only supports wav and mp3
        // Check for supported MIME types, preferring wav and mp3
        const supportedTypes = ['audio/wav', 'audio/mp3', 'audio/mpeg', 'audio/webm', 'audio/mp4', 'audio/ogg']
        audioMimeType = supportedTypes.find(type => MediaRecorder.isTypeSupported(type))
        
        if (!audioMimeType) {
          // No supported format found, show error
          statusMessage.value = 'Error: Browser does not support audio recording'
          stream.getTracks().forEach(track => track.stop())
          return
        }
        
        // Log the selected format for debugging
        console.log('Selected audio MIME type:', audioMimeType)
        
        audioChunks = []
        mediaRecorder = new MediaRecorder(stream, {
          mimeType: audioMimeType
        })
        
        mediaRecorder.ondataavailable = (event) => {
          if (event.data.size > 0) {
            audioChunks.push(event.data)
          }
        }
        
        mediaRecorder.onstop = async () => {
          const audioBlob = new Blob(audioChunks, { type: audioMimeType })
          await analyzeAudio(audioBlob)
          
          // Stop all tracks
          stream.getTracks().forEach(track => track.stop())
        }
        
        mediaRecorder.start()
        isRecording.value = true
        statusMessage.value = '🎤 Recording audio... Speak now!'
        
      } catch (error) {
        console.error('Error accessing microphone:', error)
        statusMessage.value = `Error accessing microphone: ${error.message}`
      }
    }

    // Stop audio recording
    const stopAudioRecording = () => {
      if (mediaRecorder && isRecording.value) {
        mediaRecorder.stop()
        isRecording.value = false
        statusMessage.value = 'Recording stopped. Analyzing audio...'
      }
    }

    // Analyze audio
    const analyzeAudio = async (audioBlob) => {
      try {
        isAnalyzingAudio.value = true
        statusMessage.value = '🔄 Analyzing audio with GPT-4o Audio...'
        
        // Create FormData and append the audio
        const formData = new FormData()
        // Generate filename based on actual MIME type
        const extension = audioMimeType.split('/')[1] || 'webm'
        formData.append('file', audioBlob, `recording.${extension}`)
        
        // Send to backend API
        const response = await axios.post('/api/audio', formData, {
          headers: {
            'Content-Type': 'multipart/form-data'
          }
        })
        
        latestAudioAnalysis.value = response.data
        statusMessage.value = '✅ Audio analysis complete!'
        
      } catch (error) {
        console.error('Error analyzing audio:', error)
        statusMessage.value = `Error analyzing audio: ${error.response?.data?.detail || error.message}`
      } finally {
        isAnalyzingAudio.value = false
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
      stopAnalysis,
      // Audio recording
      isRecording,
      isAnalyzingAudio,
      latestAudioAnalysis,
      startAudioRecording,
      stopAudioRecording
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
