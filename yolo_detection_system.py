import cv2
import numpy as np
import os
import time
from threading import Thread
import warnings
import pygame
from gtts import gTTS
from ultralytics import YOLO
warnings.filterwarnings('ignore')

# Initialize pygame mixer for audio
try:
    pygame.mixer.init()
    pygame.mixer.set_num_channels(8)
    print("✅ Audio system initialized")
except Exception as e:
    print(f"❌ Audio system failed: {e}")

class YOLOAnimalDetectionSystem:
    def __init__(self):
        print("🚀 Initializing REAL YOLO Animal Detection System...")
        
        # Animal classes from COCO dataset that we care about
        self.target_animals = {
            0: 'person', 14: 'bird', 15: 'cat', 16: 'dog', 
            17: 'horse', 18: 'sheep', 19: 'cow', 20: 'elephant',
            21: 'bear', 22: 'zebra', 23: 'giraffe'
        }
        
        # Load YOLO model
        self.model = self.load_yolo_model()
        
        # Detection settings
        self.confidence_threshold = 0.5
        self.last_alert_time = 0
        self.alert_cooldown = 10
        
        # Detection statistics
        self.detection_count = 0
        self.last_detected_animal = None
        self.detection_history = []
        
        # Voice alert queue
        self.alert_queue = []
        self.is_playing_audio = False
        
        print("✅ REAL YOLO Animal Detection System initialized successfully!")
    
    def load_yolo_model(self):
        """Load YOLOv8 model - it will auto-download on first run"""
        try:
            print("📥 Loading YOLOv8 model...")
            model = YOLO('yolov8n.pt')  # This will download if not exists
            print("✅ YOLOv8 model loaded successfully!")
            return model
        except Exception as e:
            print(f"❌ Error loading YOLO model: {e}")
            print("💡 Try running: pip install ultralytics==8.0.186")
            return None
    
    def generate_voice_alert(self, animal_type):
        """Generate voice alert for detected animal"""
        try:
            alert_text = f"Alert! {animal_type} detected!"
            print(f"🔊 {alert_text}")
            
            # Create alerts directory
            os.makedirs('static/alerts', exist_ok=True)
            
            # Generate TTS audio file
            tts = gTTS(text=alert_text, lang='en', slow=False)
            alert_path = f"static/alerts/alert_{animal_type}_{int(time.time())}.mp3"
            tts.save(alert_path)
            
            # Play audio in separate thread
            audio_thread = Thread(target=self._play_audio_thread, args=(alert_path, animal_type))
            audio_thread.daemon = True
            audio_thread.start()
                
        except Exception as e:
            print(f"❌ Error generating voice alert: {e}")
            self.play_fallback_sound()
    
    def _play_audio_thread(self, audio_path, animal_type):
        """Thread for playing audio"""
        try:
            if os.path.exists(audio_path):
                channel = pygame.mixer.Channel(0)
                sound = pygame.mixer.Sound(audio_path)
                channel.play(sound)
                
                print(f"🎵 Playing audio: {animal_type}")
                
                # Wait for playback to complete
                while channel.get_busy():
                    time.sleep(0.1)
                
                # Clean up
                try:
                    os.remove(audio_path)
                except:
                    pass
                    
            else:
                print(f"❌ Audio file not found: {audio_path}")
                self.play_fallback_sound()
                
        except Exception as e:
            print(f"❌ Error in audio thread: {e}")
            self.play_fallback_sound()
        
        finally:
            self.is_playing_audio = False
            
            # Play next queued alert
            if self.alert_queue:
                next_animal = self.alert_queue.pop(0)
                time.sleep(1)
                self.generate_voice_alert(next_animal)
    
    def play_fallback_sound(self):
        """Play fallback system beep sound"""
        try:
            import winsound
            winsound.Beep(1000, 500)
        except:
            print("⚠️ Could not play fallback sound")
    
    def play_animal_sound(self, animal_type):
        """Play specific animal sound when clicked"""
        try:
            # Define animal sounds
            animal_sounds = {
                'dog': 'Woof Woof',
                'cat': 'Meow Meow', 
                'bird': 'Tweet Tweet',
                'cow': 'Moo Moo',
                'horse': 'Neigh Neigh',
                'sheep': 'Baa Baa',
                'elephant': 'Trumpet',
                'bear': 'Growl',
                'zebra': 'Bray',
                'giraffe': 'Bleat'
            }
            
            sound_text = animal_sounds.get(animal_type, f"{animal_type} sound")
            alert_text = f"{sound_text}! {animal_type} detected!"
            
            print(f"🔊 Generating sound for: {animal_type}")
            
            # Create alerts directory
            os.makedirs('static/alerts', exist_ok=True)
            
            # Generate TTS for animal sound
            tts = gTTS(text=alert_text, lang='en', slow=False)
            sound_path = f"static/alerts/{animal_type}_sound_{int(time.time())}.mp3"
            tts.save(sound_path)
            
            # Play in separate thread
            audio_thread = Thread(target=self._play_audio_thread, args=(sound_path, animal_type))
            audio_thread.daemon = True
            audio_thread.start()
            
            print(f"🔊 Played {animal_type} sound: {alert_text}")
            
        except Exception as e:
            print(f"❌ Error playing animal sound: {e}")
            self.play_fallback_sound()
    
    def process_frame(self, frame):
        """Process frame with REAL YOLO detection"""
        detections = []
        current_time = time.time()
        
        if self.model is None:
            return frame, detections
        
        try:
            # Run YOLO inference
            results = self.model(frame, verbose=False)  # verbose=False to reduce output
            
            for result in results:
                for box in result.boxes:
                    confidence = box.conf.item()
                    class_id = int(box.cls.item())
                    
                    # Check if it's an animal we care about and confidence is high enough
                    if (class_id in self.target_animals and 
                        confidence > self.confidence_threshold and
                        self.target_animals[class_id] not in ['person']):  # Skip person
                        
                        animal_type = self.target_animals[class_id]
                        
                        # Get bounding box coordinates
                        x1, y1, x2, y2 = box.xyxy[0].tolist()
                        x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)
                        
                        # Draw bounding box
                        color = (0, 255, 0)  # Green
                        cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
                        
                        # Add label with background
                        label = f"{animal_type}: {confidence:.2f}"
                        label_size = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.7, 2)[0]
                        cv2.rectangle(frame, (x1, y1-label_size[1]-10), 
                                    (x1+label_size[0], y1), color, -1)
                        cv2.putText(frame, label, (x1, y1-10), 
                                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
                        
                        detection_data = {
                            'class': animal_type,
                            'confidence': float(confidence),
                            'bbox': [x1, y1, x2, y2],
                            'timestamp': time.strftime('%H:%M:%S')
                        }
                        
                        detections.append(detection_data)
                        
                        # Trigger voice alert with cooldown
                        if (current_time - self.last_alert_time > self.alert_cooldown and
                            animal_type != self.last_detected_animal):
                            
                            self.last_alert_time = current_time
                            self.detection_count += 1
                            self.last_detected_animal = animal_type
                            
                            # Add to history
                            self.detection_history.append({
                                'animal': animal_type,
                                'confidence': confidence,
                                'timestamp': time.strftime('%Y-%m-%d %H:%M:%S')
                            })
                            
                            # Keep history manageable
                            if len(self.detection_history) > 50:
                                self.detection_history.pop(0)
                            
                            # Generate voice alert
                            self.generate_voice_alert(animal_type)
                            
        except Exception as e:
            print(f"❌ Error in YOLO detection: {e}")
        
        return frame, detections
    
    def process_video_file(self, video_path):
        """Process uploaded video file with YOLO"""
        print(f"🎥 Processing video with YOLO: {video_path}")
        cap = cv2.VideoCapture(video_path)
        results = []
        
        frame_count = 0
        while True:
            ret, frame = cap.read()
            if not ret:
                break
                
            if frame_count % 10 == 0:  # Process every 10th frame
                processed_frame, detections = self.process_frame(frame)
                if detections:
                    results.extend(detections)
            
            frame_count += 1
        
        cap.release()
        return results
    
    def process_image_file(self, image_path):
        """Process uploaded image file with YOLO"""
        print(f"🖼️ Processing image with YOLO: {image_path}")
        frame = cv2.imread(image_path)
        
        if frame is None:
            print(f"❌ Could not load image: {image_path}")
            return [], None
        
        processed_frame, detections = self.process_frame(frame)
        
        # Save processed image
        output_path = f"static/uploads/processed_{os.path.basename(image_path)}"
        cv2.imwrite(output_path, processed_frame)
        
        return detections, output_path
    
    def get_detection_stats(self):
        """Get detection statistics"""
        animal_counts = {}
        for detection in self.detection_history:
            animal = detection['animal']
            animal_counts[animal] = animal_counts.get(animal, 0) + 1
        
        most_common = max(animal_counts, key=animal_counts.get) if animal_counts else 'None'
        
        return {
            'total_detections': self.detection_count,
            'last_animal': self.last_detected_animal,
            'last_alert': time.strftime('%H:%M:%S', time.localtime(self.last_alert_time)) 
                         if self.last_alert_time > 0 else 'Never',
            'system_status': 'Active (YOLO)',
            'animal_counts': animal_counts,
            'most_common_animal': most_common,
            'detection_history': self.detection_history[-10:]
        }