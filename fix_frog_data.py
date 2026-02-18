import os
import shutil
import random

TRAIN_FROG = r"D:\pest_detection\dataset\train\frog"
TEST_FROG = r"D:\pest_detection\dataset\test\frog"

def fix_frog_split():
    if not os.path.exists(TRAIN_FROG):
        print("❌ Train frog folder missing!")
        return

    os.makedirs(TEST_FROG, exist_ok=True)

    # Check validation set
    test_files = os.listdir(TEST_FROG)
    if len(test_files) > 0:
        print(f"✅ Test set already has {len(test_files)} images.")
        return

    print("⚠️ Test set is empty! Moving images from Train...")
    
    train_files = os.listdir(TRAIN_FROG)
    if len(train_files) < 10:
        print("❌ Not enough training images to split.")
        return
        
    # Move 20%
    move_count = int(len(train_files) * 0.2)
    files_to_move = train_files[-move_count:] # Take from end
    
    print(f"Moving {len(files_to_move)} images to test set...")
    
    for f in files_to_move:
        src = os.path.join(TRAIN_FROG, f)
        dst = os.path.join(TEST_FROG, f)
        shutil.move(src, dst)
        
    print("✅ Fixed Frog Data Split!")

if __name__ == "__main__":
    fix_frog_split()
