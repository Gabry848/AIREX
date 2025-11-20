#!/usr/bin/env python3
"""
Manual prompt testing script for OpenRouter API
Usage: python test_prompt.py
"""

import requests
import json
import sys

API_KEY = "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"
API_URL = "https://openrouter.ai/api/v1/chat/completions"

def test_prompt(model: str, prompt: str, system_prompt: str = None):
    """Send a single prompt to the model and return response"""

    messages = []
    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})
    messages.append({"role": "user", "content": prompt})

    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }

    data = {
        "model": model,
        "messages": messages
    }

    print(f"\n{'='*70}")
    print(f"MODEL: {model}")
    print(f"{'='*70}")
    if system_prompt:
        print(f"SYSTEM: {system_prompt[:100]}...")
    print(f"PROMPT: {prompt[:200]}...")
    print(f"{'='*70}\n")
    print("Sending request...")

    try:
        response = requests.post(API_URL, headers=headers, json=data, timeout=60)
        response.raise_for_status()

        result = response.json()
        content = result['choices'][0]['message']['content']

        print(f"\n{'='*70}")
        print("RESPONSE:")
        print(f"{'='*70}")
        print(content)
        print(f"\n{'='*70}")

        # Print usage stats if available
        if 'usage' in result:
            usage = result['usage']
            print(f"\nTokens - Prompt: {usage.get('prompt_tokens', 'N/A')}, "
                  f"Completion: {usage.get('completion_tokens', 'N/A')}, "
                  f"Total: {usage.get('total_tokens', 'N/A')}")

        return content

    except requests.exceptions.RequestException as e:
        print(f"\n❌ ERROR: {e}")
        if hasattr(e, 'response') and e.response is not None:
            print(f"Response: {e.response.text}")
        return None

if __name__ == "__main__":
    # Interactive mode
    print("="*70)
    print("MANUAL PROMPT TESTING TOOL")
    print("="*70)

    print("\nAvailable models:")
    print("1. x-ai/grok-4.1-fast")
    print("2. openai/gpt-5-mini")
    print("3. Custom model name")

    choice = input("\nSelect model (1-3): ").strip()

    if choice == "1":
        model = "x-ai/grok-4.1-fast"
    elif choice == "2":
        model = "openai/gpt-5-mini"
    elif choice == "3":
        model = input("Enter model name: ").strip()
    else:
        print("Invalid choice")
        sys.exit(1)

    system_prompt = input("\nSystem prompt (press Enter to skip): ").strip()
    if not system_prompt:
        system_prompt = None

    print("\nEnter your prompt (press Ctrl+D or Ctrl+Z when done):")
    prompt_lines = []
    try:
        while True:
            line = input()
            prompt_lines.append(line)
    except EOFError:
        pass

    prompt = "\n".join(prompt_lines)

    if not prompt:
        print("No prompt provided")
        sys.exit(1)

    test_prompt(model, prompt, system_prompt)
