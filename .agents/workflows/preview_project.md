---
description: How to build and preview the full project (Next.js + AI backend)
---

# Preview Full Project

## Step 1: Start the Python AI Backend

1. Open a terminal and run:
```bash
cd src/ai-backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --host 0.0.0.0 --port 8080 --reload
```

2. Keep this terminal running.

## Step 2: Start the Next.js Frontend

1. Open a **second** terminal and run:
// turbo
```bash
npm install
```
// turbo
```bash
npm run dev
```

2. Open http://localhost:9002 in your browser.

## Step 3: Test the Full Flow

1. Log in or sign up at http://localhost:9002/login
2. Go to the Dashboard
3. Upload a medical image (JPEG, PNG)
4. Click "Run AI Diagnosis"
5. The image is sent to the Python backend → ResNet-50 model → prediction returned
6. Results (disease, confidence, severity, recommendations) appear on screen and are saved to Firestore
