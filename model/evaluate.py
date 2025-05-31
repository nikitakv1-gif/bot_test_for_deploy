def evaluate_model(model, dataloader):
        model.eval()
        all_preds = []
        all_labels = []

        with torch.no_grad():
            for batch in dataloader:
                input_ids_text = batch['input_ids_text'].to(device)
                attention_mask_text = batch['attention_mask_text'].to(device)
                input_ids_plus = batch['input_ids_plus'].to(device)
                attention_mask_plus = batch['attention_mask_plus'].to(device)
                input_ids_minus = batch['input_ids_minus'].to(device)
                attention_mask_minus = batch['attention_mask_minus'].to(device)
                labels = batch['labels'].to(device)

                outputs = model(
                    input_ids_text, attention_mask_text,
                    input_ids_plus, attention_mask_plus,
                    input_ids_minus, attention_mask_minus
                )

                preds = outputs.argmax(dim=1).cpu().numpy()
                true_labels = labels.cpu().numpy()
                all_preds.extend(preds)
                all_labels.extend(true_labels)

        report = classification_report(all_labels, all_preds, digits=4)
        print("Evaluation on validation set:\n", report)