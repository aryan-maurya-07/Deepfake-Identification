import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader, Dataset
from torchvision import transforms
from torchvision.models import resnet50, ResNet50_Weights
from sklearn.metrics import precision_score, recall_score, f1_score
from PIL import Image
import os, glob, cv2, random
import numpy as np

# ------------------- Device -------------------
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print(f"Using device: {device}")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATASET_DIR = os.path.join(BASE_DIR, "dataset")

# ------------------- Dataset -------------------
class DeepfakeDataset(Dataset):
    def __init__(self, root_dir, transform=None, n_frames_per_video=5):
        self.root_dir = root_dir
        self.transform = transform
        self.samples = []
        self.video_frames = {}
        self.n_frames_per_video = n_frames_per_video

        for label, cls in enumerate(["fake", "real"]):
            cls_folder = os.path.join(root_dir, cls)
            for file in glob.glob(os.path.join(cls_folder, "*")):
                if file.lower().endswith((".jpg", ".png")):
                    self.samples.append((file, label, False))
                elif file.lower().endswith((".mp4", ".avi")):
                    self.samples.append((file, label, True))
                    cap = cv2.VideoCapture(file)
                    self.video_frames[file] = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
                    cap.release()

        # Expand dataset for multiple frames per video
        expanded_samples = []
        for filepath, label, is_video in self.samples:
            if is_video:
                for _ in range(n_frames_per_video):
                    expanded_samples.append((filepath, label, True))
            else:
                expanded_samples.append((filepath, label, False))
        self.samples = expanded_samples

    def __len__(self):
        return len(self.samples)

    def __getitem__(self, idx):
        filepath, label, is_video = self.samples[idx]
        if not is_video:
            img = Image.open(filepath).convert("RGB")
        else:
            cap = cv2.VideoCapture(filepath)
            total_frames = self.video_frames[filepath]
            frame_no = random.randint(0, total_frames - 1)
            cap.set(cv2.CAP_PROP_POS_FRAMES, frame_no)
            ret, frame = cap.read()
            cap.release()
            img = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))

        if self.transform:
            img = self.transform(img)
        return img, label

# ------------------- Transforms -------------------
train_transform = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.RandomResizedCrop(224, scale=(0.8, 1.0)),
    transforms.RandomRotation(15),
    transforms.ColorJitter(brightness=0.2, contrast=0.2, saturation=0.2),
    transforms.RandomHorizontalFlip(),
    transforms.ToTensor(),
    transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
])

val_transform = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
    transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
])

# ------------------- DataLoaders -------------------
train_dataset = DeepfakeDataset(os.path.join(DATASET_DIR, "train"), transform=train_transform)
val_dataset   = DeepfakeDataset(os.path.join(DATASET_DIR, "val"), transform=val_transform)
test_dataset  = DeepfakeDataset(os.path.join(DATASET_DIR, "test"), transform=val_transform)

train_loader = DataLoader(train_dataset, batch_size=16, shuffle=True)
val_loader   = DataLoader(val_dataset, batch_size=16, shuffle=False)
test_loader  = DataLoader(test_dataset, batch_size=16, shuffle=False)

# ------------------- Model -------------------
model = resnet50(weights=ResNet50_Weights.DEFAULT)

# Freeze all layers first
for param in model.parameters():
    param.requires_grad = False

# Replace last layer
num_ftrs = model.fc.in_features
model.fc = nn.Linear(num_ftrs, 2)
model = model.to(device)

# ------------------- Loss (with class weights) -------------------
# Compute class distribution
labels = [lbl for _, lbl, _ in train_dataset.samples]
class_counts = np.bincount(labels)
weights = 1.0 / torch.tensor(class_counts, dtype=torch.float)
weights = weights / weights.sum()  # normalize
criterion = nn.CrossEntropyLoss(weight=weights.to(device))

# Optimizer & Scheduler
optimizer = optim.Adam(model.fc.parameters(), lr=1e-4)  # only train last layer first
scheduler = optim.lr_scheduler.ReduceLROnPlateau(optimizer, mode="max", patience=3, factor=0.5)

# ------------------- Training -------------------
num_epochs = 20
best_acc = 0.0
MODEL_PATH = os.path.join(BASE_DIR, "resnet50_deepfake.pth")

for epoch in range(num_epochs):
    print(f"\nEpoch {epoch+1}/{num_epochs}")

    # -------- Training --------
    model.train()
    running_loss, running_corrects = 0.0, 0
    all_preds, all_labels = [], []

    for inputs, labels in train_loader:
        inputs, labels = inputs.to(device), labels.to(device)
        optimizer.zero_grad()

        outputs = model(inputs)
        _, preds = torch.max(outputs, 1)
        loss = criterion(outputs, labels)

        loss.backward()
        optimizer.step()

        running_loss += loss.item() * inputs.size(0)
        running_corrects += torch.sum(preds == labels.data)

        all_preds.extend(preds.cpu().numpy())
        all_labels.extend(labels.cpu().numpy())

    epoch_loss = running_loss / len(train_dataset)
    epoch_acc = running_corrects.double() / len(train_dataset)
    epoch_precision = precision_score(all_labels, all_preds, average="binary")
    epoch_recall = recall_score(all_labels, all_preds, average="binary")
    epoch_f1 = f1_score(all_labels, all_preds, average="binary")

    print(f"Train Loss: {epoch_loss:.4f}, Acc: {epoch_acc:.4f}, "
          f"Precision: {epoch_precision:.4f}, Recall: {epoch_recall:.4f}, F1: {epoch_f1:.4f}")

    # -------- Validation --------
    model.eval()
    val_loss, val_corrects = 0.0, 0
    val_preds, val_labels = [], []

    with torch.no_grad():
        for inputs, labels in val_loader:
            inputs, labels = inputs.to(device), labels.to(device)
            outputs = model(inputs)
            _, preds = torch.max(outputs, 1)
            loss = criterion(outputs, labels)

            val_loss += loss.item() * inputs.size(0)
            val_corrects += torch.sum(preds == labels.data)

            val_preds.extend(preds.cpu().numpy())
            val_labels.extend(labels.cpu().numpy())

    val_loss /= len(val_dataset)
    val_acc = val_corrects.double() / len(val_dataset)
    val_precision = precision_score(val_labels, val_preds, average="binary")
    val_recall = recall_score(val_labels, val_preds, average="binary")
    val_f1 = f1_score(val_labels, val_preds, average="binary")

    print(f"Val Loss: {val_loss:.4f}, Acc: {val_acc:.4f}, "
          f"Precision: {val_precision:.4f}, Recall: {val_recall:.4f}, F1: {val_f1:.4f}")

    scheduler.step(val_acc)

    # Save best model
    if val_acc > best_acc:
        best_acc = val_acc
        torch.save(model.state_dict(), MODEL_PATH)
        print(f"✅ Best model saved at {MODEL_PATH} (Val Acc: {best_acc:.4f})")

# ------------------- Fine-tuning whole model -------------------
print("\n🔓 Unfreezing all layers for fine-tuning...")
for param in model.parameters():
    param.requires_grad = True
optimizer = optim.Adam(model.parameters(), lr=1e-5)  # lower LR for fine-tuning

for epoch in range(5):  # fine-tune for a few extra epochs
    print(f"\nFine-tune Epoch {epoch+1}/5")

    model.train()
    running_loss, running_corrects = 0.0, 0

    for inputs, labels in train_loader:
        inputs, labels = inputs.to(device), labels.to(device)
        optimizer.zero_grad()

        outputs = model(inputs)
        _, preds = torch.max(outputs, 1)
        loss = criterion(outputs, labels)

        loss.backward()
        optimizer.step()

        running_loss += loss.item() * inputs.size(0)
        running_corrects += torch.sum(preds == labels.data)

    epoch_loss = running_loss / len(train_dataset)
    epoch_acc = running_corrects.double() / len(train_dataset)
    print(f"Fine-tune Loss: {epoch_loss:.4f}, Acc: {epoch_acc:.4f}")

torch.save(model.state_dict(), MODEL_PATH)
print(f"\n🎉 Final model saved at {MODEL_PATH}")
