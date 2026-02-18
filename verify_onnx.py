import cv2
import numpy as np
import os

ONNX_MODEL_PATH = "best_pest_model_cpu.onnx"
IMAGE_PATH = r"d:\pest_detection\pest\train\aphids\jpg_0.jpg" 
CLASS_NAMES = [
    "aphids", "armyworm", "beetle", "bollworm", 
    "grasshopper", "mites", "mosquito", "sawfly", "stem_borer"
]

def verify_onnx():
    if not os.path.exists(ONNX_MODEL_PATH):
        print(f"Error: {ONNX_MODEL_PATH} not found.")
        return

    
    # Try with ONNX Runtime first to check model validity
    import onnxruntime as ort
    try:
        print("Checking model with ONNX Runtime...")
        ort_session = ort.InferenceSession(ONNX_MODEL_PATH)
        print("✅ ONNX Runtime loaded the model successfully!")
    except Exception as e:
        print(f"❌ ONNX Runtime failed to load model: {e}")

    print(f"Loading ONNX model from {ONNX_MODEL_PATH} with OpenCV...")
    try:
        net = cv2.dnn.readNetFromONNX(ONNX_MODEL_PATH)
        print("✅ OpenCV loaded the model successfully!")
    except Exception as e:
        print(f"❌ OpenCV failed to load model: {e}")
        return
    
    # Try different backends
    try:
        net.setPreferableBackend(cv2.dnn.DNN_BACKEND_OPENCV)
        net.setPreferableTarget(cv2.dnn.DNN_TARGET_CPU)
    except Exception as e:
        print(f"Warning setting backend: {e}")

    print(f"Reading image from {IMAGE_PATH}...")
    image = cv2.imread(IMAGE_PATH)
    if image is None:
        print("Error: Could not read image.")
        return

    # Preprocessing
    # Match the PyTorch transforms:
    # Resize -> 160x160
    # ToTensor (transforms [0,255] to [0,1])
    # Normalize (mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
    
    # In OpenCV, blobFromImage can handle scale and mean subtraction.
    # But standard deviation division is per channel.
    # blobFromImage: (pixel - mean) * scale
    # We want: (pixel/255 - mean_normalized) / std_normalized
    # = (pixel - mean_normalized*255) * (1/255 * 1/std_normalized)
    
    # However, std is different per channel. So we can't use single blobFromImage if we want exactness.
    # Let's do manual preprocessing to be consistent with C++ "manual" approach I wrote.
    
    input_size = (160, 160)
    resized = cv2.resize(image, input_size)
    
    # Convert BGR to RGB
    rgb = cv2.cvtColor(resized, cv2.COLOR_BGR2RGB)
    
    # Normalize
    rgb = rgb.astype(np.float32) / 255.0
    mean = np.array([0.485, 0.456, 0.406], dtype=np.float32)
    std = np.array([0.229, 0.224, 0.225], dtype=np.float32)
    
    rgb = (rgb - mean) / std
    
    # Transpose to (1, 3, 160, 160)
    blob = np.transpose(rgb, (2, 0, 1))
    blob = np.expand_dims(blob, axis=0)
    
    net.setInput(blob)
    
    print("Running inference...")
    outputs = net.forward()
    
    # Get result
    scores = outputs[0]
    class_id = np.argmax(scores)
    confidence = scores[class_id]
    
    print(f"Predicted Class Index: {class_id}")
    print(f"Predicted Class Name: {CLASS_NAMES[class_id]}")
    print(f"Confidence (Logit): {confidence}")
    print("Scores:", scores)
    
    expected_class = "aphids"
    if CLASS_NAMES[class_id] == expected_class:
        print("✅ SUCCESS: Correctly classified as aphids!")
    else:
        print(f"⚠️ WARNING: Classified as {CLASS_NAMES[class_id]}, expected {expected_class}")

if __name__ == "__main__":
    verify_onnx()
