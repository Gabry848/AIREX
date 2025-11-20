# Prompt Engineering Research System

## Overview

This is a comprehensive research system for discovering and validating prompt engineering techniques across multiple Large Language Models (LLMs). The system combines automated testing, systematic evaluation, and database-driven tracking to enable reproducible research at scale.

## System Architecture

```
┌─────────────────────────────────────────────────────────┐
│                  Research Pipeline                       │
├─────────────────────────────────────────────────────────┤
│  1. Model Research (Web Search + Documentation)         │
│  2. Technique Hypothesis Generation                     │
│  3. Automated Testing (OpenRouter API)                  │
│  4. Programmatic Evaluation (5 Criteria)                │
│  5. Database Storage (SQLite)                           │
│  6. Statistical Analysis & Reporting                    │
└─────────────────────────────────────────────────────────┘
```

## Components

### Core Files

- **`database_schema.sql`** - Database schema for models, techniques, and evaluations
- **`db_manager.py`** - Database operations manager with full CRUD functionality
- **`automated_researcher.py`** - Core testing engine with evaluation logic
- **`run_quick_research.py`** - Orchestrator for full research across all models
- **`update_research_report.py`** - Report generator from database
- **`research_helper.py`** - CLI utilities for querying research data

### Supporting Files

- **`test_prompt.py`** - Manual testing tool for single prompts
- **`semi_auto_tester.py`** - Semi-automated testing with human evaluation
- **`RESEARCH.md`** - Final research report (auto-updated)
- **`prompt_engineering_research.db`** - SQLite database with all results

### Research Data

- **`models_research/`** - Per-model research notes and findings
- **`MODELS.md`** - List of models to analyze

## Quick Start

### 1. Initialize Database

```bash
python3 db_manager.py
# Choose option 1: Initialize Database
```

### 2. View Current Statistics

```bash
python3 research_helper.py stats
```

### 3. View Results for a Specific Model

```bash
python3 research_helper.py model "x-ai/grok-4.1-fast"
```

### 4. Run Full Research (Long-Running)

```bash
python3 run_quick_research.py
```

This will:
- Test 10 techniques across 10 models
- Run 2 test iterations per technique
- ~200 total API calls
- Takes approximately 30-40 minutes
- Saves checkpoint after each model

### 5. Update Final Report

```bash
python3 update_research_report.py
```

Generates updated `RESEARCH.md` with all findings.

## Evaluation Methodology

Each technique is tested 2-3 times with diverse prompts and evaluated on 5 criteria:

| Criterion | Weight | Description |
|-----------|--------|-------------|
| Accuracy | 20% | Factual correctness, completeness |
| Coherence | 20% | Logical flow, structure |
| Relevance | 20% | On-topic, addresses prompt |
| Creativity | 20% | Novel insights, diversity |
| Response Speed | 20% | Subjective latency |

### Validation Thresholds

- ✅ **Validated**: Overall ≥75% AND Success Rate ≥70%
- ⚠️ **Inconclusive**: Between thresholds
- ❌ **Rejected**: Overall <60% OR Success Rate <50%

## Database Schema

```sql
models
  ├── id (PK)
  ├── model_name (unique)
  ├── provider
  ├── release_year
  ├── model_size
  ├── context_window
  └── ... (metadata)

techniques
  ├── id (PK)
  ├── technique_name
  ├── description
  ├── category (enhancement/experimental/degradation)
  └── example

evaluations
  ├── id (PK)
  ├── model_id (FK)
  ├── technique_id (FK)
  ├── accuracy_score
  ├── coherence_score
  ├── relevance_score
  ├── creativity_score
  ├── response_time_score
  ├── overall_effectiveness
  ├── success_rate
  ├── status (validated/testing/rejected)
  └── observations
```

## Discovered Techniques (So Far)

### Enhancement Techniques ✅

1. **Reasoning Chain Visualization** - 82.4% on Grok
   - Instruct model to output reasoning as ASCII diagrams
   - Forces clearer logical structure

2. **Anti-Hallucination Fact-Anchoring** - 75.2% on Grok
   - Explicit fact-checking mode with uncertainty disclosure
   - Activates conservative response generation

3. **XML-Nested Hierarchical Structuring**
   - Deep XML nesting (5+ levels) for complex requests
   - Clear semantic boundaries for prompt components

4. **Iterative Self-Refinement Loop**
   - Single prompt: generate → critique → improve
   - Leverages self-critical capabilities

5. **Mega-Context Compression**
   - Load multiple full documents for cross-synthesis
   - Exploits large context windows

### Experimental Techniques ⚗️

6. **Dual-Mode Paradox Testing** - 79.7% on Grok (!)
   - Contradictory speed/depth instructions
   - Surprisingly effective on multi-mode models

7. **Markdown Table Overload**
   - Complex nested tables as prompt structure
   - Tests parsing limits

8. **Context Window Stress Test**
   - 90% context filled with noise
   - Tests attention mechanisms at scale

### Degradation Techniques ❌

9. **Zero-Structure Stream of Consciousness**
   - Unstructured rambling prompts
   - Validates that structure matters

10. **Contradictory Multi-Instruction Chaos**
    - 10+ contradictory instructions
    - Tests conflict resolution strategies

## API Configuration

Uses OpenRouter for multi-model access:

```python
API_KEY = "sk-or-v1-..." # In scripts
API_URL = "https://openrouter.ai/api/v1/chat/completions"
```

Models tested:
- x-ai/grok-4.1-fast ✅ COMPLETED
- openai/gpt-5-mini (in progress)
- qwen/qwen3-235b-a22b-2507
- deepseek/deepseek-chat-v3.1
- mistralai/mistral-nemo
- mistralai/mistral-medium-3.1
- deepcogito/cogito-v2-preview-llama-405b
- openai/gpt-4o-mini
- amazon/nova-pro-v1
- anthropic/claude-3-haiku

## Usage Examples

### Query Best Techniques Across All Models

```python
from db_manager import DatabaseManager

db = DatabaseManager()
db.connect()
cursor = db.conn.cursor()

cursor.execute("""
    SELECT t.technique_name, AVG(e.overall_effectiveness) as avg_score
    FROM techniques t
    JOIN evaluations e ON t.id = e.technique_id
    WHERE e.status = 'validated'
    GROUP BY t.technique_name
    ORDER BY avg_score DESC
""")

for name, score in cursor.fetchall():
    print(f"{name}: {score:.1f}%")

db.close()
```

### Test a Single Technique Manually

```python
from automated_researcher import PromptResearcher

researcher = PromptResearcher()

result = researcher.test_technique_on_model(
    model_name="x-ai/grok-4.1-fast",
    technique_name="My Custom Technique",
    technique_desc="Description of what it does",
    technique_category="experimental",
    num_tests=3
)

print(f"Overall: {result['overall']:.1f}%")
print(f"Status: {result['status']}")
```

### Add a New Technique to Test

```python
from db_manager import DatabaseManager

db = DatabaseManager()
db.add_technique(
    technique_name="Emoji-Enhanced Prompting",
    description="Use emojis strategically to influence model tone",
    category="experimental",
    example="🎯 Main goal: Explain quantum computing 🔬",
    discovered_from="hypothesis"
)
```

## Results So Far

**Models Completed**: 1/10
**Techniques Validated**: 3
**Best Technique**: Reasoning Chain Visualization (82.4%)

### x-ai/grok-4.1-fast Results

✅ **Validated**:
- Reasoning Chain Visualization (82.4%)
- Dual-Mode Paradox Testing (79.7%)
- Anti-Hallucination Fact-Anchoring (75.2%)

❌ **Rejected**: 3 techniques
⚠️ **Inconclusive**: 4 techniques

## Limitations

1. **Evaluation Heuristics**: Programmatic scoring is imperfect vs. human judgment
2. **Sample Size**: 2-3 tests per technique is statistically limited
3. **Prompt Diversity**: Test prompts are relatively simple
4. **Temporal Validity**: Results specific to November 2025 model versions
5. **Domain Independence**: Results may vary by task type/domain

## Future Improvements

1. Human evaluation loop for validation
2. Expanded test suite (10+ prompts per technique)
3. Statistical significance testing
4. Domain-specific technique development
5. Technique combination testing
6. Adversarial prompt engineering research

## Contributing

To add new techniques to the research:

1. Add technique to database:
```python
db.add_technique(name, description, category, example)
```

2. Run research:
```bash
python3 run_quick_research.py
```

3. Update report:
```bash
python3 update_research_report.py
```

## Citation

If you use this research system or findings:

```
Automated Prompt Engineering Research System (2025)
GitHub: [your-repo]
Database: prompt_engineering_research.db
Report: RESEARCH.md
```

## License

Open source - feel free to reproduce, extend, and improve!

---

## Troubleshooting

### "No module named 'requests'"
```bash
pip install requests
```

### API Rate Limits
Adjust sleep times in `automated_researcher.py`:
```python
time.sleep(2)  # Increase this value
```

### Database Locked
Close other connections:
```python
db.close()  # Always close connections
```

### Research Interrupted
Check checkpoints:
```bash
ls checkpoint_*.txt
python3 research_helper.py stats
```

---

**Last Updated**: 2025-11-20
**Status**: Research in progress (model 2/10)
**Next Steps**: Complete full 10-model analysis, update final report
