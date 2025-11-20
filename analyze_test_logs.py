#!/usr/bin/env python3
"""
Analyze test logs to extract results when database save fails
"""

import re
from collections import defaultdict

def parse_test_log(log_file):
    """Parse the remaining_models_log.txt to extract results"""

    with open(log_file, 'r') as f:
        content = f.read()

    results = {}
    current_model = None
    current_technique = None

    # Find all model sections
    model_pattern = r'# MODEL \d+/\d+: (.+)'
    models = re.findall(model_pattern, content)

    for model in models:
        results[model] = {
            'techniques': {},
            'validated': 0,
            'rejected': 0,
            'inconclusive': 0
        }

    # Split by model
    model_sections = re.split(r'# MODEL \d+/\d+: ', content)[1:]

    for i, section in enumerate(model_sections):
        if i >= len(models):
            break

        model = models[i]

        # Find technique results
        technique_pattern = r'Testing: (.+?)\n.*?Category: (\w+)'
        techniques_found = re.findall(technique_pattern, section, re.DOTALL)

        for technique_name, category in techniques_found:
            # Find scores for this technique
            scores_pattern = rf'Testing: {re.escape(technique_name)}.*?Overall: ([\d.]+)%.*?Overall: ([\d.]+)%'
            scores = re.findall(scores_pattern, section, re.DOTALL)

            if scores and len(scores[0]) == 2:
                score1 = float(scores[0][0])
                score2 = float(scores[0][1])
                avg_score = (score1 + score2) / 2

                # Determine status
                if category == 'degradation':
                    status = 'validated' if avg_score < 60 else 'rejected'
                else:
                    if avg_score >= 75 and min(score1, score2) >= 70:
                        status = 'validated'
                    elif avg_score < 60:
                        status = 'rejected'
                    else:
                        status = 'inconclusive'

                results[model]['techniques'][technique_name] = {
                    'scores': [score1, score2],
                    'avg': avg_score,
                    'status': status,
                    'category': category
                }

                results[model][status] += 1

    return results

def print_results_summary(results):
    """Print formatted summary of results"""

    print("="*70)
    print("COMPREHENSIVE TEST RESULTS")
    print("="*70)

    for model, data in results.items():
        print(f"\n### {model}")
        print(f"  ✅ Validated: {data['validated']}")
        print(f"  ❌ Rejected: {data['rejected']}")
        print(f"  ⚠️  Inconclusive: {data['inconclusive']}")

        if data['techniques']:
            validated = {k: v for k, v in data['techniques'].items() if v['status'] == 'validated'}
            if validated:
                print(f"\n  Top Validated Techniques:")
                for tech, info in sorted(validated.items(), key=lambda x: x[1]['avg'], reverse=True)[:3]:
                    print(f"    - {tech}: {info['avg']:.1f}%")

    # Global statistics
    print(f"\n{'='*70}")
    print("GLOBAL STATISTICS")
    print(f"{'='*70}")

    total_v = sum(data['validated'] for data in results.values())
    total_r = sum(data['rejected'] for data in results.values())
    total_i = sum(data['inconclusive'] for data in results.values())

    print(f"Total Models Tested: {len(results)}")
    print(f"Total Validated Techniques: {total_v}")
    print(f"Total Rejected Techniques: {total_r}")
    print(f"Total Inconclusive: {total_i}")

    # Find best technique overall
    all_techniques = defaultdict(list)
    for model, data in results.items():
        for tech, info in data['techniques'].items():
            if info['status'] == 'validated':
                all_techniques[tech].append(info['avg'])

    if all_techniques:
        print(f"\nBest Techniques Across All Models:")
        for tech, scores in sorted(all_techniques.items(), key=lambda x: sum(x[1])/len(x[1]), reverse=True)[:5]:
            avg = sum(scores) / len(scores)
            print(f"  - {tech}: {avg:.1f}% (validated on {len(scores)} models)")

def save_to_markdown(results, output_file):
    """Save results to markdown file"""

    with open(output_file, 'w') as f:
        f.write("# Complete Test Results Analysis\n\n")
        f.write("**Generated from log analysis**\n\n")
        f.write("---\n\n")

        for model, data in results.items():
            f.write(f"## {model}\n\n")
            f.write(f"- ✅ Validated: {data['validated']}\n")
            f.write(f"- ❌ Rejected: {data['rejected']}\n")
            f.write(f"- ⚠️ Inconclusive: {data['inconclusive']}\n\n")

            if data['techniques']:
                f.write("### Techniques Tested\n\n")
                for tech, info in sorted(data['techniques'].items(), key=lambda x: x[1]['avg'], reverse=True):
                    status_icon = {'validated': '✅', 'rejected': '❌', 'inconclusive': '⚠️'}[info['status']]
                    f.write(f"{status_icon} **{tech}**: {info['avg']:.1f}% ({info['status']})\n")
                f.write("\n")

            f.write("---\n\n")

    print(f"\n✅ Results saved to: {output_file}")

if __name__ == "__main__":
    print("Analyzing test logs...")
    results = parse_test_log("/home/user/AIREX/remaining_models_log.txt")
    print_results_summary(results)
    save_to_markdown(results, "/home/user/AIREX/ANALYZED_RESULTS.md")
