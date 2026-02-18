import os
import shutil
import requests
from tqdm import tqdm

# ==============================
# CONFIG
# ==============================
PEST_SOURCE_DIR = r"D:\pest_detection\pest"
DEST_BASE_DIR = r"D:\pest_detection\dataset"
TRAIN_DIR = os.path.join(DEST_BASE_DIR, "train")
TEST_DIR = os.path.join(DEST_BASE_DIR, "test")

FROG_REPO_URL = "https://github.com/jonshamir/frog-dataset/archive/refs/heads/master.zip"

# ==============================
# UTILS
# ==============================
def download_and_extract_frog():
    # Only download if not already present
    if os.path.exists(os.path.join(TRAIN_DIR, "frog")):
        print("🐸 Frog dataset seems to be present.")
        return

    print("⬇ Downloading Frog Dataset...")
    zip_path = os.path.join(DEST_BASE_DIR, "frog.zip")
    
    try:
        r = requests.get(FROG_REPO_URL, stream=True)
        with open(zip_path, 'wb') as f:
            for chunk in r.iter_content(chunk_size=1024): 
                if chunk: f.write(chunk)
        
        print("📦 Extracting Frog Dataset...")
        shutil.unpack_archive(zip_path, DEST_BASE_DIR)
        
        # Move extracted files
        extracted_root = os.path.join(DEST_BASE_DIR, "frog-dataset-master")
        if not os.path.exists(extracted_root):
             # Try generic search
             for d in os.listdir(DEST_BASE_DIR):
                 if "frog-dataset" in d and os.path.isdir(os.path.join(DEST_BASE_DIR, d)):
                     extracted_root = os.path.join(DEST_BASE_DIR, d)
                     break
        
        # The frog dataset usually has 'data-clean' or similar. 
        # We'll just grab all images and split them.
        all_frogs = []
        for root, dirs, files in os.walk(extracted_root):
            for file in files:
                if file.lower().endswith(('.jpg', '.png')):
                    all_frogs.append(os.path.join(root, file))
        
        # Split 80/20
        split_idx = int(len(all_frogs) * 0.8)
        train_frogs = all_frogs[:split_idx]
        test_frogs = all_frogs[split_idx:]
        
        # Copy to Train/Test
        os.makedirs(os.path.join(TRAIN_DIR, "frog"), exist_ok=True)
        os.makedirs(os.path.join(TEST_DIR, "frog"), exist_ok=True)
        
        for img in train_frogs: shutil.copy(img, os.path.join(TRAIN_DIR, "frog"))
        for img in test_frogs: shutil.copy(img, os.path.join(TEST_DIR, "frog"))
        
        print(f"✅ Frog data added! ({len(train_frogs)} train, {len(test_frogs)} test)")
        
        # Cleanup
        os.remove(zip_path)
        shutil.rmtree(extracted_root)
        
    except Exception as e:
        print(f"❌ Error setting up frogs: {e}")

def merge_original_pests():
    print("🐜 Merging original pests...")
    
    # We expect PEST_SOURCE_DIR to have 'train' and 'test' subfolders 
    # OR class folders directly. Let's check.
    
    if os.path.exists(os.path.join(PEST_SOURCE_DIR, "train")):
        # Structure is pest/train/class
        splits = ["train", "test"]
        for split in splits:
            src_split = os.path.join(PEST_SOURCE_DIR, split)
            dst_split = os.path.join(DEST_BASE_DIR, split)
            
            if not os.path.exists(src_split): continue
            
            for class_name in os.listdir(src_split):
                src_class = os.path.join(src_split, class_name)
                dst_class = os.path.join(dst_split, class_name)
                
                if os.path.isdir(src_class):
                    print(f"   Copying {class_name} ({split})...")
                    os.makedirs(dst_class, exist_ok=True)
                    for f in os.listdir(src_class):
                        shutil.copy(os.path.join(src_class, f), dst_class)
    else:
        # Flat structure? (Just classes)
        # Assuming we need to split if it's flat.
        # But previous investigation showed train/test exist.
        print("⚠ Unexpected structure in pest folder. Check manually if empty.")

# ==============================
# MAIN
# ==============================
if __name__ == "__main__":
    copy_clean_water = False # Assuming already done by prepare_dataset.py
    
    merge_original_pests()
    download_and_extract_frog()
    
    print("\n🎉 DATASET READY FOR TRAINING!")
    print(f"Location: {DEST_BASE_DIR}")
    
    # List classes
    print("Classes:", os.listdir(TRAIN_DIR))
