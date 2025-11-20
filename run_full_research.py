#!/usr/bin/env python3
"""
Full Research Orchestrator
Runs complete prompt engineering research across all models
"""

import time
from automated_researcher import PromptResearcher
from db_manager import DatabaseManager

# Models to test (from MODELS.md)
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

def run_research_for_model(researcher, model_name: str):
    """Run complete research for one model"""
    print(f"\n{'#'*70}")
    print(f"# RESEARCHING MODEL: {model_name}")
    print(f"{'#'*70}\n")

    db = DatabaseManager()

    # Get all techniques from database
    techniques = db.get_all_techniques()

    if not techniques:
        print("❌ No techniques found in database!")
        return

    print(f"Found {len(techniques)} techniques to test\n")

    validated_count = 0
    rejected_count = 0
    inconclusive_count = 0

    for i, tech in enumerate(techniques, 1):
        print(f"\n[{i}/{len(techniques)}] Testing: {tech['technique_name']}")

        try:
            result = researcher.test_technique_on_model(
                model_name=model_name,
                technique_name=tech['technique_name'],
                technique_desc=tech['description'],
                technique_category=tech['category'],
                num_tests=3
            )

            if result:
                if result['status'] == 'validated':
                    validated_count += 1
                elif result['status'] == 'rejected':
                    rejected_count += 1
                else:
                    inconclusive_count += 1

            # Rate limiting between techniques
            time.sleep(2)

        except Exception as e:
            print(f"❌ Error testing technique: {e}")
            continue

    # Print summary for this model
    print(f"\n{'='*70}")
    print(f"MODEL SUMMARY: {model_name}")
    print(f"{'='*70}")
    print(f"✅ Validated: {validated_count}")
    print(f"❌ Rejected: {rejected_count}")
    print(f"⚠️ Inconclusive: {inconclusive_count}")
    print(f"{'='*70}\n")

    return {
        'model': model_name,
        'validated': validated_count,
        'rejected': rejected_count,
        'inconclusive': inconclusive_count
    }

def main():
    print("="*70)
    print("FULL PROMPT ENGINEERING RESEARCH")
    print("="*70)
    print(f"Models to test: {len(MODELS)}")
    print(f"Target: 10 validated techniques per model")
    print("="*70)

    researcher = PromptResearcher()
    results = []

    for i, model in enumerate(MODELS, 1):
        print(f"\n\n{'#'*70}")
        print(f"# MODEL {i}/{len(MODELS)}")
        print(f"{'#'*70}\n")

        try:
            result = run_research_for_model(researcher, model)
            results.append(result)

            # Longer pause between models
            if i < len(MODELS):
                print(f"\nPausing 5 seconds before next model...")
                time.sleep(5)

        except Exception as e:
            print(f"❌ Error with model {model}: {e}")
            results.append({
                'model': model,
                'validated': 0,
                'rejected': 0,
                'inconclusive': 0,
                'error': str(e)
            })
            continue

    # Final summary
    print("\n\n" + "="*70)
    print("RESEARCH COMPLETE - FINAL SUMMARY")
    print("="*70)

    total_validated = sum(r['validated'] for r in results)
    total_rejected = sum(r['rejected'] for r in results)
    total_inconclusive = sum(r['inconclusive'] for r in results)

    print(f"\nTotal across all models:")
    print(f"  ✅ Validated: {total_validated}")
    print(f"  ❌ Rejected: {total_rejected}")
    print(f"  ⚠️ Inconclusive: {total_inconclusive}")

    print(f"\nPer-model breakdown:")
    for r in results:
        status = "❌ ERROR" if 'error' in r else f"✅ {r['validated']} validated"
        print(f"  {r['model']}: {status}")

    print("\n" + "="*70)
    print("Database updated with all results")
    print("Run 'python research_helper.py stats' to see detailed statistics")
    print("="*70)

    # Print database statistics
    db = DatabaseManager()
    db.print_statistics()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️ Research interrupted by user")
    except Exception as e:
        print(f"\n\n❌ Fatal error: {e}")
