"""
Technique Manager Module for AIREX project.
Provides functions to manage models, techniques, experiments, and improvements.
"""

import logging
from typing import Optional, Dict, Any
from datetime import datetime
from db import get_connection, close_connection

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def add_model(name: str, source_url: Optional[str] = None, notes: Optional[str] = None) -> int:
    """
    Adds a new AI model to the database.

    Args:
        name: Name of the model (must be unique)
        source_url: URL to the model documentation or source
        notes: Additional notes about the model

    Returns:
        int: ID of the newly created model

    Raises:
        ValueError: If name is empty or model already exists
        Exception: If database operation fails
    """
    if not name or not name.strip():
        raise ValueError("Model name cannot be empty")

    conn = None
    try:
        conn = get_connection()
        with conn.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO models (name, source_url, notes)
                VALUES (%s, %s, %s)
                RETURNING id
                """,
                (name.strip(), source_url, notes)
            )
            model_id = cursor.fetchone()['id']
            conn.commit()
            logger.info(f"Model '{name}' added successfully with ID: {model_id}")
            return model_id
    except Exception as e:
        if conn:
            conn.rollback()
        logger.error(f"Failed to add model '{name}': {e}")
        raise
    finally:
        close_connection(conn)


def add_technique(
    name: str,
    description: str,
    origin_type: str = 'online'
) -> int:
    """
    Adds a new prompt engineering technique to the database.

    Args:
        name: Name of the technique (must be unique)
        description: Detailed description of the technique
        origin_type: Origin of the technique ('online', 'deduced', 'invented', 'random')

    Returns:
        int: ID of the newly created technique

    Raises:
        ValueError: If required fields are empty or origin_type is invalid
        Exception: If database operation fails
    """
    if not name or not name.strip():
        raise ValueError("Technique name cannot be empty")

    if not description or not description.strip():
        raise ValueError("Technique description cannot be empty")

    valid_origins = ['online', 'deduced', 'invented', 'random']
    if origin_type not in valid_origins:
        raise ValueError(f"Invalid origin_type. Must be one of: {', '.join(valid_origins)}")

    conn = None
    try:
        conn = get_connection()
        with conn.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO techniques (name, description, origin_type)
                VALUES (%s, %s, %s)
                RETURNING id
                """,
                (name.strip(), description.strip(), origin_type)
            )
            technique_id = cursor.fetchone()['id']
            conn.commit()
            logger.info(f"Technique '{name}' added successfully with ID: {technique_id}")
            return technique_id
    except Exception as e:
        if conn:
            conn.rollback()
        logger.error(f"Failed to add technique '{name}': {e}")
        raise
    finally:
        close_connection(conn)


def link_model_technique(
    model_id: int,
    technique_id: int,
    score_for_this_model: float = 0.0,
    works_for_model: bool = True
) -> int:
    """
    Links a technique to a model with performance metrics.

    Args:
        model_id: ID of the model
        technique_id: ID of the technique
        score_for_this_model: Performance score (0-10)
        works_for_model: Whether the technique works for this model

    Returns:
        int: ID of the created link

    Raises:
        ValueError: If score is out of range or IDs are invalid
        Exception: If database operation fails
    """
    if score_for_this_model < 0 or score_for_this_model > 10:
        raise ValueError("score_for_this_model must be between 0 and 10")

    if model_id <= 0 or technique_id <= 0:
        raise ValueError("model_id and technique_id must be positive integers")

    conn = None
    try:
        conn = get_connection()
        with conn.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO model_techniques (model_id, technique_id, score_for_this_model, works_for_model)
                VALUES (%s, %s, %s, %s)
                ON CONFLICT (technique_id, model_id)
                DO UPDATE SET
                    score_for_this_model = EXCLUDED.score_for_this_model,
                    works_for_model = EXCLUDED.works_for_model
                RETURNING id
                """,
                (model_id, technique_id, score_for_this_model, works_for_model)
            )
            link_id = cursor.fetchone()['id']
            conn.commit()
            logger.info(
                f"Linked technique {technique_id} to model {model_id} "
                f"with score {score_for_this_model}"
            )
            return link_id
    except Exception as e:
        if conn:
            conn.rollback()
        logger.error(f"Failed to link technique {technique_id} to model {model_id}: {e}")
        raise
    finally:
        close_connection(conn)


def log_experiment(
    technique_id: int,
    test_prompt: str,
    model_used: str,
    api_response_text: Optional[str] = None,
    score: Optional[float] = None,
    is_regression: bool = False
) -> int:
    """
    Logs an experimental test of a technique.

    Args:
        technique_id: ID of the technique being tested
        test_prompt: The prompt used in the test
        model_used: Name/identifier of the model used
        api_response_text: The response from the API
        score: Performance score (0-10)
        is_regression: Whether this test is a regression test

    Returns:
        int: ID of the logged experiment

    Raises:
        ValueError: If required fields are empty or score is out of range
        Exception: If database operation fails
    """
    if technique_id <= 0:
        raise ValueError("technique_id must be a positive integer")

    if not test_prompt or not test_prompt.strip():
        raise ValueError("test_prompt cannot be empty")

    if not model_used or not model_used.strip():
        raise ValueError("model_used cannot be empty")

    if score is not None and (score < 0 or score > 10):
        raise ValueError("score must be between 0 and 10")

    conn = None
    try:
        conn = get_connection()
        with conn.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO experiments (
                    technique_id, test_prompt, model_used,
                    api_response_text, score, is_regression
                )
                VALUES (%s, %s, %s, %s, %s, %s)
                RETURNING id
                """,
                (
                    technique_id,
                    test_prompt.strip(),
                    model_used.strip(),
                    api_response_text,
                    score,
                    is_regression
                )
            )
            experiment_id = cursor.fetchone()['id']
            conn.commit()
            logger.info(
                f"Experiment logged for technique {technique_id} "
                f"with model '{model_used}' (ID: {experiment_id})"
            )
            return experiment_id
    except Exception as e:
        if conn:
            conn.rollback()
        logger.error(f"Failed to log experiment for technique {technique_id}: {e}")
        raise
    finally:
        close_connection(conn)


def update_technique_score(
    technique_id: int,
    effectiveness_score: Optional[float] = None,
    reliability_score: Optional[float] = None
) -> bool:
    """
    Updates the effectiveness and/or reliability score of a technique.

    Args:
        technique_id: ID of the technique to update
        effectiveness_score: New effectiveness score (0-10)
        reliability_score: New reliability score (0-10)

    Returns:
        bool: True if update was successful

    Raises:
        ValueError: If scores are out of range or no score provided
        Exception: If database operation fails
    """
    if technique_id <= 0:
        raise ValueError("technique_id must be a positive integer")

    if effectiveness_score is None and reliability_score is None:
        raise ValueError("At least one score must be provided")

    if effectiveness_score is not None and (effectiveness_score < 0 or effectiveness_score > 10):
        raise ValueError("effectiveness_score must be between 0 and 10")

    if reliability_score is not None and (reliability_score < 0 or reliability_score > 10):
        raise ValueError("reliability_score must be between 0 and 10")

    conn = None
    try:
        conn = get_connection()
        with conn.cursor() as cursor:
            # Build dynamic update query
            updates = []
            params = []

            if effectiveness_score is not None:
                updates.append("effectiveness_score = %s")
                params.append(effectiveness_score)

            if reliability_score is not None:
                updates.append("reliability_score = %s")
                params.append(reliability_score)

            # Add updated_at (will be handled by trigger, but included for clarity)
            updates.append("updated_at = CURRENT_TIMESTAMP")

            params.append(technique_id)

            query = f"""
                UPDATE techniques
                SET {', '.join(updates)}
                WHERE id = %s
                RETURNING id
            """

            cursor.execute(query, params)
            result = cursor.fetchone()

            if not result:
                raise ValueError(f"Technique with ID {technique_id} not found")

            conn.commit()
            logger.info(f"Technique {technique_id} scores updated successfully")
            return True
    except Exception as e:
        if conn:
            conn.rollback()
        logger.error(f"Failed to update technique {technique_id} scores: {e}")
        raise
    finally:
        close_connection(conn)


def add_improvement(
    technique_id: int,
    parent_technique_id: Optional[int] = None,
    delta_score: Optional[float] = None,
    notes: Optional[str] = None
) -> int:
    """
    Records an improvement to a technique.

    Args:
        technique_id: ID of the improved technique
        parent_technique_id: ID of the parent technique (if applicable)
        delta_score: Change in score from parent technique
        notes: Notes about the improvement

    Returns:
        int: ID of the improvement record

    Raises:
        ValueError: If technique_id is invalid
        Exception: If database operation fails
    """
    if technique_id <= 0:
        raise ValueError("technique_id must be a positive integer")

    conn = None
    try:
        conn = get_connection()
        with conn.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO improvements (technique_id, parent_technique_id, delta_score, notes)
                VALUES (%s, %s, %s, %s)
                RETURNING id
                """,
                (technique_id, parent_technique_id, delta_score, notes)
            )
            improvement_id = cursor.fetchone()['id']
            conn.commit()
            logger.info(f"Improvement record created with ID: {improvement_id}")
            return improvement_id
    except Exception as e:
        if conn:
            conn.rollback()
        logger.error(f"Failed to add improvement for technique {technique_id}: {e}")
        raise
    finally:
        close_connection(conn)
