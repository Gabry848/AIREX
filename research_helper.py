#!/usr/bin/env python3
"""
Research Helper - Quick commands for managing research data
"""

import sys
from db_manager import DatabaseManager

def add_technique_quick(name: str, desc: str, category: str = "experimental"):
    """Quickly add a technique"""
    db = DatabaseManager()
    db.add_technique(name, desc, category)

def record_evaluation(model: str, technique: str, scores: dict, obs: str = ""):
    """Quickly record an evaluation"""
    db = DatabaseManager()
    db.add_evaluation(
        model_name=model,
        technique_name=technique,
        accuracy=scores.get('accuracy', 0),
        coherence=scores.get('coherence', 0),
        relevance=scores.get('relevance', 0),
        creativity=scores.get('creativity', 0),
        response_time=scores.get('response_time', 0),
        observations=obs
    )

def validate_technique(model: str, technique: str, success_rate: float):
    """Mark technique as validated"""
    db = DatabaseManager()
    db.update_evaluation_status(model, technique, 'validated', success_rate)

def reject_technique(model: str, technique: str):
    """Mark technique as rejected"""
    db = DatabaseManager()
    db.update_evaluation_status(model, technique, 'rejected', 0)

def show_model_results(model: str):
    """Show all results for a model"""
    db = DatabaseManager()
    results = db.get_evaluations_for_model(model)

    print(f"\n{'='*70}")
    print(f"RESULTS FOR: {model}")
    print(f"{'='*70}\n")

    validated = [r for r in results if r['status'] == 'validated']
    testing = [r for r in results if r['status'] == 'testing']
    rejected = [r for r in results if r['status'] == 'rejected']

    print(f"✓ Validated: {len(validated)}")
    print(f"⧗ Testing: {len(testing)}")
    print(f"✗ Rejected: {len(rejected)}\n")

    if validated:
        print("VALIDATED TECHNIQUES:")
        print("-" * 70)
        for r in validated:
            print(f"• {r['technique_name']}")
            print(f"  Overall: {r['overall_effectiveness']:.1f}% | Success Rate: {r['success_rate']:.1f}%")
            print(f"  Category: {r['category']}")
            if r['observations']:
                print(f"  Notes: {r['observations'][:100]}...")
            print()

def list_all_techniques():
    """List all discovered techniques"""
    db = DatabaseManager()
    techniques = db.get_all_techniques()

    print(f"\n{'='*70}")
    print(f"ALL DISCOVERED TECHNIQUES ({len(techniques)})")
    print(f"{'='*70}\n")

    for t in techniques:
        print(f"• {t['technique_name']}")
        print(f"  {t['description'][:100]}...")
        print(f"  Category: {t['category']} | Source: {t['discovered_from']}")
        print()

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python research_helper.py stats")
        print("  python research_helper.py model <model_name>")
        print("  python research_helper.py techniques")
        sys.exit(1)

    cmd = sys.argv[1]

    if cmd == "stats":
        db = DatabaseManager()
        db.print_statistics()
    elif cmd == "model" and len(sys.argv) > 2:
        show_model_results(sys.argv[2])
    elif cmd == "techniques":
        list_all_techniques()
