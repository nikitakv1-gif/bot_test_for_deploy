from model.ThreeInputModel import ThreeInputModel
from model.dataset import ReviewsDataset
import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import os
from memory_profiler import memory_usage
from huggingface_hub import hf_hub_download
import torch


base_path = os.path.dirname(__file__)  # Путь до текущего файла model/__init__.py

path_to_model = os.path.join(base_path, 'presave', 'model.pt')
path_to_tokenizer = os.path.join(base_path, 'presave')
def model():
    model = ThreeInputModel('cointegrated/rubert-tiny2', num_labels=5)
    if os.path.exists(path_to_model):
        model.load_state_dict(torch.load(path_to_model, map_location = 'cpu'))
    else:
        model_path = hf_hub_download(
        repo_id="nizenkiy/three-input-pt-model",
        filename="model.pt",
    )
        model.load_state_dict(torch.load(model_path, map_location='cpu'))
    model.eval()
    tokenizer = AutoTokenizer.from_pretrained(path_to_tokenizer)
    emotion_model = "cointegrated/rubert-tiny-sentiment-balanced"
    emotion_tokenizer = AutoTokenizer.from_pretrained(emotion_model)
    model_sent = AutoModelForSequenceClassification.from_pretrained(emotion_model)
    model_sent.eval()
    return model, tokenizer, model_sent, emotion_tokenizer
