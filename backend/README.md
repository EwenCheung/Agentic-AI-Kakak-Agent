# Backend

This directory contains the backend code for the Kakak Agent.

## Getting Started for Backend

1.  Change directory to backend `cd backend`
2.  Install dependencies: `pip install -r requirements.txt`
3.  Run the development server: `uvicorn src.main:app --reload --host 0.0.0.0 --port 8000`
4.  Run the worker.py with `python -m src.worker`
