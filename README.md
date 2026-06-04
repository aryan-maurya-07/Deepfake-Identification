# Deepfake Identification System

## Overview

The Deepfake Identification System is an AI-powered web application that detects whether an uploaded image or video is real or AI-generated (deepfake).

This project combines a React frontend, a Python Flask backend, and a deep learning model for deepfake detection.

## Features

* User-friendly React interface
* Image and video upload support
* Deepfake detection using AI/ML
* Detection result with confidence score
* Dashboard for users
* Login and Signup pages
* Upload history page
* Responsive design

## Technologies Used

### Frontend

* React.js
* React Router
* CSS3
* Vite

### Backend

* Python
* Flask
* OpenCV
* PyTorch

### AI/ML

* ResNet50 Deep Learning Model
* Image Processing
* Deepfake Classification

## Project Structure

```text
Deepfake-Identification/
│
├── Backend/
│   ├── app.py
│   ├── model.py
│   ├── train_model.py
│   └── requirements.txt
│
├── frontend/
│   └── deepfake/
│       ├── src/
│       ├── public/
│       └── package.json
│
├── .gitignore
└── README.md
```

## Installation

### Clone Repository

```bash
git clone https://github.com/aryan-maurya-07/Deepfake-Identification.git
cd Deepfake-Identification
```

### Backend Setup

```bash
cd Backend
pip install -r requirements.txt
python app.py
```

### Frontend Setup

```bash
cd frontend/deepfake
npm install
npm run dev
```

## Future Enhancements

* Real-time webcam detection
* Advanced deepfake video analysis
* User authentication with JWT
* Detection history storage
* Cloud deployment

## Authors

Aryan Maurya
BE Information Technology
K.C. College of Engineering

## License

This project is developed for educational and research purposes.
