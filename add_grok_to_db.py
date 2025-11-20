#!/usr/bin/env python3
"""Add Grok 4.1 Fast to database"""

from db_manager import DatabaseManager

db = DatabaseManager()

# Add model
model_id = db.add_model(
    model_name="x-ai/grok-4.1-fast",
    provider="xAI",
    release_year=2025,
    model_size="~314B parameters",
    architecture="Unified reasoning/non-reasoning architecture",
    context_window=2000000,  # 2M tokens
    description="Fast variant of Grok 4.1 with 4x speed, 1/10th cost, 2M context window, and 3x lower hallucination rate",
    strengths="Massive context, fast iteration, low cost, reasoning transparency, low hallucination rate, agentic capabilities",
    weaknesses="Limited real-world testing, potential X/Twitter bias, less documentation than competitors",
    research_notes="Ranked #1 on LMArena. Two modes: reasoning (CoT) and non-reasoning. Trained with RL for tool use."
)

print(f"Model added with ID: {model_id}")
