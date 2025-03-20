
# 🎵 Hand Gesture Music Player

Control your music with intuitive, AI-powered hand gestures! This project uses computer vision and machine learning techniques to detect hand gestures in real time and convert them into music control commands.

![Demo GIF](https://via.placeholder.com/640x480.png?text=Demo+GIF+Placeholder)  
*Add your demo video or GIF here*

---

## 🚀 Features

- **Gesture-Controlled Playback:**
  - 👋 **Right hand - Left Wave:** Skip to the next track.
  - 👉 **Left hand - Right Wave:** Go back to the previous track.
  - 👌 **OK Gesture:** Toggle play/pause.
  - 🤏 **Pinch Gesture:** Adjust system volume.

- **Real-Time Hand Tracking:**  
  Visual feedback is provided via the webcam feed, with hand landmarks and gesture actions overlaid on the video.

- **System-Wide Volume Control:**  
  Uses Windows Core Audio API via `pycaw` to modify the system volume directly.

- **Playlist Management:**  
  Music files are dynamically loaded from a designated `songs` folder, allowing you to manage your playlist easily.

- **Interactive On-Screen Feedback:**  
  Visual cues indicate current actions (e.g., next song, previous song, play/pause, volume changes).

---

## 🛠️ Requirements

- **Python:** 3.8 or higher
- **Operating System:** Windows (for system volume control)
- **Webcam:** Required for gesture detection
- **Development Environment:** [PyCharm](https://www.jetbrains.com/pycharm/)  
  *Using PyCharm simplifies the installation and management of libraries without directly dealing with the command-line shell.*

### Libraries Used

| Library          | Purpose                                        |
|------------------|------------------------------------------------|
| OpenCV           | Captures and processes webcam video            |
| MediaPipe        | Provides AI-powered hand tracking and gesture recognition |
| Pygame           | Manages music playback                         |
| NumPy            | Supports mathematical operations               |
| pycaw            | Controls the system volume on Windows          |
| Comtypes         | Interfaces with Windows Core Audio API         |

---

## 📥 Installation

### 1. Clone the Repository
```bash
git clone https://github.com/yourusername/hand-gesture-music-player.git
cd hand-gesture-music-player
```

### 2. Set Up a Virtual Environment (Recommended)
```bash
python -m venv env
# Activate the virtual environment:
# On Windows:
env\Scripts\activate
# On macOS/Linux:
source env/bin/activate
```

### 3. Install Dependencies
If you’re using **PyCharm**, simply open the project and use the built-in package manager to install the required libraries (listed in `requirements.txt`). Alternatively, install them via the command line:
```bash
pip install -r requirements.txt
```

### 4. Add Your Music Files
Create a folder named `songs` in the project root and add your `.mp3` files there:
```bash
mkdir songs
# Place your MP3 files into the songs folder.
```

---

## 🎮 Usage

1. **Run the Program:**
   ```bash
   python Fingers_count.py
   ```

2. **Control Your Music:**
   - **Next Track:** Wave your right hand (leftward wave).
   - **Previous Track:** Wave your left hand (rightward wave).
   - **Play/Pause:** Show the OK gesture (thumb and index finger touching).
   - **Volume Control:** Perform the pinch gesture with your right hand.

3. **Exit the Application:**  
   Press the **`Q`** key to quit.

---

## 🧠 How It Works

- **Hand Tracking:**  
  Uses MediaPipe to detect 21 hand landmarks in real time from the webcam feed.

- **Gesture Recognition:**  
  Custom functions analyze the position and movement of hand landmarks to interpret gestures:
  - **Wave Gestures:** Change tracks.
  - **OK Gesture:** Toggle play/pause.
  - **Pinch Gesture:** Adjust the system volume by mapping the distance between the thumb and index finger.

- **Audio Playback and Control:**  
  Pygame handles the playback of music files, while pycaw adjusts the system volume based on the detected pinch gesture.

- **Interactive Visual Feedback:**  
  OpenCV overlays hand landmarks and gesture messages onto the webcam feed for user feedback.

---

---

## 🚨 Troubleshooting

- **No Hand Detected?**
  - Ensure your webcam is connected and functioning.
  - Improve lighting and keep your hand within the camera frame.
  - Clean your webcam lens.

- **Music Not Playing?**
  - Verify that the `songs` folder contains valid `.mp3` files.
  - Check that file names do not include unsupported special characters.

- **Volume Not Adjusting?**
  - Run the application as an Administrator (required for system volume control).
  - Ensure your gestures are clear and within the detection zone.

---


---

## 📧 Contact

- **GitHub:** [Your GitHub Profile](https://github.com/flipfelly)
- **Email:** gontijofotografia@gmail.com

---

*Developed with love using PyCharm for hassle-free library management and development.*  
*Enjoy controlling your music with just a wave of your hand!*
