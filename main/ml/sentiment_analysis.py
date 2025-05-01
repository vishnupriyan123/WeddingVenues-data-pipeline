from transformers import pipeline

classifier = pipeline("text-classification", model="./arima_model", tokenizer="distilbert-base-uncased")

preds = classifier(["The venue was amazing!", "Nothing went as planned..."])
print(preds)
