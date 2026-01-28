import cv2
import mediapipe as mp
import math
import numpy as np
import sounddevice as sd
import time

# ==========================================
#              CONFIGURATION
# ==========================================
SMILE_THRESHOLD = 45        # The ratio needed to pass the visual test
AUDIO_DURATION = 4          # How long to record voice (seconds)
SAMPLE_RATE = 44100         # Standard audio quality

# ==========================================
#              AI SETUP
# ==========================================
mp_face_mesh = mp.solutions.face_mesh
face_mesh = mp_face_mesh.FaceMesh(max_num_faces=1, refine_landmarks=True)

# Global Variables to store results
visual_status = "PENDING"   # PENDING, HEALTHY, RISK
audio_status = "PENDING"    # PENDING, STABLE, UNSTABLE
mode = "MENU"               # MENU, VISUAL, AUDIO

# ==========================================
#           HELPER FUNCTIONS
# ==========================================

def calculate_smile_ratio(landmarks, w, h):
    """Calculates the smile gap using geometry."""
    # Mouth Corners (Left: 61, Right: 291)
    p1 = (int(landmarks[61].x * w), int(landmarks[61].y * h))
    p2 = (int(landmarks[291].x * w), int(landmarks[291].y * h))
    
    # Face Width (Left: 234, Right: 454)
    f1 = (int(landmarks[234].x * w), int(landmarks[234].y * h))
    f2 = (int(landmarks[454].x * w), int(landmarks[454].y * h))
    
    # Calculate Distances
    mouth_dist = math.hypot(p2[0]-p1[0], p2[1]-p1[1])
    face_dist = math.hypot(f2[0]-f1[0], f2[1]-f1[1])
    
    # The Ratio
    ratio = (mouth_dist / face_dist) * 100
    return ratio, p1, p2

def run_audio_analysis():
    """Records audio and checks for voice tremors (Shimmer)."""
    print("Microphone Active... Recording.")
    
    # 1. Record Audio
    recording = sd.rec(int(AUDIO_DURATION * SAMPLE_RATE), samplerate=SAMPLE_RATE, channels=1)
    sd.wait()  # Wait until recording is finished
    
    # 2. Analyze Stability (Simple Standard Deviation Check)
    # Flatten the audio data to a simple list of numbers
    data = recording.flatten()
    
    # Calculate Volume Variance (Tremor)
    # A steady "Ahhh" has low variance. A shaky voice has high variance.
    # We multiply by 1000 to make the number readable.
    shakiness_score = np.std(data) * 1000 
    
    return shakiness_score

# ==========================================
#             MAIN APP LOOP
# ==========================================
cap = cv2.VideoCapture(0)

while True:
    ret, frame = cap.read()
    if not ret: break
    
    # formatting the frame
    frame = cv2.flip(frame, 1)
    h, w, _ = frame.shape
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    
    # Draw the Black Dashboard Header
    cv2.rectangle(frame, (0, 0), (w, 140), (20, 20, 20), -1)
    
    # ------------------------------------------------
    # MODE 1: THE MENU (Dashboard)
    # ------------------------------------------------
    if mode == "MENU":
        cv2.putText(frame, "NEUROLENS: MULTIMODAL DIAGNOSIS", (30, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)
        
        # Instructions
        cv2.putText(frame, "[V] Run Visual Test", (30, 80), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 1)
        cv2.putText(frame, "[A] Run Audio Test", (30, 110), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 1)
        cv2.putText(frame, "[Q] Quit App", (30, 140), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (100, 100, 100), 1)

        # The Patient Chart (Right Side)
        cv2.putText(frame, "DIAGNOSTIC CHART:", (w-350, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (200, 200, 200), 1)
        
        # Color Logic for Status
        v_color = (0, 255, 0) if "HEALTHY" in visual_status else (0, 0, 255) if "RISK" in visual_status else (200, 200, 200)
        a_color = (0, 255, 0) if "STABLE" in audio_status else (0, 0, 255) if "UNSTABLE" in audio_status else (200, 200, 200)
        
        cv2.putText(frame, f"Vision: {visual_status}", (w-350, 80), cv2.FONT_HERSHEY_SIMPLEX, 0.7, v_color, 2)
        cv2.putText(frame, f"Audio:  {audio_status}", (w-350, 110), cv2.FONT_HERSHEY_SIMPLEX, 0.7, a_color, 2)

    # ------------------------------------------------
    # MODE 2: VISUAL TEST (Smile)
    # ------------------------------------------------
    elif mode == "VISUAL":
        results = face_mesh.process(rgb_frame)
        cv2.putText(frame, "TEST 1: FACIAL MASKING", (30, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 2)
        cv2.putText(frame, "Instruction: Smile and press 'SPACE'", (30, 90), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (200, 200, 200), 1)
        
        if results.multi_face_landmarks:
            for face_landmarks in results.multi_face_landmarks:
                ratio, p1, p2 = calculate_smile_ratio(face_landmarks.landmark, w, h)
                
                # Draw Live Feedback
                color = (0, 255, 0) if ratio > SMILE_THRESHOLD else (0, 0, 255)
                cv2.line(frame, p1, p2, color, 3)
                cv2.putText(frame, f"Ratio: {int(ratio)}", (p1[0], p1[1] + 30), cv2.FONT_HERSHEY_SIMPLEX, 1, color, 2)
                
                # Capture Logic
                if cv2.waitKey(1) & 0xFF == 32: # 32 is Spacebar
                    if ratio > SMILE_THRESHOLD:
                        visual_status = "HEALTHY"
                    else:
                        visual_status = "RISK DETECTED"
                    mode = "MENU" # Return to menu

    # ------------------------------------------------
    # MODE 3: AUDIO TEST (Voice)
    # ------------------------------------------------
    elif mode == "AUDIO":
        cv2.putText(frame, "TEST 2: VOCAL TREMOR", (30, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        cv2.putText(frame, "Instruction: Press 'S' and say 'Ahhhhh'", (30, 90), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (200, 200, 200), 1)
        
        # Start Recording Logic
        if cv2.waitKey(1) & 0xFF == ord('s'):
            # Visual Indicator that we are working
            cv2.rectangle(frame, (0, 0), (w, h), (0, 0, 0), -1)
            cv2.putText(frame, "LISTENING...", (w//2 - 100, h//2), cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0, 0, 255), 2)
            cv2.imshow("NeuroLens Prototype", frame)
            cv2.waitKey(1) # Force screen update
            
            # Run the math
            score = run_audio_analysis()
            
            # Threshold Logic (Experimental)
            # A very quiet/steady room is usually < 10. A loud/shaky voice varies more.
            # For this prototype, we check if there is *enough* volume but *low* variance.
            # Simplified:
            if score < 50: 
                audio_status = "STABLE (Healthy)"
            else:
                audio_status = "UNSTABLE (Risk)"
            
            mode = "MENU"

    # Show the App
    cv2.imshow("NeuroLens Prototype", frame)
    
    # Global Key Controls
    key = cv2.waitKey(1) & 0xFF
    if key == ord('q'): break     # Quit
    if key == ord('v'): mode = "VISUAL"
    if key == ord('a'): mode = "AUDIO"

cap.release()
cv2.destroyAllWindows()