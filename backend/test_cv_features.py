"""
Test script for CV feature extraction
Demonstrates the extraction of behavioral features from an image
"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from cv_features import CVFeatureExtractor
import cv2
import numpy as np

def create_test_image():
    """Create a simple test image with a circle (simulating a face)"""
    img = np.ones((480, 640, 3), dtype=np.uint8) * 200  # Light gray background
    
    # Draw a simple face-like structure
    center = (320, 240)
    cv2.circle(img, center, 100, (150, 150, 150), -1)  # Face circle
    cv2.circle(img, (280, 220), 10, (50, 50, 50), -1)   # Left eye
    cv2.circle(img, (360, 220), 10, (50, 50, 50), -1)   # Right eye
    cv2.ellipse(img, (320, 260), (40, 20), 0, 0, 180, (50, 50, 50), 2)  # Smile
    
    return img

def test_cv_extraction():
    """Test CV feature extraction with a sample image"""
    print("=" * 60)
    print("CV Feature Extraction Test")
    print("=" * 60)
    
    # Create test image
    print("\n1. Creating test image...")
    img = create_test_image()
    
    # Encode to JPEG
    print("2. Encoding image to JPEG...")
    success, buffer = cv2.imencode('.jpg', img)
    if not success:
        print("Error: Failed to encode image")
        return False
    
    img_bytes = buffer.tobytes()
    print(f"   Image size: {len(img_bytes)} bytes")
    
    # Initialize extractor
    print("\n3. Initializing CV Feature Extractor...")
    extractor = CVFeatureExtractor()
    
    # Extract features
    print("4. Extracting CV features...")
    features = extractor.extract_features(img_bytes)
    
    # Display results
    print("\n" + "=" * 60)
    print("EXTRACTED CV FEATURES")
    print("=" * 60)
    print(f"  Head Pitch:   {features['head_pitch']:>6.1f}° (negative=down, positive=up)")
    print(f"  Head Yaw:     {features['head_yaw']:>6.1f}° (negative=left, positive=right)")
    print(f"  Head Roll:    {features['head_roll']:>6.1f}° (head tilt)")
    print(f"  Eye Gaze:     {features['eye_gaze']:>10} (on_screen/away/unknown)")
    print(f"  Motion Level: {features['motion_level']:>10} (low/medium/high)")
    print("=" * 60)
    
    # Cleanup
    extractor.cleanup()
    
    # Interpretation
    print("\n📊 INTERPRETATION:")
    print("  Note: This is a simple test image without a real face.")
    print("  With a real face photo, MediaPipe will detect facial landmarks")
    print("  and extract meaningful head pose and gaze information.")
    
    print("\n✅ Test completed successfully!")
    return True

def test_multiple_frames():
    """Test motion detection with multiple frames"""
    print("\n" + "=" * 60)
    print("Motion Detection Test (Multiple Frames)")
    print("=" * 60)
    
    extractor = CVFeatureExtractor()
    
    # Create 3 frames with increasing change
    frames = []
    for i in range(3):
        img = np.ones((480, 640, 3), dtype=np.uint8) * (200 + i * 10)
        # Add some random noise to simulate motion
        noise = np.random.randint(-20, 20, img.shape, dtype=np.int16)
        img = np.clip(img.astype(np.int16) + noise * i, 0, 255).astype(np.uint8)
        
        success, buffer = cv2.imencode('.jpg', img)
        frames.append(buffer.tobytes())
    
    print("\nExtracting features from 3 consecutive frames...")
    for i, frame_bytes in enumerate(frames):
        features = extractor.extract_features(frame_bytes)
        print(f"  Frame {i+1}: Motion Level = {features['motion_level']}")
    
    extractor.cleanup()
    print("✅ Motion detection test completed!")

if __name__ == "__main__":
    print("\n🔬 Starting CV Feature Extraction Tests\n")
    
    try:
        # Run basic extraction test
        if test_cv_extraction():
            # Run motion detection test
            test_multiple_frames()
            
            print("\n" + "=" * 60)
            print("All tests passed! 🎉")
            print("=" * 60)
            print("\n💡 Next Steps:")
            print("  1. Run the backend server: python main.py")
            print("  2. Run the frontend: cd ../frontend && npm run dev")
            print("  3. Test with a real camera in the browser")
            print()
    except Exception as e:
        print(f"\n❌ Error during testing: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
