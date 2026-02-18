import os
import shutil
import random
import requests
from tqdm import tqdm
from sklearn.model_selection import train_test_split

# ==============================
# CONFIG
# ==============================
BASE_DIR = r"D:\pest_detection\dataset"
TRAIN_DIR = os.path.join(BASE_DIR, "train")
TEST_DIR = os.path.join(BASE_DIR, "test")

FROG_REPO_URL = "https://github.com/jonshamir/frog-dataset/archive/refs/heads/master.zip"

# Create base folders
os.makedirs(TRAIN_DIR, exist_ok=True)
os.makedirs(TEST_DIR, exist_ok=True)

# ==============================
# UTILITY FUNCTIONS
# ==============================

def download_and_extract_zip(url, extract_to):
    zip_path = os.path.join(extract_to, "temp.zip")
    
    # Ensure directory exists
    os.makedirs(extract_to, exist_ok=True)

    print("Downloading dataset...")
    try:
        response = requests.get(url, stream=True)
        response.raise_for_status() # Check for HTTP errors
        total_size = int(response.headers.get('content-length', 0))

        with open(zip_path, "wb") as file, tqdm(
            desc="Downloading",
            total=total_size,
            unit="B",
            unit_scale=True
        ) as bar:
            for data in response.iter_content(chunk_size=1024):
                file.write(data)
                bar.update(len(data))

        print("Extracting...")
        shutil.unpack_archive(zip_path, extract_to)
        os.remove(zip_path)
        print("Done!")
    except Exception as e:
        print(f"Error downloading/extracting: {e}")
        if os.path.exists(zip_path):
            os.remove(zip_path)

def split_dataset(source_folder, class_name, test_size=0.2):
    images = []
    for root, dirs, files in os.walk(source_folder):
        for file in files:
            if file.lower().endswith((".jpg", ".jpeg", ".png")):
                images.append(os.path.join(root, file))

    if not images:
        print(f"No images found for {class_name} in {source_folder}")
        return

    # Handle case where there are too few images to split
    if len(images) < 2:
        print(f"Not enough images to split for {class_name}. Copying to train only.")
        train_imgs = images
        test_imgs = []
    else:
        train_imgs, test_imgs = train_test_split(images, test_size=test_size, random_state=42)

    train_class_dir = os.path.join(TRAIN_DIR, class_name)
    test_class_dir = os.path.join(TEST_DIR, class_name)

    os.makedirs(train_class_dir, exist_ok=True)
    os.makedirs(test_class_dir, exist_ok=True)

    print(f"Copying images for {class_name}...")
    for img in train_imgs:
        try:
            shutil.copy(img, train_class_dir)
        except Exception as e:
            print(f"Error copying {img}: {e}")

    for img in test_imgs:
        try:
            shutil.copy(img, test_class_dir)
        except Exception as e:
            print(f"Error copying {img}: {e}")

    print(f"{class_name} → {len(train_imgs)} train, {len(test_imgs)} test images")

# ==============================
# DOWNLOAD FROG DATASET
# ==============================

def setup_frog_dataset():
    temp_dir = r"D:\pest_detection\temp_frog"
    # Clean up previous temp run if exists
    if os.path.exists(temp_dir):
        shutil.rmtree(temp_dir)
    os.makedirs(temp_dir, exist_ok=True)

    download_and_extract_zip(FROG_REPO_URL, temp_dir)

    # Find extracted folder
    extracted_folder = None
    for folder in os.listdir(temp_dir):
        # GitHub archives usually unzip to RepoName-BranchName
        if folder.startswith("frog-dataset") or folder.startswith("dataset"):
             # Look for the internal structure, sometimes it's nested
             candidate = os.path.join(temp_dir, folder)
             if os.path.isdir(candidate):
                 extracted_folder = candidate
                 break

    if extracted_folder:
        # The frog dataset zip structure might be specific, but we'll search recursively via split_dataset
        split_dataset(extracted_folder, "frog")
    else:
        print("Could not find extracted folder for frog dataset.")

    # Cleanup
    if os.path.exists(temp_dir):
        shutil.rmtree(temp_dir)

# ==============================
# ADD CUSTOM DATASET (Manual URL)
# ==============================

def download_custom_images(image_urls, class_name):
    class_temp_dir = os.path.join(BASE_DIR, "temp_" + class_name)
    if os.path.exists(class_temp_dir):
        shutil.rmtree(class_temp_dir)
    os.makedirs(class_temp_dir, exist_ok=True)

    print(f"Downloading {class_name} images...")

    detection_count = 0
    for i, url in enumerate(image_urls):
        try:
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                with open(os.path.join(class_temp_dir, f"{class_name}_{i}.jpg"), "wb") as f:
                    f.write(response.content)
                detection_count += 1
        except Exception as e:
            print(f"Failed to download {url}: {e}")
    
    if detection_count > 0:
        split_dataset(class_temp_dir, class_name)
    else:
        print(f"No images downloaded for {class_name}.")

    if os.path.exists(class_temp_dir):
        shutil.rmtree(class_temp_dir)

# ==============================
# MAIN
# ==============================

if __name__ == "__main__":
    print("=== Dataset Auto Setup Started ===")
    
    # Check dependencies
    try:
        import requests
        import tqdm
        import sklearn
    except ImportError as e:
        print("Missing dependencies! Please run:")
        print("pip install requests tqdm scikit-learn")
        exit(1)

    # 1️⃣ Frog dataset
    print("\n--- Processing Frog Dataset ---")
    setup_frog_dataset()

    # 2️⃣ Example: Add clean water images manually
    print("\n--- Processing Clean Water Dataset ---")
    clean_water_urls = [
         # Unsplash source images (random water textures)
        "https://images.unsplash.com/photo-1541675154750-0444c7d51e8e?ixlib=rb-4.0.3&w=1080&fit=max&q=80&fm=jpg&crop=entropy&cs=tinysrgb",
        "https://images.unsplash.com/photo-1437482078695-73f5ca6c96e2?ixlib=rb-4.0.3&w=1080&fit=max&q=80&fm=jpg&crop=entropy&cs=tinysrgb",
        "https://images.unsplash.com/photo-1562016600-ece13e8ba570?ixlib=rb-4.0.3&w=1080&fit=max&q=80&fm=jpg&crop=entropy&cs=tinysrgb",
        "https://images.unsplash.com/photo-1500375592092-40eb2168fd21?ixlib=rb-4.0.3&w=1080&fit=max&q=80&fm=jpg&crop=entropy&cs=tinysrgb"
    ]

    download_custom_images(clean_water_urls, "clean_water")

    print("\n=== All Datasets Prepared Successfully ===")
