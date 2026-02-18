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
CONFIDENCE_THRESHOLD = 0.75 # Balanced: Detects real pests, ignores noise
CONFIRM_FRAMES = 5 # Faster response (approx 0.2s)
VARIANCE_THRESHOLD = 200 # Lowered to allow water ripples

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

    # Initialize Webcam (Try USB Index 1 first, then Default Index 0)
    print("Attempting to connect to USB Camera (Index 1)...")
    cap = cv2.VideoCapture(1)
    
    if not cap.isOpened():
        print("USB Camera not found. Falling back to Internal Camera (Index 0)...")
        cap = cv2.VideoCapture(0)

    if not cap.isOpened():
        print("Error: Could not access any webcam.")
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

        # Motion Filtering & Bounding Box
        motion_detected = False
        x, y, w, h = 0, 0, 0, 0 # Bounding box coords
        
        if prev_frame is not None:
            gray1 = cv2.cvtColor(prev_frame, cv2.COLOR_BGR2GRAY)
            gray2 = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            diff = cv2.absdiff(gray1, gray2)
            _, thresh = cv2.threshold(diff, 25, 255, cv2.THRESH_BINARY)
            
            # Dilate to fill holes
            dilated = cv2.dilate(thresh, None, iterations=2)
            
            # Find contours
            contours, _ = cv2.findContours(dilated, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            for contour in contours:
                if cv2.contourArea(contour) < 500: # Ignore tiny noise
                    continue
                
                motion_detected = True
                (x, y, w, h) = cv2.boundingRect(contour)
                # Draw Box around moving pest
                cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 255), 2)

            motion_ratio = np.sum(thresh) / thresh.size

            if not motion_detected and motion_ratio < 0.01:
                # If no significant motion, just show background status
                # But we still run variance check below just in case
                pass
        
        prev_frame = frame.copy()

        # Draw "Target Zone" if no motion detected (Guide user)
        if not motion_detected:
            h_img, w_img = frame.shape[:2]
            cv2.rectangle(frame, (w_img//4, h_img//4), (3*w_img//4, 3*h_img//4), (200, 200, 200), 1)
            cv2.putText(frame, "Place Pest Here", (w_img//3, h_img//2), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (200,200,200), 1)

        # 2️⃣ Variance Check (Filter out empty backgrounds)

        # 2️⃣ Variance Check (Filter out empty backgrounds)
        # Empty walls/water usually have low variance (uniform color)
        bg_gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        bg_variance = cv2.Laplacian(bg_gray, cv2.CV_64F).var()

        if bg_variance < VARIANCE_THRESHOLD:
             # If variance is low, it's likely just a wall or empty water
             detection_counter = 0 # Reset counter
             cv2.putText(frame, "Background - Safe", (10, 30), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
             cv2.imshow("Water Tank AI", frame)
             if cv2.waitKey(1) & 0xFF == ord('q'):
                break
             continue

        # Run Model
        input_data = preprocess(frame)
        outputs = session.run([output_name], {input_name: input_data})
        logits = outputs[0][0]

        # Softmax
        exp_logits = np.exp(logits - np.max(logits))
        probs = exp_logits / np.sum(exp_logits)

        class_id = np.argmax(probs)
        confidence = probs[class_id]

        # Logit Difference Check (Is it really differentiating?)
        # If top two classes are close, it's confused -> Ignore
        sorted_probs = np.sort(probs)
        prob_diff = sorted_probs[-1] - sorted_probs[-2]
        
        # Temporal Filtering
        # Relaxed logic:
        # 1. Confidence > 0.75 (Balanced)
        # 2. Probability difference > 0.15 (Less strict confusion check)
        if confidence > CONFIDENCE_THRESHOLD and prob_diff > 0.15:
             detection_counter += 1
        else:
            # Decay counter slowly instead of instant reset? 
            # (Optional, but instant reset is safer for false positives)
            if detection_counter > 0:
                detection_counter -= 1

        if detection_counter >= CONFIRM_FRAMES:
            status = "⚠ CONTAMINATED"
            color = (0, 0, 255)
            
            # Draw explicit Bounding Box if we have one from motion
            if motion_detected:
                 cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 0, 255), 4)
                 cv2.putText(frame, "DETECTED", (x, y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0,0,255), 2)
            
        else:
            status = "✅ SAFE"
            color = (0, 255, 0)
            
        # Display Result
        if status == "⚠ CONTAMINATED":
             detected_class = CLASS_NAMES[class_id]
             label = f"{detected_class} ({confidence:.2f})"
             cv2.putText(frame, label, (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)
             print(f"!!! ALERT: {detected_class} ({confidence:.2f})")
        
        # Show variance for tuning
        cv2.putText(frame, f"Var: {int(bg_variance)} | Conf: {confidence:.2f}",
                    (10, frame.shape[0] - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (200, 200, 200), 1)

        cv2.putText(frame, status,
                    (10, 100), cv2.FONT_HERSHEY_SIMPLEX,
                    1.0, color, 3)

        cv2.imshow("Water Tank AI", frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
