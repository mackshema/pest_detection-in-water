import os
import shutil
from sklearn.model_selection import train_test_split
from tqdm import tqdm

# Config
SOURCE_PEST_DIR = r"D:\pest_detection\pest"
DEST_BASE_DIR = r"D:\pest_detection\dataset"
TRAIN_DIR = os.path.join(DEST_BASE_DIR, "train")
TEST_DIR = os.path.join(DEST_BASE_DIR, "test")

# Ensure destination exists
os.makedirs(TRAIN_DIR, exist_ok=True)
os.makedirs(TEST_DIR, exist_ok=True)

def copy_images(images, destination_folder):
    os.makedirs(destination_folder, exist_ok=True)
    for img_path in images:
        try:
            shutil.copy(img_path, destination_folder)
        except Exception as e:
            print(f"Error copying {img_path}: {e}")

def process_pest_data():
    if not os.path.exists(SOURCE_PEST_DIR):
        print(f"Source directory {SOURCE_PEST_DIR} not found!")
        return

    # Get all pest classes
    classes = [d for d in os.listdir(SOURCE_PEST_DIR) if os.path.isdir(os.path.join(SOURCE_PEST_DIR, d))]
    
    print(f"Found {len(classes)} pest classes: {classes}")

    for class_name in tqdm(classes, desc="Processing Pests"):
        class_path = os.path.join(SOURCE_PEST_DIR, class_name)
        images = [os.path.join(class_path, f) for f in os.listdir(class_path) if f.lower().endswith(('.jpg', '.jpeg', '.png'))]
        
        if not images:
            continue

        # Split 80/20
        train_imgs, test_imgs = train_test_split(images, test_size=0.2, random_state=42)
        
        # Copy to destination
        copy_images(train_imgs, os.path.join(TRAIN_DIR, class_name))
        copy_images(test_imgs, os.path.join(TEST_DIR, class_name))

    print("✅ Pest data merged successfully!")

def check_dataset_status():
    print("\n--- Final Dataset Status ---")
    for split in ["train", "test"]:
        path = os.path.join(DEST_BASE_DIR, split)
        if not os.path.exists(path):
            print(f"{split} folder missing!")
            continue
            
        classes = os.listdir(path)
        print(f"[{split.upper()}] has {len(classes)} classes: {classes}")
        for c in classes:
            count = len(os.listdir(os.path.join(path, c)))
            print(f"  - {c}: {count} images")

if __name__ == "__main__":
    process_pest_data()
    check_dataset_status()
