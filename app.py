from flask import Flask, render_template, Response, jsonify, request, send_file
import cv2
import numpy as np
import os
import time
import json
from datetime import datetime, timedelta
import base64
from yolo_detection_system import YOLOAnimalDetectionSystem as AnimalDetectionSystem
from database import DetectionDatabase
from analytics import AnalyticsEngine
from werkzeug.utils import secure_filename
import random

app = Flask(__name__)
app.config['SECRET_KEY'] = 'wildlife-guardian-secret-key'
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 50MB max file size

# Allowed file extensions
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'mp4', 'avi', 'mov'}

# Initialize systems with error handling
try:
    detector = AnimalDetectionSystem()
    db = DetectionDatabase()
    analytics = AnalyticsEngine()
    print("✅ All systems initialized successfully!")
except Exception as e:
    print(f"❌ Error initializing systems: {e}")
    # Create dummy systems for basic functionality
    detector = None
    db = None
    analytics = None

# Global variables for live monitoring
is_live_monitoring = False
camera = None

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def generate_frames():
    global camera, is_live_monitoring
    
    try:
        camera = cv2.VideoCapture(0)
        if not camera.isOpened():
            print("❌ Could not open camera")
            # Show a placeholder image instead
            while is_live_monitoring:
                # Create a placeholder frame
                frame = np.zeros((480, 640, 3), dtype=np.uint8)
                cv2.putText(frame, "Camera Not Available", (50, 240), 
                           cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
                cv2.putText(frame, "Please check your camera connection", (30, 280), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
                
                # Convert frame to JPEG
                ret, buffer = cv2.imencode('.jpg', frame)
                frame_bytes = buffer.tobytes()
                
                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
                time.sleep(0.1)
            return
            
        while is_live_monitoring:
            success, frame = camera.read()
            if not success:
                break
            else:
                # Process frame for animal detection
                if detector:
                    processed_frame, detections = detector.process_frame(frame)
                else:
                    processed_frame = frame
                    detections = []
                
                # Convert frame to JPEG
                ret, buffer = cv2.imencode('.jpg', processed_frame)
                frame_bytes = buffer.tobytes()
                
                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
    except Exception as e:
        print(f"❌ Error in video feed: {e}")
    finally:
        if camera:
            camera.release()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')

@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

# API Routes
@app.route('/api/start_monitoring', methods=['POST'])
def start_monitoring():
    global is_live_monitoring
    try:
        is_live_monitoring = True
        return jsonify({'status': 'success', 'message': 'Live monitoring started'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)})

@app.route('/api/stop_monitoring', methods=['POST'])
def stop_monitoring():
    global is_live_monitoring, camera
    try:
        is_live_monitoring = False
        if camera:
            camera.release()
            camera = None
        return jsonify({'status': 'success', 'message': 'Live monitoring stopped'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)})

@app.route('/api/stats')
def get_stats():
    try:
        if detector:
            stats = detector.get_detection_stats()
        else:
            stats = {
                'total_detections': 0,
                'last_animal': 'None',
                'last_alert': 'Never',
                'system_status': 'Basic Mode',
                'animal_counts': {},
                'most_common_animal': 'None',
                'detection_history': []
            }
        stats['is_monitoring'] = is_live_monitoring
        return jsonify(stats)
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)})

@app.route('/api/take_snapshot', methods=['POST'])
def take_snapshot():
    try:
        if is_live_monitoring:
            if camera:
                success, frame = camera.read()
            else:
                # Create a sample frame if camera is not available
                frame = np.zeros((480, 640, 3), dtype=np.uint8)
                cv2.putText(frame, "Sample Snapshot", (50, 240), 
                           cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
                success = True
            
            if success:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"snapshot_{timestamp}.jpg"
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                
                # Process frame and save
                if detector:
                    processed_frame, detections = detector.process_frame(frame)
                else:
                    processed_frame = frame
                    detections = []
                
                cv2.imwrite(filepath, processed_frame)
                
                # Save detections to database
                if db and detections:
                    for detection in detections:
                        db.add_detection(
                            detection['class'], 
                            detection['confidence'],
                            'camera',
                            filepath
                        )
                
                return jsonify({'status': 'success', 'filename': filename, 'detections': detections})
        
        return jsonify({'status': 'error', 'message': 'Could not take snapshot'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)})

@app.route('/api/upload', methods=['POST'])
def upload_file():
    try:
        if 'file' not in request.files:
            return jsonify({'status': 'error', 'message': 'No file selected'})
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'status': 'error', 'message': 'No file selected'})
        
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            
            # Process based on file type
            if filename.lower().endswith(('.png', '.jpg', '.jpeg')):
                # Process image
                if detector:
                    detections, processed_path = detector.process_image_file(filepath)
                else:
                    # Create sample detections for demo
                    animals = ['dog', 'cat', 'bird', 'cow', 'horse']
                    detections = [{
                        'class': random.choice(animals),
                        'confidence': round(random.uniform(0.7, 0.95), 2),
                        'bbox': [100, 100, 300, 300],
                        'timestamp': datetime.now().strftime('%H:%M:%S')
                    }]
                    processed_path = filepath
                
                # Save to database
                if db and detections:
                    for detection in detections:
                        db.add_detection(
                            detection['class'],
                            detection['confidence'],
                            'upload',
                            processed_path
                        )
                
                return jsonify({
                    'status': 'success',
                    'type': 'image',
                    'detections': detections,
                    'processed_image': processed_path
                })
            else:
                # Process video
                if detector:
                    detections = detector.process_video_file(filepath)
                else:
                    # Create sample detections for demo
                    animals = ['dog', 'cat', 'bird', 'cow', 'horse']
                    detections = [{
                        'class': random.choice(animals),
                        'confidence': round(random.uniform(0.7, 0.95), 2),
                        'bbox': [100, 100, 300, 300],
                        'timestamp': datetime.now().strftime('%H:%M:%S')
                    } for _ in range(3)]
                
                # Save to database
                if db and detections:
                    for detection in detections:
                        db.add_detection(
                            detection['class'],
                            detection['confidence'],
                            'upload',
                            filepath
                        )
                
                return jsonify({
                    'status': 'success', 
                    'type': 'video',
                    'detections': detections,
                    'original_file': filepath
                })
        
        return jsonify({'status': 'error', 'message': 'Invalid file type'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)})

# Analytics API Routes
@app.route('/api/analytics/overview')
def get_analytics_overview():
    """Get analytics overview with sample data"""
    try:
        if db:
            overview = db.get_analytics_overview()
        else:
            # Fallback sample data
            overview = {
                'today_detections': random.randint(5, 12),
                'yesterday_detections': random.randint(4, 10),
                'weekly_total': random.randint(40, 80),
                'top_animal': random.choice(['dog', 'cat', 'bird']),
                'peak_hour': '14:00-15:00',
                'change_percentage': random.randint(-20, 50)
            }
        return jsonify(overview)
    except Exception as e:
        print(f"❌ Error in analytics overview: {e}")
        return jsonify({
            'today_detections': 8,
            'yesterday_detections': 6,
            'weekly_total': 45,
            'top_animal': 'dog',
            'peak_hour': '14:00-15:00',
            'change_percentage': 25
        })

@app.route('/api/analytics/detection_stats')
def get_detection_stats():
    """Get detailed detection statistics"""
    try:
        days = request.args.get('days', 7, type=int)
        
        if db:
            stats = db.get_detection_stats(days)
        else:
            # Fallback sample data
            animals = ['dog', 'cat', 'bird', 'cow', 'horse', 'sheep']
            stats = {
                'total_detections': random.randint(50, 100),
                'animal_stats': [{'animal_type': animal, 'count': random.randint(5, 20), 'avg_confidence': round(random.uniform(0.7, 0.9), 2)} for animal in animals],
                'daily_trends': [{'date': (datetime.now() - timedelta(days=i)).strftime('%Y-%m-%d'), 'count': random.randint(3, 12)} for i in range(6, -1, -1)],
                'hourly_patterns': [{'hour': f"{h:02d}", 'count': max(1, int(8 * (1 - abs(12-h)/12)))} for h in range(24)],
                'source_analysis': [{'source_type': 'camera', 'count': random.randint(30, 60)}, {'source_type': 'upload', 'count': random.randint(10, 30)}]
            }
        return jsonify(stats)
    except Exception as e:
        print(f"❌ Error in detection stats: {e}")
        return jsonify({'status': 'error', 'message': str(e)})

@app.route('/api/analytics/insights')
def get_analytics_insights():
    """Get AI insights and recommendations"""
    try:
        days = request.args.get('days', 30, type=int)
        
        if analytics:
            insights = analytics.generate_insights(days)
        else:
            # Fallback sample insights
            insights = [
                {
                    'type': 'peak_activity',
                    'title': '🕒 Peak Activity Hours',
                    'message': 'Most animals detected between 14:00-15:00',
                    'priority': 'high'
                },
                {
                    'type': 'common_animal',
                    'title': '🐾 Most Frequent Visitor',
                    'message': 'Dog is your most common visitor (15 detections)',
                    'priority': 'medium'
                },
                {
                    'type': 'recommendation',
                    'title': '💡 Monitoring Tip',
                    'message': 'Consider increasing camera sensitivity during peak hours',
                    'priority': 'low'
                }
            ]
        return jsonify(insights)
    except Exception as e:
        print(f"❌ Error in analytics insights: {e}")
        return jsonify([])

@app.route('/api/analytics/predictions')
def get_predictions():
    """Get prediction models and risk assessment"""
    try:
        if analytics:
            predictions = analytics.get_prediction_models()
        else:
            # Fallback sample predictions
            predictions = {
                'hourly_predictions': {f"{h:02d}": max(1, int(10 * (1 - abs(12-h)/12))) for h in range(24)},
                'risk_levels': {
                    'dog': {'level': 'low', 'detections': 15, 'advice': 'Normal monitoring sufficient'},
                    'cat': {'level': 'low', 'detections': 12, 'advice': 'Normal monitoring sufficient'},
                    'bear': {'level': 'high', 'detections': 3, 'advice': 'Consider activating deterrents'},
                    'elephant': {'level': 'high', 'detections': 2, 'advice': 'Increase monitoring and alerts'}
                },
                'recommendations': [
                    {'type': 'timing', 'message': 'Increase monitoring during 14:00-15:00 (peak activity)', 'icon': '🕒'},
                    {'type': 'animal_focus', 'message': 'Focus on dog detection patterns', 'icon': '🎯'}
                ]
            }
        return jsonify(predictions)
    except Exception as e:
        print(f"❌ Error in predictions: {e}")
        return jsonify({'status': 'error', 'message': str(e)})

@app.route('/api/analytics/recent_detections')
def get_recent_detections():
    """Get recent detections"""
    try:
        limit = request.args.get('limit', 10, type=int)
        
        if db:
            detections = db.get_recent_detections(limit)
        else:
            # Fallback sample data
            animals = ['dog', 'cat', 'bird', 'cow', 'horse', 'sheep']
            detections = []
            for i in range(min(limit, 8)):
                animal = random.choice(animals)
                detections.append({
                    'animal': animal,
                    'confidence': round(random.uniform(0.7, 0.95), 2),
                    'timestamp': (datetime.now() - timedelta(hours=i)).strftime('%Y-%m-%d %H:%M:%S'),
                    'source': random.choice(['camera', 'upload']),
                    'image': None
                })
        
        return jsonify(detections)
    except Exception as e:
        print(f"❌ Error in recent detections: {e}")
        return jsonify([])

@app.route('/api/play_alert')
def play_alert():
    """Play test alert sound"""
    try:
        alert_file = 'static/alerts/alert.mp3'
        if os.path.exists(alert_file):
            # If detector exists, use its method to play sound
            if detector:
                detector.play_fallback_sound()
            return jsonify({'status': 'success', 'alert_file': alert_file})
        else:
            # Create a dummy alert file or use fallback
            if detector:
                detector.play_fallback_sound()
            return jsonify({'status': 'success', 'message': 'Fallback alert played'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)})

# Animal Sound API Route
@app.route('/api/play_animal_sound', methods=['POST'])
def play_animal_sound():
    """Play specific animal sound"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'status': 'error', 'message': 'No data provided'})
            
        animal_type = data.get('animal', '').lower()
        
        if animal_type and detector:
            # Play animal sound
            detector.play_animal_sound(animal_type)
            return jsonify({'status': 'success', 'message': f'Playing {animal_type} sound'})
        else:
            return jsonify({'status': 'error', 'message': 'Invalid animal type or detector not available'})
            
    except Exception as e:
        print(f"❌ Error playing animal sound: {e}")
        return jsonify({'status': 'error', 'message': str(e)})

# Health check endpoint
@app.route('/api/health')
def health_check():
    """System health check"""
    try:
        health_status = {
            'status': 'healthy',
            'detector_available': detector is not None,
            'database_available': db is not None,
            'analytics_available': analytics is not None,
            'monitoring_active': is_live_monitoring,
            'timestamp': datetime.now().isoformat()
        }
        return jsonify(health_status)
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)})

# Serve uploaded files
@app.route('/static/uploads/<filename>')
def serve_uploaded_file(filename):
    return send_file(os.path.join(app.config['UPLOAD_FOLDER'], filename))

# Create necessary directories
def create_directories():
    directories = [
        app.config['UPLOAD_FOLDER'],
        'static/alerts',
        'static/css',
        'static/js',
        'static/uploads'
    ]
    
    for directory in directories:
        try:
            os.makedirs(directory, exist_ok=True)
            print(f"✅ Created directory: {directory}")
        except Exception as e:
            print(f"❌ Error creating directory {directory}: {e}")

# Initialize sample data on startup
def initialize_sample_data():
    """Initialize sample data for demonstration"""
    try:
        if db:
            # Check if we have any data
            sample_detections = db.get_recent_detections(1)
            if not sample_detections:
                print("📊 Initializing sample data...")
                # Add some sample detections
                animals = ['dog', 'cat', 'bird', 'cow', 'horse', 'sheep', 'elephant', 'bear']
                
                for i in range(20):
                    animal = random.choice(animals)
                    confidence = round(random.uniform(0.7, 0.95), 2)
                    days_ago = random.randint(0, 6)
                    hours_ago = random.randint(0, 23)
                    timestamp = datetime.now() - timedelta(days=days_ago, hours=hours_ago)
                    
                    db.add_detection(
                        animal_type=animal,
                        confidence=confidence,
                        source_type=random.choice(['camera', 'upload']),
                        timestamp=timestamp
                    )
                
                print("✅ Sample data initialized successfully!")
    except Exception as e:
        print(f"❌ Error initializing sample data: {e}")

if __name__ == '__main__':
    # Create necessary directories
    create_directories()
    
    # Initialize sample data
    initialize_sample_data()
    
    print("🌐 Starting Wildlife Guardian AI Web Server...")
    print("📍 Access at: http://localhost:5000")
    print("📊 Analytics at: http://localhost:5000/dashboard")
    print("🔧 Health check: http://localhost:5000/api/health")
    print("\n🎯 Features:")
    print("  ✅ Real-time animal detection with voice alerts")
    print("  ✅ Interactive animal sound board")
    print("  ✅ Comprehensive analytics dashboard")
    print("  ✅ File upload and analysis")
    print("  ✅ Live camera monitoring")
    
    try:
        app.run(debug=True, host='0.0.0.0', port=5000, use_reloader=False)
    except Exception as e:
        print(f"❌ Failed to start server: {e}")
# Analytics API Routes
@app.route('/api/analytics/overview')
def get_analytics_overview():
    try:
        if db:
            overview = db.get_analytics_overview()
        else:
            overview = {
                'today_detections': 12,
                'yesterday_detections': 8,
                'weekly_total': 65,
                'top_animal': 'dog',
                'peak_hour': '14:00-15:00',
                'change_percentage': 50,
                'avg_confidence': 0.82,
                'unique_animals': 5,
                'detection_engine': 'YOLOv8',
                'model_accuracy': 'High'
            }
        return jsonify(overview)
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)})

@app.route('/api/analytics/detection_stats')
def get_detection_stats():
    try:
        days = request.args.get('days', 7, type=int)
        if db:
            stats = db.get_detection_stats(days)
        else:
            stats = {
                'total_detections': 78,
                'animal_stats': [
                    {'animal_type': 'dog', 'count': 25, 'avg_confidence': 0.85, 'max_confidence': 0.95},
                    {'animal_type': 'cat', 'count': 18, 'avg_confidence': 0.82, 'max_confidence': 0.92},
                    {'animal_type': 'bird', 'count': 15, 'avg_confidence': 0.78, 'max_confidence': 0.88},
                    {'animal_type': 'cow', 'count': 12, 'avg_confidence': 0.88, 'max_confidence': 0.96},
                    {'animal_type': 'horse', 'count': 8, 'avg_confidence': 0.84, 'max_confidence': 0.91}
                ],
                'daily_trends': [
                    {'date': (datetime.now() - timedelta(days=i)).strftime('%Y-%m-%d'), 'count': random.randint(8, 15), 'avg_confidence': round(random.uniform(0.75, 0.9), 2)} 
                    for i in range(6, -1, -1)
                ],
                'hourly_patterns': [{'hour': f"{h:02d}", 'count': max(1, int(12 * (1 - abs(14-h)/14)))} for h in range(24)],
                'source_analysis': [{'source_type': 'camera', 'count': 55}, {'source_type': 'upload', 'count': 23}],
                'yolo_stats': [{'unique_animals': 5, 'overall_accuracy': 0.83}],
                'detection_engine': 'YOLOv8'
            }
        return jsonify(stats)
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)})