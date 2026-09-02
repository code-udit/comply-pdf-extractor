# Comply PDF Extractor

**Developed By:** Udit Gunagi

🔗 **Live Demo:** [https://comply-pdf-frontend.onrender.com](https://comply-pdf-frontend.onrender.com)
📦 **GitHub Repository:** [https://github.com/code-udit/comply-pdf-extractor.git](https://github.com/code-udit/comply-pdf-extractor.git)

---

## Overview

**Comply PDF Extractor** is a full-stack document intelligence application that automatically parses SERFF-style insurance filing PDFs, distinguishes **headings** from **body text**, and presents the structured result through a clean, searchable web interface.

It was built as a take-home assignment for **Comply**, addressing the core problem: *compliance professionals need to track filings and extract structured data from PDFs without manually combing through them.*

The system takes a raw, unstructured PDF and turns it into a hierarchical, navigable set of `{heading, text}` sections — ready to be consumed by a UI, an API, or a downstream compliance workflow.

---

## Table of Contents

- [Features](#features)
- [Architecture](#architecture)
- [Tech Stack](#tech-stack)
- [Project Structure](#project-structure)
- [Getting Started](#getting-started)
  - [Prerequisites](#prerequisites)
  - [Backend Setup](#backend-setup)
  - [Frontend Setup](#frontend-setup)
  - [Running with Docker](#running-with-docker)
- [API Reference](#api-reference)
- [Extraction Pipeline](#extraction-pipeline)
- [Sample Documents](#sample-documents)
- [Deployment](#deployment)
- [Assignment Context](#assignment-context)
- [Future Improvements](#future-improvements)

---

## Features

- 📄 **Drag-and-drop PDF upload** with client-side validation
- 🧠 **Automated heading vs. body-text classification** using layout, typography, and semantic signals — not just font size
- 🗂️ **Hierarchical section grouping** (headings, sub-headings, and their associated blocks) rather than a flat list
- 🔍 **In-app search and filtering** by semantic type (heading, paragraph, table, list)
- ⚡ **FastAPI backend** exposing a single, well-typed extraction endpoint
- 🎨 **Modern, responsive React + TypeScript UI** built for readability of dense compliance documents
- 🩺 **Health check endpoint** for uptime monitoring
- 🐳 **Fully containerized** with Docker Compose for one-command local setup
- 📈 **Scalable design** — stateless extraction requests mean the API can be horizontally scaled to handle any number of documents

---

## Architecture

```
┌──────────────┐        PDF Upload         ┌───────────────────┐
│   React UI   │ ───────────────────────▶  │   FastAPI Backend  │
│ (TypeScript) │                            │                    │
│              │ ◀─────────────────────── │  /api/extract       │
└──────────────┘     Structured JSON        └─────────┬──────────┘
                                                        │
                                                        ▼
                                          ┌───────────────────────────┐
                                          │   Extraction Pipeline      │
                                          │  1. Raw PDF Extraction     │
                                          │  2. Noise & Layout Cleaning│
                                          │  3. Semantic Classification│
                                          │  4. Heading/Section Grouping│
                                          └───────────────────────────┘
```

The user uploads a filing, the frontend calls the API, and the backend runs the document through a multi-stage pipeline before returning clean, structured JSON that the UI renders as a readable, navigable document outline.

---

## Tech Stack

**Backend**
- Python 3.12
- FastAPI + Uvicorn
- PyMuPDF (`pymupdf`) for low-level PDF parsing
- Pydantic for data modeling and validation
- Pytest for automated testing

**Frontend**
- React 19 + TypeScript
- Vite (build tool & dev server)
- ESLint for code quality

**Infrastructure**
- Docker & Docker Compose
- Deployed on Render

---

## Project Structure

```
comply-pdf-extractor/
├── backend/
│   ├── app/
│   │   ├── main.py                 # FastAPI app entrypoint & CORS config
│   │   ├── api/
│   │   │   ├── extract.py          # POST /api/extract endpoint
│   │   │   └── validation.py       # Upload validation & error handling
│   │   ├── extraction/
│   │   │   ├── pdf_loader.py       # PDF loading utilities
│   │   │   ├── raw_extractor.py    # Raw text/block extraction (PyMuPDF)
│   │   │   ├── layout_analyzer.py  # Font, position & layout analysis
│   │   │   ├── page_layout_analyzer.py
│   │   │   └── noise_detector.py   # Header/footer/watermark filtering
│   │   ├── semantic/
│   │   │   ├── classifier.py       # Heading vs. body-text classification
│   │   │   ├── processor.py        # Semantic block processing
│   │   │   └── grouping.py         # Hierarchical section grouping
│   │   ├── services/
│   │   │   └── cleaning_service.py # Document cleaning pipeline
│   │   └── models/                 # Pydantic models (document, section, API schemas)
│   ├── tests/                      # Unit & integration tests
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/
│   ├── src/
│   │   ├── App.tsx                 # Main UI: upload, search, section viewer
│   │   ├── App.css / index.css
│   │   └── assets/
│   ├── package.json
│   └── Dockerfile
├── docker-compose.yml
└── README.md
```

---

## Getting Started

### Prerequisites

- Python 3.12+
- Node.js 20+
- npm
- (Optional) Docker & Docker Compose

### Backend Setup

```bash
cd backend
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

pip install -r requirements.txt

uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at `http://localhost:8000`, with interactive docs at `http://localhost:8000/docs`.

### Frontend Setup

```bash
cd frontend
npm install

cp .env.example .env
# Set VITE_API_URL to your backend URL, e.g.:
# VITE_API_URL=http://localhost:8000/api/extract

npm run dev
```

The app will be available at `http://localhost:5173`.

### Running with Docker

From the project root:

```bash
docker compose up --build
```

This starts the backend on `http://localhost:8000` and the frontend on `http://localhost:5173`, wired together automatically.

---

## API Reference

### `POST /api/extract`

Uploads a PDF and returns its structured heading/body-text breakdown.

**Request:** `multipart/form-data` with a `file` field containing the PDF.

**Response:**

```json
{
  "metadata": {
    "request_id": "b3f1...e9",
    "filename": "AMGN-135003565.pdf",
    "page_count": 4,
    "processing_time_ms": 182.34,
    "block_count": 27
  },
  "sections": [
    {
      "heading": "General Filing Information",
      "level": 1,
      "page_start": 1,
      "page_end": 1,
      "blocks": [
        {
          "page_number": 1,
          "source_block_index": 3,
          "semantic_type": "paragraph",
          "text": "...",
          "confidence": 0.92,
          "signals": { "...": "..." }
        }
      ],
      "children": []
    }
  ]
}
```

### `GET /health`

Simple health check used for uptime monitoring and deployment readiness probes.

---

## Extraction Pipeline

The extraction engine runs a filing through four stages:

1. **Raw Extraction** — Parses the PDF with PyMuPDF, capturing every text block along with its position, font, and size on each page.
2. **Cleaning & Noise Detection** — Strips repeated headers, footers, page numbers, and watermark artifacts that would otherwise pollute the output.
3. **Semantic Classification** — Classifies each block as a `heading`, `paragraph`, `table`, `list`, or `unknown` using a combination of layout signals (font size, boldness, whitespace), pattern rules (numbered sections, known SERFF section names), and confidence scoring — rather than relying on font size alone.
4. **Hierarchical Grouping** — Groups classified blocks under their parent headings, building a nested section tree (headings, sub-headings, and the body text that belongs to each) that mirrors how a human would read the document.

This layered approach makes the pipeline robust across differently formatted filings, rather than being tuned to a single document template.

---

## Sample Documents

Three sample SERFF filing PDFs were provided for testing and are used throughout the backend test suite:

- `AMGN-135003565.pdf`
- `NYLM-134614243.pdf`
- `UNAM-135051123.pdf`

---

## Deployment

- **Frontend:** Deployed on Render as a static/Node build → [https://comply-pdf-frontend.onrender.com](https://comply-pdf-frontend.onrender.com)
- **Backend:** Containerized with the provided `Dockerfile`, ready for deployment on any container platform (Render, Railway, Fly.io, AWS, etc.)
- CORS is configured on the backend to allow the deployed frontend origin, and the extraction endpoint is stateless — every request is self-contained and temporary files are cleaned up immediately after processing — so the API can scale horizontally to handle any number of concurrent documents.

---

## Assignment Context

This project was built in response to a take-home assignment from **Comply** (received September 1, 2026, due September 3, 2 PM), which asked for:

1. A Python extraction script that programmatically distinguishes headings from body text as `{heading, text}` pairs.
2. A FastAPI endpoint that runs the extraction on an uploaded document and returns structured JSON.
3. A React UI that lets a user upload a filing, trigger extraction, and view the results in a readable layout.

The solution above satisfies all three requirements end-to-end, with an emphasis on layout-aware classification (rather than naive heuristics), a scalable, stateless API, and a polished, searchable frontend experience.

---

## Future Improvements

- OCR support for scanned/image-based filings
- User authentication and per-user document history
- Export extracted sections to JSON/CSV/DOCX
- Batch upload and processing of multiple filings at once
- Confidence-based manual correction UI for edge-case classifications

---

## License

This project was developed as part of a technical assignment and is provided for evaluation purposes.
