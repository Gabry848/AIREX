# Sistema di Ricerca Avanzata su Prompt Engineering

Questo sistema esegue ricerca automatizzata per scoprire e testare tecniche di prompt engineering su vari modelli AI.

## Struttura del Progetto

```
AIREX/
├── MODELS.md                      # Lista dei modelli da analizzare
├── database_schema.sql            # Schema del database SQLite
├── prompt_research.py             # Sistema base di ricerca e testing
├── model_researcher.py            # Logica di ricerca per modello
├── run_complete_research.py       # Script principale orchestrazione
├── view_results.py                # Visualizzatore risultati
├── prompt_engineering_research.db # Database SQLite (generato)
├── research_results.json          # Export JSON risultati (generato)
└── RESEARCH.md                    # Report finale (generato)
```

## Componenti Principali

### 1. Database SQLite (`prompt_engineering_research.db`)

Contiene 4 tabelle principali:
- **models**: Informazioni sui modelli AI
- **prompt_techniques**: Catalogo delle tecniche
- **technique_tests**: Risultati dei test
- **technique_hypotheses**: Ipotesi da validare

### 2. Sistema di Valutazione

Ogni risposta viene valutata con 5 criteri (0-100%):
- **Coherence**: Coerenza e struttura logica
- **Relevance**: Pertinenza alla domanda
- **Completeness**: Completezza della risposta
- **Accuracy**: Accuratezza delle informazioni
- **Creativity**: Originalità e creatività

### 3. Tecniche Testate

Il sistema testa ~20 tecniche per modello, tra cui:

**Tecniche Strutturali:**
- Chain-of-Thought (CoT)
- Few-Shot Learning
- Meta-Prompting
- Triple-Check Enforcement

**Tecniche Semantiche:**
- Role Playing
- Ultra-Verbose
- Excessive Politeness

**Tecniche Psicologiche:**
- Competitive Framing
- Time Pressure Simulation
- Reverse Psychology

**Tecniche Avversarie:**
- Emoji Overload
- Broken Syntax
- Language Mixing
- Constraint Injection

## Workflow di Ricerca

Per ogni modello in `MODELS.md`:

1. **Ricerca Informazioni**
   - Query al modello stesso per auto-descrizione
   - Estrazione metadati (provider, anno, dimensione, etc.)

2. **Generazione Ipotesi**
   - Uso del modello per generare idee di tecniche
   - Aggiunta di tecniche creative/sperimentali

3. **Testing Sistematico**
   - Ogni tecnica testata 3 volte
   - Su 5 domande standard diverse
   - Valutazione multi-criterio automatica

4. **Selezione Top 10**
   - Ordinamento per performance media
   - Identificazione delle 10 migliori tecniche

5. **Salvataggio**
   - Tutti i dati salvati nel database SQLite
   - Risultati intermedi in JSON

## Come Usare

### Esecuzione Completa

```bash
# Esegui la ricerca su tutti i modelli
python3 run_complete_research.py
```

Questo processo può richiedere diverse ore (dipende dal numero di modelli e dalla velocità dell'API).

### Visualizzare Risultati Parziali

```bash
# Mostra statistiche e top tecniche
python3 view_results.py
```

### Testing Singolo Modello

```python
from model_researcher import ModelResearcher

researcher = ModelResearcher()
result = researcher.run_full_research_on_model("openai/gpt-4o-mini")
researcher.close()
```

### Query Personalizzate sul Database

```python
from prompt_research import PromptResearchSystem

research = PromptResearchSystem()

# Ottieni statistiche per un modello
stats = research.get_technique_stats("openai/gpt-4o-mini")

# Esporta risultati
research.export_results()

research.close()
```

## Output Generati

### Durante l'Esecuzione

- `results_<model_name>.json`: Risultati per singolo modello
- Log dettagliati in console

### Al Completamento

- **`RESEARCH.md`**: Report finale con analisi e considerazioni
- **`prompt_engineering_research.db`**: Database completo
- **`research_results.json`**: Export JSON di tutti i dati

## Estensioni Possibili

1. **Nuove Tecniche**: Aggiungi tecniche in `model_researcher.py` → `_generate_creative_techniques()`
2. **Nuovi Criteri**: Modifica `evaluate_response()` in `prompt_research.py`
3. **Nuove Domande**: Modifica `test_questions` in `model_researcher.py`
4. **Nuovi Modelli**: Aggiungi alla lista in `MODELS.md`

## Configurazione API

La chiave API OpenRouter è configurata in `prompt_research.py`:

```python
OPENROUTER_API_KEY = "sk-or-v1-..."
```

## Note Importanti

- **Rate Limiting**: Gli script includono pause (2-10 secondi) tra richieste
- **Costi**: Ogni modello richiede ~100-150 chiamate API
- **Tempo**: Stima ~30-60 minuti per modello
- **Robustezza**: Gli script gestiscono errori e continuano con il prossimo test

## Troubleshooting

### Database non trovato
```bash
python3 -c "from prompt_research import PromptResearchSystem; PromptResearchSystem()"
```

### Errori API
- Verifica la chiave API
- Controlla i limiti di rate
- Verifica che il modello sia disponibile su OpenRouter

### Visualizzazione
```bash
# Installa dipendenze opzionali
pip install tabulate
```

## Licenza e Uso

Questo sistema è per scopi di ricerca e sperimentazione. I risultati possono variare e dipendono dalla disponibilità e versione dei modelli su OpenRouter.

---

**Buona ricerca! 🚀**
