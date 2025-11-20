#!/usr/bin/env python3
"""
Test rapido del sistema su un singolo modello
"""

from model_researcher import ModelResearcher
import sys

def main():
    # Usa un modello veloce ed economico per il test
    test_model = "openai/gpt-4o-mini"

    print(f"\n{'='*60}")
    print(f" TEST RAPIDO DEL SISTEMA")
    print(f" Modello: {test_model}")
    print(f"{'='*60}\n")

    researcher = ModelResearcher()

    try:
        # Test 1: Ricerca informazioni
        print("→ Test 1: Ricerca informazioni sul modello...")
        model_info = researcher.research_model_info(test_model)
        print(f"✓ Informazioni raccolte")

        # Test 2: Test singola tecnica
        print("\n→ Test 2: Test di una tecnica (Chain-of-Thought)...")
        technique = {
            "name": "Chain-of-Thought Test",
            "description": "Test della tecnica CoT",
            "category": "test",
            "is_positive": True,
            "prompt_template": "Pensa passo per passo: {question}"
        }

        test_questions = ["Quanto fa 15 * 7?"]

        result = researcher.test_technique_on_model(test_model, technique, test_questions)
        print(f"✓ Tecnica testata - Score medio: {result['average_score']:.2f}%")

        # Test 3: Verifica salvataggio nel database
        print("\n→ Test 3: Verifica dati nel database...")
        stats = researcher.research_system.get_technique_stats(test_model)
        print(f"✓ Trovate {len(stats)} tecniche nel database")

        if stats:
            print("\nRisultati:")
            for s in stats:
                print(f"  - {s['technique_name']}: {s['avg_score']:.2f}%")

        print("\n" + "="*60)
        print(" TEST COMPLETATO CON SUCCESSO!")
        print("="*60)
        print("\nIl sistema è pronto per la ricerca completa.")
        print("Esegui: python3 run_complete_research.py\n")

    except Exception as e:
        print(f"\n✗ ERRORE: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

    finally:
        researcher.close()


if __name__ == "__main__":
    main()
