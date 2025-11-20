#!/usr/bin/env python3
"""
Semi-Automated Testing Script
- Automates API requests
- Requires manual evaluation of responses
- Saves results to database
"""

import requests
import json
import time
from db_manager import DatabaseManager

API_KEY = "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"
API_URL = "https://openrouter.ai/api/v1/chat/completions"

def send_request(model: str, prompt: str, system_prompt: str = None):
    """Send request to OpenRouter API"""
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

    try:
        response = requests.post(API_URL, headers=headers, json=data, timeout=120)
        response.raise_for_status()
        result = response.json()
        return result['choices'][0]['message']['content']
    except Exception as e:
        print(f"❌ Error: {e}")
        return None

def manual_evaluation():
    """Prompt user for manual evaluation scores"""
    print("\n" + "="*70)
    print("MANUAL EVALUATION REQUIRED")
    print("="*70)
    print("Rate the response on each criterion (0-100):")

    accuracy = float(input("Accuracy (factual correctness): "))
    coherence = float(input("Coherence (logical flow): "))
    relevance = float(input("Relevance (on-topic): "))
    creativity = float(input("Creativity (novel insights): "))
    response_time = float(input("Response Speed (subjective, 100=instant, 0=very slow): "))

    observations = input("\nObservations/Notes: ")

    return {
        'accuracy': accuracy,
        'coherence': coherence,
        'relevance': relevance,
        'creativity': creativity,
        'response_time': response_time,
        'overall': (accuracy + coherence + relevance + creativity + response_time) / 5,
        'observations': observations
    }

def test_technique(model_name: str, technique_name: str, test_prompts: list, system_prompt: str = None):
    """Test a technique with multiple prompts"""
    print(f"\n{'='*70}")
    print(f"TESTING: {technique_name}")
    print(f"MODEL: {model_name}")
    print(f"NUMBER OF TESTS: {len(test_prompts)}")
    print(f"{'='*70}\n")

    all_scores = []
    db = DatabaseManager()

    for i, prompt in enumerate(test_prompts, 1):
        print(f"\n--- TEST {i}/{len(test_prompts)} ---")
        print(f"Prompt: {prompt[:200]}...")

        # Send request
        response = send_request(model_name, prompt, system_prompt)

        if not response:
            print("❌ Request failed, skipping...")
            continue

        print(f"\n{'='*70}")
        print("RESPONSE:")
        print(f"{'='*70}")
        print(response)
        print(f"{'='*70}")

        # Manual evaluation
        scores = manual_evaluation()
        all_scores.append(scores)

        # Add small delay to avoid rate limiting
        time.sleep(2)

    # Calculate aggregate scores
    if all_scores:
        avg_scores = {
            'accuracy': sum(s['accuracy'] for s in all_scores) / len(all_scores),
            'coherence': sum(s['coherence'] for s in all_scores) / len(all_scores),
            'relevance': sum(s['relevance'] for s in all_scores) / len(all_scores),
            'creativity': sum(s['creativity'] for s in all_scores) / len(all_scores),
            'response_time': sum(s['response_time'] for s in all_scores) / len(all_scores),
        }
        avg_overall = sum(avg_scores.values()) / len(avg_scores)

        print(f"\n{'='*70}")
        print("AGGREGATE RESULTS")
        print(f"{'='*70}")
        print(f"Average Accuracy: {avg_scores['accuracy']:.1f}%")
        print(f"Average Coherence: {avg_scores['coherence']:.1f}%")
        print(f"Average Relevance: {avg_scores['relevance']:.1f}%")
        print(f"Average Creativity: {avg_scores['creativity']:.1f}%")
        print(f"Average Response Time: {avg_scores['response_time']:.1f}%")
        print(f"OVERALL EFFECTIVENESS: {avg_overall:.1f}%")
        print(f"{'='*70}")

        # Save to database
        observations = " | ".join([s['observations'] for s in all_scores if s['observations']])
        db.add_evaluation(
            model_name=model_name,
            technique_name=technique_name,
            accuracy=avg_scores['accuracy'],
            coherence=avg_scores['coherence'],
            relevance=avg_scores['relevance'],
            creativity=avg_scores['creativity'],
            response_time=avg_scores['response_time'],
            observations=observations
        )

        # Determine status
        success_count = sum(1 for s in all_scores if s['overall'] >= 70)
        success_rate = (success_count / len(all_scores)) * 100

        if avg_overall >= 75 and success_rate >= 70:
            status = "validated"
            print(f"\n✅ TECHNIQUE VALIDATED (Overall: {avg_overall:.1f}%, Success Rate: {success_rate:.1f}%)")
        elif avg_overall < 60 or success_rate < 50:
            status = "rejected"
            print(f"\n❌ TECHNIQUE REJECTED (Overall: {avg_overall:.1f}%, Success Rate: {success_rate:.1f}%)")
        else:
            status = "testing"
            print(f"\n⚠️ TECHNIQUE NEEDS MORE TESTING (Overall: {avg_overall:.1f}%, Success Rate: {success_rate:.1f}%)")

        db.update_evaluation_status(model_name, technique_name, status, success_rate)

        return avg_overall, success_rate, status
    else:
        print("\n❌ No successful tests completed")
        return None, None, "rejected"


if __name__ == "__main__":
    print("="*70)
    print("SEMI-AUTOMATED TECHNIQUE TESTING")
    print("="*70)

    # Example usage
    print("\nThis script will:")
    print("1. Send prompts to the API automatically")
    print("2. Display responses")
    print("3. Ask YOU to manually evaluate each response")
    print("4. Save results to database")
    print("\nThis ensures human oversight while automating the tedious parts.")

    input("\nPress Enter to continue or Ctrl+C to exit...")
