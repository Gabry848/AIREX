#!/usr/bin/env python3
"""
Quick Research - 2 tests per technique for faster completion
"""

import time
from automated_researcher import PromptResearcher
from db_manager import DatabaseManager

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

def main():
    print("="*70)
    print("QUICK RESEARCH MODE - 2 tests per technique")
    print("="*70)

    researcher = PromptResearcher()
    db = DatabaseManager()

    # Get techniques
    techniques = db.get_all_techniques()
    print(f"Testing {len(techniques)} techniques across {len(MODELS)} models")
    print(f"Total tests: ~{len(techniques) * len(MODELS) * 2}")
    print("="*70)

    all_results = []

    for model_idx, model in enumerate(MODELS, 1):
        print(f"\n{'#'*70}")
        print(f"# MODEL {model_idx}/{len(MODELS)}: {model}")
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
                    num_tests=2  # Quick mode
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

                time.sleep(1)  # Rate limiting

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
        with open(f"/home/user/AIREX/checkpoint_{model_idx}.txt", "w") as f:
            f.write(f"Completed: {model}\n")
            f.write(f"Validated: {model_results['validated']}\n")

        time.sleep(3)  # Pause between models

    # Final report
    print("\n\n" + "="*70)
    print("RESEARCH COMPLETE!")
    print("="*70)

    total_v = sum(r['validated'] for r in all_results)
    total_r = sum(r['rejected'] for r in all_results)
    total_i = sum(r['inconclusive'] for r in all_results)

    print(f"\nGlobal Results:")
    print(f"  ✅ Total Validated: {total_v}")
    print(f"  ❌ Total Rejected: {total_r}")
    print(f"  ⚠️ Total Inconclusive: {total_i}")

    print(f"\nBy Model:")
    for r in all_results:
        print(f"  {r['model']}: {r['validated']}✅ {r['rejected']}❌ {r['inconclusive']}⚠️")

    # Save summary
    with open("/home/user/AIREX/research_summary.txt", "w") as f:
        f.write("PROMPT ENGINEERING RESEARCH SUMMARY\n")
        f.write("="*70 + "\n\n")
        for r in all_results:
            f.write(f"{r['model']}\n")
            f.write(f"  Validated: {r['validated']}\n")
            f.write(f"  Rejected: {r['rejected']}\n")
            f.write(f"  Inconclusive: {r['inconclusive']}\n")
            f.write(f"  Top techniques:\n")
            sorted_tech = sorted(r['techniques'], key=lambda x: x['overall'], reverse=True)[:3]
            for t in sorted_tech:
                f.write(f"    - {t['name']}: {t['overall']:.1f}% ({t['status']})\n")
            f.write("\n")

    print("\nSummary saved to research_summary.txt")
    print("="*70)

    db.print_statistics()

if __name__ == "__main__":
    main()
