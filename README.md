# Animal-intrusion-detection
⭐ AI-powered wildlife monitoring and animal intrusion detection system using YOLO, OpenCV, and Flask with real-time camera monitoring, voice alerts, analytics dashboard, image/video detection, and intelligent farm protection features.

# 🐾 Wildlife Guardian AI
---

## ✨ Features

- 🎯 Real-time animal detection using YOLOv8
- 📷 Live webcam monitoring
- 🔊 Voice alerts with animal-specific sounds
- 🖼️ Image and video upload analysis
- 📊 Analytics dashboard with detection statistics
- 🧠 AI-based insights and predictions
- 🌐 Flask-based interactive web interface
- 💾 Detection history and database support
- 📈 YOLO confidence tracking and monitoring
- 🎨 Modern responsive frontend UI
- ⚡ Real-time detection processing

---

## 🛠️ Technologies Used

- Python
- Flask
- OpenCV
- Ultralytics YOLOv8
- NumPy
- Pandas
- Matplotlib
- SQLite
- gTTS
- Pygame
- HTML/CSS/JavaScript

---

## 📂 Project Structure

```bash
WILDLIFE1/
│
├── static/
│   ├── css/
│   └── js/
│
├── templates/
│   ├── base.html
│   ├── dashboard.html
│   └── index.html
│
├── .gitignore
├── README.md
├── app.py
├── analytics.py
├── database.py
├── detection_system.py
├── yolo_detection_system.py
├── test_yolo.py
├── requirements.txt
└── yolov3.cfg
```

---

## 🚀 Installation

### 1️⃣ Clone the Repository

```bash
git clone https://github.com/Sahana-Surimutt/Animal-intrusion-detection.git
cd Animal-intrusion-detection
```

---

### 2️⃣ Create Virtual Environment

```bash
python -m venv venv
```

---

### 3️⃣ Activate Virtual Environment

#### Windows

```bash
venv\Scripts\activate
```

#### Linux / Mac

```bash
source venv/bin/activate
```

---

### 4️⃣ Install Dependencies

```bash
pip install -r requirements.txt
```

---

### 5️⃣ Install Ultralytics YOLO

```bash
pip install ultralytics
```

---

### 6️⃣ Run the Application

```bash
python app.py
```

---

## 🌐 Access the Application

### 🏠 Main Application

```bash
http://localhost:5000
```

### 📊 Analytics Dashboard

```bash
http://localhost:5000/dashboard
```

### 🔧 Health Check API

```bash
http://localhost:5000/api/health
```

---

## 📥 YOLO Model Information

- YOLOv8 model automatically downloads during first execution.
- If required, YOLOv3 weights can be downloaded manually.

### Download YOLOv3 Weights

```bash
https://pjreddie.com/media/files/yolov3.weights
```

---

## 🎯 Supported Animals

- Dog
- Cat
- Bird
- Cow
- Horse
- Sheep
- Elephant
- Bear
- Zebra
- Giraffe

---

## 🔊 Voice Alert System

The system generates:

- Real-time voice alerts
- Animal-specific sound notifications
- Emergency intrusion warnings
- Smart alert cooldown handling

Powered using:

- gTTS
- Pygame audio engine

---

## 📊 Analytics Features

- Detection trends analysis
- Peak activity hour tracking
- Animal frequency statistics
- YOLO confidence analytics
- Risk level prediction
- AI-generated recommendations
- Detection history tracking
- Real-time monitoring insights

---

## 🧠 How It Works

1. Webcam captures live video frames.
2. YOLOv8 processes frames for animal detection.
3. OpenCV draws bounding boxes and confidence labels.
4. Voice alerts are generated automatically.
5. Detection data is stored in the database.
6. Analytics dashboard visualizes insights and trends.

---

## 📸 Demo Features

- 🎥 Live camera monitoring
- 🖼️ Upload image/video detection
- 📊 Real-time analytics dashboard
- 🔊 Voice alert notifications
- 📈 Detection statistics visualization

---

## 🔮 Future Enhancements

- SMS & Email alert system
- IoT-based farm protection
- Cloud deployment support
- Drone surveillance integration
- Night vision camera support
- Custom-trained wildlife detection models
- Mobile application integration
- Multi-camera support

---

### 🎯 Real-time Detection

<img width="640" height="480" alt="snapshot_20251202_200804" src="https://github.com/user-attachments/assets/024eb87e-c92a-462a-ba33-add2c54db246" />

---

## 👩‍💻 Developed By

**Sahana Surimutt**

---

## 📜 License

This project is developed for educational and research purposes.
