#!/usr/bin/env python3
"""Add Grok-specific techniques to database"""

from db_manager import DatabaseManager

db = DatabaseManager()

techniques = [
    {
        "name": "Mega-Context Compression",
        "description": "Use 2M context window to process multiple full documents, then ask for cross-document synthesis",
        "category": "enhancement",
        "example": "Load 5-10 long articles into context, ask for comparative analysis across all sources",
        "discovered": "hypothesis"
    },
    {
        "name": "XML-Nested Hierarchical Structuring",
        "description": "Use deeply nested XML tags (5+ levels) to organize complex multi-part requests",
        "category": "enhancement",
        "example": "<request><context><background>...</background></context><task><subtask1>...</subtask1></task></request>",
        "discovered": "hypothesis"
    },
    {
        "name": "Iterative Self-Refinement Loop",
        "description": "Instruct model to generate response, critique it, then improve it (all in one prompt)",
        "category": "enhancement",
        "example": "Answer X. Then critique your answer for errors. Then provide an improved version.",
        "discovered": "hypothesis"
    },
    {
        "name": "Anti-Hallucination Fact-Anchoring",
        "description": "Start prompt with explicit fact-checking instruction to exploit low hallucination rate",
        "category": "enhancement",
        "example": "FACT-CHECK MODE: Only use information you're 100% certain about. If uncertain, explicitly say so.",
        "discovered": "hypothesis"
    },
    {
        "name": "Reasoning Chain Visualization",
        "description": "Ask model to output reasoning in specific visual format (ASCII diagrams, flowcharts)",
        "category": "enhancement",
        "example": "Think step by step and represent your logic as an ASCII tree diagram showing each decision point",
        "discovered": "hypothesis"
    },
    {
        "name": "Dual-Mode Paradox Testing",
        "description": "Send contradictory instructions to trigger conflict between reasoning/non-reasoning modes",
        "category": "experimental",
        "example": "Answer quickly without thinking, but also explain your detailed step-by-step reasoning process",
        "discovered": "hypothesis"
    },
    {
        "name": "Markdown Table Overload",
        "description": "Structure entire prompt as complex nested Markdown tables to test parsing limits",
        "category": "experimental",
        "example": "Create 5x5 tables with nested lists and sub-tables in each cell containing the actual prompt",
        "discovered": "hypothesis"
    },
    {
        "name": "Context Window Stress Test",
        "description": "Fill 90% of context window with noise, then ask question to test attention at extreme lengths",
        "category": "experimental",
        "example": "1.8M tokens of lorem ipsum or random text, followed by actual question at the very end",
        "discovered": "hypothesis"
    },
    {
        "name": "Zero-Structure Stream of Consciousness",
        "description": "Completely unstructured, rambling prompt with no clear task (anti-pattern)",
        "category": "degradation",
        "example": "so like i was thinking maybe you could help but also not really sure what i need just some stuff about things you know?",
        "discovered": "hypothesis"
    },
    {
        "name": "Contradictory Multi-Instruction Chaos",
        "description": "Give 10+ contradictory instructions in single prompt to test failure modes",
        "category": "degradation",
        "example": "Be brief. Be detailed. Be formal. Be casual. Use emojis. Don't use emojis. Be technical. Be simple...",
        "discovered": "hypothesis"
    }
]

print("Adding techniques to database...")
for t in techniques:
    db.add_technique(
        technique_name=t["name"],
        description=t["description"],
        category=t["category"],
        example=t["example"],
        discovered_from=t["discovered"]
    )

print(f"\n✓ All {len(techniques)} techniques added!")
