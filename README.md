# Animal-intrusion-detection
⭐ AI-powered wildlife monitoring and animal intrusion detection system using YOLO, OpenCV, and Flask with real-time camera monitoring, voice alerts, analytics dashboard, image/video detection, and intelligent farm protection features.

# Wildlife Guardian AI 🐾

An AI-powered smart wildlife monitoring and animal intrusion detection system using YOLO, OpenCV, Flask, and real-time voice alerts. Detects animals from live camera feed, uploaded images, and videos with an interactive analytics dashboard and alert system.

---

## ✨ Features

* 🎯 Real-time animal detection using YOLO
* 📷 Live webcam monitoring
* 🔊 Voice alerts with animal-specific sounds
* 🖼️ Image and video upload analysis
* 📊 Analytics dashboard with detection statistics
* 🧠 AI-based insights and predictions
* 🌐 Flask-based interactive web interface
* 💾 Detection history and database support
* 📈 YOLO confidence tracking and monitoring
* 🎨 Modern responsive frontend UI

---

## 🛠️ Technologies Used

* Python
* Flask
* OpenCV
* YOLOv8 / YOLOv3
* NumPy
* Pandas
* Matplotlib
* gTTS
* Pygame
* SQLite
* HTML/CSS/JavaScript

---

## 📂 Project Structure

```bash
├── app.py
├── analytics.py
├── database.py
├── detection_system.py
├── yolo_detection_system.py
├── templates/
├── static/
├── yolov3.cfg
├── yolov3.weights
├── yolov8n.pt
├── requirements.txt
└── detections.db
```

---

## 🚀 Installation

### 1️⃣ Clone the repository

```bash
git clone <your-repository-link>
cd wildlife-guardian-ai
```

### 2️⃣ Create virtual environment

```bash
python -m venv venv
```

### 3️⃣ Activate virtual environment

#### Windows

```bash
venv\Scripts\activate
```

#### Linux / Mac

```bash
source venv/bin/activate
```

### 4️⃣ Install dependencies

```bash
pip install -r requirements.txt
```

### 5️⃣ Run the application

```bash
python app.py
```

---

## 🌐 Access the Application

### Main Application

```bash
http://localhost:5000
```

### Analytics Dashboard

```bash
http://localhost:5000/dashboard
```

### Health Check API

```bash
http://localhost:5000/api/health
```

---

## 🎯 Supported Animals

* Dog
* Cat
* Bird
* Cow
* Horse
* Sheep
* Elephant
* Bear

---

## 🔊 Voice Alert System

The system generates:

* Real-time audio alerts
* Animal-specific sound notifications
* Emergency intrusion warnings

Powered using:

* gTTS
* Pygame audio engine

---

## 📊 Analytics Features

* Detection trends
* Peak activity hours
* Animal frequency analysis
* YOLO confidence analytics
* Risk level predictions
* AI-generated recommendations

---

## 🧠 How It Works

1. Webcam captures live frames.
2. YOLO processes frames for animal detection.
3. OpenCV draws bounding boxes and labels.
4. Voice alerts are generated automatically.
5. Detection data is stored in the database.
6. Analytics dashboard visualizes insights.

---

## 📸 Demo Features

* Live camera monitoring
* Upload image/video detection
* Real-time dashboard analytics
* Voice alert notifications
* Interactive animal sound board

---

## 🔮 Future Enhancements

* SMS & Email alerts
* IoT-based farm protection
* Cloud deployment
* Drone surveillance integration
* Night vision support
* Custom-trained wildlife models
* Mobile application support

---

## 👩‍💻 Developed By

**Sahana Surimutt**

