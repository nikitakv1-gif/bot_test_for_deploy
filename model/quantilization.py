from torch.quantization import quantize_dynamic
from ThreeInputModel import ThreeInputModel
import os
import torch

def main():
    base_path = os.path.dirname(__file__)  # Путь до текущего файла model/__init__.py

    path_to_model = os.path.join(base_path, 'presave', 'model.pt')
    path_to_tokenizer = os.path.join(base_path, 'presave')

    model = ThreeInputModel('cointegrated/rubert-tiny2', num_labels=5)
    model.load_state_dict(torch.load(path_to_model, map_location = 'cpu'))

    model_quantized = quantize_dynamic(
        model, {torch.nn.Linear}, dtype=torch.qint8
    )

    torch.save(model_quantized.state_dict(), "model_quantized.pt")

if __name__ == '__main__':
    main()