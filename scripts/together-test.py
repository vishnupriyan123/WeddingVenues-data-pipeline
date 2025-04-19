from together import Together

api_key = "35cbdd4541bb056a890a759b831267bf20ad0fb77f61486f86d0f8932b484b2c"
model = "mistralai/Mistral-7B-Instruct-v0.1"  # ✅ Serverless model

client = Together(api_key=api_key)

messages = [
    {"role": "system", "content": "You are a helpful assistant."},
    {"role": "user", "content": "What is the capital of France?"}
]

try:
    response = client.chat.completions.create(
        model=model,
        messages=messages
    )
    print("✅ SUCCESS:")
    print(response.choices[0].message.content)

except Exception as e:
    print("❌ ERROR:", e)