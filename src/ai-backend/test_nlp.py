import os
import sys

# Move to the ai-backend directory to import local modules
sys.path.append(os.path.join(os.getcwd(), "src", "ai-backend"))

import doctor

def test_pipeline():
    print("--- 🩺 AI Doctor NLP Pipeline Integration Test ---")
    
    test_notes = "Patient presents with chronic cough for 4 weeks, weight loss, and severe night sweats. Some chest pain reported."
    predicted_disease = "Tuberculosis"
    
    print(f"INPUT NOTES: {test_notes}")
    print(f"VISION PREDICTION: {predicted_disease}")
    
    print("\n[STEP 1-5] Processing...")
    # This will trigger model loading if not already cached
    result = doctor.analyze_clinical_notes(test_notes, predicted_disease)
    
    print(f"\nRESULTS:")
    print(f"- Extracted Medical Terms: {result['extracted_symptoms']}")
    print(f"- Symptom Confidence: {result['symptom_confidence']}%")
    print(f"- Reasoning: {result['reasoning']}")
    print(f"- Best NLP Match: {result['best_nlp_match']}")
    
    print("\n[STEP 6] Final Decision Fusion...")
    final = doctor.make_final_decision(85.0, result['symptom_confidence'])
    print(f"- Final Confidence: {final['final_confidence']}%")
    print(f"- Verdict: {final['verdict']}")
    print(f"- Status: {final['status']}")

if __name__ == "__main__":
    test_pipeline()
