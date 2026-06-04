import torch
import torch.nn as nn
from torchvision import models, transforms
from PIL import Image
import cv2
import numpy as np

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# Load trained model
model = models.resnet50(pretrained=False)
num_ftrs = model.fc.in_features
model.fc = nn.Linear(num_ftrs, 2)
model.load_state_dict(torch.load("resnet50_deepfake.pth", map_location=device))
model.to(device)
model.eval()

transform = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
    transforms.Normalize([0.485, 0.456, 0.406], 
                         [0.229, 0.224, 0.225])
])

def predict_image(image_path):
    img = Image.open(image_path).convert("RGB")
    img = transform(img).unsqueeze(0).to(device)
    with torch.no_grad():
        output = model(img)
        pred = torch.argmax(output, 1).item()
    return "real" if pred == 1 else "fake"

def predict_video(video_path, n_frames=5):
    cap = cv2.VideoCapture(video_path)
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    preds = []

    for _ in range(n_frames):
        frame_num = np.random.randint(0, total_frames)
        cap.set(cv2.CAP_PROP_POS_FRAMES, frame_num)
        ret, frame = cap.read()
        if not ret:
            continue
        img = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
        img = transform(img).unsqueeze(0).to(device)
        with torch.no_grad():
            output = model(img)
            pred = torch.argmax(output, 1).item()
            preds.append(pred)

    cap.release()
    if len(preds) == 0:
        return "unknown"
    final_pred = max(set(preds), key=preds.count)
    return "real" if final_pred == 1 else "fake"
