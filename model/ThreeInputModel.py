import pandas as pd
import numpy as np
# from google.colab import drive
from transformers import AutoTokenizer
import os
from transformers import AutoModel
import torch
import torch.nn as nn
from torch.utils.data import Dataset
from torch.utils.data import DataLoader


class ThreeInputModel(nn.Module):
    def __init__(self, pretrained_model_name, num_labels):
        super().__init__()
        self.bert = AutoModel.from_pretrained(pretrained_model_name)
        hidden_size = self.bert.config.hidden_size

        self.classifier = nn.Linear(hidden_size * 3, num_labels)

    def forward(
        self,
        input_ids_text=None, attention_mask_text=None,
        input_ids_plus=None, attention_mask_plus=None,
        input_ids_minus=None, attention_mask_minus=None,
        device = None
    ):
        if device is None:
            device = torch.device('cpu')
        if input_ids_text is not None:
            batch_size, max_length = input_ids_text.shape
        elif input_ids_plus is not None:
            batch_size, max_length = input_ids_plus.shape
        elif input_ids_minus is not None:
            batch_size, max_length = input_ids_minus.shape
        else:
            # Если все None, тогда установить разумные значения или кинуть ошибку
            batch_size, max_length = 1, 128
        if input_ids_text is None:
            input_ids_text = torch.zeros((batch_size, max_length), dtype=torch.long, device=device)
            attention_mask_text = torch.zeros((batch_size, max_length), dtype=torch.long, device=device)

        if input_ids_plus is None:
            input_ids_plus = torch.zeros((batch_size, max_length), dtype=torch.long, device=device)
            attention_mask_plus = torch.zeros((batch_size, max_length), dtype=torch.long, device=device)

        if input_ids_minus is None:
            input_ids_minus = torch.zeros((batch_size, max_length), dtype=torch.long, device=device)
            attention_mask_minus = torch.zeros((batch_size, max_length), dtype=torch.long, device=device)

        outputs_text = self.bert(input_ids=input_ids_text, attention_mask=attention_mask_text)
        outputs_plus = self.bert(input_ids=input_ids_plus, attention_mask=attention_mask_plus)
        outputs_minus = self.bert(input_ids=input_ids_minus, attention_mask=attention_mask_minus)

        combined = torch.cat([
            outputs_text.last_hidden_state[:,0,:],
            outputs_plus.last_hidden_state[:,0,:],
            outputs_minus.last_hidden_state[:,0,:]
        ], dim=1)

        logits = self.classifier(combined)

        return logits
