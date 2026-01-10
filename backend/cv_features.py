"""
CV Feature Extraction Service
Extracts computer vision features for behavioral analysis.
Features: head pose, eye gaze, motion level
"""
import mediapipe as mp
import cv2
import numpy as np
from typing import Dict, Optional
import logging

logger = logging.getLogger(__name__)

class CVFeatureExtractor:
    """Extract CV features from video frames using MediaPipe"""
    
    def __init__(self):
        # Initialize MediaPipe Face Mesh
        self.mp_face_mesh = mp.solutions.face_mesh
        self.face_mesh = self.mp_face_mesh.FaceMesh(
            static_image_mode=True,
            max_num_faces=1,
            refine_landmarks=True,
            min_detection_confidence=0.5
        )
        
        # Store previous frame for motion detection
        self.prev_frame = None
    
    def extract_features(self, image_bytes: bytes) -> Dict[str, any]:
        """
        Extract CV features from image
        
        Args:
            image_bytes: Image data in bytes
            
        Returns:
            Dictionary with CV features:
            - head_pitch: Head tilt up/down (degrees)
            - head_yaw: Head turn left/right (degrees)
            - head_roll: Head tilt left/right (degrees)
            - eye_gaze: "on_screen", "away", or "unknown"
            - motion_level: "low", "medium", or "high"
        """
        try:
            # Decode image
            nparr = np.frombuffer(image_bytes, np.uint8)
            image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            
            if image is None:
                logger.error("Failed to decode image")
                return self._default_features()
            
            # Convert BGR to RGB
            rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            
            # Process with MediaPipe
            results = self.face_mesh.process(rgb_image)
            
            if not results.multi_face_landmarks:
                logger.info("No face detected")
                return self._default_features()
            
            # Get first face landmarks
            face_landmarks = results.multi_face_landmarks[0]
            
            # Extract head pose
            head_pose = self._estimate_head_pose(face_landmarks, rgb_image.shape)
            
            # Extract eye gaze
            eye_gaze = self._estimate_eye_gaze(face_landmarks, head_pose)
            
            # Calculate motion level
            motion_level = self._calculate_motion(image)
            
            return {
                "head_pitch": round(head_pose["pitch"], 1),
                "head_yaw": round(head_pose["yaw"], 1),
                "head_roll": round(head_pose["roll"], 1),
                "eye_gaze": eye_gaze,
                "motion_level": motion_level
            }
            
        except Exception as e:
            logger.error(f"Error extracting CV features: {str(e)}")
            return self._default_features()
    
    def _estimate_head_pose(self, face_landmarks, image_shape) -> Dict[str, float]:
        """Estimate head pose angles from face landmarks"""
        height, width = image_shape[:2]
        
        # Key landmark points for head pose estimation
        # Nose tip
        nose_tip = face_landmarks.landmark[1]
        # Chin
        chin = face_landmarks.landmark[152]
        # Left eye outer corner
        left_eye = face_landmarks.landmark[33]
        # Right eye outer corner
        right_eye = face_landmarks.landmark[263]
        # Left mouth corner
        left_mouth = face_landmarks.landmark[61]
        # Right mouth corner
        right_mouth = face_landmarks.landmark[291]
        
        # Convert normalized coordinates to pixel coordinates
        nose_2d = np.array([nose_tip.x * width, nose_tip.y * height])
        chin_2d = np.array([chin.x * width, chin.y * height])
        left_eye_2d = np.array([left_eye.x * width, left_eye.y * height])
        right_eye_2d = np.array([right_eye.x * width, right_eye.y * height])
        
        # Calculate pitch (up/down tilt)
        # Negative = looking down, Positive = looking up
        face_height = np.linalg.norm(nose_2d - chin_2d)
        nose_y_position = (nose_tip.y - 0.5) * 2  # Normalize to -1 to 1
        pitch = nose_y_position * -30  # Scale to degrees
        
        # Calculate yaw (left/right turn)
        # Negative = turned left, Positive = turned right
        eye_center_x = (left_eye.x + right_eye.x) / 2
        nose_offset = (nose_tip.x - eye_center_x) * 2  # Normalize
        yaw = nose_offset * 30  # Scale to degrees
        
        # Calculate roll (head tilt)
        # Negative = tilted left, Positive = tilted right
        eye_angle = np.arctan2(
            right_eye_2d[1] - left_eye_2d[1],
            right_eye_2d[0] - left_eye_2d[0]
        )
        roll = np.degrees(eye_angle)
        
        return {
            "pitch": pitch,
            "yaw": yaw,
            "roll": roll
        }
    
    def _estimate_eye_gaze(self, face_landmarks, head_pose: Dict[str, float]) -> str:
        """Estimate if eyes are looking at screen or away"""
        # Simple heuristic based on head pose
        pitch = head_pose["pitch"]
        yaw = head_pose["yaw"]
        
        # If head is roughly facing forward, assume on_screen
        if abs(pitch) < 20 and abs(yaw) < 25:
            return "on_screen"
        else:
            return "away"
    
    def _calculate_motion(self, current_frame) -> str:
        """Calculate motion level by comparing with previous frame"""
        # Convert to grayscale for motion detection
        gray = cv2.cvtColor(current_frame, cv2.COLOR_BGR2GRAY)
        gray = cv2.GaussianBlur(gray, (21, 21), 0)
        
        if self.prev_frame is None:
            self.prev_frame = gray
            return "low"
        
        # Compute difference between current and previous frame
        frame_delta = cv2.absdiff(self.prev_frame, gray)
        thresh = cv2.threshold(frame_delta, 25, 255, cv2.THRESH_BINARY)[1]
        
        # Calculate percentage of changed pixels
        motion_pixels = np.sum(thresh > 0)
        total_pixels = thresh.shape[0] * thresh.shape[1]
        motion_percent = (motion_pixels / total_pixels) * 100
        
        # Update previous frame
        self.prev_frame = gray
        
        # Classify motion level
        if motion_percent < 1:
            return "low"
        elif motion_percent < 5:
            return "medium"
        else:
            return "high"
    
    def _default_features(self) -> Dict[str, any]:
        """Return default features when detection fails"""
        return {
            "head_pitch": 0,
            "head_yaw": 0,
            "head_roll": 0,
            "eye_gaze": "unknown",
            "motion_level": "low"
        }
    
    def cleanup(self):
        """Cleanup resources"""
        if self.face_mesh:
            self.face_mesh.close()
