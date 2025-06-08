import torch
import torch.nn.functional as F
import plotly.express as px
import pandas as pd

def get_emotion_logits_from_full_text(model_sent, emotion_tokenizer, text, plus_text=None, minus_text=None, max_length=512, device = None):
    total_logits = []

    if device is None:
        device = torch.device('cpu')

    if text is not None:
        inputs = emotion_tokenizer(text, return_tensors='pt', truncation=True, max_length=max_length).to(device)
        logits = model_sent(**inputs).logits
        total_logits.append(logits)

    if plus_text is not None:
        inputs = emotion_tokenizer(plus_text, return_tensors='pt', truncation=True, max_length=max_length).to(device)
        logits = model_sent(**inputs).logits
        total_logits.append(logits)

    if minus_text is not None:
        inputs = emotion_tokenizer(minus_text, return_tensors='pt', truncation=True, max_length=max_length).to(device)
        logits = model_sent(**inputs).logits
        total_logits.append(logits)

    avg_logits = torch.stack(total_logits).mean(dim=0)

    return avg_logits

def predict(model, tokenizer, emotion_model, emotion_tokenizer, excel_work = None, texts=None, plus_texts=None, minus_texts=None, max_length=46, device='cpu'):
    device = torch.device(device)
    model.eval()
    with torch.no_grad():
        if texts is not None:
            inputs_text = tokenizer(texts, padding='max_length', truncation=True, max_length=max_length, return_tensors='pt').to(device)
        inputs_plus = None
        if plus_texts is not None:
            inputs_plus = tokenizer(plus_texts, padding='max_length', truncation=True, max_length=max_length, return_tensors='pt').to(device)

        inputs_minus = None
        if minus_texts is not None:
            inputs_minus = tokenizer(minus_texts, padding='max_length', truncation=True, max_length=max_length, return_tensors='pt').to(device)

        logits = model(
            input_ids_text=inputs_text.input_ids if inputs_text is not None else None,
            attention_mask_text=inputs_text.attention_mask if inputs_text is not None else None,
            input_ids_plus=inputs_plus.input_ids if inputs_plus is not None else None,
            attention_mask_plus=inputs_plus.attention_mask if inputs_plus is not None else None,
            input_ids_minus=inputs_minus.input_ids if inputs_minus is not None else None,
            attention_mask_minus=inputs_minus.attention_mask if inputs_minus is not None else None,
            device = device
        )

        probs = F.softmax(logits, dim=1)
        preds = torch.argmax(probs, dim=1)+1

        emotion_logits = []

        if emotion_model and emotion_tokenizer:
            for i, text in enumerate(texts):
              plus_text = plus_texts[i] if plus_texts is not None else None
              minus_text = minus_texts[i] if minus_texts is not None else None
              logits = get_emotion_logits_from_full_text(emotion_model, emotion_tokenizer, text, plus_text, minus_text, max_length=512, device = device)
              probs_emo = F.softmax(logits[0], dim=0).cpu().tolist()
              emotion_logits.append(probs_emo)
        else:
            emotion_logits = None

    result = {
        "preds": preds.cpu().tolist(),
        "probs": probs.cpu().tolist(),
        "emotion_logits": emotion_logits}


    star = result['preds']
    emo = result['emotion_logits']
    NPS = []
    emo_h_l = []
    prom = 0
    neu = 0
    dis = 0
    for i in range(len(star)):
        star_h = star[i]
        emo_h = emo[i]
        emo_h_n = emo_h[1]
        emo_h_p = emo_h[2]
        emo_h_nega = emo_h[0]
        print(star_h, emo_h_nega, emo_h_n,emo_h_p)
        emo_avg = (emo_h_p - emo_h_nega + 1/2*emo_h_n)
        nps_score = round((star[i]-1)/4 * emo_avg,1)
        if nps_score < 0:
            nps_score = 0
        NPS.append(nps_score*10)
        if nps_score > 0.6:
            prom += 1
        elif nps_score < 0.2:
            dis += 1
        else:
            neu += 1
    if len(NPS) == 1:
        return str(abs(NPS[0]))
    graph = px.histogram(
    x=NPS,
    template='plotly_white',
    color_discrete_sequence=['#8D230F'],
    labels={
        'x': 'Оценка NPS',  # Переименовываем ось X
        'y': 'Кол-во оценок'      # Переименовываем ось Y
        }
    )
    NPS_num = prom/(prom+dis+neu)*100 - dis/(prom+dis+neu)*100

    user_df = pd.DataFrame({"Общий отзыв": texts,
                              "Плюсы": plus_texts,
                              "Минусы": minus_texts,
                              "Звезды": result["preds"],
                              "NPS": NPS})
    
    f = excel_work.user_data(user_df)

    return NPS_num, graph, f