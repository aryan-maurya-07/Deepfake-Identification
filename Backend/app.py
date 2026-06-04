from flask import Flask, request, jsonify
from flask_cors import CORS
from werkzeug.utils import secure_filename
from pymongo import MongoClient
import os
from datetime import datetime
import pytz  # ✅ Use pytz for IST timezone

# PyTorch imports
import torch
import torch.nn as nn
from torchvision import models, transforms
from PIL import Image
import cv2
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
CORS(app)

# ------------------- Config -------------------
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# ------------------- MongoDB Connection -------------------
client = MongoClient("mongodb://127.0.0.1:27017/")
db = client["deepfake_db2"]
users_col = db["users"]
results_col = db["results"]

# ------------------- IST Timezone -------------------
IST = pytz.timezone("Asia/Kolkata")

# ------------------- Load Trained Model -------------------
MODEL_PATH = "resnet50_deepfake.pth"
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

model = models.resnet50(weights=None)
num_ftrs = model.fc.in_features
model.fc = nn.Linear(num_ftrs, 2)  # 0=Fake, 1=Real
model.load_state_dict(torch.load(MODEL_PATH, map_location=device))
model.to(device)
model.eval()

# Transforms
preprocess = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
    transforms.Normalize([0.485, 0.456, 0.406],
                         [0.229, 0.224, 0.225])
])

# ------------------- Prediction Function -------------------
def predict_deepfake(filepath):
    try:
        if filepath.lower().endswith(('.mp4', '.avi', '.mov')):
            cap = cv2.VideoCapture(filepath)
            total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            frame_no = max(total_frames // 2, 0)
            cap.set(cv2.CAP_PROP_POS_FRAMES, frame_no)
            ret, frame = cap.read()
            cap.release()
            if not ret:
                raise ValueError("Cannot read frame from video")
            img = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
        else:
            img = Image.open(filepath).convert("RGB")

        img_tensor = preprocess(img).unsqueeze(0).to(device)
        with torch.no_grad():
            outputs = model(img_tensor)
            probs = torch.softmax(outputs, dim=1)
            confidence, predicted = torch.max(probs, 1)

        result = "Fake" if predicted.item() == 0 else "Real"
        return {"result": result, "confidence": float(confidence)}

    except Exception as e:
        return {"result": "Error", "confidence": 0, "error": str(e)}

# ------------------- User Signup -------------------
@app.route('/signup', methods=['POST'])
def signup():
    data = request.json
    name = data.get('name')
    email = data.get('email')
    password = data.get('password')
    if not (name and email and password):
        return jsonify({"success": False, "message": "All fields are required"}), 400

    if users_col.find_one({"email": email}):
        return jsonify({"success": False, "message": "Email already exists"}), 400

    hashed_pw = generate_password_hash(password)
    user_id = users_col.insert_one({
        "username": name,
        "email": email,
        "password": hashed_pw,
        "created_at": datetime.now(IST)  # ✅ store IST time
    }).inserted_id

    return jsonify({"success": True, "message": "User registered successfully", "user_id": str(user_id)})

# ------------------- User Login -------------------
@app.route('/login', methods=['POST'])
def login():
    data = request.json
    email = data.get('email')
    password = data.get('password')
    if not (email and password):
        return jsonify({"success": False, "message": "Email and password required"}), 400

    user = users_col.find_one({"email": email})
    if not user or not check_password_hash(user["password"], password):
        return jsonify({"success": False, "message": "Invalid credentials"}), 401

    user_data = {
        "id": str(user["_id"]),
        "username": user["username"],
        "email": user["email"]
    }
    return jsonify({"success": True, "message": "Login successful", "user": user_data})

# ------------------- File Upload -------------------
@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({"success": False, "message": "No file part"}), 400

    file = request.files['file']
    user_id = request.form.get('user_id')
    if not user_id:
        return jsonify({"success": False, "message": "User ID is required"}), 400
    if file.filename == '':
        return jsonify({"success": False, "message": "No file selected"}), 400

    filename = secure_filename(file.filename)
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(filepath)

    prediction = predict_deepfake(filepath)
    result = prediction['result']
    confidence = prediction['confidence']

    results_col.insert_one({
        "user_id": user_id,
        "filename": filename,
        "result": result,
        "confidence": confidence,
        "created_at": datetime.now(IST)  # ✅ store IST time
    })

    return jsonify({
        "success": True,
        "filename": filename,
        "result": result,
        "confidence": confidence
    })

# ------------------- Direct Prediction API -------------------
@app.route('/predict_deepfake', methods=['POST'])
def predict_endpoint():
    if 'file' not in request.files:
        return jsonify({"success": False, "message": "No file uploaded"}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({"success": False, "message": "No file selected"}), 400

    filename = secure_filename(file.filename)
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(filepath)

    prediction = predict_deepfake(filepath)
    return jsonify(prediction)

# ------------------- Get Results / History -------------------
@app.route('/results/<user_id>', methods=['GET'])
def get_results(user_id):
    results = list(results_col.find({"user_id": user_id}).sort("created_at", -1))
    formatted = []
    for r in results:
        formatted.append({
            "id": str(r["_id"]),
            "filename": r["filename"],
            "result": r["result"],
            "confidence": r["confidence"],
            "created_at": r.get("created_at").isoformat() if r.get("created_at") else None
        })
    return jsonify({"success": True, "results": formatted})

@app.route('/history/<user_id>', methods=['GET'])
def get_history(user_id):
    uploads = list(results_col.find({"user_id": user_id}).sort("created_at", -1))
    formatted = []
    for u in uploads:
        formatted.append({
            "id": str(u["_id"]),
            "filename": u["filename"],
            "result": u["result"],
            "confidence": u["confidence"],
            "created_at": u.get("created_at").isoformat() if u.get("created_at") else None
        })
    return jsonify({"success": True, "uploads": formatted})

# ------------------- Run Server -------------------
print("Available routes:")
for rule in app.url_map.iter_rules():
    print(rule, rule.methods)

if __name__ == "__main__":
    app.run(debug=True)
