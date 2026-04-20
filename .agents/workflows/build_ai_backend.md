---
description: How to build and run the Python AI backend
---

# Build & Run AI Backend

## Prerequisites
- Python 3.10+ installed and available in PATH
- pip (comes with Python)

## Steps

1. Open a terminal and navigate to the AI backend directory:
```bash
cd src/ai-backend
```

2. Create a virtual environment (recommended):
```bash
python -m venv venv
venv\Scripts\activate    # Windows
# source venv/bin/activate  # macOS/Linux
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

> **Note:** PyTorch is ~2GB. This will take a few minutes on first install.

4. Start the FastAPI server:
```bash
uvicorn main:app --host 0.0.0.0 --port 8080 --reload
```

5. Verify the server is running:
- Visit http://localhost:8080 in your browser
- Or run: `curl http://localhost:8080/health`

## Environment Variables (Optional)
- `MODEL_WEIGHTS_PATH` – Path to custom trained model weights (.pth file). If not set, uses pretrained ImageNet weights (demo mode).
- `PORT` – Server port (default: 8080)
