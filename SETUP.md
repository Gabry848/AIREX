# AIREX - Setup Guide

## Overview
AIREX (AI Research and Experimentation) is a system for tracking and analyzing prompt engineering techniques across different AI models.

## Prerequisites
- Python 3.8 or higher
- PostgreSQL database on Railway (or any PostgreSQL instance)
- pip (Python package manager)

## Installation Steps

### 1. Clone and Navigate to Project
```bash
cd /home/user/AIREX
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Configure Environment Variables
Copy the example environment file and configure it:
```bash
cp .env.example .env
```

Edit `.env` and set your Railway PostgreSQL connection string:
```bash
DATABASE_URL=postgresql://username:password@hostname:port/database_name
```

You can find your DATABASE_URL in the Railway dashboard under your PostgreSQL service.

### 4. Initialize the Database
Run the initialization script to create all tables:
```bash
python init_db.py
```

This will:
- Test the database connection
- Create all required tables
- Set up indexes and triggers
- Verify the setup

### 5. Verify Installation
You can verify the installation by running:
```bash
python -c "from db import test_connection; print('Success!' if test_connection() else 'Failed')"
```

## Database Schema

### Tables Created:
1. **models** - Stores AI model information
2. **techniques** - Stores prompt engineering techniques
3. **model_techniques** - Links techniques to models (N:N relationship)
4. **experiments** - Logs experimental tests
5. **improvements** - Tracks technique improvements

## Usage Examples

### Adding a Model
```python
from technique_manager import add_model

model_id = add_model(
    name="GPT-4",
    source_url="https://openai.com/gpt-4",
    notes="OpenAI's latest model"
)
```

### Adding a Technique
```python
from technique_manager import add_technique

technique_id = add_technique(
    name="Chain of Thought",
    description="Ask the model to think step by step",
    origin_type="online"
)
```

### Linking Technique to Model
```python
from technique_manager import link_model_technique

link_model_technique(
    model_id=1,
    technique_id=1,
    score_for_this_model=8.5,
    works_for_model=True
)
```

### Logging an Experiment
```python
from technique_manager import log_experiment

experiment_id = log_experiment(
    technique_id=1,
    test_prompt="Solve this math problem step by step: 2+2",
    model_used="GPT-4",
    api_response_text="Let me think step by step...",
    score=9.0,
    is_regression=False
)
```

### Updating Technique Scores
```python
from technique_manager import update_technique_score

update_technique_score(
    technique_id=1,
    effectiveness_score=8.5,
    reliability_score=9.0
)
```

## Project Structure
```
AIREX/
├── db.py                    # Database connection module
├── schema.sql               # Database schema definition
├── technique_manager.py     # Core business logic functions
├── init_db.py              # Database initialization script
├── requirements.txt         # Python dependencies
├── .env.example            # Environment variables template
├── .env                    # Your actual environment variables (git-ignored)
└── SETUP.md                # This file
```

## Troubleshooting

### Connection Issues
If you get connection errors:
1. Verify DATABASE_URL is correctly set in `.env`
2. Check that your Railway PostgreSQL service is running
3. Ensure your IP is whitelisted (Railway usually allows all by default)

### Import Errors
If you get import errors:
```bash
pip install -r requirements.txt --upgrade
```

### Permission Issues
If init_db.py is not executable:
```bash
chmod +x init_db.py
```

## Security Notes
- Never commit `.env` file to version control
- Keep your DATABASE_URL secret
- Use environment variables for all sensitive data
- The code includes input validation and SQL injection prevention

## Next Steps
The project is now ready for the AITDEVS agent to:
- Start adding models and techniques
- Run experiments
- Analyze results
- Iterate on techniques

## Support
For issues or questions, refer to the main README.md or project documentation.
