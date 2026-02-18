
import cv2
import sys
import traceback

model_path = "best_pest_model_cpu.onnx"
print(f"OpenCV Version: {cv2.__version__}")
print(f"Attempting to load model: {model_path}")

try:
    net = cv2.dnn.readNetFromONNX(model_path)
    print("Model loaded successfully!")
except Exception:
    traceback.print_exc()

print("Finished.")
