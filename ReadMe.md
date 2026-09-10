# DSA Prep Assistant

An AI-powered, full-stack web application that turns any DSA problem into a complete, structured study resource — brute-force, better, and optimal approaches with code in four languages, complexities, and interview follow-ups — then organizes everything by pattern for tracked, long-term revision.

Built as a personal interview-preparation tool: paste a problem, and the app generates a verified-structure breakdown, classifies its DSA pattern automatically, and stores it for spaced revision.

> Built to make DSA interview preparation faster, structured, and more organized using AI.

## Live Demo

**[Open DSA Prep Assistant](https://ai-powered-coding-platform-obut.onrender.com/)**

## Backend API: 
https://ai-coding-platform-api.onrender.com

## API Documentation:
https://ai-coding-platform-api.onrender.com/docs

---


## Features

- **AI solution generation** — for any problem, generates brute-force, better, and optimal approaches, each with the idea, code, and time/space complexity.
- **Multi-language code** — every approach is provided in Java, C++, Python, and C, with syntax highlighting and per-approach language tabs.
- **Interview follow-ups** — each problem includes likely follow-up/variation questions an interviewer might ask.
- **Automatic pattern classification** — every problem is tagged with its DSA pattern (Arrays, Dynamic Programming, Graphs, etc.) by the AI.
- **Dashboard** — analytics over your solved problems: total solved, breakdown by pattern, and which patterns you haven't covered yet.
- **Pattern Tracker** — a two-level (pattern → sub-pattern) curriculum where the AI suggests canonical interview questions per sub-pattern, with completion tracking, difficulty tags, and search-links to LeetCode and GeeksforGeeks.
- **Personal notes** — add your own notes to any problem for revision.
- **Difficulty tags** — mark problems Easy / Medium / Hard.
- **Edit & regenerate** — refine a problem's description and regenerate its solution in place.
- **Light / dark mode.**

---

## Architecture & Engineering Decisions

This project is deliberately structured around a few decisions that make it resilient rather than a thin wrapper around an LLM API:

### Multi-provider failover
Solution generation runs through a **swappable provider interface** with automatic failover between two LLM providers (Groq and Google Gemini). If the primary provider fails — rate limits, overload, or an outage — the app automatically retries with the secondary provider before surfacing an error. Provider order is configurable from a single value. This keeps the app working even when any one free-tier provider hits its daily quota or a demand spike.

### Resilient handling of imperfect LLM output
LLMs don't reliably return clean JSON, especially when asked to embed multi-line, indented code inside JSON string fields (raw newlines and tabs are illegal in JSON). The generation layer **sanitizes and repairs malformed model output before parsing**, so a slightly malformed response is recovered rather than crashing the request.

### Retry with exponential backoff
Transient provider errors (e.g. HTTP 429/503) are retried with increasing delays before falling through to the secondary provider, smoothing over short-lived rate limits and demand spikes.

### Separation of raw data and derived views
Problems and their generated solutions are stored once; the Dashboard and Pattern Tracker compute their analytics as **derived views** over that data rather than duplicating it.

### Lightweight classification
Pattern tagging and question suggestions use minimal, targeted model calls (classifying or suggesting only, not regenerating full solutions) to stay fast and cheap.

---

## Tech Stack

### Frontend
- **React.js** – User interface
- **Vite** – Frontend build tool
- **CSS** – Styling

### Backend
- **Python**
- **FastAPI** – REST API framework
- **SQLite** – Database

### AI & LLM
- **Google Gemini** – AI provider

### Deployment & DevOps
- **Vercel** – React/Vite frontend deployment
- **Render** – FastAPI backend deployment
- **Git & GitHub** – Version control and source management

---
## Deployment

The application uses a separate frontend and backend deployment architecture:

- **Frontend:** React + Vite → **Vercel**
- **Backend:** FastAPI → **Render**
- **Database:** SQLite
- **AI Services:** Groq (Primary) + Google Gemini (Fallback)

---
## Project Structure

```
dsa-prep/
├── main.py            # FastAPI app: endpoints, database models, sessions
├── generator.py       # AI layer: provider failover, prompts, JSON parsing
├── requirements.txt   # Backend dependencies
├── .env               # API keys (not committed)
├── .gitignore
├── dsa.db             # SQLite database (not committed)
└── frontend/          # React + Vite single-page app
    └── src/
        ├── App.jsx
        └── App.css
```

---

## Setup & Running Locally

### Prerequisites
- Python 3.13+
- Node.js (LTS)
- A free [Google Gemini API key](https://aistudio.google.com)

### 1. Backend

From the project root (`dsa-prep`):

```bash
# Create and activate a virtual environment
python -m venv venv
venv\Scripts\activate          # Windows
# source venv/bin/activate     # macOS/Linux

# Install dependencies
pip install -r requirements.txt
```

Create a `.env` file in the project root with your API keys:

```
GROQ_API_KEY=your_groq_key_here
GEMINI_API_KEY=your_gemini_key_here
```

Run the backend:

```bash
uvicorn main:app --reload
```

The API runs at `http://localhost:8000` (interactive docs at `http://localhost:8000/docs`).

### 2. Frontend

In a **separate terminal**, from the `frontend` folder:

```bash
cd frontend
npm install
npm run dev
```

Open `http://localhost:5173` in your browser.

> Both servers must be running at the same time: the backend (port 8000) handles generation and data; the frontend (port 5173) is the UI.

---

## How It Works

1. You paste a DSA problem (title optional) and pick a difficulty.
2. The backend sends it to the AI provider, which returns a structured JSON breakdown (explanation, approaches in four languages, complexities, follow-ups, and the DSA pattern).
3. The response is parsed (with repair for malformed output), stored in SQLite, and the pattern is recorded.
4. The Dashboard and Pattern Tracker read this data to show your coverage and progress.

---

## Possible Future Work

- Verify generated code by executing it against test cases (correctness checking).
- Spaced-repetition revision scheduling.
- Attempt-first mode (attempt before revealing the solution).
- Direct verified problem links via a problem-slug lookup.

---

## Notes

This project was developed with AI-assisted tooling. The architecture, design decisions, and debugging were directed and reviewed throughout.
