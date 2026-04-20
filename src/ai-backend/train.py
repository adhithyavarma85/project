"""
DiseaseAI – Training Script
Train the ResNet-50 disease classifier on your own medical image dataset.

Usage:
    python train.py --data_dir ./dataset --epochs 25 --batch_size 16

Dataset folder structure:
    dataset/
    ├── train/
    │   ├── Normal/          (put normal/healthy images here)
    │   ├── Pneumonia/       (put pneumonia X-ray images here)
    │   ├── Tuberculosis/
    │   ├── Melanoma/
    │   ├── Diabetic_Retinopathy/
    │   ├── Brain_Tumor/
    │   └── Breast_Cancer/
    └── val/
        ├── Normal/
        ├── Pneumonia/
        └── ...  (same structure as train)

You can download free medical image datasets from:
    - Kaggle: https://www.kaggle.com/datasets
    - NIH Chest X-rays: https://nihcc.app.box.com/v/ChestXray-NIHCC
    - ISIC Skin Lesion: https://www.isic-archive.com/
    - Brain Tumor MRI: https://www.kaggle.com/datasets/masoudnickparvar/brain-tumor-mri-dataset
"""

import os
import argparse
import time
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader
from torchvision import datasets
from model import DiseaseClassifier, train_transform, inference_transform, DISEASE_LABELS


def train_model(data_dir: str, epochs: int = 25, batch_size: int = 16,
                learning_rate: float = 0.001, freeze_backbone: bool = True,
                output_path: str = "disease_model_best.pth"):
    """
    Train the disease classification model on your custom dataset.
    """

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"\n{'='*60}")
    print(f"  DiseaseAI – Training Pipeline")
    print(f"{'='*60}")
    print(f"  Device:         {device}")
    print(f"  Dataset:        {data_dir}")
    print(f"  Epochs:         {epochs}")
    print(f"  Batch Size:     {batch_size}")
    print(f"  Learning Rate:  {learning_rate}")
    print(f"  Freeze Backbone: {freeze_backbone}")
    print(f"{'='*60}\n")

    # ── Load Dataset ──────────────────────────────────
    train_dir = os.path.join(data_dir, "train")
    val_dir = os.path.join(data_dir, "val")

    if not os.path.exists(train_dir):
        print(f"ERROR: Training directory not found: {train_dir}")
        print(f"\nCreate this folder structure:")
        print(f"  {data_dir}/")
        print(f"  ├── train/")
        for label in DISEASE_LABELS:
            folder_name = label.replace(" / ", "_").replace(" ", "_").replace("(", "").replace(")", "")
            print(f"  │   ├── {folder_name}/")
        print(f"  └── val/")
        print(f"      └── (same subfolders as train)")
        return

    train_dataset = datasets.ImageFolder(train_dir, transform=train_transform)
    val_dataset = datasets.ImageFolder(val_dir, transform=inference_transform) if os.path.exists(val_dir) else None

    num_classes = len(train_dataset.classes)
    print(f"  Found {len(train_dataset)} training images in {num_classes} classes:")
    for cls_name in train_dataset.classes:
        cls_idx = train_dataset.class_to_idx[cls_name]
        count = sum(1 for _, label in train_dataset.samples if label == cls_idx)
        print(f"    - {cls_name}: {count} images")

    train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True, num_workers=0, pin_memory=True, drop_last=True)

    val_loader = None
    if val_dataset:
        val_loader = DataLoader(val_dataset, batch_size=batch_size, shuffle=False, num_workers=0, pin_memory=True)
        print(f"\n  Found {len(val_dataset)} validation images")

    # ── Initialize Model ──────────────────────────────
    model = DiseaseClassifier(num_classes=num_classes, freeze_backbone=freeze_backbone)
    model = model.to(device)

    # ── Loss & Optimizer ──────────────────────────────
    criterion = nn.CrossEntropyLoss()

    # Only optimize parameters that require gradients
    params_to_optimize = [p for p in model.parameters() if p.requires_grad]
    optimizer = optim.Adam(params_to_optimize, lr=learning_rate, weight_decay=1e-4)

    # Learning rate scheduler — reduce LR when validation loss plateaus
    scheduler = optim.lr_scheduler.ReduceLROnPlateau(optimizer, mode='min', factor=0.5, patience=3)

    # ── Training Loop ─────────────────────────────────
    best_accuracy = 0.0
    print(f"\n  Starting training...\n")

    for epoch in range(epochs):
        model.train()
        running_loss = 0.0
        correct = 0
        total = 0
        start_time = time.time()

        for batch_idx, (images, labels) in enumerate(train_loader):
            images, labels = images.to(device), labels.to(device)

            optimizer.zero_grad()
            outputs = model(images)
            loss = criterion(outputs, labels)
            loss.backward()
            optimizer.step()

            running_loss += loss.item()
            _, predicted = torch.max(outputs, 1)
            total += labels.size(0)
            correct += (predicted == labels).sum().item()

        epoch_loss = running_loss / len(train_loader)
        epoch_acc = (correct / total) * 100
        epoch_time = time.time() - start_time

        # ── Validation ────────────────────────────────
        val_loss = 0.0
        val_acc = 0.0
        if val_loader:
            model.eval()
            val_correct = 0
            val_total = 0
            val_running_loss = 0.0

            with torch.no_grad():
                for images, labels in val_loader:
                    images, labels = images.to(device), labels.to(device)
                    outputs = model(images)
                    loss = criterion(outputs, labels)
                    val_running_loss += loss.item()
                    _, predicted = torch.max(outputs, 1)
                    val_total += labels.size(0)
                    val_correct += (predicted == labels).sum().item()

            val_loss = val_running_loss / len(val_loader)
            val_acc = (val_correct / val_total) * 100
            scheduler.step(val_loss)

        # ── Print Progress ────────────────────────────
        print(f"  Epoch [{epoch+1:3d}/{epochs}] "
              f"| Train Loss: {epoch_loss:.4f} | Train Acc: {epoch_acc:.1f}% "
              f"| Val Loss: {val_loss:.4f} | Val Acc: {val_acc:.1f}% "
              f"| Time: {epoch_time:.1f}s")

        # ── Save Best Model ───────────────────────────
        current_acc = val_acc if val_loader else epoch_acc
        if current_acc > best_accuracy:
            best_accuracy = current_acc
            checkpoint = {
                'model_state_dict': model.state_dict(),
                'accuracy': best_accuracy,
                'epoch': epoch + 1,
                'num_classes': num_classes,
                'class_names': train_dataset.classes,
                'optimizer_state_dict': optimizer.state_dict()
            }
            torch.save(checkpoint, output_path)
            print(f"  ★ Saved best model (accuracy: {best_accuracy:.1f}%)")

    print(f"\n{'='*60}")
    print(f"  Training Complete!")
    print(f"  Best Accuracy: {best_accuracy:.1f}%")
    print(f"  Model saved to: {output_path}")
    print(f"{'='*60}")
    print(f"\n  To use your trained model, start the server with:")
    print(f"    MODEL_WEIGHTS_PATH={output_path} uvicorn main:app --port 8080")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Train DiseaseAI classifier")
    parser.add_argument("--data_dir", type=str, required=True, help="Path to dataset folder")
    parser.add_argument("--epochs", type=int, default=25, help="Number of training epochs")
    parser.add_argument("--batch_size", type=int, default=16, help="Batch size")
    parser.add_argument("--lr", type=float, default=0.001, help="Learning rate")
    parser.add_argument("--freeze", action="store_true", help="Freeze backbone (recommended for small datasets)")
    parser.add_argument("--output", type=str, default="disease_model_best.pth", help="Output weights path")

    args = parser.parse_args()
    train_model(
        data_dir=args.data_dir,
        epochs=args.epochs,
        batch_size=args.batch_size,
        learning_rate=args.lr,
        freeze_backbone=args.freeze,
        output_path=args.output
    )
