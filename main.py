from model import model
from app import create_app

model, tokenizer, model_sent, emotion_tokenizer = model()
app = create_app()

app.config["model"] = model
app.config['tokenizer'] = tokenizer
app.config["model_sent"] = model_sent
app.config['emotion_tokenizer'] = emotion_tokenizer

application = app

if __name__ == "__main__":
    app.run(debug = True)
    # port = int(os.environ,get("PORT", 4000))
    # app.run(host = "0.0.0.0", port = port)
