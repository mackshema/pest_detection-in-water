import os
import time
import subprocess
import re

DATASET_ROOT = r"D:\pest_detection\dataset"
LIVE_DETECT_PATH = r"D:\pest_detection\live_detect.py"

def wait_for_dataset():
    print("⏳ Waiting for dataset setup to complete...")
    start_time = time.time()
    while True:
        # Check for key folders: frog and at least one pest
        frog_ready = os.path.exists(os.path.join(DATASET_ROOT, "train", "frog"))
        pest_ready = os.path.exists(os.path.join(DATASET_ROOT, "train", "aphids"))
        
        if frog_ready and pest_ready:
            print("✅ Dataset Ready!")
            break
            
        if time.time() - start_time > 300: # 5 min timeout
            print("❌ Dataset setup timed out or failed.")
            return False
            
        time.sleep(5)
    return True

def update_live_detect_classes():
    print("📝 Updating live_detect.py class list...")
    
    # Get actual classes
    train_dir = os.path.join(DATASET_ROOT, "train")
    classes = sorted([d for d in os.listdir(train_dir) if os.path.isdir(os.path.join(train_dir, d))])
    
    # Read file with utf-8 encoding to avoid charmap errors
    with open(LIVE_DETECT_PATH, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Regex to find existing CLASS_NAMES list
    # Look for CLASS_NAMES = [ ... ]
    pattern = r"CLASS_NAMES = \[\s*.*?\s*\]"
    
    new_list_str = "CLASS_NAMES = [\n"
    for c in classes:
        new_list_str += f'    "{c}",\n'
    new_list_str += "]"
    
    # Replace
    new_content = re.sub(pattern, new_list_str, content, flags=re.DOTALL)
    
    with open(LIVE_DETECT_PATH, 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    print(f"✅ Updated class list with {len(classes)} classes.")

def run_training():
    print("\n🚀 STARTING TRAINING (10 Epochs)...")
    print("This will take approx 10-15 mins on CPU.")
    # Use 'py' instead of 'python' to ensure it runs
    subprocess.run(["py", r"D:\pest_detection\train_cpu.py"], check=True)
    
    print("\n🔄 Converting trained model to ONNX...")
    subprocess.run(["py", r"D:\pest_detection\convert_to_onnx.py"], check=True)
    
    print("\n✨ Model Updated Successfully!")

if __name__ == "__main__":
    if wait_for_dataset():
        try:
            run_training()
            update_live_detect_classes()
            print("\n🎉 ALL DONE! Run 'python d:\\pest_detection\\live_detect.py' to test.")
        except Exception as e:
            print(f"\n❌ Error during process: {e}")
