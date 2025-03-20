"""
This code creates a hand gesture-controlled music player system that combines:
1. Computer Vision (cv2) for camera input
2. MediaPipe's AI hand tracking for gesture recognition
3. Pygame for music playback functionality
4. Windows audio APIs for system volume control
5. Mathematical calculations for gesture interpretation

Key components enabled by the libraries:
- Real-time hand tracking (mediapipe)
- Music playlist management (pygame + os)
- System-level volume adjustment (pycaw + ctypes)
- Visual interface (cv2)
- Gesture timing controls (time)
"""

import cv2
import pygame
import math
import numpy as np
import mediapipe as mp
from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
import os
import time

# Initialize pygame mixer
pygame.mixer.init()

# ===========================================
# PART 2: SETTING UP THE MUSIC AND VOLUME
# ===========================================

# --- Let's Make a Playlist First! ---
# We need to find all the MP3s in your "songs" folder
# (Pro tip: Create this folder and add some bangers first!)
songs_folder = "songs"  # Your personal DJ booth directory

# Hunt down all MP3 files like a music detective
music_files = [
    os.path.join(songs_folder, f)  # Build full file paths
    for f in os.listdir(songs_folder)  # Check every file
    if f.endswith(".mp3")  # Only grab actual music files
]

# Alphabetical order because chaos is bad for playlists
music_files.sort()  # A-B-C sorting for your tracks

# --- Jukebox Setup ---
current_song_index = 0  # Start with the first track
# (Fun fact: "mixer.music" is Pygame's DJ turntable )
pygame.mixer.music.load(music_files[current_song_index])  # Load first song

# --- Becoming the Volume Master ---
# (This is where we "hack" into Windows' volume controls)

# Step 1: Find the computer's speakers
devices = AudioUtilities.GetSpeakers()

# Step 2: Activate the volume controls
interface = devices.Activate(
    IAudioEndpointVolume._iid_,  # Volume access
    CLSCTX_ALL,  # All-access security pass
    None  # No extra tricks needed
)

# Step 3: Make the volume controls usable
volume = cast(interface, POINTER(IAudioEndpointVolume))

# Step 4: Check the volume range
volRange = volume.GetVolumeRange()  # How quiet/loud can we go?
minVol, maxVol = volRange[0], volRange[1]  # Usually -65.25db (silent) to 0db (BOOM)

"""
Real Talk:
1. The music loading is like making a mixtape:
   - You put MP3s in the "songs" folder
   - The code arranges them alphabetically
   - Pygame becomes your Walkman to play them

2. The volume setup is basically:
   "Hello Windows, I'll be taking over the sound system now" 🎛️
   (This lets our gestures control your actual system volume later)

Watch Out For:
- No MP3s in "songs" folder? This code will cry
- Weird volume math later because Windows uses decibels (-65.25 to 0)
- Pygame needs to be initialized first (which we did earlier)
"""

# ===========================================
# PART 3: TEACHING THE COMPUTER TO SEE HANDS
# ===========================================

# --- Magic Hand Tracking Setup ---
mp_hands = mp.solutions.hands  # Google's secret hand sauce
mp_drawing = mp.solutions.drawing_utils  # Tools to draw hand skeletons
hands = mp_hands.Hands(
    static_image_mode=False,  # Using video
    max_num_hands=2,  # "I can handle two hands... but not a zombie apocalypse"
    min_detection_confidence=0.5,  # "I need to be 50% sure it's a hand"
    min_tracking_confidence=0.5  # "I'll keep tracking unless I get confused"
)

# --- Webcam Setup ---
cap = cv2.VideoCapture(0)  # Use the main webcam
wCam, hCam = 640, 480  # "640x480 resolution
cap.set(3, wCam)  # Set width
cap.set(4, hCam)  # Set height

# ===========================================
# PART 4: THE PROGRAM'S BRAIN (MEMORY VARIABLES)
# ===========================================

# Volume Memory
last_volume = volume.GetMasterVolumeLevel()  # "Remember where we left the volume"

# Gesture cooldown (Prevent Spam)
cooldown_time = 1.0  # 1-second timeout
last_wave_time = 0

# On-Screen Messages
message_duration = 1
current_message = ""
message_start_time = 0

"""
Key Explanations:
1. Hand Tracking:
- Google's MediaPipe does the heavy lifting 
- static_image_mode=False = Optimized for video (not photos)
- Confidence levels = How sure the AI needs to be (0.5 = 50% sure)

2. Camera Setup:
- 0 = Default webcam (change to 1 if you have multiple cameras)
- 640x480 = Sweet spot between quality and speed

3. Why Cooldowns?:
- Prevents accidental "next song" spam when waving
- Like a refractory period for gestures
"""

'''
===========================================
PART 5: THE GESTURE DICTIONARY 
===========================================

Gesture Cheat Sheet:
┌───────────────┬───────────────────────────────┐
│    Gesture    │         How It Works          │
├───────────────┼───────────────────────────────┤
│ 👋 Left Wave  │ All fingertips left of wrist  │
│ 👋 Right Wave │ All fingertips right of wrist │
│ 🔊 Volume     │ Index+thumb up, others down   │
│ ⏯️ Play/Pause │ OK sign + straight fingers    │
└───────────────┴───────────────────────────────┘
- Finger joints work like Russian nesting dolls:
  - landmark[8] = index tip
  - landmark[6] = index middle joint
  - Lower y value = higher up on screen
- MediaPipe hand landmarks are like finger GPS 
  (21 points per hand, 0 = wrist, 4 = thumb tip)
'''


def is_wave_left(landmarks):
    wrist = landmarks.landmark[0]    # its like de anchor point of the hand
    finger_tips = [landmarks.landmark[i] for i in [4, 8, 12, 16, 20]]  # The numbers represent all fingertips
    return all(tip.x < wrist.x - 0.1 for tip in finger_tips)  # all fingertips to the left of the wrist


def is_wave_right(landmarks):
    wrist = landmarks.landmark[0]
    finger_tips = [landmarks.landmark[i] for i in [4, 8, 12, 16, 20]]
    return all(tip.x > wrist.x + 0.1 for tip in finger_tips)  # all fingertips to the right of the wrist


def is_volume_control_gesture(landmarks):
    index_up = landmarks.landmark[8].y < landmarks.landmark[6].y  # index finger straight up
    thumb_up = landmarks.landmark[4].x < landmarks.landmark[3].x

    middle_down = landmarks.landmark[12].y > landmarks.landmark[10].y
    ring_down = landmarks.landmark[16].y > landmarks.landmark[14].y
    pinky_down = landmarks.landmark[20].y > landmarks.landmark[18].y
    return index_up and thumb_up and middle_down and ring_down and pinky_down  # "Pinch" sign

#  for the ok sign
last_gesture_time = 0
gesture_cooldown = 1
def is_play_pause_gesture(landmarks):
    # Check for "OK" gesture (thumb and index touching, other fingers extended)
    thumb_tip = landmarks.landmark[4]
    index_tip = landmarks.landmark[8]

    # Check distance between thumb and index (touching)
    distance = math.hypot(thumb_tip.x - index_tip.x, thumb_tip.y - index_tip.y)

    # Check other fingers are extended
    middle_up = landmarks.landmark[12].y < landmarks.landmark[10].y
    ring_up = landmarks.landmark[16].y < landmarks.landmark[14].y
    pinky_up = landmarks.landmark[20].y < landmarks.landmark[18].y

    return distance < 0.05 and middle_up and ring_up and pinky_up # Ok sign


print("Guideline:\n")
print(" - Wave left (right hand) → Next song")
print(" - Wave right (left hand) → Previous song")
print(" - Pinch gesture (right hand) → Control volume")
print(" - OK gesture (thumb+index touch) → Play/Pause")

# ===========================================
# PART 6: THE MAIN SHOW! (Where Magic Happens)
# ===========================================

while True:
    # Step 1: Check webcam feed
    success, frame = cap.read()
    if not success:
        break

    # Mirror mode to help with the comprehension
    frame = cv2.flip(frame, 1)  # 1 = "Make me look good in selfies"

    # MediaPipe needs RGB colors
    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    # Ask MediaPipe: "Do you see hands in this frame?"
    results = hands.process(frame_rgb)

    # Convert Windows' volume range to human % (0-100)
    volPer = int(np.interp(last_volume, [minVol, maxVol], [0, 100]))
    volume_gesture_active = False  # Volume control not active... yet
    current_time = time.time()

    # If hands detected
    if results.multi_hand_landmarks and results.multi_handedness:
        for hand_landmark, hand_handedness in zip(results.multi_hand_landmarks, results.multi_handedness):
            # Draw hand connections
            mp_drawing.draw_landmarks(frame, hand_landmark, mp_hands.HAND_CONNECTIONS)

            # Wave detection (with cooldown to prevent DJ spam)
            if current_time - last_wave_time > cooldown_time:
                # Next song trigger, the first music will start when you trigger this, and then you can use it normally
                if is_wave_left(hand_landmark):
                    current_song_index = (current_song_index + 1) % len(music_files) #to prevent errors
                    pygame.mixer.music.load(music_files[current_song_index])
                    pygame.mixer.music.play()
                    current_message = "Next Song"
                    message_start_time = current_time
                    last_wave_time = current_time

                # Previous song trigger
                elif is_wave_right(hand_landmark):
                    current_song_index = (current_song_index - 1) % len(music_files)
                    pygame.mixer.music.load(music_files[current_song_index])
                    pygame.mixer.music.play()
                    current_message = "Previous Song"
                    message_start_time = current_time
                    last_wave_time = current_time

                # Play/Pause trigger
                elif is_play_pause_gesture(hand_landmark) and (current_time - last_gesture_time) > gesture_cooldown:
                    if pygame.mixer.music.get_busy(): #if the music IS PLAYING
                        pygame.mixer.music.pause()
                        current_message = "Paused"
                    else:
                        pygame.mixer.music.unpause()
                        current_message = "Playing"
                    message_start_time = current_time
                    last_gesture_time = current_time

            # Volume control section 🔊
            if is_volume_control_gesture(hand_landmark):
                volume_gesture_active = True
                h, w, _ = frame.shape  # Get screen dimensions

                # Get thumb and index positions (the volume tweezers)
                thumb = hand_landmark.landmark[4]
                index = hand_landmark.landmark[8]
                thumb_x, thumb_y = int(thumb.x * w), int(thumb.y * h)
                index_x, index_y = int(index.x * w), int(index.y * h)

                # Draw UI elements (because style matters)
                cv2.circle(frame, (thumb_x, thumb_y), 15, (255, 0, 255), cv2.FILLED)  # Purple thumb
                cv2.circle(frame, (index_x, index_y), 15, (255, 0, 255), cv2.FILLED)  # Purple index
                cv2.line(frame, (thumb_x, thumb_y), (index_x, index_y), (255, 0, 255), 3)  # Connect them

                # Math magic to convert finger distance to volume
                length = math.hypot(index_x - thumb_x, index_y - thumb_y)
                new_volume = np.interp(length, [30, 250], [minVol, maxVol])  # Scale it!
                last_volume = new_volume
                volume.SetMasterVolumeLevel(new_volume, None)  # LOUDER PLEASE!

                # Visual volume bar
                volBar = np.interp(length, [30, 250], [400, 150])
                volPer = int(np.interp(length, [30, 250], [0, 100]))
                cv2.rectangle(frame, (50, 150), (85, 400), (0, 255, 0), 3)  # Bar outline
                cv2.rectangle(frame, (50, int(volBar)), (85, 400), (0, 255, 0), cv2.FILLED)  # Fill it

    # Show temporary messages
    if current_message and (current_time - message_start_time < message_duration):
        cv2.putText(frame, current_message, (40, 70),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)  # Green text
    else:
        current_message = ""  # Clear message after timeout

    # Display volume percentage (the people demand numbers!)
    cv2.putText(frame, f'Volume: {volPer}%', (40, 450),
                cv2.FONT_HERSHEY_COMPLEX, 1, (0, 255, 0), 2)

    # Show frame
    cv2.imshow("Music Player", frame)

    # Exit key (because even magic shows end) 🚪
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break  # "Goodbye cruel world!" 👋

# ===========================================
# AFTER PARTY CLEANUP
# ===========================================
cap.release()  # Turn off camera (privacy first!)
cv2.destroyAllWindows()  # Close all windows
pygame.mixer.quit()  # Stop music

"""
Pro Tips:
1. The 30-250 range in volume control? That's pixel distance!
   - 30px apart = Min volume
   - 250px apart = Max volume
2. Purple connection line? That's ✨ aesthetic ✨
3. Message positions (40,70) and (40,450) = Top-left and bottom-left
4. waitKey(1) = 1ms refresh rate 

Common Issues :
- Hand not detected? Make sure:
  - Good lighting 
  - Hand fully in frame 
  - Not too close/far ↔
- Volume not changing? Check your antivirus blocking audio access!
"""