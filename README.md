# NeuroLens: Parkinson's Symptom Detector 

NeuroLens is a desktop app that helps screen for early signs of Parkinson's Disease using your webcam and microphone.

It looks for two things that are hard for humans to catch:
1.  **Facial Masking:** When you think you're smiling, but your face muscles don't move enough.
2.  **Voice Tremors:** Tiny vibrations in your voice that indicate instability.

##  The Goal
Parkinson's is often diagnosed too late. This tool tries to solve that by digitizing the standard neurological exam. Instead of guessing, it uses computer vision and audio analysis to give you a concrete score.

## ⚙️ How It Works

### 1. The Vision Test (Hypomimia)
* **What it does:** It tracks 468 points on your face using **Google MediaPipe**.
* **The Math:** It calculates a "Smile Ratio" (how wide your mouth opens relative to your face).
* **The Diagnosis:** If you press the button to say "I am smiling" but the camera sees your muscles aren't moving, it flags a risk.

### 2. The Audio Test (Voice Tremor)
* **What it does:** It listens to you say "Ahhhhh" for 5 seconds.
* **The Math:** It looks at the sound waves to find "Shimmer" (volume instability).
* **The Diagnosis:** A steady voice is healthy. A shaky voice (high variance) gets flagged.

---

##  Built With
* **Python** (The brain of the app)
* **OpenCV** (For the camera)
* **MediaPipe** (For face tracking)
* **SoundDevice & NumPy** (For audio analysis)

---

##  How to Run It

1.  **Clone this repo**
    ```bash
    git clone [https://github.com/srikrishna9458/NeuroLens-Parkinsons-Detector.git](https://github.com/srikrishna9458/NeuroLens-Parkinsons-Detector.git)
    cd NeuroLens
    ```
2.  **Install the libraries**
    ```bash
    pip install opencv-python mediapipe sounddevice numpy scipy
    ```
3.  **Start the App**
    ```bash
    python main.py
    ```

### 🎮 Controls
* **Press `V`** -> Go to **Visual Test**. (Smile and press Spacebar).
* **Press `A`** -> Go to **Audio Test**. (Press 'S' and say 'Ahhh').
* **Press `Q`** -> Quit.

---

##  A Note on the Tech
Right now, this is a **Feature Extraction Prototype**. It uses math rules and geometry to detect symptoms.


---

**Author:** G Sri krishnan

