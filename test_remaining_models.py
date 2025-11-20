#!/usr/bin/env python3
"""
Test only available models from the availability check
"""

import time
from automated_researcher import PromptResearcher
from db_manager import DatabaseManager

# Only available models (excluding grok which is already done)
MODELS_TO_TEST = [
    "qwen/qwen3-235b-a22b-2507",
    "deepseek/deepseek-chat-v3.1",
    "mistralai/mistral-nemo",
    "mistralai/mistral-medium-3.1",
    "deepcogito/cogito-v2-preview-llama-405b",
    "openai/gpt-4o-mini",
    "amazon/nova-pro-v1",
    "anthropic/claude-3-haiku"
]

def main():
    print("="*70)
    print("CONTINUING RESEARCH ON AVAILABLE MODELS")
    print("="*70)
    print(f"Already completed: x-ai/grok-4.1-fast")
    print(f"Testing now: {len(MODELS_TO_TEST)} remaining models")
    print("="*70)

    researcher = PromptResearcher()
    db = DatabaseManager()

    # Get techniques
    techniques = db.get_all_techniques()
    print(f"\nTesting {len(techniques)} techniques per model")
    print(f"Total tests: ~{len(techniques) * len(MODELS_TO_TEST) * 2} API calls\n")

    all_results = []

    for model_idx, model in enumerate(MODELS_TO_TEST, 1):
        print(f"\n{'#'*70}")
        print(f"# MODEL {model_idx+1}/10: {model}")
        print(f"# (Testing {model_idx}/{len(MODELS_TO_TEST)} of remaining models)")
        print(f"{'#'*70}\n")

        model_results = {
            'model': model,
            'validated': 0,
            'rejected': 0,
            'inconclusive': 0,
            'techniques': []
        }

        for tech_idx, tech in enumerate(techniques, 1):
            print(f"\n[{tech_idx}/{len(techniques)}] {tech['technique_name']}")

            try:
                result = researcher.test_technique_on_model(
                    model_name=model,
                    technique_name=tech['technique_name'],
                    technique_desc=tech['description'],
                    technique_category=tech['category'],
                    num_tests=2
                )

                if result:
                    model_results['techniques'].append({
                        'name': tech['technique_name'],
                        'status': result['status'],
                        'overall': result['overall']
                    })

                    if result['status'] == 'validated':
                        model_results['validated'] += 1
                    elif result['status'] == 'rejected':
                        model_results['rejected'] += 1
                    else:
                        model_results['inconclusive'] += 1

                time.sleep(1)

            except Exception as e:
                print(f"  ❌ Error: {e}")
                continue

        # Model summary
        print(f"\n{'='*70}")
        print(f"SUMMARY: {model}")
        print(f"{'='*70}")
        print(f"✅ Validated: {model_results['validated']}")
        print(f"❌ Rejected: {model_results['rejected']}")
        print(f"⚠️ Inconclusive: {model_results['inconclusive']}")
        print(f"{'='*70}\n")

        all_results.append(model_results)

        # Save checkpoint
        with open(f"/home/user/AIREX/checkpoint_model_{model_idx+1}.txt", "w") as f:
            f.write(f"Completed: {model}\n")
            f.write(f"Validated: {model_results['validated']}\n")
            f.write(f"Rejected: {model_results['rejected']}\n")
            f.write(f"Inconclusive: {model_results['inconclusive']}\n")

        time.sleep(3)

    # Final report
    print("\n\n" + "="*70)
    print("ALL MODELS COMPLETE!")
    print("="*70)

    total_v = sum(r['validated'] for r in all_results)
    total_r = sum(r['rejected'] for r in all_results)
    total_i = sum(r['inconclusive'] for r in all_results)

    print(f"\nGlobal Results (8 new models):")
    print(f"  ✅ Total Validated: {total_v}")
    print(f"  ❌ Total Rejected: {total_r}")
    print(f"  ⚠️ Total Inconclusive: {total_i}")

    print(f"\nBy Model:")
    for r in all_results:
        print(f"  {r['model']}: {r['validated']}✅ {r['rejected']}❌ {r['inconclusive']}⚠️")

    print("\n" + "="*70)
    print("Including Grok (already tested): 9 total models")
    print("="*70)

    db.print_statistics()

if __name__ == "__main__":
    main()
