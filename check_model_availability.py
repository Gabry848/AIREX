#!/usr/bin/env python3
"""
Check which models from MODELS.md are available on OpenRouter
"""

import requests
import time

API_KEY = "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"
API_URL = "https://openrouter.ai/api/v1/chat/completions"

MODELS = [
    "x-ai/grok-4.1-fast",
    "openai/gpt-5-mini",
    "qwen/qwen3-235b-a22b-2507",
    "deepseek/deepseek-chat-v3.1",
    "mistralai/mistral-nemo",
    "mistralai/mistral-medium-3.1",
    "deepcogito/cogito-v2-preview-llama-405b",
    "openai/gpt-4o-mini",
    "amazon/nova-pro-v1",
    "anthropic/claude-3-haiku"
]

def test_model_availability(model_name):
    """Test if a model is available by sending a minimal request"""
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }

    data = {
        "model": model_name,
        "messages": [{"role": "user", "content": "test"}],
        "max_tokens": 10
    }

    try:
        response = requests.post(API_URL, headers=headers, json=data, timeout=30)

        if response.status_code == 200:
            return True, "Available"
        elif response.status_code == 404:
            return False, "Model not found"
        elif response.status_code == 401:
            return False, "Unauthorized (API key issue)"
        elif response.status_code == 503:
            return False, "Service unavailable"
        else:
            return False, f"Error {response.status_code}"
    except Exception as e:
        return False, f"Exception: {str(e)[:50]}"

print("="*70)
print("CHECKING MODEL AVAILABILITY ON OPENROUTER")
print("="*70)

available_models = []
unavailable_models = []

for i, model in enumerate(MODELS, 1):
    print(f"\n[{i}/{len(MODELS)}] Testing: {model}")
    is_available, status = test_model_availability(model)

    if is_available:
        print(f"  ✅ AVAILABLE")
        available_models.append(model)
    else:
        print(f"  ❌ UNAVAILABLE - {status}")
        unavailable_models.append((model, status))

    time.sleep(1)  # Rate limiting

print("\n" + "="*70)
print("SUMMARY")
print("="*70)

print(f"\n✅ AVAILABLE MODELS ({len(available_models)}):")
for model in available_models:
    print(f"  - {model}")

print(f"\n❌ UNAVAILABLE MODELS ({len(unavailable_models)}):")
for model, reason in unavailable_models:
    print(f"  - {model}: {reason}")

print("\n" + "="*70)

# Save results
with open("/home/user/AIREX/available_models.txt", "w") as f:
    f.write("# Available Models on OpenRouter\n\n")
    for model in available_models:
        f.write(f"{model}\n")

print(f"\nAvailable models saved to: available_models.txt")
print(f"Ready to test {len(available_models)} models")
