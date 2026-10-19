# RepoSense AI — Developer Getting Started Guide

Welcome to RepoSense AI! This guide gets your local development environment set up from scratch.

---

## 1. System Requirements

- **Operating System:** Windows 10/11, macOS, or Linux
- **Python:** Version 3.11 or newer (tested with Python 3.14)
- **Node.js:** Version 18.0 or newer (tested with v24.13)
- **npm:** Version 9.0 or newer (tested with 11.8)
- **Git:** Version 2.30 or newer

---

## 2. Quick Setup Commands

### Step 1: Clone the repository
```bash
git clone https://github.com/your-username/RepoSense-AI.git
cd RepoSense-AI
```

### Step 2: Configure Environment
Copy the example environment file:
```bash
cp .env.example .env
```

### Step 3: Start the Backend API
```bash
# Windows
python -m venv backend/.venv
backend\.venv\Scripts\pip install -r backend/requirements.txt
backend\.venv\Scripts\uvicorn app.main:app --app-dir backend --reload --port 8000

# Linux / macOS
python3 -m venv backend/.venv
source backend/.venv/bin/activate
pip install -r backend/requirements.txt
uvicorn app.main:app --app-dir backend --reload --port 8000
```

Verify backend health in another terminal:
```bash
curl http://127.0.0.1:8000/api/v1/health
```

### Step 4: Start the Frontend UI
In a new terminal window:
```bash
cd frontend
npm install
npm run dev
```

Open [http://localhost:5173](http://localhost:5173) in your browser.

---

## 3. Running Automated Tests

Run backend tests:
```bash
backend\.venv\Scripts\pytest -v backend/tests
```

Run frontend tests:
```bash
cd frontend
npm run test:run
```

Run frontend production build verification:
```bash
cd frontend
npm run build
```
