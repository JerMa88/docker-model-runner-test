import os, time, requests

# Compose‑injected:
#   LLM_URL   => base endpoint, e.g. http://model-runner.docker.internal/engines/llama.cpp/v1
#   LLM_MODEL => model identifier,    e.g. ai/smollm2
LLM_URL   = os.environ["LLM_URL"].rstrip("/")
LLM_MODEL = os.environ["LLM_MODEL"]

# wait for the model runner to be ready
for _ in range(15):
    try:
        if requests.get(f"{LLM_URL}/models").ok:
            break
    except requests.exceptions.RequestException:
        time.sleep(1)
else:
    raise RuntimeError("Model runner did not become ready in time")

# build an OpenAI‑compatible payload
payload = {
    "model": LLM_MODEL,
    "messages": [
        {"role": "system", "content": "You are bench testing."},
        {"role": "user",   "content": "Hello from bench!"}
    ]
}

# call the chat/completions endpoint
resp = requests.post(f"{LLM_URL}/chat/completions", json=payload)
resp.raise_for_status()

print("Model response:")
print(resp.json())
