# 👁️ Dockerized Eye Blink Detection & Fatigue Monitoring System

A real-time **computer vision eye-blink detection system** built with **Python, OpenCV, MediaPipe, Flask, WebSockets, and Docker**.

The application captures webcam video directly in the browser, sends frames to a Dockerized computer-vision backend, detects eye blinks using the **Eye Aspect Ratio (EAR)**, and streams the processed video and statistics back to the browser.

---

## 🎥 Demo

![Eye Blink Detection Docker Demo](assets/demo.gif)

---

## 🚀 Features

- 🎥 Real-time webcam capture through the browser
- 👁️ Eye landmark detection using MediaPipe Face Mesh
- 📐 Eye Aspect Ratio (EAR) based blink detection
- 🔢 Real-time blink counting
- 📊 Live EAR measurement
- ⏱️ Tracks time since the last blink
- 🔔 Browser notification after 5 seconds without blinking
- 🔄 Real-time communication using WebSockets
- 🐳 Fully Dockerized computer-vision backend
- 🌐 Flask web interface
- 📦 Reproducible Python dependencies
- ⚡ Real-time processed video streaming

---

## 🧠 How It Works

The system follows this pipeline:

```text
                ┌─────────────────────┐
                │   Browser Webcam    │
                └──────────┬──────────┘
                           │
                           │ Video Frames
                           ▼
                ┌─────────────────────┐
                │      WebSocket      │
                └──────────┬──────────┘
                           │
                           ▼
          ┌────────────────────────────────┐
          │       Docker Container          │
          │                                │
          │  Flask + Flask-Sock            │
          │          │                     │
          │          ▼                     │
          │      OpenCV                   │
          │          │                     │
          │          ▼                     │
          │    MediaPipe Face Mesh        │
          │          │                     │
          │          ▼                     │
          │    EAR Calculation             │
          │          │                     │
          │          ▼                     │
          │    Blink Detection             │
          └──────────────┬─────────────────┘
                         │
                         │ Processed Frame
                         │ + Blink Statistics
                         ▼
                ┌─────────────────────┐
                │      Browser        │
                │                     │
                │ Processed Video     │
                │ Blink Count        │
                │ EAR                 │
                │ Last Blink          │
                │ Notification        │
                └─────────────────────┘
```

---

## 📐 Blink Detection Algorithm

The system uses the **Eye Aspect Ratio (EAR)** to determine whether the eye is open or closed.

The EAR is calculated as:

```text
        ||p2 - p6|| + ||p3 - p5||
EAR =  ─────────────────────────────
              2 × ||p1 - p4||
```

Where:

- `p1` and `p4` represent the horizontal eye landmarks.
- `p2`, `p3`, `p5`, and `p6` represent vertical eye landmarks.

When the EAR falls below the configured threshold, the eye is considered closed.

Current threshold:

```python
EAR_THRESHOLD = 0.23
```

A blink is counted when the eye transitions from:

```text
OPEN → CLOSED → OPEN
```

---

## 🐳 Why Docker?

Docker isolates the computer-vision environment and makes the application easier to reproduce.

Instead of requiring every user to manually install:

- Python
- OpenCV
- MediaPipe
- NumPy
- Flask
- Flask-Sock

the required environment is packaged into a Docker image.

This makes the project easier to run consistently across different systems.

---

## 🛠️ Technologies Used

| Technology | Purpose |
|---|---|
| Python | Core programming language |
| OpenCV | Image processing |
| MediaPipe | Face and eye landmark detection |
| NumPy | Numerical calculations |
| Flask | Web application backend |
| Flask-Sock | WebSocket communication |
| JavaScript | Browser webcam and UI |
| WebSocket | Real-time frame transmission |
| Docker | Containerization |
| HTML/CSS | Web interface |

---

## 📁 Project Structure

```text
my_flask_app/
│
├── assets/
│   └── demo.gif
│
├── templates/
│   └── index.html
│
├── blink_detector.py
├── docker_app.py
├── Dockerfile
├── requirements.txt
├── .dockerignore
├── .gitignore
└── README.md
```

---

# 🐳 Running the Project with Docker

## 1. Prerequisites

Install:

- Docker Desktop
- A modern web browser with webcam support

Check Docker installation:

```bash
docker --version
```

Example:

```text
Docker version 28.x.x
```

---

## 2. Clone the Repository

```bash
git clone https://github.com/YOUR_USERNAME/YOUR_REPOSITORY.git
```

Move into the project directory:

```bash
cd YOUR_REPOSITORY
```

---

## 3. Build the Docker Image

Run:

```bash
docker build -t eye-blink-detector .
```

This command:

1. Reads the `Dockerfile`
2. Creates the Python environment
3. Installs the required dependencies
4. Copies the application into the image
5. Creates the Docker image

---

## 4. Run the Docker Container

Run:

```bash
docker run --rm -p 5000:5000 eye-blink-detector
```

The application will start inside the Docker container.

You should see Flask running on:

```text
http://0.0.0.0:5000
```

---

## 5. Open the Web Application

Open your browser and visit:

```text
http://localhost:5000
```

Allow the browser to access your webcam.

The application will then:

```text
Webcam
   ↓
Browser
   ↓
WebSocket
   ↓
Docker
   ↓
OpenCV + MediaPipe
   ↓
Blink Detection
   ↓
Processed Video
   ↓
Browser
```

---

# 🔔 Browser Notification

The application monitors the time elapsed since the last detected blink.

If no blink is detected for more than:

```text
5 seconds
```

the browser displays a notification:

```text
Blink Reminder

You haven't blinked for 5 seconds!
```

The notification is generated by the browser rather than the Docker container.

This architecture is intentional because Docker containers should not directly depend on the host operating system's desktop notification system.

---

# 🔌 WebSocket Communication

The application uses WebSockets for real-time communication.

The browser sends JPEG frames to:

```text
/ws
```

The Flask backend processes each frame and returns:

```json
{
    "image": "...",
    "blink_count": 10,
    "ear": 0.25,
    "last_blink": 1.4,
    "notification": false
}
```

The browser then updates the interface without refreshing the page.

---

# ⚙️ Configuration

The blink sensitivity can be modified in:

```text
docker_app.py
```

Current threshold:

```python
EAR_THRESHOLD = 0.23
```

A lower threshold generally requires the eye to close more before being considered a blink.

The notification interval can also be modified in the backend logic.

---

# 🧪 Local Development Without Docker

You can also run the Flask application directly using Python.

Create and activate a virtual environment:

```bash
python -m venv venv
```

Windows:

```bash
venv\Scripts\activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Run:

```bash
python docker_app.py
```

Then open:

```text
http://localhost:5000
```

---

# 🐳 Useful Docker Commands

### List running containers

```bash
docker ps
```

### List all containers

```bash
docker ps -a
```

### List Docker images

```bash
docker images
```

### Stop a container

```bash
docker stop CONTAINER_ID
```

### Remove a container

```bash
docker rm CONTAINER_ID
```

### Remove the image

```bash
docker rmi eye-blink-detector
```

### Rebuild the image

```bash
docker build -t eye-blink-detector .
```

### Run the container

```bash
docker run --rm -p 5000:5000 eye-blink-detector
```

---

# 🧩 Technical Challenges Solved

During development, several engineering challenges were addressed:

### 1. Python Dependency Compatibility

OpenCV, MediaPipe, and NumPy versions need to be compatible.

The project uses a compatible dependency combination to avoid NumPy/MediaPipe conflicts.

### 2. Webcam Access

Instead of attempting to access the host webcam directly from inside Docker, the browser captures the webcam stream.

This allows:

```text
Browser → Docker Backend
```

rather than:

```text
Docker → Host Webcam
```

### 3. Real-Time Communication

WebSockets are used instead of traditional HTTP requests to continuously transmit frames and receive processed results.

### 4. Browser Notifications

Notifications are handled on the browser side so that the user receives the alert on the host system.

---

# ⚠️ Limitations

The current system has several limitations:

- Detection accuracy depends on lighting conditions.
- Poor camera quality can affect landmark detection.
- Very large head movements can affect detection.
- The current configuration is optimized for one face.
- EAR threshold may need adjustment for different users and cameras.
- Browser webcam permissions are required.

---

# 🔮 Future Improvements

Potential improvements include:

- [ ] Configurable EAR threshold
- [ ] Improved blink detection using temporal filtering
- [ ] Eye fatigue scoring
- [ ] Drowsiness detection
- [ ] Head pose estimation
- [ ] Multiple-face support
- [ ] FPS monitoring
- [ ] Performance optimization
- [ ] Automated testing
- [ ] Docker Compose configuration
- [ ] CI/CD using GitHub Actions
- [ ] Cloud deployment
- [ ] Persistent analytics dashboard

---

# 👨‍💻 Author

**Your Name**

B.Tech Mechatronics Engineering

Interested in:

- Robotics
- Computer Vision
- Embedded Systems
- Autonomous Systems
- AI
- Docker & Software Engineering

---

## ⭐ Project Highlights

This project demonstrates the integration of:

```text
Computer Vision
      +
MediaPipe
      +
OpenCV
      +
Python
      +
Flask
      +
WebSockets
      +
JavaScript
      +
Docker
```

The goal was not only to build a blink detector, but to develop a **complete real-time computer-vision application with a containerized backend**.
## Challenges Faced

During development, several challenges were encountered:

- Python 3.14 compatibility issues
- MediaPipe API changes
- NumPy binary incompatibility
- Matplotlib and Pillow dependency errors
- Virtual environment setup
- Webcam initialization
- Notification handling

These issues were resolved by creating a clean Python 3.11 virtual environment, reinstalling dependencies, and debugging package imports.

---

## Future Improvements

- Driver drowsiness detection
- Blink statistics
- CSV logging
- Docker support
- Multi-face detection
- Performance optimization
- FPS counter
- Dark mode interface

---

## Author

**Sahil Patel**

B.Tech in Mechatronics Engineering

Interested in:

- Robotics
- Computer Vision
- Drone development
- Embedded Systems
