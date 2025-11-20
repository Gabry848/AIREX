AIREX is an open-source autonomous research and experimentation engine designed to discover, analyze, and validate prompt-engineering techniques across multiple LLMs.

The system:
- reads a curated list of 50+ models from OpenRouter
- extracts prompt-engineering techniques from documentation, examples, and behavioral patterns
- generates new techniques using logical inference or controlled randomization
- tests every technique using real API calls (OpenRouter)
- evaluates performance through automatic scoring and A/B comparisons
- stores all experiments, techniques, and results into a structured Railway PostgreSQL database

The agent runs in a continuous loop for hours or days, autonomously discovering high-performance prompting strategies and building a growing knowledge base.  
Its goal is to map the “prompt engineering landscape” across models and generate new, experimentally-validated techniques.

This project aims to push forward autonomous AI research and help developers, researchers, and model builders understand how prompting strategies affect model behavior.
