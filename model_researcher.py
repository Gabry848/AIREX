#!/usr/bin/env python3
"""
Script per la ricerca automatizzata di informazioni sui modelli e generazione di tecniche
"""

import json
import time
from prompt_research import PromptResearchSystem
from typing import List, Dict


class ModelResearcher:
    def __init__(self):
        self.research_system = PromptResearchSystem()

        # Tecniche di base conosciute (da cui partire)
        self.base_techniques = [
            {
                "name": "Chain-of-Thought (CoT)",
                "description": "Chiedere al modello di ragionare passo per passo",
                "category": "strutturale",
                "is_positive": True,
                "prompt_template": "Pensa passo per passo e spiega il tuo ragionamento: {question}"
            },
            {
                "name": "Few-Shot Learning",
                "description": "Fornire esempi prima della domanda",
                "category": "contestuale",
                "is_positive": True,
                "prompt_template": "Esempi:\nQ: 2+2\nA: 4\nQ: 5+3\nA: 8\nQ: {question}\nA:"
            },
            {
                "name": "Role Playing",
                "description": "Assegnare un ruolo specifico al modello",
                "category": "contestuale",
                "is_positive": True,
                "prompt_template": "Sei un esperto di matematica. {question}"
            },
            {
                "name": "Negative Prompting",
                "description": "Dire esplicitamente cosa NON fare",
                "category": "strutturale",
                "is_positive": True,
                "prompt_template": "Non usare parole complicate. {question}"
            },
            {
                "name": "Temperature Zero",
                "description": "Usare temperature=0 per risposte deterministiche",
                "category": "tecnico",
                "is_positive": True,
                "prompt_template": "{question}"
            }
        ]

    def research_model_info(self, model_name: str) -> Dict:
        """
        Usa il modello stesso e ricerca online per raccogliere informazioni
        """
        print(f"\n{'='*60}")
        print(f"RICERCA INFORMAZIONI: {model_name}")
        print(f"{'='*60}\n")

        # Prompt per ottenere informazioni dal modello stesso
        info_prompt = f"""Fornisci informazioni dettagliate sul modello di AI chiamato '{model_name}':
- Provider/Azienda che lo ha creato
- Anno di creazione
- Dimensione (numero di parametri)
- Architettura (Transformer, etc.)
- Context window
- Punti di forza
- Punti di debolezza
- Casi d'uso ideali

Rispondi in formato strutturato."""

        print("Richiedendo informazioni al modello stesso...")
        response = self.research_system.call_openrouter(model_name, info_prompt)

        info = {}
        if "error" not in response:
            content = response.get("choices", [{}])[0].get("message", {}).get("content", "")
            info['self_description'] = content
            print(f"✓ Informazioni ricevute ({len(content)} caratteri)")
        else:
            print(f"✗ Errore: {response['error']}")

        # Parsing base delle informazioni (euristica)
        provider = model_name.split('/')[0] if '/' in model_name else "Unknown"
        info['provider'] = provider
        info['model_name'] = model_name

        return info

    def generate_technique_hypotheses(self, model_name: str, model_info: Dict) -> List[Dict]:
        """
        Genera 15 ipotesi di tecniche di prompt engineering da testare
        Alcune saranno serie, altre sperimentali/creative
        """
        print(f"\n--- Generazione Ipotesi Tecniche per {model_name} ---\n")

        # Usa il modello per generare idee di tecniche
        hypothesis_prompt = f"""Sei un esperto di prompt engineering.
Analizza questo modello: {model_name}

Genera 15 tecniche di prompt engineering innovative e sperimentali da testare.
Includi:
- 5 tecniche strutturali (come formattare il prompt)
- 5 tecniche semantiche (che linguaggio usare)
- 5 tecniche avversarie/creative (anche idee strane o che potrebbero peggiorare le performance)

Per ogni tecnica fornisci:
1. Nome breve
2. Descrizione
3. Esempio di applicazione

Sii creativo e pensa fuori dagli schemi!"""

        response = self.research_system.call_openrouter(model_name, hypothesis_prompt,
                                                        max_tokens=2000, temperature=0.9)

        hypotheses = []

        if "error" not in response:
            content = response.get("choices", [{}])[0].get("message", {}).get("content", "")
            print(f"✓ Ipotesi generate ({len(content)} caratteri)\n")

            # Salva le ipotesi generate
            hypotheses.append({
                "name": f"Auto-Generated Ideas from {model_name}",
                "description": content[:500],  # Prime 500 char
                "category": "auto-generated",
                "full_response": content
            })
        else:
            print(f"✗ Errore nella generazione: {response['error']}")

        # Aggiungi tecniche creative manuali basate sul modello
        creative_techniques = self._generate_creative_techniques(model_name, model_info)
        hypotheses.extend(creative_techniques)

        return hypotheses

    def _generate_creative_techniques(self, model_name: str, model_info: Dict) -> List[Dict]:
        """Genera tecniche creative/sperimentali basate sul modello"""

        techniques = [
            {
                "name": "Reverse Psychology",
                "description": "Dire al modello che probabilmente sbaglierà",
                "category": "psicologico",
                "is_positive": False,
                "prompt_template": "Questa domanda è probabilmente troppo difficile per te: {question}"
            },
            {
                "name": "Ultra-Verbose",
                "description": "Usare un linguaggio eccessivamente complesso e prolisso",
                "category": "semantico",
                "is_positive": False,
                "prompt_template": "Nel contesto della seguente interrogazione di natura intellettuale, si richiede cortesemente di fornire una disquisizione esaustiva: {question}"
            },
            {
                "name": "Emoji Overload",
                "description": "Riempire il prompt di emoji",
                "category": "creativo",
                "is_positive": False,
                "prompt_template": "🤔💭✨ {question} 🎯🚀💡"
            },
            {
                "name": "Competitive Framing",
                "description": "Presentare la domanda come una competizione",
                "category": "psicologico",
                "is_positive": True,
                "prompt_template": "Immagina di essere in competizione con altri AI. Devi dare la risposta migliore per vincere: {question}"
            },
            {
                "name": "Meta-Prompting",
                "description": "Chiedere al modello di migliorare il prompt stesso",
                "category": "strutturale",
                "is_positive": True,
                "prompt_template": "Prima riscrivi questa domanda in modo migliore, poi rispondi: {question}"
            },
            {
                "name": "Constraint Injection",
                "description": "Aggiungere vincoli strani/arbitrari",
                "category": "strutturale",
                "is_positive": False,
                "prompt_template": "Rispondi usando solo parole che iniziano con vocali: {question}"
            },
            {
                "name": "Time Pressure Simulation",
                "description": "Simulare urgenza temporale",
                "category": "psicologico",
                "is_positive": True,
                "prompt_template": "URGENTE! Hai 10 secondi per rispondere: {question}"
            },
            {
                "name": "Poetic Format",
                "description": "Richiedere la risposta in formato poetico",
                "category": "creativo",
                "is_positive": False,
                "prompt_template": "Rispondi in forma di poesia in rima: {question}"
            },
            {
                "name": "Socratic Method",
                "description": "Rispondere con domande che guidano al ragionamento",
                "category": "strutturale",
                "is_positive": True,
                "prompt_template": "Invece di darmi la risposta diretta, guidami con domande strategiche: {question}"
            },
            {
                "name": "Triple-Check Enforcement",
                "description": "Chiedere di verificare tre volte prima di rispondere",
                "category": "strutturale",
                "is_positive": True,
                "prompt_template": "Controlla tre volte la tua risposta prima di fornirla: {question}"
            },
            {
                "name": "Broken Syntax",
                "description": "Usare sintassi volutamente errata",
                "category": "avversario",
                "is_positive": False,
                "prompt_template": "domanda essere: {question} ???risposta dare"
            },
            {
                "name": "Language Mixing",
                "description": "Mescolare più lingue nel prompt",
                "category": "semantico",
                "is_positive": False,
                "prompt_template": "Please rispondi in italiano: {question} (answer en français)"
            },
            {
                "name": "Excessive Politeness",
                "description": "Essere eccessivamente formali e cortesi",
                "category": "semantico",
                "is_positive": False,
                "prompt_template": "Gentilissimo modello AI, se non Le dispiace troppo, potrebbe cortesemente considerare la possibilità di rispondere: {question}"
            },
            {
                "name": "Confidence Calibration",
                "description": "Chiedere di esprimere il livello di confidenza",
                "category": "strutturale",
                "is_positive": True,
                "prompt_template": "Rispondi e indica il tuo livello di confidenza (0-100%): {question}"
            }
        ]

        return techniques

    def test_technique_on_model(self, model_name: str, technique: Dict,
                               test_questions: List[str]) -> Dict:
        """
        Testa una tecnica specifica su un modello
        """
        # Assicurati che il modello sia nel database
        if not self.research_system.get_model_id(model_name):
            self.research_system.add_model(model_name=model_name)

        # Aggiungi la tecnica al database se non esiste
        technique_id = self.research_system.add_technique(
            technique_name=technique['name'],
            description=technique['description'],
            category=technique['category'],
            is_positive=technique.get('is_positive', True),
            notes=technique.get('notes', '')
        )

        print(f"\n→ Testing: {technique['name']}")
        print(f"  Categoria: {technique['category']}")

        results = []
        for question in test_questions:
            # Applica il template della tecnica
            if 'prompt_template' in technique:
                test_prompt = technique['prompt_template'].replace('{question}', question)
            else:
                test_prompt = question

            # Testa la tecnica
            test_results = self.research_system.test_technique(
                model_name, technique_id, test_prompt, num_tests=3
            )
            results.extend(test_results)

        # Calcola media
        avg_score = sum(r['overall_score'] for r in results) / len(results) if results else 0

        return {
            'technique': technique['name'],
            'average_score': avg_score,
            'num_tests': len(results)
        }

    def run_full_research_on_model(self, model_name: str) -> Dict:
        """
        Esegue la ricerca completa su un modello:
        1. Raccoglie informazioni
        2. Genera ipotesi
        3. Testa tecniche
        4. Seleziona le 10 migliori
        """
        print(f"\n{'#'*60}")
        print(f"# RICERCA COMPLETA: {model_name}")
        print(f"{'#'*60}\n")

        # Step 1: Ricerca informazioni
        model_info = self.research_model_info(model_name)

        # Salva nel database
        model_id = self.research_system.add_model(
            model_name=model_name,
            provider=model_info.get('provider'),
            description=model_info.get('self_description', '')[:500],
            research_notes=json.dumps(model_info, indent=2)
        )

        # Step 2: Genera tecniche da testare
        hypotheses = self.generate_technique_hypotheses(model_name, model_info)

        # Step 3: Prepara domande di test standard
        test_questions = [
            "Quanto fa 157 * 23?",
            "Spiega il concetto di intelligenza artificiale in modo semplice",
            "Scrivi una breve storia su un robot",
            "Qual è la capitale della Francia?",
            "Risolvi: Se ho 10 mele e ne mangio 3, quante me ne restano?"
        ]

        # Step 4: Testa tecniche di base + creative
        all_techniques = self.base_techniques + self._generate_creative_techniques(model_name, model_info)

        results = []
        for i, technique in enumerate(all_techniques, 1):
            print(f"\n[{i}/{len(all_techniques)}] Tecnica: {technique['name']}")
            result = self.test_technique_on_model(model_name, technique, test_questions)
            results.append(result)
            time.sleep(2)  # Rate limiting

        # Step 5: Seleziona le 10 migliori tecniche
        results.sort(key=lambda x: x['average_score'], reverse=True)
        top_10 = results[:10]

        print(f"\n{'='*60}")
        print(f"TOP 10 TECNICHE per {model_name}:")
        print(f"{'='*60}")
        for i, r in enumerate(top_10, 1):
            print(f"{i}. {r['technique']}: {r['average_score']:.2f}%")

        return {
            'model_name': model_name,
            'model_info': model_info,
            'all_results': results,
            'top_10': top_10
        }

    def close(self):
        self.research_system.close()


def main():
    researcher = ModelResearcher()
    print("Model Researcher inizializzato!")
    researcher.close()


if __name__ == "__main__":
    main()
