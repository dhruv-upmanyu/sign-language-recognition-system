from huggingface_hub import hf_hub_download
from tensorflow.keras.models import load_model

model = None

def load_sign_language_model():
    global model

    if model is None:
        model_path = hf_hub_download(
            repo_id="dhruv-upmanyu/sign-language-recognition-model",
            filename="model.h5"
        )

        model = load_model(model_path)
        print("Model loaded successfully!")

    return model
