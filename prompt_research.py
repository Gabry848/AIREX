#!/usr/bin/env python3
"""
Sistema di ricerca per tecniche di Prompt Engineering
"""

import sqlite3
import requests
import json
import time
from datetime import datetime
from typing import List, Dict, Tuple, Optional
import re

# Configurazione API OpenRouter
OPENROUTER_API_KEY = "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"
OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"

DB_PATH = "prompt_engineering_research.db"


class PromptResearchSystem:
    def __init__(self, db_path: str = DB_PATH):
        self.db_path = db_path
        self.conn = None
        self.init_database()

    def init_database(self):
        """Inizializza il database SQLite"""
        self.conn = sqlite3.connect(self.db_path)
        self.conn.row_factory = sqlite3.Row

        # Leggi e esegui lo schema
        with open('database_schema.sql', 'r') as f:
            schema = f.read()
            self.conn.executescript(schema)

        self.conn.commit()
        print(f"✓ Database inizializzato: {self.db_path}")

    def add_model(self, model_name: str, **kwargs) -> int:
        """Aggiunge un modello al database"""
        cursor = self.conn.cursor()

        # Controlla se esiste già
        cursor.execute("SELECT id FROM models WHERE model_name = ?", (model_name,))
        existing = cursor.fetchone()
        if existing:
            return existing[0]

        cursor.execute("""
            INSERT INTO models (model_name, provider, year_created, size_parameters,
                              architecture, context_window, description, research_notes)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            model_name,
            kwargs.get('provider'),
            kwargs.get('year_created'),
            kwargs.get('size_parameters'),
            kwargs.get('architecture'),
            kwargs.get('context_window'),
            kwargs.get('description'),
            kwargs.get('research_notes')
        ))

        self.conn.commit()
        return cursor.lastrowid

    def add_technique(self, technique_name: str, description: str,
                     category: str, is_positive: bool, notes: str = "") -> int:
        """Aggiunge una tecnica di prompt engineering"""
        cursor = self.conn.cursor()

        # Controlla se esiste già
        cursor.execute("SELECT id FROM prompt_techniques WHERE technique_name = ?",
                      (technique_name,))
        existing = cursor.fetchone()
        if existing:
            return existing[0]

        cursor.execute("""
            INSERT INTO prompt_techniques (technique_name, description, category,
                                          is_positive, notes)
            VALUES (?, ?, ?, ?, ?)
        """, (technique_name, description, category, is_positive, notes))

        self.conn.commit()
        return cursor.lastrowid

    def call_openrouter(self, model: str, prompt: str,
                       max_tokens: int = 1000, temperature: float = 0.7) -> Dict:
        """Effettua una chiamata API a OpenRouter"""
        headers = {
            "Authorization": f"Bearer {OPENROUTER_API_KEY}",
            "Content-Type": "application/json"
        }

        data = {
            "model": model,
            "messages": [
                {"role": "user", "content": prompt}
            ],
            "max_tokens": max_tokens,
            "temperature": temperature
        }

        try:
            response = requests.post(OPENROUTER_URL, headers=headers, json=data)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"✗ Errore nella chiamata API: {e}")
            return {"error": str(e)}

    def evaluate_response(self, prompt: str, response: str,
                         expected_behavior: str = None) -> Dict[str, float]:
        """
        Valuta una risposta secondo 5 criteri (0-100%)

        Criteri:
        1. Coherence: La risposta è logica e ben strutturata?
        2. Relevance: La risposta è pertinente alla domanda?
        3. Completeness: La risposta copre tutti gli aspetti richiesti?
        4. Accuracy: Le informazioni sembrano accurate?
        5. Creativity: La risposta mostra originalità?
        """

        # Sistema di valutazione basato su euristiche
        scores = {}

        # 1. Coherence - lunghezza e struttura
        response_length = len(response.split())
        has_structure = bool(re.search(r'[\.\!\?]\s+[A-Z]', response))
        coherence = min(100, (response_length / 50) * 50 + (50 if has_structure else 0))
        scores['coherence_score'] = round(coherence, 2)

        # 2. Relevance - parole chiave del prompt nella risposta
        prompt_words = set(prompt.lower().split())
        response_words = set(response.lower().split())
        relevance_ratio = len(prompt_words & response_words) / max(len(prompt_words), 1)
        scores['relevance_score'] = round(min(100, relevance_ratio * 150), 2)

        # 3. Completeness - lunghezza della risposta
        completeness = min(100, (response_length / 100) * 100)
        scores['completeness_score'] = round(completeness, 2)

        # 4. Accuracy - presenza di disclaimer, numeri, fatti
        has_numbers = bool(re.search(r'\d+', response))
        has_uncertainty = bool(re.search(r'(potrebbe|forse|probabilmente|circa)',
                                        response, re.IGNORECASE))
        accuracy = 50 + (20 if has_numbers else 0) + (30 if not has_uncertainty else 0)
        scores['accuracy_score'] = round(accuracy, 2)

        # 5. Creativity - varietà lessicale e lunghezza
        unique_words = len(set(response.lower().split()))
        creativity = min(100, (unique_words / response_length * 100) if response_length > 0 else 0)
        scores['creativity_score'] = round(creativity, 2)

        # Overall score
        scores['overall_score'] = round(sum(scores.values()) / 5, 2)

        return scores

    def test_technique(self, model_name: str, technique_id: int,
                      test_prompt: str, num_tests: int = 3) -> List[Dict]:
        """
        Testa una tecnica su un modello con test multipli
        """
        results = []
        model_id = self.get_model_id(model_name)

        for i in range(num_tests):
            print(f"  Test {i+1}/{num_tests}...", end=" ")

            # Chiamata API
            response_data = self.call_openrouter(model_name, test_prompt)

            if "error" in response_data:
                print(f"✗ Errore")
                continue

            response_text = response_data.get("choices", [{}])[0].get("message", {}).get("content", "")

            # Valutazione
            scores = self.evaluate_response(test_prompt, response_text)

            # Salva nel database
            cursor = self.conn.cursor()
            cursor.execute("""
                INSERT INTO technique_tests
                (model_id, technique_id, test_prompt, response, coherence_score,
                 relevance_score, completeness_score, accuracy_score, creativity_score,
                 overall_score)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                model_id, technique_id, test_prompt, response_text,
                scores['coherence_score'], scores['relevance_score'],
                scores['completeness_score'], scores['accuracy_score'],
                scores['creativity_score'], scores['overall_score']
            ))
            self.conn.commit()

            results.append(scores)
            print(f"✓ Overall: {scores['overall_score']}%")

            # Rate limiting
            time.sleep(2)

        return results

    def get_model_id(self, model_name: str) -> Optional[int]:
        """Ottiene l'ID di un modello dal database"""
        cursor = self.conn.cursor()
        cursor.execute("SELECT id FROM models WHERE model_name = ?", (model_name,))
        result = cursor.fetchone()
        return result[0] if result else None

    def get_technique_stats(self, model_name: str) -> List[Dict]:
        """Ottiene le statistiche delle tecniche per un modello"""
        model_id = self.get_model_id(model_name)

        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT
                pt.technique_name,
                AVG(tt.overall_score) as avg_score,
                COUNT(tt.id) as num_tests,
                AVG(tt.coherence_score) as avg_coherence,
                AVG(tt.relevance_score) as avg_relevance,
                AVG(tt.completeness_score) as avg_completeness,
                AVG(tt.accuracy_score) as avg_accuracy,
                AVG(tt.creativity_score) as avg_creativity
            FROM technique_tests tt
            JOIN prompt_techniques pt ON tt.technique_id = pt.id
            WHERE tt.model_id = ?
            GROUP BY tt.technique_id
            ORDER BY avg_score DESC
        """, (model_id,))

        return [dict(row) for row in cursor.fetchall()]

    def add_hypothesis(self, model_name: str, technique_name: str,
                      hypothesis: str) -> int:
        """Aggiunge un'ipotesi di tecnica da testare"""
        model_id = self.get_model_id(model_name)

        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT INTO technique_hypotheses (model_id, technique_name, hypothesis)
            VALUES (?, ?, ?)
        """, (model_id, technique_name, hypothesis))

        self.conn.commit()
        return cursor.lastrowid

    def export_results(self, output_file: str = "research_results.json"):
        """Esporta tutti i risultati in JSON"""
        cursor = self.conn.cursor()

        # Esporta tutto
        cursor.execute("SELECT * FROM best_techniques_per_model")
        best_techniques = [dict(row) for row in cursor.fetchall()]

        cursor.execute("SELECT * FROM technique_statistics")
        stats = [dict(row) for row in cursor.fetchall()]

        results = {
            "timestamp": datetime.now().isoformat(),
            "best_techniques_per_model": best_techniques,
            "overall_statistics": stats
        }

        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)

        print(f"✓ Risultati esportati in {output_file}")

    def close(self):
        """Chiude la connessione al database"""
        if self.conn:
            self.conn.close()


def main():
    """Funzione principale di test"""
    research = PromptResearchSystem()

    # Test base
    print("\n=== Sistema di Ricerca Prompt Engineering ===\n")
    print("Database inizializzato correttamente!")
    print(f"Pronto per testare tecniche su modelli AI\n")

    research.close()


if __name__ == "__main__":
    main()
