#!/usr/bin/env python3
"""
Script per visualizzare i risultati della ricerca dal database
"""

import sqlite3
import json
from typing import List, Dict
from tabulate import tabulate


DB_PATH = "prompt_engineering_research.db"


def view_all_models():
    """Visualizza tutti i modelli nel database"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute("""
        SELECT model_name, provider, COUNT(DISTINCT tt.technique_id) as num_techniques_tested
        FROM models m
        LEFT JOIN technique_tests tt ON m.id = tt.model_id
        GROUP BY m.id
        ORDER BY m.model_name
    """)

    rows = cursor.fetchall()
    data = [[r['model_name'], r['provider'], r['num_techniques_tested']] for r in rows]

    print("\n=== MODELLI NEL DATABASE ===\n")
    print(tabulate(data, headers=['Modello', 'Provider', 'Tecniche Testate'], tablefmt='grid'))
    print(f"\nTotale: {len(rows)} modelli\n")

    conn.close()


def view_top_techniques(model_name: str = None, limit: int = 10):
    """Visualizza le top tecniche per un modello o globalmente"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    if model_name:
        cursor.execute("""
            SELECT
                pt.technique_name,
                pt.category,
                AVG(tt.overall_score) as avg_score,
                AVG(tt.coherence_score) as coherence,
                AVG(tt.relevance_score) as relevance,
                AVG(tt.completeness_score) as completeness,
                AVG(tt.accuracy_score) as accuracy,
                AVG(tt.creativity_score) as creativity,
                COUNT(tt.id) as num_tests
            FROM technique_tests tt
            JOIN prompt_techniques pt ON tt.technique_id = pt.id
            JOIN models m ON tt.model_id = m.id
            WHERE m.model_name = ?
            GROUP BY pt.id
            ORDER BY avg_score DESC
            LIMIT ?
        """, (model_name, limit))

        print(f"\n=== TOP {limit} TECNICHE PER {model_name} ===\n")
    else:
        cursor.execute("""
            SELECT
                pt.technique_name,
                pt.category,
                AVG(tt.overall_score) as avg_score,
                AVG(tt.coherence_score) as coherence,
                AVG(tt.relevance_score) as relevance,
                AVG(tt.completeness_score) as completeness,
                AVG(tt.accuracy_score) as accuracy,
                AVG(tt.creativity_score) as creativity,
                COUNT(tt.id) as num_tests,
                COUNT(DISTINCT tt.model_id) as num_models
            FROM technique_tests tt
            JOIN prompt_techniques pt ON tt.technique_id = pt.id
            GROUP BY pt.id
            ORDER BY avg_score DESC
            LIMIT ?
        """, (limit,))

        print(f"\n=== TOP {limit} TECNICHE GLOBALI ===\n")

    rows = cursor.fetchall()
    data = []
    for i, r in enumerate(rows, 1):
        data.append([
            i,
            r['technique_name'][:30],
            r['category'],
            f"{r['avg_score']:.1f}%",
            f"{r['coherence']:.1f}",
            f"{r['relevance']:.1f}",
            f"{r['completeness']:.1f}",
            f"{r['accuracy']:.1f}",
            f"{r['creativity']:.1f}",
            r['num_tests']
        ])

    headers = ['#', 'Tecnica', 'Categoria', 'Score', 'Coh', 'Rel', 'Com', 'Acc', 'Cre', 'Tests']
    print(tabulate(data, headers=headers, tablefmt='grid'))
    print()

    conn.close()


def view_worst_techniques(limit: int = 10):
    """Visualizza le tecniche peggiori"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            pt.technique_name,
            pt.category,
            AVG(tt.overall_score) as avg_score,
            COUNT(tt.id) as num_tests
        FROM technique_tests tt
        JOIN prompt_techniques pt ON tt.technique_id = pt.id
        GROUP BY pt.id
        HAVING num_tests >= 3
        ORDER BY avg_score ASC
        LIMIT ?
    """, (limit,))

    rows = cursor.fetchall()
    data = [[r['technique_name'], r['category'], f"{r['avg_score']:.1f}%", r['num_tests']]
            for r in rows]

    print(f"\n=== TECNICHE MENO EFFICACI (Bottom {limit}) ===\n")
    print(tabulate(data, headers=['Tecnica', 'Categoria', 'Score Medio', 'Tests'], tablefmt='grid'))
    print()

    conn.close()


def view_statistics():
    """Visualizza statistiche generali"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    # Stats generali
    cursor.execute("SELECT COUNT(*) as count FROM models")
    num_models = cursor.fetchone()['count']

    cursor.execute("SELECT COUNT(*) as count FROM prompt_techniques")
    num_techniques = cursor.fetchone()['count']

    cursor.execute("SELECT COUNT(*) as count FROM technique_tests")
    num_tests = cursor.fetchone()['count']

    cursor.execute("SELECT AVG(overall_score) as avg FROM technique_tests")
    avg_score = cursor.fetchone()['avg'] or 0

    print("\n=== STATISTICHE GENERALI ===\n")
    print(f"Modelli nel database:    {num_models}")
    print(f"Tecniche testate:        {num_techniques}")
    print(f"Test totali eseguiti:    {num_tests}")
    print(f"Score medio globale:     {avg_score:.2f}%")
    print()

    # Statistiche per categoria
    cursor.execute("""
        SELECT
            pt.category,
            COUNT(DISTINCT pt.id) as num_techniques,
            AVG(tt.overall_score) as avg_score
        FROM prompt_techniques pt
        LEFT JOIN technique_tests tt ON pt.id = tt.technique_id
        GROUP BY pt.category
        ORDER BY avg_score DESC
    """)

    rows = cursor.fetchall()
    data = [[r['category'], r['num_techniques'], f"{r['avg_score'] or 0:.1f}%"] for r in rows]

    print("=== PERFORMANCE PER CATEGORIA ===\n")
    print(tabulate(data, headers=['Categoria', 'Num. Tecniche', 'Score Medio'], tablefmt='grid'))
    print()

    conn.close()


def export_to_markdown(output_file: str = "current_results.md"):
    """Esporta i risultati attuali in un file markdown"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    content = "# Risultati Parziali della Ricerca\n\n"

    # Per ogni modello
    cursor.execute("SELECT * FROM models ORDER BY model_name")
    models = cursor.fetchall()

    for model in models:
        content += f"\n## {model['model_name']}\n\n"

        # Top 10 tecniche per questo modello
        cursor.execute("""
            SELECT
                pt.technique_name,
                AVG(tt.overall_score) as avg_score
            FROM technique_tests tt
            JOIN prompt_techniques pt ON tt.technique_id = pt.id
            WHERE tt.model_id = ?
            GROUP BY pt.id
            ORDER BY avg_score DESC
            LIMIT 10
        """, (model['id'],))

        techniques = cursor.fetchall()
        if techniques:
            content += "### Top 10 Tecniche\n\n"
            for i, tech in enumerate(techniques, 1):
                content += f"{i}. **{tech['technique_name']}**: {tech['avg_score']:.2f}%\n"
        else:
            content += "*Nessun test ancora eseguito*\n"

        content += "\n---\n"

    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(content)

    print(f"✓ Esportato in {output_file}")

    conn.close()


def main():
    import sys

    print("\n" + "="*60)
    print(" VISUALIZZATORE RISULTATI RICERCA PROMPT ENGINEERING")
    print("="*60)

    try:
        view_statistics()
        view_all_models()
        view_top_techniques(limit=15)
        view_worst_techniques(limit=10)

        print("\n→ Per esportare i risultati in markdown: export_to_markdown()")
        print("→ Per vedere tecniche di un modello specifico: view_top_techniques('model_name')")
        print()

    except sqlite3.OperationalError as e:
        print(f"\n✗ Errore: {e}")
        print("  Il database potrebbe non essere ancora stato creato.")
        print("  Esegui prima 'python run_complete_research.py'\n")


if __name__ == "__main__":
    main()
