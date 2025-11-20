#!/usr/bin/env python3
"""
Demo script showing how to use AIREX system.
This demonstrates the basic workflow for tracking prompt engineering techniques.
"""

import os
from technique_manager import (
    add_model,
    add_technique,
    link_model_technique,
    log_experiment,
    update_technique_score
)


def demo_basic_workflow():
    """Demonstrate basic AIREX workflow."""

    print("=" * 70)
    print("AIREX Demo: Basic Workflow")
    print("=" * 70)

    # Step 1: Add models
    print("\n1. Adding AI Models...")
    gpt4_id = add_model(
        name="GPT-4",
        source_url="https://openai.com/gpt-4",
        notes="OpenAI's most advanced model"
    )
    print(f"   ✓ Added GPT-4 (ID: {gpt4_id})")

    claude_id = add_model(
        name="Claude-3-Opus",
        source_url="https://anthropic.com",
        notes="Anthropic's flagship model"
    )
    print(f"   ✓ Added Claude-3-Opus (ID: {claude_id})")

    # Step 2: Add techniques
    print("\n2. Adding Prompt Engineering Techniques...")
    cot_id = add_technique(
        name="Chain of Thought",
        description="Encourage the model to break down complex problems step by step",
        origin_type="online"
    )
    print(f"   ✓ Added Chain of Thought (ID: {cot_id})")

    few_shot_id = add_technique(
        name="Few-Shot Learning",
        description="Provide 2-5 examples before asking the main question",
        origin_type="online"
    )
    print(f"   ✓ Added Few-Shot Learning (ID: {few_shot_id})")

    # Step 3: Link techniques to models
    print("\n3. Linking Techniques to Models...")
    link_model_technique(
        model_id=gpt4_id,
        technique_id=cot_id,
        score_for_this_model=9.0
    )
    print(f"   ✓ Linked Chain of Thought to GPT-4 (score: 9.0)")

    link_model_technique(
        model_id=claude_id,
        technique_id=cot_id,
        score_for_this_model=8.5
    )
    print(f"   ✓ Linked Chain of Thought to Claude (score: 8.5)")

    # Step 4: Run experiments
    print("\n4. Running Experiments...")
    exp_id = log_experiment(
        technique_id=cot_id,
        test_prompt="Calculate 15% of 240, showing your work step by step.",
        model_used="GPT-4",
        api_response_text="Let me solve this step by step:\n1. Convert 15% to decimal: 0.15\n2. Multiply: 0.15 × 240 = 36\nAnswer: 36",
        score=9.5,
        is_regression=False
    )
    print(f"   ✓ Logged experiment (ID: {exp_id}, score: 9.5)")

    # Step 5: Update technique scores based on experiments
    print("\n5. Updating Technique Scores...")
    update_technique_score(
        technique_id=cot_id,
        effectiveness_score=9.2,
        reliability_score=8.8
    )
    print(f"   ✓ Updated Chain of Thought scores (eff: 9.2, rel: 8.8)")

    print("\n" + "=" * 70)
    print("✓ Demo completed successfully!")
    print("=" * 70)


def main():
    """Main entry point."""
    if not os.getenv('DATABASE_URL'):
        print("ERROR: DATABASE_URL environment variable not set!")
        print("Please set it with: export DATABASE_URL='postgresql://...'")
        return 1

    try:
        demo_basic_workflow()
        return 0
    except Exception as e:
        print(f"\nERROR: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    import sys
    sys.exit(main())
