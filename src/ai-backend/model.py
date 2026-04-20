"""
DiseaseAI – Custom Deep Learning Model
ResNet-50 based classifier with transfer learning for medical image diagnosis.
Train this model on your own dataset to get accurate predictions.
"""

import torch
import torch.nn as nn
from torchvision import models, transforms
from PIL import Image
import os
  
# ──────────────────────────────────────────────
# Disease Categories
# ──────────────────────────────────────────────
DISEASE_LABELS = [
    "Normal / Healthy",
    "Pneumonia",
    "Tuberculosis",
    "Skin Lesion (Melanoma)",
    "Diabetic Retinopathy",
    "Brain Tumor",
    "Breast Cancer"
]

DISEASE_INFO = {
    "Normal / Healthy": {
        "severity": "None",
        "description": "No significant abnormalities detected in the uploaded image. The tissue appears healthy based on AI analysis.",
        "recommendation": "Continue routine check-ups. Maintain a healthy lifestyle and schedule regular screenings as recommended by your healthcare provider."
    },
    "Pneumonia": {
        "severity": "Moderate to High",
        "description": "Signs consistent with pneumonia detected. The AI identified opacity patterns in the lung fields that may indicate an active infection or inflammation.",
        "recommendation": "Seek immediate medical consultation. A chest X-ray review by a radiologist, blood tests, and possible sputum culture are recommended."
    },
    "Tuberculosis": {
        "severity": "High",
        "description": "Radiological patterns suggestive of tuberculosis (TB) were detected, including possible cavitary lesions or upper lobe infiltrates.",
        "recommendation": "Urgent medical evaluation is required. A sputum AFB test, Mantoux test, and consultation with a pulmonologist are strongly recommended."
    },
    "Skin Lesion (Melanoma)": {
        "severity": "High",
        "description": "The uploaded skin image shows features consistent with a potentially malignant melanoma, including asymmetry, irregular borders, or color variation.",
        "recommendation": "Consult a dermatologist immediately for a biopsy and histopathological examination. Early detection significantly improves outcomes."
    },
    "Diabetic Retinopathy": {
        "severity": "Moderate",
        "description": "Retinal image analysis suggests signs of diabetic retinopathy, such as microaneurysms, hemorrhages, or exudates in the fundus.",
        "recommendation": "Schedule an appointment with an ophthalmologist. Blood sugar management is critical."
    },
    "Brain Tumor": {
        "severity": "Critical",
        "description": "MRI/CT scan analysis detected abnormal mass-like features that may indicate a brain tumor. Further differential diagnosis is essential.",
        "recommendation": "Immediate consultation with a neurologist/neurosurgeon is essential. Further imaging and possibly a biopsy are required."
    },
    "Breast Cancer": {
        "severity": "High",
        "description": "Image analysis reveals suspicious features such as irregular masses, microcalcifications, or architectural distortion.",
        "recommendation": "Urgent referral to a breast specialist for further imaging and core needle biopsy."
    }
}



# ──────────────────────────────────────────────
# Image Preprocessing
# ──────────────────────────────────────────────

# Training transforms (with data augmentation)
train_transform = transforms.Compose([
    transforms.Resize((256, 256)),
    transforms.RandomResizedCrop(224),
    transforms.RandomHorizontalFlip(),
    transforms.RandomRotation(15),
    transforms.ColorJitter(brightness=0.2, contrast=0.2, saturation=0.1),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
])

# Inference transforms (no augmentation)
inference_transform = transforms.Compose([
    transforms.Resize((256, 256)),
    transforms.CenterCrop(224),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
])


# ──────────────────────────────────────────────
# Model Architecture
# ──────────────────────────────────────────────

class DiseaseClassifier(nn.Module):
    """
    Custom disease classification CNN based on ResNet-50 with transfer learning.
    
    Architecture:
    - ResNet-50 backbone (pretrained on ImageNet)
    - Custom classification head with dropout for regularization
    - BatchNorm for stable training
    
    To train on your own data:
        1. Organize images into folders: dataset/train/{disease_name}/
        2. Run: python train.py --data_dir ./dataset --epochs 25
        3. The trained weights are saved as 'disease_model_best.pth'
    """

    def __init__(self, num_classes: int = 7, freeze_backbone: bool = False):
        super(DiseaseClassifier, self).__init__()

        # Load pretrained ResNet-50 backbone
        self.backbone = models.resnet50(weights=models.ResNet50_Weights.IMAGENET1K_V2)

        # Optionally freeze backbone layers (useful for small datasets)
        if freeze_backbone:
            for param in self.backbone.parameters():
                param.requires_grad = False

        # Replace the final classification head
        in_features = self.backbone.fc.in_features  # 2048 for ResNet-50
        self.backbone.fc = nn.Sequential(
            nn.Dropout(0.4),
            nn.Linear(in_features, 512),
            nn.ReLU(inplace=True),
            nn.BatchNorm1d(512),
            nn.Dropout(0.3),
            nn.Linear(512, 256),
            nn.ReLU(inplace=True),
            nn.Linear(256, num_classes)
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.backbone(x)


# ──────────────────────────────────────────────
# Model Loading & Inference Utilities
# ──────────────────────────────────────────────

def load_model(weights_path: str = None, num_classes: int = 7) -> DiseaseClassifier:
    """
    Load the disease classification model.
    If weights_path is provided, loads your custom trained weights.
    Otherwise uses pretrained ImageNet backbone (demo mode — predictions won't be medically accurate).
    """
    model = DiseaseClassifier(num_classes=num_classes)

    if weights_path and os.path.exists(weights_path):
        try:
            checkpoint = torch.load(weights_path, map_location=torch.device('cpu'))
            # Support both raw state_dict and full checkpoint
            if isinstance(checkpoint, dict) and 'model_state_dict' in checkpoint:
                model.load_state_dict(checkpoint['model_state_dict'])
                print(f"[MODEL] Loaded trained weights from {weights_path}")
                if 'accuracy' in checkpoint:
                    print(f"[MODEL] Model accuracy at save time: {checkpoint['accuracy']:.2f}%")
            else:
                model.load_state_dict(checkpoint)
                print(f"[MODEL] Loaded state dict from {weights_path}")
        except Exception as e:
            print(f"[MODEL] Warning: Could not load weights: {e}")
            print("[MODEL] Falling back to demo mode (pretrained ImageNet)")
    else:
        print("[MODEL] ⚠ No trained weights found — running in DEMO mode")
        print("[MODEL]   Predictions will NOT be medically accurate.")
        print("[MODEL]   Train the model: python train.py --data_dir ./dataset --epochs 25")

    model.eval()
    return model


def preprocess_image(image: Image.Image) -> torch.Tensor:
    """Preprocess a PIL Image for model inference."""
    if image.mode != 'RGB':
        image = image.convert('RGB')
    tensor = inference_transform(image)
    return tensor.unsqueeze(0)  # Add batch dimension


def predict_image(model: DiseaseClassifier, image: Image.Image) -> dict:
    """
    Run prediction on a single image.
    Returns prediction label, confidence, and top-3 predictions.
    """
    input_tensor = preprocess_image(image)

    with torch.no_grad():
        output = model(input_tensor)
        probabilities = torch.nn.functional.softmax(output, dim=1)
        confidence, predicted_idx = torch.max(probabilities, 1)

    predicted_class = DISEASE_LABELS[predicted_idx.item()]
    confidence_score = round(float(confidence.item()) * 100, 2)

    # Top-3 predictions
    top3_probs, top3_indices = torch.topk(probabilities, k=min(3, len(DISEASE_LABELS)), dim=1)
    top3 = []
    for i in range(top3_probs.size(1)):
        label = DISEASE_LABELS[top3_indices[0][i].item()]
        prob = round(float(top3_probs[0][i].item()) * 100, 2)
        top3.append({"disease": label, "confidence": prob})

    disease_info = DISEASE_INFO.get(predicted_class, {})

    return {
        "prediction": predicted_class,
        "confidence": confidence_score,
        "severity": disease_info.get("severity", "Unknown"),
        "description": disease_info.get("description", ""),
        "recommendation": disease_info.get("recommendation", ""),
        "status": "Normal" if predicted_idx.item() == 0 else "Alert",
        "top3_predictions": top3
    }
