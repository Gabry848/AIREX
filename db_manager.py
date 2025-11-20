#!/usr/bin/env python3
"""
Database Manager for Prompt Engineering Research
Handles all database operations for storing and retrieving research data.
"""

import sqlite3
import json
from datetime import datetime
from typing import List, Dict, Optional, Tuple
import os

DB_PATH = "prompt_engineering_research.db"

class DatabaseManager:
    def __init__(self, db_path: str = DB_PATH):
        self.db_path = db_path
        self.conn = None

    def connect(self):
        """Establish database connection"""
        self.conn = sqlite3.connect(self.db_path)
        self.conn.row_factory = sqlite3.Row
        return self.conn

    def close(self):
        """Close database connection"""
        if self.conn:
            self.conn.close()

    def initialize_database(self):
        """Initialize database with schema"""
        self.connect()
        with open('database_schema.sql', 'r') as f:
            schema = f.read()
        self.conn.executescript(schema)
        self.conn.commit()
        print("✓ Database initialized successfully")
        self.close()

    # ==================== MODEL OPERATIONS ====================

    def add_model(self, model_name: str, **kwargs) -> int:
        """Add a new model to the database"""
        self.connect()
        cursor = self.conn.cursor()

        columns = ['model_name'] + list(kwargs.keys())
        values = [model_name] + list(kwargs.values())
        placeholders = ','.join(['?' for _ in columns])

        query = f"""
        INSERT INTO models ({','.join(columns)})
        VALUES ({placeholders})
        """

        try:
            cursor.execute(query, values)
            self.conn.commit()
            model_id = cursor.lastrowid
            print(f"✓ Model '{model_name}' added with ID: {model_id}")
            return model_id
        except sqlite3.IntegrityError:
            print(f"⚠ Model '{model_name}' already exists")
            cursor.execute("SELECT id FROM models WHERE model_name = ?", (model_name,))
            return cursor.fetchone()[0]
        finally:
            self.close()

    def get_model(self, model_name: str) -> Optional[Dict]:
        """Get model information"""
        self.connect()
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM models WHERE model_name = ?", (model_name,))
        row = cursor.fetchone()
        self.close()
        return dict(row) if row else None

    def update_model(self, model_name: str, **kwargs):
        """Update model information"""
        self.connect()
        cursor = self.conn.cursor()

        set_clause = ','.join([f"{key} = ?" for key in kwargs.keys()])
        values = list(kwargs.values()) + [model_name]

        query = f"UPDATE models SET {set_clause} WHERE model_name = ?"
        cursor.execute(query, values)
        self.conn.commit()
        print(f"✓ Model '{model_name}' updated")
        self.close()

    # ==================== TECHNIQUE OPERATIONS ====================

    def add_technique(self, technique_name: str, description: str,
                     category: str = None, example: str = None,
                     discovered_from: str = 'hypothesis') -> int:
        """Add a new prompt engineering technique"""
        self.connect()
        cursor = self.conn.cursor()

        query = """
        INSERT INTO techniques (technique_name, description, category, example, discovered_from)
        VALUES (?, ?, ?, ?, ?)
        """

        cursor.execute(query, (technique_name, description, category, example, discovered_from))
        self.conn.commit()
        technique_id = cursor.lastrowid
        print(f"✓ Technique '{technique_name}' added with ID: {technique_id}")
        self.close()
        return technique_id

    def get_technique(self, technique_name: str) -> Optional[Dict]:
        """Get technique information"""
        self.connect()
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM techniques WHERE technique_name = ?", (technique_name,))
        row = cursor.fetchone()
        self.close()
        return dict(row) if row else None

    def get_all_techniques(self) -> List[Dict]:
        """Get all techniques"""
        self.connect()
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM techniques ORDER BY created_at DESC")
        rows = cursor.fetchall()
        self.close()
        return [dict(row) for row in rows]

    # ==================== EVALUATION OPERATIONS ====================

    def add_evaluation(self, model_name: str, technique_name: str,
                      accuracy: float = 0, coherence: float = 0,
                      relevance: float = 0, creativity: float = 0,
                      response_time: float = 0, observations: str = "") -> int:
        """Add or update an evaluation for a model-technique pair"""
        self.connect()
        cursor = self.conn.cursor()

        # Get model and technique IDs
        cursor.execute("SELECT id FROM models WHERE model_name = ?", (model_name,))
        model_row = cursor.fetchone()
        if not model_row:
            self.close()
            raise ValueError(f"Model '{model_name}' not found")
        model_id = model_row[0]

        cursor.execute("SELECT id FROM techniques WHERE technique_name = ?", (technique_name,))
        technique_row = cursor.fetchone()
        if not technique_row:
            self.close()
            raise ValueError(f"Technique '{technique_name}' not found")
        technique_id = technique_row[0]

        # Calculate overall effectiveness
        scores = [accuracy, coherence, relevance, creativity, response_time]
        overall = sum(scores) / len(scores)

        query = """
        INSERT INTO evaluations
        (model_id, technique_id, accuracy_score, coherence_score, relevance_score,
         creativity_score, response_time_score, overall_effectiveness, observations)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(model_id, technique_id) DO UPDATE SET
            accuracy_score = excluded.accuracy_score,
            coherence_score = excluded.coherence_score,
            relevance_score = excluded.relevance_score,
            creativity_score = excluded.creativity_score,
            response_time_score = excluded.response_time_score,
            overall_effectiveness = excluded.overall_effectiveness,
            observations = excluded.observations,
            updated_at = CURRENT_TIMESTAMP
        """

        cursor.execute(query, (model_id, technique_id, accuracy, coherence,
                              relevance, creativity, response_time, overall, observations))
        self.conn.commit()
        eval_id = cursor.lastrowid
        print(f"✓ Evaluation added/updated for {model_name} + {technique_name}")
        self.close()
        return eval_id

    def update_evaluation_status(self, model_name: str, technique_name: str,
                                status: str, success_rate: float = None):
        """Update evaluation status"""
        self.connect()
        cursor = self.conn.cursor()

        query = """
        UPDATE evaluations
        SET status = ?, success_rate = COALESCE(?, success_rate), updated_at = CURRENT_TIMESTAMP
        WHERE model_id = (SELECT id FROM models WHERE model_name = ?)
        AND technique_id = (SELECT id FROM techniques WHERE technique_name = ?)
        """

        cursor.execute(query, (status, success_rate, model_name, technique_name))
        self.conn.commit()
        print(f"✓ Evaluation status updated to '{status}'")
        self.close()

    def get_evaluations_for_model(self, model_name: str) -> List[Dict]:
        """Get all evaluations for a specific model"""
        self.connect()
        cursor = self.conn.cursor()

        query = """
        SELECT
            t.technique_name,
            t.description,
            t.category,
            e.accuracy_score,
            e.coherence_score,
            e.relevance_score,
            e.creativity_score,
            e.response_time_score,
            e.overall_effectiveness,
            e.success_rate,
            e.test_count,
            e.status,
            e.observations
        FROM evaluations e
        JOIN techniques t ON e.technique_id = t.id
        JOIN models m ON e.model_id = m.id
        WHERE m.model_name = ?
        ORDER BY e.overall_effectiveness DESC
        """

        cursor.execute(query, (model_name,))
        rows = cursor.fetchall()
        self.close()
        return [dict(row) for row in rows]

    # ==================== STATISTICS ====================

    def get_statistics(self) -> Dict:
        """Get overall research statistics"""
        self.connect()
        cursor = self.conn.cursor()

        stats = {}

        # Count models
        cursor.execute("SELECT COUNT(*) FROM models")
        stats['total_models'] = cursor.fetchone()[0]

        # Count techniques
        cursor.execute("SELECT COUNT(*) FROM techniques")
        stats['total_techniques'] = cursor.fetchone()[0]

        # Count validated techniques
        cursor.execute("SELECT COUNT(*) FROM evaluations WHERE status = 'validated'")
        stats['validated_techniques'] = cursor.fetchone()[0]

        # Count rejected techniques
        cursor.execute("SELECT COUNT(*) FROM evaluations WHERE status = 'rejected'")
        stats['rejected_techniques'] = cursor.fetchone()[0]

        # Get best technique overall
        cursor.execute("""
            SELECT t.technique_name, AVG(e.overall_effectiveness) as avg_score
            FROM evaluations e
            JOIN techniques t ON e.technique_id = t.id
            WHERE e.status = 'validated'
            GROUP BY t.technique_name
            ORDER BY avg_score DESC
            LIMIT 1
        """)
        best = cursor.fetchone()
        stats['best_technique'] = dict(best) if best else None

        self.close()
        return stats

    def print_statistics(self):
        """Print formatted statistics"""
        stats = self.get_statistics()
        print("\n" + "="*50)
        print("RESEARCH STATISTICS")
        print("="*50)
        print(f"Total Models Analyzed: {stats['total_models']}")
        print(f"Total Techniques Discovered: {stats['total_techniques']}")
        print(f"Validated Techniques: {stats['validated_techniques']}")
        print(f"Rejected Techniques: {stats['rejected_techniques']}")
        if stats['best_technique']:
            print(f"Best Technique: {stats['best_technique']['technique_name']} "
                  f"(avg score: {stats['best_technique']['avg_score']:.2f}%)")
        print("="*50 + "\n")


# ==================== HELPER FUNCTIONS ====================

def init_db():
    """Initialize the database"""
    db = DatabaseManager()
    db.initialize_database()

def add_model_interactive():
    """Interactive model addition"""
    db = DatabaseManager()
    model_name = input("Model name: ")
    provider = input("Provider: ")
    release_year = input("Release year: ")
    model_size = input("Model size: ")
    description = input("Description: ")

    db.add_model(
        model_name=model_name,
        provider=provider,
        release_year=int(release_year) if release_year else None,
        model_size=model_size,
        description=description
    )

def show_stats():
    """Show research statistics"""
    db = DatabaseManager()
    db.print_statistics()


if __name__ == "__main__":
    print("Prompt Engineering Research - Database Manager")
    print("1. Initialize Database")
    print("2. Add Model")
    print("3. Show Statistics")

    choice = input("\nChoice: ")

    if choice == "1":
        init_db()
    elif choice == "2":
        add_model_interactive()
    elif choice == "3":
        show_stats()
