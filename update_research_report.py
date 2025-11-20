#!/usr/bin/env python3
"""
Update RESEARCH.md with final results from database
"""

from db_manager import DatabaseManager
from datetime import datetime

def generate_final_report():
    db = DatabaseManager()

    # Get all stats
    stats = db.get_statistics()

    # Get all models
    db.connect()
    cursor = db.conn.cursor()
    cursor.execute("SELECT DISTINCT model_name FROM models ORDER BY model_name")
    models = [row[0] for row in cursor.fetchall()]
    db.close()

    print("Generating final report...")
    print(f"Models analyzed: {len(models)}")
    print(f"Total techniques: {stats['total_techniques']}")
    print(f"Validated: {stats['validated_techniques']}")

    # Generate sections
    report_sections = {
        'executive_summary': generate_executive_summary(db, stats),
        'model_results': generate_model_results(db, models),
        'cross_model_analysis': generate_cross_model_analysis(db, models),
        'statistics_table': generate_statistics_table(db, models),
    }

    # Read current report
    with open('/home/user/AIREX/RESEARCH.md', 'r') as f:
        report = f.read()

    # Update placeholders
    report = report.replace('[TO BE UPDATED WITH FINAL RESULTS]', report_sections['executive_summary'])
    report = report.replace('*Report Generated*: [TO BE UPDATED WITH COMPLETION TIME]',
                          f"*Report Generated*: {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}")

    # Replace model sections
    for model in models:
        model_text = f"### {models.index(model) + 1}. {model}\n"
        if model == "x-ai/grok-4.1-fast":
            continue  # Already filled
        else:
            model_text += generate_single_model_section(db, model)

        # Find and replace
        placeholder = f"**[Testing in progress]**" if "gpt-5-mini" in model else "**[Pending]**"
        section_marker = f"{models.index(model) + 1}. {model}"
        report = report.replace(section_marker + "\n" + placeholder, model_text)

    # Add cross-model analysis
    report = report.replace('[TO BE UPDATED AFTER ALL MODELS COMPLETE]',
                          report_sections['cross_model_analysis'])

    # Add statistics table
    report = report.replace('| x-ai/grok-4.1-fast | 3 | 3 | 4 | Reasoning Chain Visualization | 82.4% |',
                          report_sections['statistics_table'])

    # Write updated report
    with open('/home/user/AIREX/RESEARCH.md', 'w') as f:
        f.write(report)

    print("\n✅ Report updated successfully!")
    return report

def generate_executive_summary(db, stats):
    summary = f"""
**Research Completed**: {datetime.now().strftime('%Y-%m-%d')}

Key Findings:
- Identified **{stats['validated_techniques']} validated techniques** across all models
- Tested **{stats['total_techniques']} unique techniques** systematically
- Analyzed **{stats['total_models']} frontier LLMs** from major providers
- Discovered model-specific optimizations and universal patterns
"""
    if stats['best_technique']:
        summary += f"- Best overall technique: **{stats['best_technique']['technique_name']}** "
        summary += f"(avg: {stats['best_technique']['avg_score']:.1f}%)\n"

    return summary

def generate_single_model_section(db, model_name):
    evaluations = db.get_evaluations_for_model(model_name)

    if not evaluations:
        return "- **Status**: Testing not completed\n"

    validated = [e for e in evaluations if e['status'] == 'validated']
    rejected = [e for e in evaluations if e['status'] == 'rejected']

    section = f"- **Validated Techniques**: {len(validated)}\n"

    if validated:
        section += "- **Top Techniques**:\n"
        for e in sorted(validated, key=lambda x: x['overall_effectiveness'], reverse=True)[:3]:
            section += f"  - {e['technique_name']} ({e['overall_effectiveness']:.1f}%)\n"

    return section

def generate_model_results(db, models):
    results = ""
    for model in models:
        evaluations = db.get_evaluations_for_model(model)
        validated = [e for e in evaluations if e['status'] == 'validated']
        results += f"\n**{model}**: {len(validated)} validated techniques\n"

    return results

def generate_cross_model_analysis(db, models):
    db.connect()
    cursor = db.conn.cursor()

    # Find universal techniques (validated on >=70% of models)
    cursor.execute("""
        SELECT t.technique_name, COUNT(DISTINCT e.model_id) as model_count,
               AVG(e.overall_effectiveness) as avg_score
        FROM techniques t
        JOIN evaluations e ON t.id = e.technique_id
        WHERE e.status = 'validated'
        GROUP BY t.technique_name
        HAVING model_count >= ?
        ORDER BY model_count DESC, avg_score DESC
    """, (len(models) * 0.7,))

    universal = cursor.fetchall()

    analysis = "\n### Universal Techniques\n"
    if universal:
        analysis += "Techniques validated across ≥70% of models:\n\n"
        for tech, count, score in universal:
            analysis += f"- **{tech}**: Validated on {count}/{len(models)} models (avg: {score:.1f}%)\n"
    else:
        analysis += "No techniques validated across ≥70% of models.\n"

    # Model-specific techniques
    cursor.execute("""
        SELECT t.technique_name, m.model_name, e.overall_effectiveness
        FROM techniques t
        JOIN evaluations e ON t.id = e.technique_id
        JOIN models m ON e.model_id = m.id
        WHERE e.status = 'validated'
        AND t.id IN (
            SELECT technique_id FROM evaluations
            WHERE status = 'validated'
            GROUP BY technique_id
            HAVING COUNT(DISTINCT model_id) = 1
        )
        ORDER BY e.overall_effectiveness DESC
    """)

    specific = cursor.fetchall()

    analysis += "\n### Model-Specific Techniques\n"
    if specific:
        analysis += "Techniques that only validated on one model:\n\n"
        for tech, model, score in specific[:10]:
            analysis += f"- **{tech}** on {model}: {score:.1f}%\n"
    else:
        analysis += "No exclusively model-specific techniques found.\n"

    db.close()
    return analysis

def generate_statistics_table(db, models):
    table = ""

    for model in models:
        evaluations = db.get_evaluations_for_model(model)

        if not evaluations:
            continue

        validated = [e for e in evaluations if e['status'] == 'validated']
        rejected = [e for e in evaluations if e['status'] == 'rejected']
        inconclusive = [e for e in evaluations if e['status'] == 'testing']

        best = sorted(evaluations, key=lambda x: x['overall_effectiveness'], reverse=True)[0] if evaluations else None

        table += f"| {model} | {len(validated)} | {len(rejected)} | {len(inconclusive)} | "

        if best:
            table += f"{best['technique_name']} | {best['overall_effectiveness']:.1f}% |\n"
        else:
            table += "N/A | N/A |\n"

    return table

if __name__ == "__main__":
    generate_final_report()
