import cv2
import numpy as np
from PIL import Image
from tensorflow.keras.preprocessing.image import img_to_array #type:ignore
import base64
from io import BytesIO

# Specific 5 classes from model
CLASS_NAMES = ['Coca-Cola', 'Happy', 'Sleep', 'Thank You', 'Hello']

class Predictor:
    def __init__(self, model):
        self.model = model
        self.input_shape = model.input_shape[1:3]  # (height, width) assuming (None, h, w, 3)
    
    def preprocess_image(self, image):
        """Preprocess image: resize, normalize to [0,1]"""
        if isinstance(image, str):  # base64
            image = self.base64_to_image(image)
        # Convert to RGB if needed
        if len(image.shape) == 3 and image.shape[2] == 4:
            image = cv2.cvtColor(image, cv2.COLOR_BGRA2RGB)
        elif len(image.shape) == 3 and image.shape[2] == 1:
            image = cv2.cvtColor(image, cv2.COLOR_GRAY2RGB)
        # Resize
        h, w = self.input_shape
        image = cv2.resize(image, (w, h))
        # Normalize [0,255] -> [0,1]
        image = image.astype('float32') / 255.0
        # Add batch dim
        image = np.expand_dims(image, axis=0)
        return image
    
    def predict(self, image):
        processed = self.preprocess_image(image)
        predictions = self.model.predict(processed, verbose=0)
        class_idx = np.argmax(predictions[0])
        confidence = float(predictions[0][class_idx])
        label = CLASS_NAMES[class_idx]
        return {'label': label, 'confidence': confidence, 'class_idx': int(class_idx)}
    
    def base64_to_image(self, base64_str):
        header, data = base64_str.split(',')
        img_data = base64.b64decode(data)
        img = Image.open(BytesIO(img_data))
        img = np.array(img)
        img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
        return img
    
    def extract_frames(self, video_path, max_frames=30):
        """Extract frames from video"""
        cap = cv2.VideoCapture(video_path)
        frames = []
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        step = max(1, total_frames // max_frames)
        frame_idx = 0
        while frame_idx < total_frames:
            cap.set(cv2.CAP_PROP_POS_FRAMES, frame_idx)
            ret, frame = cap.read()
            if ret:
                frames.append(frame)
            frame_idx += step
        cap.release()
        # Predict on all, average confidences or take majority
        preds = [self.predict(frame)['confidence'] * self.predict(frame)['class_idx'] for frame in frames]
        avg_idx = int(np.mean(preds))
        confidence = np.mean([self.predict(frame)['confidence'] for frame in frames])
        label = CLASS_NAMES[avg_idx % len(CLASS_NAMES)]  # Safeguard
        return {'label': label, 'confidence': float(confidence), 'class_idx': avg_idx}

