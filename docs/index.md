# Cloud VM Price Finder Documentation

<div style="text-align: center;">
  <video src="https://media.frhn.me/socialvmfinder.mp4" controls autoplay loop muted width="600"></video>
</div>

## Overview

Cloud VM Price Finder is designed to aggregate, store, and display virtual machine pricing data from multiple cloud providers. It features a high-performance FastAPI backend, a PostgreSQL database, and a modern, responsive React frontend built with Vite and Shadcn UI.

The application automatically keeps its pricing data up-to-date with a background scheduler and provides a powerful, filterable interface for users to find and compare virtual machine instances.

---

## Features

- **Multi-Provider Support**: Built to aggregate data from providers like AWS, GCP, and more.
- **Persistent Data Storage**: Uses a PostgreSQL database to store and serve pricing data efficiently.
- **Automated Data Refresh**: A background scheduler (APScheduler) runs within the backend service to periodically fetch fresh pricing data.
- **High-Performance Backend**: Built with FastAPI, providing a fast, asynchronous API.
- **Modern Frontend**: A responsive and beautiful UI built with React, Vite, Tailwind CSS, and Shadcn UI.
- **Powerful Filtering & Pagination**: The interface allows for multi-select filtering, sorting, and pagination, all handled by the server.

---

## Technical Stack

- **Frontend:** React, Vite, TypeScript, Tailwind CSS, Shadcn UI, Axios, TanStack Query
- **Backend:** Python, FastAPI, Pydantic
- **Database:** PostgreSQL
- **ORM:** SQLAlchemy (with async support)
- **Web Server:** Nginx (Reverse Proxy), Gunicorn (Application Server), Uvicorn (Worker)
- **Cloud APIs:**
  - AWS: Boto3
  - GCP: Google Cloud Client Libraries

---

## API Endpoints

All endpoints are available under the `/api/v1` prefix.

| Method | Endpoint   | Description                                                                         |
| ------ | ---------- | ----------------------------------------------------------------------------------- |
| GET    | /filters/options | Provides unique, distinct values for all filter dropdowns on the frontend.                                                |
| GET    | /instances   | Fetches a paginated list of VM instances with powerful filtering & sorting.                       |
| GET    | /providers | Lists all providers that currently have data in the database. |
| GET    | /regions   | Lists all regions, optionally filtered by provider.     |
| GET    | /metrics    | Returns basic metrics like total record count and last update times.                   |
| GET    | /health      | A simple health check endpoint.                                        |

---

## Data Schema

### VMInstance

All VM data is normalized to the following schema:

- `instance_name`: str — Name/type of the VM instance
- `provider`: str — Cloud provider name
- `region`: str — Cloud region
- `vcpus`: int — Number of virtual CPUs
- `memory_gb`: float — Amount of RAM in GB
- `storage_gb`: int — Storage size in GB
- `storage_type`: str — Type of storage (e.g., SSD, HDD, EBS)
- `hourly_cost`: float — On-demand hourly price (USD)
- `monthly_cost`: float — Estimated monthly price (USD)
- `spot_price`: float (optional) — Spot/preemptible price (if available)
- `currency`: str — Currency (default: USD)
- `instance_family`: str (optional) — Instance family/type
- `network_performance`: str (optional) — Network performance description
- `last_updated`: datetime — Timestamp of last data refresh

---

## Adding a New Provider

1. Create a new provider class in `app/providers/` inheriting from `BaseProvider`.
2. Implement the `fetch_data()` method to return a list of `VMInstance` objects.
3. Register the provider in the scheduler and (optionally) in the API endpoints.

---

## Local Development Setup

## 1. Backend Setup

### 1. Clone the Repository:

```bash
git clone https://github.com/frhanjav/vm-pricing-api.git
cd vm-pricing-api
```

### 2. Create and Activate a Python Virtual Environment:

```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Python Dependencies:

```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables:

- Create a `.env` file in the project root.
- Add your local database URL and any other necessary settings:

```ini
# .env
DATABASE_URL="postgresql+asyncpg://user:password@localhost/cloud_pricing"
CORS_ORIGINS="http://localhost:5173"
AWS_ACCESS_KEY_ID="your_key"
AWS_SECRET_ACCESS_KEY="your_secret"
```

### 5. Testing Data Fetching

A standalone script `test_fetch.py` is provided to test fetching and saving AWS pricing data to CSV:

```sh
python -m app.test_fetch
```

### 6. Run the Database Migration:

- You can use the migration script to populate your database for the first time.

```bash
python -m app.migrate_csv_to_postgres
```

## 2. Frontend Setup

### 1. Navigate to the Frontend Directory:

```bash
cd frontend
```

### 2. Install Node.js Dependencies:

```bash
npm install
```

### 3. Configure Environment Variables:

- Create a `.env.development` file in the frontend directory.
- Add the URL for your local backend API:

```ini
# frontend/.env.development
VITE_API_BASE_URL=http://127.0.0.1:8000/api/v1
```

## 3. Running the Application

Run the backend and frontend servers simultaneously in two separate terminals from the project root.

### Terminal 1 (Backend):

```bash
uvicorn app.main:app --reload
```

### Terminal 2 (Frontend):

```bash
cd frontend
npm run dev
```

You can now access the frontend at http://localhost:5173.

---