import torch
import torch.nn as nn
from torchvision import models
import os

# Define constants matching training
# Define constants matching training
DATA_DIR = r"D:\pest_detection\dataset\train"
try:
    NUM_CLASSES = len([d for d in os.listdir(DATA_DIR) if os.path.isdir(os.path.join(DATA_DIR, d))])
    print(f"Detected {NUM_CLASSES} classes from dataset.")
except:
    NUM_CLASSES = 11 # Default fallback (9 pests + clean_water + frog)
IMAGE_SIZE = 160
MODEL_PATH = r"D:\pest_detection\best_pest_model_cpu.pth"
ONNX_PATH = r"D:\pest_detection\best_pest_model_cpu.onnx"

def convert_to_onnx():
    print("Loading model architecture...")
    # Recreate the model structure
    weights = models.ResNet18_Weights.DEFAULT
    model = models.resnet18(weights=weights)
    
    # Modify the final layer as done in training
    num_ftrs = model.fc.in_features
    model.fc = nn.Linear(num_ftrs, NUM_CLASSES)
    
    print(f"Loading weights from {MODEL_PATH}...")
    try:
        # Load the state dict
        state_dict = torch.load(MODEL_PATH, map_location=torch.device('cpu'))
        model.load_state_dict(state_dict)
    except FileNotFoundError:
        print(f"Error: Model file not found at {MODEL_PATH}")
        return
    except Exception as e:
        print(f"Error loading weights: {e}")
        return

    model.eval()
    
    # Create a dummy input for tracing (Batch Size, Channels, Height, Width)
    dummy_input = torch.randn(1, 3, IMAGE_SIZE, IMAGE_SIZE)
    
    print(f"Exporting to ONNX at {ONNX_PATH}...")
    try:
        torch.onnx.export(
            model, 
            dummy_input, 
            ONNX_PATH, 
            verbose=False,
            input_names=['input'], 
            output_names=['output'],
            opset_version=11
        )
        print("✅ Conversion successful!")
    except Exception as e:
        print(f"Error during export: {e}")

if __name__ == "__main__":
    convert_to_onnx()
