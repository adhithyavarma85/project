"""Minimal test - print key diagnostic fields only."""
import urllib.request, json

boundary = "----TB123"
img_path = "dataset/train/Brain_Tumor/tumor_mri_axial_1_1774167033856.png"
desc = "Patient is a 45-year-old male with progressive headaches, blurred vision, partial seizure, and mild short-term memory impairment."

body = b""
body += ("--" + boundary + "\r\n").encode()
body += b"Content-Disposition: form-data; name=\"file\"; filename=\"t.png\"\r\n"
body += b"Content-Type: image/png\r\n\r\n"
with open(img_path, "rb") as f:
    body += f.read()
body += b"\r\n"
body += ("--" + boundary + "\r\n").encode()
body += b"Content-Disposition: form-data; name=\"description\"\r\n\r\n"
body += desc.encode() + b"\r\n"
body += ("--" + boundary + "--\r\n").encode()

req = urllib.request.Request("http://localhost:8080/predict", data=body,
    headers={"Content-Type": "multipart/form-data; boundary=" + boundary})

try:
    resp = urllib.request.urlopen(req, timeout=30)
    d = json.loads(resp.read())
    print("PRED:", d.get("prediction"))
    print("IMG%:", d.get("image_confidence"))
    print("SYM%:", d.get("symptom_confidence"))
    print("FIN%:", d.get("final_confidence"))
    print("NLP:", d.get("best_nlp_match"))
    print("DIS:", d.get("has_dissonance"))
    print("RSN:", d.get("clinical_reasoning"))
    print("VER:", d.get("verdict"))
except Exception as e:
    print("ERR:", e)
