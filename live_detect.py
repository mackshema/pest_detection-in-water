import cv2
import numpy as np
import onnxruntime as ort
import time

# ==============================
# CONFIGURATION
# ==============================
INPUT_WIDTH = 160
INPUT_HEIGHT = 160
INPUT_HEIGHT = 160
INPUT_HEIGHT = 160
INPUT_HEIGHT = 160
CONFIDENCE_THRESHOLD = 0.85 # Stricter to reduce false positives
CONFIRM_FRAMES = 10 # Wait longer confirm detection (approx 0.5s)
VARIANCE_THRESHOLD = 300 # Increased to filter more water noise

MEAN = np.array([0.485, 0.456, 0.406], dtype=np.float32)
STD = np.array([0.229, 0.224, 0.225], dtype=np.float32)

CLASS_NAMES = [
    "aphids", "armyworm", "beetle", "bollworm", "clean_water",
    "frog", "grasshopper", "mites", "mosquito",
    "sawfly", "stem_borer"
]

# ==============================
# PREPROCESSING (Water Optimized)
# ==============================
def preprocess(frame):
    img = cv2.resize(frame, (INPUT_WIDTH, INPUT_HEIGHT))
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    img = img.astype(np.float32) / 255.0
    img = (img - MEAN) / STD
    img = img.transpose(2, 0, 1)
    img = np.expand_dims(img, axis=0)
    return img

# ==============================
# WATER ENHANCEMENT
# ==============================
def enhance_water_image(frame):
    # Reduce noise
    frame = cv2.GaussianBlur(frame, (5, 5), 0)

    # Improve contrast (CLAHE)
    lab = cv2.cvtColor(frame, cv2.COLOR_BGR2LAB)
    l, a, b = cv2.split(lab)
    clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
    l = clahe.apply(l)
    lab = cv2.merge((l, a, b))
    frame = cv2.cvtColor(lab, cv2.COLOR_LAB2BGR)

    return frame

# ==============================
# MAIN
# ==============================
def main():

    model_path = "best_pest_model_cpu.onnx"

    print("Loading ONNX model...")
    session = ort.InferenceSession(model_path)
    input_name = session.get_inputs()[0].name
    output_name = session.get_outputs()[0].name

    # ==============================
    # CAMERA SETTINGS (USB Only)
    # ==============================
    # ==============================
    # CAMERA SETTINGS (USB Only)
    # ==============================
    print("Searching for available cameras...")
    cap = None
    
    # Try indices 0 to 3 to find a working camera
    target_camera_index = -1
    for index in range(4): # Try 0, 1, 2, 3
        print(f"Testing Camera Index {index}...")
        temp_cap = cv2.VideoCapture(index)
        if temp_cap.isOpened():
             print(f"Found Camera at Index {index}")
             # Prioritize Index 1 if found (usually external), otherwise Index 0
             if target_camera_index == -1: 
                 target_camera_index = index
             elif index == 1: # Prefer index 1 over index 0
                 target_camera_index = index
             
             temp_cap.release()
    
    if target_camera_index != -1:
        print(f"Selecting Camera Index {target_camera_index}...")
        cap = cv2.VideoCapture(target_camera_index)
        
    if cap is None or not cap.isOpened():
        print("Error: No USB Camera found. Please check connection.")
        return

    detection_counter = 0
    prev_frame = None
    last_status = "SAFE"

    print("Starting Smart Water Tank Pest Detection...")

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        # Enhance for water conditions
        frame = enhance_water_image(frame)
        display_frame = frame.copy()

        # 1. Motion Filtering
        motion_detected = False
        x, y, w, h = 0, 0, 0, 0 
        
        if prev_frame is not None:
            gray1 = cv2.cvtColor(prev_frame, cv2.COLOR_BGR2GRAY)
            gray2 = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            diff = cv2.absdiff(gray1, gray2)
            _, thresh = cv2.threshold(diff, 25, 255, cv2.THRESH_BINARY)
            dilated = cv2.dilate(thresh, None, iterations=2)
            contours, _ = cv2.findContours(dilated, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            for contour in contours:
                if cv2.contourArea(contour) < 1000: # Ignore small noise
                    continue
                
                motion_detected = True
                (x, y, w, h) = cv2.boundingRect(contour)
                cv2.rectangle(display_frame, (x, y), (x + w, y + h), (0, 255, 255), 2)

        prev_frame = frame.copy()

        # 2. Logic: ONLY RUN MODEL IF MOTION DETECTED
        if not motion_detected:
            # Check for background variance just to be sure (optional, mostly for debug)
            bg_gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            bg_variance = cv2.Laplacian(bg_gray, cv2.CV_64F).var()
            
            cv2.putText(display_frame, f"Safe (No Motion) Var:{int(bg_variance)}", (10, 50), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
            
            # Reset counter if no motion
            detection_counter = max(0, detection_counter - 1)
            
            cv2.imshow("Water Tank AI", display_frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
            continue

        # 3. Run Model (Only on motion)
        input_data = preprocess(frame)
        outputs = session.run([output_name], {input_name: input_data})
        logits = outputs[0][0]

        # Softmax
        exp_logits = np.exp(logits - np.max(logits))
        probs = exp_logits / np.sum(exp_logits)

        class_id = np.argmax(probs)
        confidence = probs[class_id]
        detected_class = CLASS_NAMES[class_id]

        # Logit Difference Check
        sorted_probs = np.sort(probs)
        prob_diff = sorted_probs[-1] - sorted_probs[-2]
        
        # 4. Alert Logic
        # Ignore 'clean_water' class
        if detected_class == 'clean_water':
             detection_counter = max(0, detection_counter - 1)
             status = "SAFE (Water)"
             color = (0, 255, 0)
        
        elif confidence > CONFIDENCE_THRESHOLD and prob_diff > 0.20:
             detection_counter += 1
             status = f"DETECTING {detected_class}..."
             color = (0, 165, 255) # Orange
        else:
             detection_counter = max(0, detection_counter - 1)
             status = "Analyzing..."
             color = (200, 200, 200)

        # Confirm Detection
        if detection_counter >= CONFIRM_FRAMES:
            status = f"⚠ CONTAMINATED: {detected_class}"
            color = (0, 0, 255) # Red
            print(f"!!! ALERT: {detected_class} ({confidence:.2f})")
            
            # Draw box if provided by motion
            if x > 0:
                 cv2.rectangle(display_frame, (x, y), (x + w, y + h), (0, 0, 255), 4)

        # Display Info
        cv2.putText(display_frame, status, (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)
        cv2.putText(display_frame, f"Conf: {confidence:.2f}", (10, display_frame.shape[0] - 10), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255,255,255), 1)

        cv2.imshow("Water Tank AI", display_frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
