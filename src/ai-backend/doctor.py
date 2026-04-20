"""
DiseaseAI – Advanced AI Doctor NLP Pipeline
Implements 7-step medical reasoning:
Input -> Preprocessing -> BERT Embedding -> NER -> Classification -> Context -> JSON
"""

import os
import torch
import numpy as np
from transformers import pipeline, AutoTokenizer, AutoModel
from scipy.spatial.distance import cosine
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
import json

# Download NLTK data (quietly)
try:
    nltk.download('punkt', quiet=True)
    nltk.download('stopwords', quiet=True)
    nltk.download('punkt_tab', quiet=True)
except:
    pass

# ──────────────────────────────────────────────
# Global Configuration & Model Initialization
# ──────────────────────────────────────────────

# Path for model caching
CACHE_DIR = os.path.join(os.getcwd(), "model_cache")
os.makedirs(CACHE_DIR, exist_ok=True)

class MedicalNLP:
    def __init__(self):
        print("[AI-DOCTOR] Initializing Clinical NLP Pipeline...")
        
        # 1. NER Pipeline (Extracting medical entities)
        # Using a model specialized in medical entities if possible, or standard NER
        try:
            self.ner_pipeline = pipeline("ner", model="dslim/bert-base-NER", device=-1) # CPU
            print("[AI-DOCTOR] NER Model Loaded: bert-base-NER")
        except:
            self.ner_pipeline = None

        # 2. Embedding Model (ClinicalBERT / BioBERT)
        # We use a compact but powerful medical-tuned model for embeddings
        self.embed_model_name = "sentence-transformers/all-MiniLM-L6-v2" # Fast & Accurate for similarity
        try:
            self.tokenizer = AutoTokenizer.from_pretrained(self.embed_model_name, cache_dir=CACHE_DIR)
            self.embed_model = AutoModel.from_pretrained(self.embed_model_name, cache_dir=CACHE_DIR)
            print(f"[AI-DOCTOR] Embedding Model Loaded: {self.embed_model_name}")
        except Exception as e:
            print(f"[AI-DOCTOR] Error loading embedding model: {e}")
            self.embed_model = None

    def preprocess(self, text: str) -> str:
        """Step 2: Text Preprocessing (NLTK)"""
        if not text: return ""
        # Lowercase & Tokenize
        tokens = word_tokenize(text.lower())
        # Remove stopwords and punctuation
        stop_words = set(stopwords.words('english'))
        filtered = [w for w in tokens if w.isalnum() and w not in stop_words]
        return " ".join(filtered)

    def get_embedding(self, text: str):
        """Step 3: BERT Embedding Extraction"""
        if not self.embed_model or not text:
            return None
        
        inputs = self.tokenizer(text, return_tensors="pt", padding=True, truncation=True, max_length=128)
        with torch.no_grad():
            outputs = self.embed_model(**inputs)
            # Use mean pooling for sentence embedding
            embeddings = outputs.last_hidden_state.mean(dim=1)
        return embeddings.squeeze().numpy()

    def extract_entities(self, text: str):
        """Step 4: Feature Extraction (NER)"""
        if not self.ner_pipeline:
            return []
        
        entities = self.ner_pipeline(text)
        # Filter for relevant tags or just return names
        return list(set([e['word'].replace("##", "") for e in entities if e['score'] > 0.5]))

    def calculate_similarity(self, text_vector, target_vector):
        """Cosine similarity helper"""
        if text_vector is None or target_vector is None:
            return 0.0
        return 1 - cosine(text_vector, target_vector)


# ──────────────────────────────────────────────
# AI Doctor Logic
# ──────────────────────────────────────────────

# Ontology: Reference symptoms for our 7 diseases
DISEASE_ONTOLOGY = {
    "Pneumonia": "persistent cough, high fever, chest pain, shortness of breath, fatigue, chills, phlegm",
    "Tuberculosis": "chronic cough, blood in sputum, weight loss, night sweats, fever, chest pain",
    "Skin Lesion (Melanoma)": "asymmetrical mole, irregular border, changing color, itching skin, bleeding growth",
    "Diabetic Retinopathy": "blurred vision, floaters, dark spots, vision loss, impaired color vision",
    "Brain Tumor": "severe headache, seizures, personality changes, nausea, vision problems, balance loss",
    "Breast Cancer": "breast lump, skin dimpling, nipple discharge, breast pain, swelling underarm",
    "Normal / Healthy": "feeling good, no pain, energetic, normal appetite, healthy sleep"
}

# Pre-calculate ontology embeddings
nlp_engine = MedicalNLP()
ONTOLOGY_VECTORS = {
    disease: nlp_engine.get_embedding(description)
    for disease, description in DISEASE_ONTOLOGY.items()
}

def analyze_clinical_notes(text: str, predicted_disease: str) -> dict:
    """
    Main entry point for Step 5 & 6: Classification & Context Integration.
    Returns structured JSON-ready dictionary.
    """
    if not text:
        return {
            "symptom_confidence": 0.0,
            "extracted_symptoms": [],
            "reasoning": "No clinical notes provided."
        }

    # 1. Preprocess
    clean_text = nlp_engine.preprocess(text)
    
    # 2. Extract Entities (NER)
    entities = nlp_engine.extract_entities(text)
    
    # 3. Get text embedding
    text_vector = nlp_engine.get_embedding(clean_text)
    
    # 4. Classification (Semantic Similarity)
    scores = {}
    for disease, vector in ONTOLOGY_VECTORS.items():
        score = nlp_engine.calculate_similarity(text_vector, vector)
        scores[disease] = float(score)

    # 5. Reasoning logic
    best_nlp_match = max(scores, key=scores.get)
    best_nlp_score = scores[best_nlp_match]
    target_vision_score = scores.get(predicted_disease, 0.0)

    # Scaling: Bio-ClinicalBERT similarity is usually 0.3 (random) to 0.9 (perfect)
    # We map 0.35 -> 0% and 0.85 -> 100%
    def scale(s): return round(min(100.0, max(0.0, (s - 0.35) * 200)), 2)
    
    symptom_confidence = scale(best_nlp_score)
    vision_match_conf = scale(target_vision_score)

    dissonance = best_nlp_match != predicted_disease
    
    reasoning = f"Clinical analysis suggests {best_nlp_match} with {symptom_confidence}% confidence."
    if not dissonance:
        reasoning += " This strongly corroborates the visual scan results."
    else:
        reasoning += f" However, the visual model suggests {predicted_disease}. This represents a clinical dissonance."

    return {
        "symptom_confidence": symptom_confidence,
        "vision_match_confidence": vision_match_conf,
        "extracted_symptoms": entities,
        "reasoning": reasoning,
        "best_nlp_match": best_nlp_match,
        "has_dissonance": dissonance,
        "all_nlp_scores": {k: round(v*100, 2) for k, v in scores.items()}
    }

def make_final_decision(image_confidence: float, symptom_confidence: float, best_nlp_match: str = None, has_dissonance: bool = False) -> dict:
    """Step 6: Context Integration & Final Verdict"""
    # Weighted average: Vision (60%), Symptoms (40%)
    # If there's dissonance, we penalize the "Unified" score to encourage clinical review
    penalty = 0.8 if has_dissonance else 1.0
    final_score = round(((image_confidence * 0.6) + (symptom_confidence * 0.4)) * penalty, 2)
    
    if final_score > 75:
        verdict = f"Critical / Verified"
        status = "Critical"
    elif final_score > 40:
        verdict = "Moderate Risk / Requires Review"
        status = "Alert"
    else:
        verdict = "Low Risk / No Acute Findings"
        status = "Normal"
        
    if has_dissonance and best_nlp_match:
        verdict = f"Dissonance Detected: Visual ({status}) vs Clinical ({best_nlp_match})"

    return {
        "final_confidence": final_score,
        "verdict": verdict,
        "status": status
    }

def get_all_symptoms():
    """Fallback for UI list"""
    return [
        "Cough", "Fever", "Chest Pain", "Weight Loss", "Vision Changes", 
        "Headache", "Mole Change", "Lump", "Fatigue"
    ]
