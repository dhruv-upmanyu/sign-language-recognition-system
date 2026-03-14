from fastapi import FastAPI, File, UploadFile, HTTPException, Body
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import shutil
import os
import tempfile
import numpy as np
import cv2
from model_loader import ModelLoader
from predictor import Predictor

app = FastAPI(title="Sign Language Recognition API")

# CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load model
try:
    model_loader = ModelLoader()
    model = model_loader.model
    predictor = Predictor(model)
except Exception as e:
    print(f"Model load error: {e}")
    model = None
    predictor = None

@app.get("/")
async def root():
    return {"message": "Sign Language Recognition API. Use /predict-image, /predict-video, /predict-frame"}

@app.post("/predict-image")
async def predict_image(file: UploadFile = File(...)):
    if not predictor:
        raise HTTPException(status_code=500, detail="Model not loaded")
    if not file.content_type.startswith('image/'):
        raise HTTPException(status_code=400, detail="Invalid image")
    
    contents = await file.read()
    nparr = np.frombuffer(contents, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    
    result = predictor.predict(img)
    return JSONResponse(content=result)

@app.post("/predict-video")
async def predict_video(file: UploadFile = File(...)):
    if not predictor:
        raise HTTPException(status_code=500, detail="Model not loaded")
    if not file.content_type.startswith('video/'):
        raise HTTPException(status_code=400, detail="Invalid video")
    
    with tempfile.NamedTemporaryFile(delete=False, suffix='.mp4') as tmp:
        shutil.copyfileobj(file.file, tmp)
        tmp_path = tmp.name
    
    try:
        result = predictor.extract_frames(tmp_path)
    finally:
        os.unlink(tmp_path)
    
    return JSONResponse(content=result)

@app.post("/predict-frame")
async def predict_frame(request: dict = Body(...)):
    if not predictor:
        raise HTTPException(status_code=500, detail="Model not loaded")
    base64_image = request.get("base64_image", "")
    if not base64_image.startswith('data:image'):
        raise HTTPException(status_code=400, detail="Invalid base64 image")
    
    result = predictor.predict(base64_image)
    return JSONResponse(content=result)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

