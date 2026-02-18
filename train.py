import torch
import torch.nn as nn
import torch.optim as optim
from torchvision import datasets, transforms, models
from torch.utils.data import DataLoader
from tqdm import tqdm
import os

# ==========================
# CONFIGURATION
# ==========================
DATA_DIR = r"D:\pest_detection\pest"
OUTPUT_PATH = r"D:\pest_detection\pest_model.pth"
BATCH_SIZE = 32
EPOCHS = 15
LR = 0.001
IMAGE_SIZE = 224

# ==========================
# DEVICE (GPU)
# ==========================
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print("Using device:", device)

# ==========================
# TRANSFORMS
# ==========================
transform = transforms.Compose([
    transforms.Resize((IMAGE_SIZE, IMAGE_SIZE)),
    transforms.ToTensor(),
    transforms.Normalize([0.485, 0.456, 0.406],
                         [0.229, 0.224, 0.225])
])

# ==========================
# DATASETS
# ==========================
train_dataset = datasets.ImageFolder(
    root=os.path.join(DATA_DIR, "train"),
    transform=transform
)

test_dataset = datasets.ImageFolder(
    root=os.path.join(DATA_DIR, "test"),
    transform=transform
)

train_loader = DataLoader(train_dataset, batch_size=BATCH_SIZE, shuffle=True)
test_loader = DataLoader(test_dataset, batch_size=BATCH_SIZE, shuffle=False)

class_names = train_dataset.classes
num_classes = len(class_names)

print("Classes:", class_names)

# ==========================
# MODEL (TRANSFER LEARNING - RESNET18)
# ==========================
model = models.resnet18(pretrained=True)
model.fc = nn.Linear(model.fc.in_features, num_classes)
model = model.to(device)

# ==========================
# LOSS & OPTIMIZER
# ==========================
criterion = nn.CrossEntropyLoss()
optimizer = optim.Adam(model.parameters(), lr=LR)

# ==========================
# TRAINING LOOP
# ==========================
best_accuracy = 0.0

for epoch in range(EPOCHS):
    model.train()
    running_loss = 0.0
    
    print(f"\nEpoch [{epoch+1}/{EPOCHS}]")
    
    for images, labels in tqdm(train_loader):
        images = images.to(device)
        labels = labels.to(device)

        optimizer.zero_grad()
        outputs = model(images)
        loss = criterion(outputs, labels)
        loss.backward()
        optimizer.step()

        running_loss += loss.item()

    print("Training Loss:", running_loss / len(train_loader))

    # ==========================
    # VALIDATION
    # ==========================
    model.eval()
    correct = 0
    total = 0

    with torch.no_grad():
        for images, labels in test_loader:
            images = images.to(device)
            labels = labels.to(device)

            outputs = model(images)
            _, predicted = torch.max(outputs, 1)

            total += labels.size(0)
            correct += (predicted == labels).sum().item()

    accuracy = 100 * correct / total
    print(f"Test Accuracy: {accuracy:.2f}%")

    # Save best model
    if accuracy > best_accuracy:
        best_accuracy = accuracy
        torch.save(model.state_dict(), OUTPUT_PATH)
        print("Model Saved!")

print("\nTraining Complete!")
print("Best Accuracy:", best_accuracy)