import os
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

# ──────────────────────────────────────────────
# Categories
# ──────────────────────────────────────────────
DISEASE_LABELS = [
    "Normal",
    "Pneumonia",
    "Tuberculosis",
    "Melanoma",
    "Diabetic_Retinopathy",
    "Brain_Tumor",
    "Breast_Cancer"
]

def generate_image(category, size=(256, 256)):
    """Generate a synthetic image that loosely represents the category."""
    
    # Base background (dark gray/black like an X-ray/MRI)
    bg_color = np.random.randint(20, 50)
    img_arr = np.full((size[1], size[0], 3), bg_color, dtype=np.uint8)
    
    # Add some base noise
    noise = np.random.randint(-10, 10, (size[1], size[0], 3), dtype=np.int16)
    img_arr = np.clip(img_arr + noise, 0, 255).astype(np.uint8)
    
    img = Image.fromarray(img_arr)
    draw = ImageDraw.Draw(img)
    
    center_x, center_y = size[0] // 2, size[1] // 2
    
    if category == "Normal":
        # Clear, soft symmetrical shape (healthy lung/brain)
        draw.ellipse([center_x-60, center_y-80, center_x+60, center_y+80], fill=(100, 100, 100))
        img = img.filter(ImageFilter.GaussianBlur(10))
        
    elif category == "Pneumonia":
        # Cloudy, widespread white patches
        draw.ellipse([center_x-60, center_y-80, center_x+60, center_y+80], fill=(90, 90, 90))
        for _ in range(5):
            x, y = np.random.randint(80, 170, 2)
            draw.ellipse([x-30, y-30, x+30, y+30], fill=(160, 160, 160))
        img = img.filter(ImageFilter.GaussianBlur(15))
        
    elif category == "Tuberculosis":
        # Small cavitary lesions (dark spots with bright borders)
        draw.ellipse([center_x-60, center_y-80, center_x+60, center_y+80], fill=(90, 90, 90))
        x, y = np.random.randint(100, 150, 2)
        draw.ellipse([x-15, y-15, x+15, y+15], outline=(200, 200, 200), width=3)
        img = img.filter(ImageFilter.GaussianBlur(5))
        
    elif category == "Melanoma":
        # Skin color background with an irregular dark asymmetrical spot
        img_arr = np.full((size[1], size[0], 3), (210, 170, 140), dtype=np.uint8)
        img = Image.fromarray(img_arr)
        draw = ImageDraw.Draw(img)
        draw.polygon([(100,100), (160, 110), (140, 170), (90, 150)], fill=(30, 20, 20))
        img = img.filter(ImageFilter.GaussianBlur(2))
        
    elif category == "Diabetic_Retinopathy":
        # Orange/Red background with small red dots (hemorrhages)
        img_arr = np.full((size[1], size[0], 3), (180, 80, 30), dtype=np.uint8)
        img = Image.fromarray(img_arr)
        draw = ImageDraw.Draw(img)
        draw.ellipse([center_x-90, center_y-90, center_x+90, center_y+90], fill=(150, 50, 20))
        for _ in range(8):
            x, y = np.random.randint(100, 150, 2)
            draw.ellipse([x-3, y-3, x+3, y+3], fill=(80, 0, 0))
        img = img.filter(ImageFilter.GaussianBlur(3))
        
    elif category == "Brain_Tumor":
        # Brain shape with a distinct bright, localized mass
        draw.ellipse([center_x-70, center_y-90, center_x+70, center_y+90], fill=(80, 80, 80))
        tx, ty = np.random.randint(100, 150, 2)
        draw.ellipse([tx-20, ty-20, tx+20, ty+20], fill=(220, 220, 220))
        img = img.filter(ImageFilter.GaussianBlur(4))
        
    elif category == "Breast_Cancer":
        # Mammogram style (very dark, with bright microcalcifications/masses)
        draw.pieslice([40, 40, 200, 240], 270, 90, fill=(70, 70, 70))
        cx, cy = np.random.randint(80, 120), np.random.randint(100, 180)
        draw.ellipse([cx-15, cy-15, cx+15, cy+15], fill=(200, 200, 200))
        img = img.filter(ImageFilter.GaussianBlur(3))
        
    return img

def main():
    base_dir = "./dataset"
    train_dir = os.path.join(base_dir, "train")
    val_dir = os.path.join(base_dir, "val")
    
    # Needs to be small so training is very fast on CPU!
    IMAGES_PER_CLASS_TRAIN = 15
    IMAGES_PER_CLASS_VAL = 5

    print("Generating Synthetic Medical Dataset...")
    
    for category in DISEASE_LABELS:
        train_cat_dir = os.path.join(train_dir, category)
        val_cat_dir = os.path.join(val_dir, category)
        
        os.makedirs(train_cat_dir, exist_ok=True)
        os.makedirs(val_cat_dir, exist_ok=True)
        
        # Generate Training Images
        for i in range(IMAGES_PER_CLASS_TRAIN):
            img = generate_image(category)
            img.save(os.path.join(train_cat_dir, f"{category}_train_{i}.jpg"))
            
        # Generate Validation Images
        for i in range(IMAGES_PER_CLASS_VAL):
            img = generate_image(category)
            img.save(os.path.join(val_cat_dir, f"{category}_val_{i}.jpg"))
            
        print(f"✅ Generated {IMAGES_PER_CLASS_TRAIN + IMAGES_PER_CLASS_VAL} images for {category}")

    print("\nDataset generation complete!")
    print("You can now run: python train.py --data_dir ./dataset --epochs 3")

if __name__ == "__main__":
    main()
