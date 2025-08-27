# Virtual Machine Finder

Designed to aggregate, store, and display virtual machine pricing data from multiple cloud providers. The application automatically keeps its pricing data up-to-date with a background scheduler and provides a powerful, filterable interface for users to find and compare virtual machine instances.

## To Run Locally

### Modify the .env files

### Backend

```bash
python3 -m venv venv && source venv/bin/activate && pip install -r requirements.txt
uvicorn app.main:app --reload
```

### Frontend

```bash
cd frontend && npm i && npm run dev
```