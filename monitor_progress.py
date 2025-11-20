#!/usr/bin/env python3
"""
Monitora il progresso della ricerca
"""

import sqlite3
import os
import time
from datetime import datetime

DB_PATH = "prompt_engineering_research.db"


def get_progress():
    """Ottiene lo stato corrente della ricerca"""
    if not os.path.exists(DB_PATH):
        return None

    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    # Conta modelli
    cursor.execute("SELECT COUNT(*) as count FROM models")
    num_models = cursor.fetchone()['count']

    # Conta tecniche
    cursor.execute("SELECT COUNT(*) as count FROM prompt_techniques")
    num_techniques = cursor.fetchone()['count']

    # Conta test
    cursor.execute("SELECT COUNT(*) as count FROM technique_tests")
    num_tests = cursor.fetchone()['count']

    # Ultimi test
    cursor.execute("""
        SELECT m.model_name, COUNT(tt.id) as num_tests
        FROM models m
        LEFT JOIN technique_tests tt ON m.id = tt.model_id
        GROUP BY m.id
        ORDER BY m.created_at DESC
    """)
    models_status = cursor.fetchall()

    conn.close()

    return {
        'num_models': num_models,
        'num_techniques': num_techniques,
        'num_tests': num_tests,
        'models_status': [dict(row) for row in models_status]
    }


def display_progress():
    """Mostra il progresso in console"""
    print("\n" + "="*70)
    print(f" MONITORAGGIO RICERCA - {datetime.now().strftime('%H:%M:%S')}")
    print("="*70)

    progress = get_progress()

    if not progress:
        print("\n✗ Database non ancora creato. La ricerca non è ancora iniziata.\n")
        return

    print(f"\nStatistiche Globali:")
    print(f"  • Modelli analizzati:     {progress['num_models']}")
    print(f"  • Tecniche catalogate:    {progress['num_techniques']}")
    print(f"  • Test totali eseguiti:   {progress['num_tests']}")

    print(f"\nStato per Modello:")
    for m in progress['models_status']:
        status = "✓ Completato" if m['num_tests'] >= 50 else f"⏳ In corso ({m['num_tests']} test)"
        print(f"  • {m['model_name']}: {status}")

    # Check log file
    if os.path.exists("research_output.log"):
        # Leggi ultime righe
        with open("research_output.log", 'r') as f:
            lines = f.readlines()
            if lines:
                print(f"\nUltima attività (dal log):")
                for line in lines[-5:]:
                    print(f"  {line.strip()}")

    print("\n" + "="*70 + "\n")


def main():
    """Modalità watch continuo"""
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == '--watch':
        print("Modalità monitoraggio continuo (Ctrl+C per uscire)")
        try:
            while True:
                display_progress()
                time.sleep(30)  # Aggiorna ogni 30 secondi
        except KeyboardInterrupt:
            print("\nMonitoraggio terminato.\n")
    else:
        display_progress()


if __name__ == "__main__":
    main()
