#!/usr/bin/env python3
"""
Integration test script for AIREX project.
This script performs a complete end-to-end test of all functionality.

Run this script in an environment with database access:
    export DATABASE_URL="postgresql://..."
    python test_integration.py
"""

import os
import sys
from datetime import datetime

# Color codes
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
RESET = '\033[0m'


def print_section(title):
    """Print section header."""
    print("\n" + "=" * 70)
    print(f"{BLUE}{title}{RESET}")
    print("=" * 70)


def print_success(message):
    """Print success message."""
    print(f"{GREEN}✓{RESET} {message}")


def print_error(message):
    """Print error message."""
    print(f"{RED}✗{RESET} {message}")


def print_info(message):
    """Print info message."""
    print(f"{BLUE}•{RESET} {message}")


def main():
    """Run integration tests."""
    print("\n" + "=" * 70)
    print(f"{BLUE}AIREX Integration Test Suite{RESET}")
    print("=" * 70)

    # Check DATABASE_URL
    if not os.getenv('DATABASE_URL'):
        print_error("DATABASE_URL environment variable not set!")
        print_info("Please set it with: export DATABASE_URL='postgresql://...'")
        return 1

    try:
        # Import modules
        print_section("Step 1: Importing Modules")
        import db
        from technique_manager import (
            add_model,
            add_technique,
            link_model_technique,
            log_experiment,
            update_technique_score,
            add_improvement
        )
        print_success("All modules imported successfully")

        # Test database connection
        print_section("Step 2: Testing Database Connection")
        if db.test_connection():
            print_success("Database connection successful!")
        else:
            print_error("Database connection failed!")
            return 1

        # Initialize database
        print_section("Step 3: Initializing Database Schema")
        print_info("Running schema.sql...")
        conn = db.get_connection()
        with open('schema.sql', 'r') as f:
            schema_sql = f.read()
        with conn.cursor() as cursor:
            cursor.execute(schema_sql)
            conn.commit()
        db.close_connection(conn)
        print_success("Database schema initialized successfully")

        # Test add_model
        print_section("Step 4: Testing add_model()")
        model_id_1 = add_model(
            name="GPT-4",
            source_url="https://openai.com/gpt-4",
            notes="OpenAI's flagship model"
        )
        print_success(f"Model 'GPT-4' added with ID: {model_id_1}")

        model_id_2 = add_model(
            name="Claude-3-Opus",
            source_url="https://anthropic.com/claude",
            notes="Anthropic's most capable model"
        )
        print_success(f"Model 'Claude-3-Opus' added with ID: {model_id_2}")

        # Test add_technique
        print_section("Step 5: Testing add_technique()")
        technique_id_1 = add_technique(
            name="Chain of Thought",
            description="Ask the model to think step by step before answering",
            origin_type="online"
        )
        print_success(f"Technique 'Chain of Thought' added with ID: {technique_id_1}")

        technique_id_2 = add_technique(
            name="Few-Shot Learning",
            description="Provide examples before asking the question",
            origin_type="online"
        )
        print_success(f"Technique 'Few-Shot Learning' added with ID: {technique_id_2}")

        technique_id_3 = add_technique(
            name="Self-Consistency",
            description="Generate multiple responses and choose the most common answer",
            origin_type="deduced"
        )
        print_success(f"Technique 'Self-Consistency' added with ID: {technique_id_3}")

        # Test link_model_technique
        print_section("Step 6: Testing link_model_technique()")
        link_id_1 = link_model_technique(
            model_id=model_id_1,
            technique_id=technique_id_1,
            score_for_this_model=9.2,
            works_for_model=True
        )
        print_success(f"Linked 'Chain of Thought' to 'GPT-4' with score 9.2")

        link_id_2 = link_model_technique(
            model_id=model_id_2,
            technique_id=technique_id_1,
            score_for_this_model=8.8,
            works_for_model=True
        )
        print_success(f"Linked 'Chain of Thought' to 'Claude-3-Opus' with score 8.8")

        link_id_3 = link_model_technique(
            model_id=model_id_1,
            technique_id=technique_id_2,
            score_for_this_model=8.5,
            works_for_model=True
        )
        print_success(f"Linked 'Few-Shot Learning' to 'GPT-4' with score 8.5")

        # Test log_experiment
        print_section("Step 7: Testing log_experiment()")
        experiment_id_1 = log_experiment(
            technique_id=technique_id_1,
            test_prompt="Solve this problem step by step: What is 15% of 240?",
            model_used="GPT-4",
            api_response_text="Let me think step by step: 1) 15% = 0.15, 2) 0.15 * 240 = 36",
            score=9.5,
            is_regression=False
        )
        print_success(f"Experiment logged with ID: {experiment_id_1}")

        experiment_id_2 = log_experiment(
            technique_id=technique_id_2,
            test_prompt="Translate to French: Hello, how are you?",
            model_used="GPT-4",
            api_response_text="Bonjour, comment allez-vous?",
            score=10.0,
            is_regression=False
        )
        print_success(f"Experiment logged with ID: {experiment_id_2}")

        # Test update_technique_score
        print_section("Step 8: Testing update_technique_score()")
        update_technique_score(
            technique_id=technique_id_1,
            effectiveness_score=9.0,
            reliability_score=8.7
        )
        print_success(f"Updated scores for technique {technique_id_1}")

        update_technique_score(
            technique_id=technique_id_2,
            effectiveness_score=8.5,
            reliability_score=9.2
        )
        print_success(f"Updated scores for technique {technique_id_2}")

        # Test add_improvement
        print_section("Step 9: Testing add_improvement()")
        improvement_id = add_improvement(
            technique_id=technique_id_3,
            parent_technique_id=technique_id_1,
            delta_score=0.5,
            notes="Self-Consistency builds upon Chain of Thought by generating multiple reasoning paths"
        )
        print_success(f"Improvement recorded with ID: {improvement_id}")

        # Verify data
        print_section("Step 10: Verifying Data in Database")
        conn = db.get_connection()
        with conn.cursor() as cursor:
            # Count models
            cursor.execute("SELECT COUNT(*) as count FROM models")
            model_count = cursor.fetchone()['count']
            print_success(f"Total models in database: {model_count}")

            # Count techniques
            cursor.execute("SELECT COUNT(*) as count FROM techniques")
            technique_count = cursor.fetchone()['count']
            print_success(f"Total techniques in database: {technique_count}")

            # Count experiments
            cursor.execute("SELECT COUNT(*) as count FROM experiments")
            experiment_count = cursor.fetchone()['count']
            print_success(f"Total experiments in database: {experiment_count}")

            # Count improvements
            cursor.execute("SELECT COUNT(*) as count FROM improvements")
            improvement_count = cursor.fetchone()['count']
            print_success(f"Total improvements in database: {improvement_count}")

            # Get latest technique with scores
            cursor.execute("""
                SELECT name, effectiveness_score, reliability_score
                FROM techniques
                WHERE effectiveness_score > 0
                ORDER BY updated_at DESC
                LIMIT 1
            """)
            latest = cursor.fetchone()
            if latest:
                print_success(
                    f"Latest technique: '{latest['name']}' "
                    f"(effectiveness: {latest['effectiveness_score']}, "
                    f"reliability: {latest['reliability_score']})"
                )

        db.close_connection(conn)

        # Final summary
        print_section("Test Summary")
        print_success("All integration tests passed!")
        print_info(f"Database is fully functional and ready for use")
        print_info(f"Created {model_count} models, {technique_count} techniques")
        print_info(f"Logged {experiment_count} experiments, {improvement_count} improvements")

        return 0

    except Exception as e:
        print_error(f"Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
