from torch.utils.data import DataLoader, Dataset
from transformers import DataCollatorWithPadding




class ReviewsDataset(Dataset):
    def __init__(self, df, tokenizer, max_length=46):
        self.df = df.reset_index(drop=True)
        self.tokenizer = tokenizer
        self.max_length = max_length

    def __len__(self):
        return len(self.df)

    def __getitem__(self, idx):
        item = self.df.loc[idx]

        text = item['text'] if pd.notna(item['text']) else ""
        plus = item['plus'] if pd.notna(item['plus']) else ""
        minus = item['minus'] if pd.notna(item['minus']) else ""

        encoding_text = self.tokenizer(text, max_length=self.max_length, padding='max_length', truncation=True, return_tensors='pt')
        encoding_plus = self.tokenizer(plus, max_length=self.max_length, padding='max_length', truncation=True, return_tensors='pt')
        encoding_minus = self.tokenizer(minus, max_length=self.max_length, padding='max_length', truncation=True, return_tensors='pt')

        return {
            'input_ids_text': encoding_text['input_ids'].squeeze(0),
            'attention_mask_text': encoding_text['attention_mask'].squeeze(0),
            'input_ids_plus': encoding_plus['input_ids'].squeeze(0),
            'attention_mask_plus': encoding_plus['attention_mask'].squeeze(0),
            'input_ids_minus': encoding_minus['input_ids'].squeeze(0),
            'attention_mask_minus': encoding_minus['attention_mask'].squeeze(0),
            'labels': torch.tensor(item['rating'], dtype=torch.long)-1,
            'text': item['text'],
            'plus': item['plus'],
            'minus': item['minus']
        }



