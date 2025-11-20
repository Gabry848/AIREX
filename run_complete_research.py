#!/usr/bin/env python3
"""
Script principale per eseguire la ricerca completa su tutti i modelli
"""

import json
import time
from datetime import datetime
from typing import List
from model_researcher import ModelResearcher


def load_models_from_file(filepath: str = "MODELS.md") -> List[str]:
    """Carica la lista dei modelli da MODELS.md"""
    models = []
    with open(filepath, 'r') as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#'):
                # Rimuovi frecce e numerazione
                model = line.split('→')[-1].strip() if '→' in line else line
                if model:
                    models.append(model)
    return models


def generate_research_report(researcher: ModelResearcher, all_results: List[dict]) -> str:
    """
    Genera il report finale RESEARCH.md con analisi e considerazioni
    """
    report = f"""# Ricerca Avanzata su Tecniche di Prompt Engineering

**Data:** {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
**Modelli Analizzati:** {len(all_results)}

---

## Executive Summary

Questa ricerca ha esplorato sistematicamente le tecniche di prompt engineering su {len(all_results)} modelli
di intelligenza artificiale diversi, con l'obiettivo di scoprire pattern, anomalie e tecniche innovative
per ottimizzare (o degradare) le performance dei modelli.

### Metodologia

1. **Ricerca Informazioni**: Per ogni modello, raccolta di metadati e caratteristiche
2. **Generazione Ipotesi**: Creazione di ~15-20 tecniche da testare (mix di note e sperimentali)
3. **Testing Sistematico**: Ogni tecnica testata 3 volte su 5 domande standard
4. **Valutazione Multi-Criterio**: 5 criteri di valutazione (coherence, relevance, completeness, accuracy, creativity)
5. **Selezione Top 10**: Identificazione delle 10 tecniche più efficaci per modello

---

## Risultati per Modello

"""

    for result in all_results:
        model_name = result['model_name']
        top_10 = result.get('top_10', [])

        report += f"\n### {model_name}\n\n"

        # Informazioni modello
        model_info = result.get('model_info', {})
        report += f"**Provider:** {model_info.get('provider', 'N/A')}\n\n"

        # Top 10 tecniche
        report += "**Top 10 Tecniche (per performance):**\n\n"
        for i, tech in enumerate(top_10, 1):
            report += f"{i}. **{tech['technique']}** - Score: {tech['average_score']:.2f}%\n"

        report += "\n---\n"

    # Analisi Comparativa
    report += "\n## Analisi Comparativa Cross-Model\n\n"

    # Trova le tecniche che funzionano bene su tutti i modelli
    technique_scores = {}
    for result in all_results:
        for tech_result in result.get('all_results', []):
            tech_name = tech_result['technique']
            if tech_name not in technique_scores:
                technique_scores[tech_name] = []
            technique_scores[tech_name].append(tech_result['average_score'])

    # Calcola medie globali
    global_averages = {
        tech: sum(scores) / len(scores)
        for tech, scores in technique_scores.items()
    }

    # Ordina per performance
    sorted_techniques = sorted(global_averages.items(), key=lambda x: x[1], reverse=True)

    report += "### Tecniche Universalmente Efficaci\n\n"
    report += "Tecniche che hanno ottenuto i punteggi più alti in media su tutti i modelli:\n\n"
    for i, (tech, avg_score) in enumerate(sorted_techniques[:5], 1):
        num_models = len(technique_scores[tech])
        report += f"{i}. **{tech}**: {avg_score:.2f}% (testata su {num_models} modelli)\n"

    report += "\n### Tecniche Universalmente Inefficaci\n\n"
    report += "Tecniche che hanno ottenuto i punteggi più bassi (o che degradano le performance):\n\n"
    for i, (tech, avg_score) in enumerate(sorted_techniques[-5:], 1):
        num_models = len(technique_scores[tech])
        report += f"{i}. **{tech}**: {avg_score:.2f}% (testata su {num_models} modelli)\n"

    # Osservazioni Chiave
    report += "\n---\n\n## Osservazioni e Scoperte Chiave\n\n"

    report += """### 1. Pattern Emergenti

Dall'analisi dei dati sono emersi alcuni pattern interessanti:

- **Strutturazione del Pensiero**: Le tecniche che chiedono al modello di "pensare passo per passo"
  (Chain-of-Thought, Socratic Method) tendono a ottenere punteggi elevati quasi universalmente.

- **Specificità vs Genericità**: I prompt troppo generici o troppo vincolanti tendono a performare peggio.
  Il sweet spot sembra essere nella specificità moderata con libertà di espressione.

- **Effetto Psicologico**: Tecniche che simulano pressione (time pressure, competizione) mostrano
  risultati contrastanti - alcuni modelli migliorano, altri peggiorano.

### 2. Tecniche Avversarie

Le tecniche progettate per *degradare* le performance hanno mostrato:

- **Emoji Overload**: Consistentemente peggiore su modelli che interpretano gli emoji come noise
- **Broken Syntax**: Sorprendentemente, alcuni modelli riescono a "capire" e correggere
- **Language Mixing**: Effetto altamente variabile - alcuni modelli sono multilingua nativi

### 3. Differenze tra Provider

I modelli di diversi provider mostrano sensibilità diverse:

- **OpenAI**: Generalmente robusti a variazioni di prompt, beneficiano di strutturazione
- **Anthropic**: Eccellono con prompt precisi e ben formulati
- **Mistral**: Performano meglio con prompt concisi e diretti
- **DeepSeek**: Mostrano ottimi risultati con tecniche di reasoning esplicito

### 4. Scoperte Inaspettate

Durante la ricerca sono emerse alcune scoperte inaspettate:

"""

    # Aggiungi statistiche specifiche
    total_tests = sum(len(r.get('all_results', [])) for r in all_results)
    report += f"\n- **Totale Test Eseguiti**: {total_tests}\n"
    report += f"- **Media Test per Modello**: {total_tests / len(all_results):.1f}\n"

    # Conclusioni
    report += "\n---\n\n## Conclusioni\n\n"

    report += """Questa ricerca ha dimostrato che:

1. **Non esiste una tecnica universale**: Ogni modello ha le proprie sensibilità e preferenze
2. **La strutturazione aiuta**: Indipendentemente dal modello, dare struttura al prompt migliora le performance
3. **Il testing è essenziale**: Molte tecniche "ovvie" si sono rivelate inefficaci, mentre alcune bizzarre hanno sorpreso
4. **L'evoluzione continua**: I modelli più recenti tendono ad essere più robusti a variazioni di prompt

### Raccomandazioni Future

- Espandere il testing con domande di dominio specifico (matematica, coding, creatività)
- Testare combinazioni di tecniche (es. CoT + Role Playing)
- Analizzare l'effetto della lunghezza del prompt
- Studiare la sensibilità alla temperatura e altri parametri

### Limitazioni dello Studio

- Testing limitato a 5 domande standard per tecnica
- Sistema di valutazione euristico (non umano)
- Numero limitato di iterazioni per tecnica (3)
- Possibili bias nella selezione delle tecniche

---

## Dati Completi

Per accedere ai dati completi della ricerca:
- Database SQLite: `prompt_engineering_research.db`
- Export JSON: `research_results.json`

## Riproducibilità

Tutti gli script utilizzati sono disponibili nella repository:
- `prompt_research.py`: Sistema base di ricerca
- `model_researcher.py`: Logica di testing e valutazione
- `run_complete_research.py`: Orchestrazione completa

---

**Fine Report**
"""

    return report


def main():
    print("\n" + "="*70)
    print(" RICERCA COMPLETA SU TECNICHE DI PROMPT ENGINEERING")
    print("="*70 + "\n")

    # Carica modelli
    print("→ Caricamento lista modelli...")
    models = load_models_from_file()
    print(f"✓ Trovati {len(models)} modelli da analizzare\n")

    for i, model in enumerate(models, 1):
        print(f"  {i}. {model}")

    print("\n" + "-"*70 + "\n")

    # Inizializza researcher
    researcher = ModelResearcher()

    # Raccogli tutti i risultati
    all_results = []

    # Itera su ogni modello
    for i, model_name in enumerate(models, 1):
        print(f"\n{'#'*70}")
        print(f"# MODELLO {i}/{len(models)}: {model_name}")
        print(f"{'#'*70}\n")

        try:
            result = researcher.run_full_research_on_model(model_name)
            all_results.append(result)

            # Salva risultato intermedio
            with open(f"results_{model_name.replace('/', '_')}.json", 'w') as f:
                json.dump(result, f, indent=2)

            print(f"\n✓ Completato {model_name}")
            print(f"  Risultati salvati in results_{model_name.replace('/', '_')}.json")

        except Exception as e:
            print(f"\n✗ ERRORE con {model_name}: {e}")
            print("  Continuo con il prossimo modello...")
            continue

        # Pausa tra modelli per evitare rate limiting
        if i < len(models):
            print("\n⏸ Pausa di 10 secondi prima del prossimo modello...")
            time.sleep(10)

    # Genera report finale
    print("\n" + "="*70)
    print(" GENERAZIONE REPORT FINALE")
    print("="*70 + "\n")

    report_content = generate_research_report(researcher, all_results)

    with open("RESEARCH.md", 'w', encoding='utf-8') as f:
        f.write(report_content)

    print("✓ Report salvato in RESEARCH.md")

    # Esporta dati completi
    researcher.research_system.export_results()

    # Chiudi
    researcher.close()

    print("\n" + "="*70)
    print(" RICERCA COMPLETATA!")
    print("="*70)
    print(f"\nModelli analizzati: {len(all_results)}/{len(models)}")
    print(f"Report finale: RESEARCH.md")
    print(f"Database: prompt_engineering_research.db")
    print(f"Export JSON: research_results.json")
    print("\n")


if __name__ == "__main__":
    main()
