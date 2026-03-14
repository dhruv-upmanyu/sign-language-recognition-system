import os
from tensorflow.keras.models import load_model

class ModelLoader:
    def __init__(self, model_path='../model/model.h5'):
        self.model_path = model_path
        self.model = self.load_model()
    
    def load_model(self):
        if not os.path.exists(self.model_path):
            raise FileNotFoundError(f"Model file not found at {self.model_path}. Please place your trained model.h5 in the model/ directory.")
        try:
            model = load_model(self.model_path)
            print("Model loaded successfully!")
            return model
        except Exception as e:
            raise RuntimeError(f"Error loading model: {str(e)}")

