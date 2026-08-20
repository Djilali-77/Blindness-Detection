import os
import cv2
import torch
import torch.nn as nn
import numpy as np
import torchvision.models as models
import torchvision.transforms as transforms
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pytorch_grad_cam import GradCAM
from pytorch_grad_cam.utils.model_targets import ClassifierOutputTarget
from pytorch_grad_cam.utils.image import show_cam_on_image

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

UPLOAD_DIR = "uploaded_images"
os.makedirs(UPLOAD_DIR, exist_ok=True)
app.mount("/images", StaticFiles(directory=UPLOAD_DIR), name="images")

ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".gif", ".webp"}

# ==========================================
# 1. Model Setup
# ==========================================
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

model = models.resnet18(weights=None)
num_features = model.fc.in_features
model.fc = nn.Linear(num_features, 5)

state_dict = torch.load('model_weights.pth', map_location=device, weights_only=True)
model.load_state_dict(state_dict)

model = model.to(device)
model.eval()

transform = transforms.Compose([
    transforms.ToTensor(),
])

# ==========================================
# 2. Image Preprocessing 
# ==========================================
def crop_and_resize(image_path, size=224):
    img = cv2.imread(image_path)
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
    _, thresh = cv2.threshold(gray, 7, 255, cv2.THRESH_BINARY)
    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    if contours:
        c = max(contours, key=cv2.contourArea)
        x, y, w, h = cv2.boundingRect(c)
        img = img[y:y+h, x:x+w]
    return cv2.resize(img, (size, size))

# ==========================================
# 3. API Endpoint
# ==========================================
@app.post("/upload-image/")
async def upload_image(file: UploadFile = File(...)):
    file_ext = os.path.splitext(file.filename)[1].lower()
    if file_ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(status_code=400, detail="Unsupported file type.")
    
    file_path = os.path.join(UPLOAD_DIR, file.filename)
    
    try:
        with open(file_path, "wb") as f:
            while content := await file.read(1024 * 1024):
                f.write(content)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save file: {str(e)}")
    finally:
        await file.close()
        
    try:
        processed_img = crop_and_resize(file_path)
        input_tensor = transform(processed_img).unsqueeze(0).to(device)
        
        with torch.no_grad():
            output = model(input_tensor)
            predicted_class = torch.argmax(output, dim=1).item()
            
        target_layers = [model.layer4[-1]]
        cam = GradCAM(model=model, target_layers=target_layers)
        targets = [ClassifierOutputTarget(predicted_class)]
        
        grayscale_cam = cam(input_tensor=input_tensor, targets=targets)[0, :]
        
        rgb_img = processed_img.astype(np.float32) / 255.0
        cam_image = show_cam_on_image(rgb_img, grayscale_cam, use_rgb=True)
        
        cam_filename = f"cam_{file.filename}"
        cam_output_path = os.path.join(UPLOAD_DIR, cam_filename)
        cv2.imwrite(cam_output_path, cv2.cvtColor(cam_image, cv2.COLOR_RGB2BGR))
        
        return {
            "message": "Image analyzed successfully!",
            "original_filename": file.filename,
            "diagnosis_level": predicted_class,
            "details": f"Patient has Diabetic Retinopathy level {predicted_class}",
            "grad_cam_image": cam_filename
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI processing failed: {str(e)}")