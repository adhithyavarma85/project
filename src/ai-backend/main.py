"""
DiseaseAI – FastAPI Diagnostic Server
Accepts medical image uploads and returns AI-powered disease predictions.
"""

import os
import io
import time
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from PIL import Image

from model import load_model, predict_image, DISEASE_LABELS
import doctor

# ──────────────────────────────────────────────
# App Setup
# ──────────────────────────────────────────────
app = FastAPI(
    title="DiseaseAI Diagnostic Engine",
    description="Custom deep learning medical image analysis with AI Doctor symptoms",
    version="2.1.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ──────────────────────────────────────────────
# Load Model
# ──────────────────────────────────────────────
WEIGHTS_PATH = os.environ.get("MODEL_WEIGHTS_PATH", None)

# Check for weights in common locations
if not WEIGHTS_PATH:
    for path in ["disease_model_best.pth", "model_weights.pth", "weights/best.pth"]:
        if os.path.exists(path):
            WEIGHTS_PATH = path
            break

model = load_model(WEIGHTS_PATH)
is_trained = WEIGHTS_PATH is not None and os.path.exists(WEIGHTS_PATH) if WEIGHTS_PATH else False

print(f"[SERVER] Model ready | Trained: {is_trained} | Classes: {len(DISEASE_LABELS)}")


# ──────────────────────────────────────────────
# Routes
# ──────────────────────────────────────────────

@app.get("/")
async def root():
    return {
        "status": "operational",
        "engine": "PyTorch ResNet-50 (Custom Trained)" if is_trained else "PyTorch ResNet-50 (Demo Mode)",
        "version": "2.1.0",
        "is_trained": is_trained,
        "classes": len(DISEASE_LABELS),
        "features": ["Image Analysis", "AI Doctor Symptom Checker"]
    }


@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "model_loaded": model is not None,
        "is_trained": is_trained,
        "device": "cpu",
        "supported_diseases": DISEASE_LABELS,
        "symptoms_available": len(doctor.get_all_symptoms())
    }

@app.get("/symptoms")
async def get_symptoms():
    """Returns a list of all symptoms categorized or as a flat list for the UI."""
    return {
        "symptoms": doctor.get_all_symptoms(),
        "mapping": doctor.SYMPTOM_MAPPING
    }


@app.post("/predict")
async def predict(
    file: UploadFile = File(...), 
    description: str = Form(None)  # New: Free-text clinical notes from patient
):
    """
    Upload a medical image and clinical notes to get a combined AI diagnosis.
    Uses ClinicalBERT for text analysis and ResNet-50 for image analysis.
    """

    # Validate file type
    allowed_types = ["image/jpeg", "image/png", "image/bmp", "image/tiff", "image/webp"]
    if file.content_type and file.content_type not in allowed_types:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type: {file.content_type}. Use JPEG, PNG, BMP, TIFF, or WebP."
        )

    try:
        # 1. Image Analysis (Vision Model)
        contents = await file.read()
        image = Image.open(io.BytesIO(contents))

        start_time = time.time()
        vision_result = predict_image(model, image)
        inference_time = round((time.time() - start_time) * 1000, 2)

        # 2. Advanced Symptom Analysis (AI Doctor NLP Pipeline)
        # Process clinical notes using BERT/ClinicalBERT
        notes_text = description if description else ""
        nlp_result = doctor.analyze_clinical_notes(notes_text, vision_result["prediction"])
        
        # 3. Final Decision (Context Integration)
        decision = doctor.make_final_decision(
            vision_result["confidence"], 
            nlp_result["symptom_confidence"],
            best_nlp_match=nlp_result["best_nlp_match"],
            has_dissonance=nlp_result["has_dissonance"]
        )

        # 4. Return Combined Analysis
        response = {
            "prediction": vision_result["prediction"],
            "image_confidence": vision_result["confidence"],
            "symptom_confidence": nlp_result["symptom_confidence"],
            "vision_match_confidence": nlp_result["vision_match_confidence"],
            "final_confidence": decision["final_confidence"],
            "verdict": decision["verdict"],
            "status": decision["status"],
            "extracted_medical_terms": nlp_result["extracted_symptoms"],
            "clinical_reasoning": nlp_result["reasoning"],
            "severity": vision_result["severity"],
            "description": vision_result["description"],
            "recommendation": vision_result["recommendation"],
            "best_nlp_match": nlp_result["best_nlp_match"],
            "has_dissonance": nlp_result["has_dissonance"],
            "top3_predictions": vision_result["top3_predictions"],
            "inference_time_ms": inference_time,
            "filename": file.filename,
            "is_trained_model": is_trained,
            "engine_info": {
                "vision": "ResNet-50 v2.1",
                "nlp": "ClinicalBERT / Medical-NER",
                "fusion": "Weighted Bayesian Context Integration"
            }
        }

        if not is_trained:
            response["warning"] = "Running in DEMO mode with ImageNet weights. Use for integration testing only."

        return response

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Prediction failed: {str(e)}")

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Prediction failed: {str(e)}")
