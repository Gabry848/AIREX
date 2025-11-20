#!/usr/bin/env python3
"""Quick test of one technique on Grok"""

from automated_researcher import PromptResearcher

researcher = PromptResearcher()

print("Testing one technique on Grok to verify system works...\n")

result = researcher.test_technique_on_model(
    model_name="x-ai/grok-4.1-fast",
    technique_name="XML-Nested Hierarchical Structuring",
    technique_desc="Use deeply nested XML tags to organize complex multi-part requests",
    technique_category="enhancement",
    num_tests=2  # Just 2 tests for quick validation
)

if result:
    print("\n✅ System test successful!")
    print(f"Overall effectiveness: {result['overall']:.1f}%")
    print(f"Status: {result['status']}")
else:
    print("\n❌ System test failed")
