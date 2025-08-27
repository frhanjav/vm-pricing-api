# Virtual Machine Finder

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