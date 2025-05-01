# sentiment_model.py

import pandas as pd
from sklearn.model_selection import train_test_split
from datasets import Dataset
from transformers import AutoTokenizer, AutoModelForSequenceClassification, TrainingArguments, Trainer
from transformers import DataCollatorWithPadding
import torch

# 1. Load your combined DataFrame
df = pd.read_csv("combined_review_data.csv")  # you should save `df_combined` from your XML logic

# 2. Clean and map polarity to numeric labels
label_map = {"positive": 2, "neutral": 1, "negative": 0}
df = df[df["polarity"].isin(label_map)]  # Filter invalid
df["label"] = df["polarity"].map(label_map)
df = df[["text", "label"]].dropna()

# 3. Split into train/test
train_texts, val_texts = train_test_split(df, test_size=0.2, random_state=42)

# 4. Convert to HuggingFace Dataset
train_ds = Dataset.from_pandas(train_texts)
val_ds = Dataset.from_pandas(val_texts)

# 5. Load tokenizer & model
model_name = "distilbert-base-uncased"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForSequenceClassification.from_pretrained(model_name, num_labels=3)

# 6. Tokenize datasets
def tokenize_function(example):
    return tokenizer(example["text"], truncation=True)

train_ds = train_ds.map(tokenize_function, batched=True)
val_ds = val_ds.map(tokenize_function, batched=True)

# 7. Trainer setup
args = TrainingArguments(
    output_dir="./results",
    evaluation_strategy="epoch",
    per_device_train_batch_size=16,
    per_device_eval_batch_size=16,
    num_train_epochs=3,
    weight_decay=0.01,
    logging_dir="./logs",
)

trainer = Trainer(
    model=model,
    args=args,
    train_dataset=train_ds,
    eval_dataset=val_ds,
    tokenizer=tokenizer,
    data_collator=DataCollatorWithPadding(tokenizer=tokenizer),
)

# 8. Train the model
trainer.train()

# 9. Save the model
trainer.save_model("./sentiment_model")

print("✅ Model training completed and saved.")
