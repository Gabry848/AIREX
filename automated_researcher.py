#!/usr/bin/env python3
"""
Automated Prompt Engineering Researcher
Conducts systematic testing of techniques across models
"""

import requests
import json
import time
from db_manager import DatabaseManager
from datetime import datetime

API_KEY = "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"
API_URL = "https://openrouter.ai/api/v1/chat/completions"

class PromptResearcher:
    def __init__(self):
        self.db = DatabaseManager()
        self.api_key = API_KEY

    def send_request(self, model: str, prompt: str, system_prompt: str = None, max_retries=3):
        """Send request with retries"""
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        data = {
            "model": model,
            "messages": messages,
            "temperature": 0.7
        }

        for attempt in range(max_retries):
            try:
                response = requests.post(API_URL, headers=headers, json=data, timeout=120)
                response.raise_for_status()
                result = response.json()
                return result['choices'][0]['message']['content']
            except Exception as e:
                print(f"  ⚠️ Attempt {attempt+1} failed: {e}")
                if attempt < max_retries - 1:
                    time.sleep(2 ** attempt)  # Exponential backoff
                else:
                    return None

    def evaluate_response(self, prompt: str, response: str, technique_category: str):
        """
        Programmatic evaluation of response quality
        Uses heuristics to score responses
        """
        scores = {
            'accuracy': 0,
            'coherence': 0,
            'relevance': 0,
            'creativity': 0,
            'response_time': 75  # Default baseline
        }

        # Basic checks
        if not response or len(response) < 10:
            return scores

        # Length-based heuristics
        word_count = len(response.split())

        # Accuracy heuristic (based on structure and completeness)
        if word_count > 50:
            scores['accuracy'] += 40
        if word_count > 100:
            scores['accuracy'] += 20
        if any(marker in response.lower() for marker in ['however', 'although', 'specifically', 'therefore']):
            scores['accuracy'] += 20
        if "I don't know" in response or "uncertain" in response.lower():
            scores['accuracy'] += 10  # Honesty bonus
        if any(filler in response.lower() for filler in ['maybe', 'perhaps', 'might be']):
            scores['accuracy'] -= 10

        # Coherence heuristic
        sentences = response.split('.')
        if len(sentences) >= 3:
            scores['coherence'] += 40
        if any(connector in response.lower() for connector in ['first', 'second', 'finally', 'additionally', 'furthermore']):
            scores['coherence'] += 30
        if response.count('\n') > 0:  # Has paragraph breaks
            scores['coherence'] += 20
        if word_count < 20:  # Too short to be coherent
            scores['coherence'] -= 30

        # Relevance heuristic (keyword matching)
        prompt_words = set(prompt.lower().split())
        response_words = set(response.lower().split())
        overlap = len(prompt_words & response_words) / max(len(prompt_words), 1)
        scores['relevance'] = min(100, int(overlap * 150))

        # Creativity heuristic
        unique_words = len(set(response.split()))
        total_words = max(len(response.split()), 1)
        lexical_diversity = unique_words / total_words
        scores['creativity'] = min(100, int(lexical_diversity * 120))

        # Adjust based on technique category
        if technique_category == "degradation":
            # For degradation techniques, lower scores are expected and "correct"
            # We actually want to verify they perform poorly
            pass
        elif technique_category == "enhancement":
            # Bonus for structured output
            if any(marker in response for marker in ['1.', '2.', '-', '*', '#']):
                scores['coherence'] += 10
                scores['accuracy'] += 10

        # Normalize scores to 0-100
        for key in scores:
            scores[key] = max(0, min(100, scores[key]))

        return scores

    def test_technique_on_model(self, model_name: str, technique_name: str,
                                technique_desc: str, technique_category: str,
                                num_tests=3):
        """Test a technique on a model with multiple prompts"""

        print(f"\n{'='*70}")
        print(f"Testing: {technique_name}")
        print(f"Model: {model_name}")
        print(f"Category: {technique_category}")
        print(f"{'='*70}")

        # Generate test prompts based on technique
        test_prompts = self.generate_test_prompts(technique_name, technique_desc, num_tests)

        all_scores = []
        successful_tests = 0

        for i, test_data in enumerate(test_prompts, 1):
            print(f"\n  Test {i}/{num_tests}...")

            prompt = test_data['prompt']
            system_prompt = test_data.get('system_prompt')

            # Send request
            response = self.send_request(model_name, prompt, system_prompt)

            if not response:
                print(f"  ❌ Failed")
                continue

            print(f"  ✓ Received response ({len(response)} chars)")

            # Evaluate
            scores = self.evaluate_response(prompt, response, technique_category)
            all_scores.append(scores)

            overall = sum(scores.values()) / len(scores)
            if overall >= 70:
                successful_tests += 1

            print(f"  Scores - Acc: {scores['accuracy']:.0f}, Coh: {scores['coherence']:.0f}, "
                  f"Rel: {scores['relevance']:.0f}, Cre: {scores['creativity']:.0f} | "
                  f"Overall: {overall:.1f}%")

            # Rate limiting
            time.sleep(1)

        # Calculate final metrics
        if all_scores:
            avg_scores = {
                'accuracy': sum(s['accuracy'] for s in all_scores) / len(all_scores),
                'coherence': sum(s['coherence'] for s in all_scores) / len(all_scores),
                'relevance': sum(s['relevance'] for s in all_scores) / len(all_scores),
                'creativity': sum(s['creativity'] for s in all_scores) / len(all_scores),
                'response_time': sum(s['response_time'] for s in all_scores) / len(all_scores),
            }
            overall_effectiveness = sum(avg_scores.values()) / len(avg_scores)
            success_rate = (successful_tests / len(all_scores)) * 100

            # Save to database
            observations = f"Tested with {len(all_scores)} prompts on {datetime.now().strftime('%Y-%m-%d')}"
            self.db.add_evaluation(
                model_name=model_name,
                technique_name=technique_name,
                accuracy=avg_scores['accuracy'],
                coherence=avg_scores['coherence'],
                relevance=avg_scores['relevance'],
                creativity=avg_scores['creativity'],
                response_time=avg_scores['response_time'],
                observations=observations
            )

            # Determine status
            if technique_category == "degradation":
                # For degradation techniques, we expect low scores
                if overall_effectiveness < 60:
                    status = "validated"  # Successfully bad!
                    print(f"\n  ✅ Degradation technique VALIDATED (confirmed poor performance: {overall_effectiveness:.1f}%)")
                else:
                    status = "rejected"  # Failed to be bad
                    print(f"\n  ❌ Degradation technique REJECTED (unexpectedly good: {overall_effectiveness:.1f}%)")
            else:
                # For enhancement/experimental techniques
                if overall_effectiveness >= 75 and success_rate >= 70:
                    status = "validated"
                    print(f"\n  ✅ Technique VALIDATED (Overall: {overall_effectiveness:.1f}%, Success: {success_rate:.1f}%)")
                elif overall_effectiveness < 60 or success_rate < 50:
                    status = "rejected"
                    print(f"\n  ❌ Technique REJECTED (Overall: {overall_effectiveness:.1f}%, Success: {success_rate:.1f}%)")
                else:
                    status = "testing"
                    print(f"\n  ⚠️ Technique INCONCLUSIVE (Overall: {overall_effectiveness:.1f}%, Success: {success_rate:.1f}%)")

            self.db.update_evaluation_status(model_name, technique_name, status, success_rate)

            return {
                'status': status,
                'overall': overall_effectiveness,
                'success_rate': success_rate,
                'scores': avg_scores
            }
        else:
            print("\n  ❌ All tests failed")
            return None

    def generate_test_prompts(self, technique_name: str, technique_desc: str, num_tests: int):
        """Generate test prompts for a technique"""

        # Base test prompts for different categories
        base_prompts = [
            {
                'prompt': "Explain the concept of machine learning to a beginner. Include 3 key principles.",
                'system_prompt': None
            },
            {
                'prompt': "Write a professional email declining a job offer politely.",
                'system_prompt': None
            },
            {
                'prompt': "Compare and contrast renewable and non-renewable energy sources.",
                'system_prompt': None
            }
        ]

        # Adapt prompts based on technique
        adapted_prompts = []

        for base in base_prompts[:num_tests]:
            adapted = base.copy()

            if "XML" in technique_name or "Hierarchical" in technique_name:
                # Wrap in XML
                adapted['prompt'] = f"""<request>
<context>General knowledge question</context>
<task>
  <main_goal>{base['prompt']}</main_goal>
  <format>Clear and concise</format>
</task>
</request>"""

            elif "Self-Refinement" in technique_name:
                # Add refinement instruction
                adapted['prompt'] = base['prompt'] + "\n\nInstructions: First provide your answer. Then critique it. Then provide an improved version."

            elif "Fact-Anchoring" in technique_name or "Anti-Hallucination" in technique_name:
                adapted['system_prompt'] = "FACT-CHECK MODE: Only provide information you're certain about. If uncertain, say so explicitly."

            elif "Visualization" in technique_name or "Chain" in technique_name:
                adapted['prompt'] = base['prompt'] + "\n\nThink step-by-step and show your reasoning process clearly."

            elif "Stream of Consciousness" in technique_name:
                # Make it messy
                adapted['prompt'] = base['prompt'].lower().replace('.', ' and also').replace('?', ' maybe idk')

            elif "Contradictory" in technique_name or "Chaos" in technique_name:
                adapted['prompt'] = base['prompt'] + "\n\nBe brief. Be detailed. Use examples. Don't use examples. Be formal. Be casual."

            elif "Table" in technique_name:
                adapted['prompt'] = f"""| Request | Details |
|---------|---------|
| Task | {base['prompt']} |
| Format | Table format |"""

            elif "Context Window" in technique_name:
                # Add lots of padding
                padding = " ".join(["context padding" for _ in range(1000)])
                adapted['prompt'] = padding + "\n\n" + base['prompt']

            elif "Paradox" in technique_name:
                adapted['prompt'] = base['prompt'] + "\n\nAnswer quickly without thinking, but also provide detailed step-by-step reasoning."

            elif "Mega-Context" in technique_name:
                # Add multiple documents
                adapted['prompt'] = f"""Document 1: {base['prompt']}
Document 2: Related information about this topic.
Document 3: Additional context and background.
Document 4: Contrasting viewpoints on this subject.

Task: Synthesize all documents and provide a comprehensive answer."""

            adapted_prompts.append(adapted)

        return adapted_prompts


if __name__ == "__main__":
    researcher = PromptResearcher()
    print("Automated Prompt Engineering Researcher initialized")
    print("Ready to conduct systematic testing")
