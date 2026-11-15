from transformers import AutoTokenizer, AutoModelForSequenceClassification

print("Downloading FinBERT...")
try:
    tokenizer = AutoTokenizer.from_pretrained("ProsusAI/finbert")
    model = AutoModelForSequenceClassification.from_pretrained("ProsusAI/finbert")
    print("Success!")
except Exception as e:
    print(f"Failed: {e}")
