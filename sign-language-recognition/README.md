# Sign Language Recognition System

## Demo
Live demo modes: Image Upload, Video Upload, Live Camera Detection for 5 signs: Coca-Cola, Happy, Sleep, Thank You, Hello.

## Local Setup (Python 3.12)

1. Ensure Python 3.12 is installed.

2. Place your trained `model.h5` in `model/`.

3. Backend:
```
cd backend
python -m venv venv
venv\\Scripts\\activate  # On Windows
# source venv/bin/activate  # On macOS/Linux
pip install -r requirements.txt
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

4. Frontend: Open `frontend/index.html` in browser (points to http://localhost:8000).
Note: backend/runtime.txt specifies Python 3.12.6 for Vercel deployment.

## Usage
- Backend runs on http://localhost:8000
- Test endpoint: `curl -X POST -F 'file=@image.jpg' http://localhost:8000/predict-image`
- Open index.html for UI.

## Deployment (Vercel)
- Backend: Deploy backend/ as Python API
- Frontend: Deploy frontend/ as static

## Tech Stack
- Backend: FastAPI + TensorFlow/Keras + OpenCV
- Frontend: HTML/CSS/JS (vanilla)

