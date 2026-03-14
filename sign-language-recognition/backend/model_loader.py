from huggingface_hub import hf_hub_download
from tensorflow.keras.models import load_model

class ModelLoader:
    model = None

    @staticmethod
    def load_model():
        if ModelLoader.model is None:
            print("Downloading model from HuggingFace...")
            model_path = hf_hub_download(
                repo_id="dhruv-upmanyu/sign-language-recognition-model",
                filename="model.h5"
            )
            print("Model path:", model_path)
            ModelLoader.model = load_model(model_path)
            print("Model loaded successfully!")
            
        return ModelLoader.model
