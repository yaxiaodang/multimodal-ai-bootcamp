from transformers import pipeline

MODEL_ID = "distilbert/distilbert-base-uncased-finetuned-sst-2-english"
REVISION = "714eb0fa89d2f80546fda750413ed43d93601a13"
TEXT = "The documentation is clear and easy to follow."

classifier = pipeline(
    task="text-classification",
    model=MODEL_ID,
    revision=REVISION,
    device=-1,
)

print("model:", MODEL_ID)
print("revision:", REVISION)
print("input:", TEXT)
print("output:", classifier(TEXT))