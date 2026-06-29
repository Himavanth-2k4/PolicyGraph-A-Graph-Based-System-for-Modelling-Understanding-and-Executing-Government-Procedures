## Policy-Aware Graph-Enhanced RAG for Government Schemes

This project is a student-grade but research-worthy prototype that provides personalized guidance on government scheme eligibility using:
- a **retrieval-augmented generation (RAG)** layer over official documents, and
- a **lightweight knowledge graph (KG)** of schemes and eligibility criteria.

### Structure

```text
.
├── api/
│   ├── __init__.py
│   ├── models.py
│   └── server.py
├── config.py
├── data/
│   ├── indices/
│   ├── processed/
│   └── raw/
├── eligibility/
│   ├── __init__.py
│   ├── engine.py
│   └── rules.py
├── ingestion/
│   ├── __init__.py
│   ├── chunking.py
│   ├── loaders.py
│   └── parsers.py
├── kg/
│   ├── __init__.py
│   ├── graph_store.py
│   └── schema.py
├── logging_utils.py
├── retrieval/
│   ├── __init__.py
│   ├── hybrid_retriever.py
│   └── vector_store.py
├── ui/
│   ├── __init__.py
│   └── app.py
├── .gitignore
├── LICENSE
├── pyproject.toml
├── README.md
└── requirements.txt
```

### Quick start (Windows development)

1. **Create and activate a virtual environment:**
   Open a terminal in the project root (e.g., `e:\python\RAG_GOV`).

   *Command Prompt (cmd):*
   ```cmd
   python -m venv .venv
   .venv\Scripts\activate
   ```

   *PowerShell:*
   ```powershell
   python -m venv .venv
   .venv\Scripts\Activate.ps1
   ```

2. **Install dependencies:**
   ```powershell
   pip install -e .
   ```

3. **Place data:**
   Place a few scheme PDFs or HTML pages into `data/raw/`.

4. **Run ingestion:**
   Run the ingestion script to populate `data/processed/` and build indices.
   ```powershell
   python ingestion/run_ingest.py
   ```

5. **Start the API server:**
   ```powershell
   uvicorn api.server:app --reload
   ```

6. **Run the Streamlit UI (in a new terminal):**
   Open a new terminal, activate the environment, and run:
   ```powershell
   streamlit run ui/app.py
   ```

This repository is intentionally minimal and focused on core research logic; students can extend modules as needed.

