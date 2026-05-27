from yolo_detection_system import YOLOAnimalDetectionSystem
import cv2
import numpy as np

def test_yolo():
    print("🧪 TESTING REAL YOLO DETECTION...")
    
    detector = YOLOAnimalDetectionSystem()
    
    if detector.model is None:
        print("❌ YOLO model not loaded. Check installation.")
        return
    
    print("✅ YOLO model loaded successfully!")
    
    # Test with sample images or camera
    print("\n🔍 Testing detection...")
    
    # Create a test frame (you can replace this with actual camera)
    frame = np.ones((480, 640, 3), dtype=np.uint8) * 128
    
    # Add some shapes to simulate objects
    cv2.rectangle(frame, (100, 100), (200, 200), (0, 0, 255), -1)  # Red rectangle
    cv2.circle(frame, (400, 200), 50, (255, 0, 0), -1)  # Blue circle
    
    processed_frame, detections = detector.process_frame(frame)
    
    if detections:
        for detection in detections:
            print(f"✅ YOLO Detected: {detection['class']} (confidence: {detection['confidence']:.2f})")
    else:
        print("❌ No objects detected (expected for simple shapes)")
    
    print("\n📊 Stats:")
    stats = detector.get_detection_stats()
    for key, value in stats.items():
        if key != 'detection_history':
            print(f"  {key}: {value}")

if __name__ == "__main__":
    test_yolo()