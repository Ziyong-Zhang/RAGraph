# RAGraph - Running the Application

## Prerequisites

- Python 3.11+
- `uv` package manager
- DeepSeek API key (set in `.env`)

## Setup

```bash
# Install dependencies
uv sync

# Configure environment
cp .env.example .env
# Edit .env and set DEEPSEEK_API_KEY
```

## Running the Application

You need **two terminals** running simultaneously:

### Terminal 1: FastAPI Backend

```bash
uv run uvicorn backend.main:app --reload
```

The backend will be available at `http://localhost:8000`.
- Health check: `http://localhost:8000/health`
- API docs: `http://localhost:8000/docs`
- Graph endpoint: `GET /api/v1/graph/{book_stem}`

### Terminal 2: Streamlit Frontend

```bash
uv run streamlit run frontend/app.py
```

The frontend will be available at `http://localhost:8501`.

## Processing an EPUB File

Before you can visualize a graph, you need to process an EPUB file:

```bash
# Place your .epub files in data/raw/books/
cp your_book.epub data/raw/books/

# Run the processing pipeline (limited to 4 chunks for testing)
uv run python scripts/run_integration.py

# Or specify a custom file:
uv run python scripts/run_integration.py --epub-path data/raw/books/your_book.epub

# Override the chunk limit:
uv run python scripts/run_integration.py --max-chunks 10
```

After processing, the output files will be in `data/raw/output/`:
- `{book_stem}_graph.graphml` - NetworkX GraphML format
- `{book_stem}_graph.json` - Cytoscape.js compatible JSON

## Running Tests

```bash
uv run pytest tests/ -v
```

## Project Structure

```
.
├── backend/
│   ├── main.py              # FastAPI app with CORS and graph endpoint
│   └── core/
│       ├── config.py         # Settings & PipelineConfig (YAML + .env)
│       ├── models.py         # Pydantic models (Character, Relationship, GraphState)
│       ├── parsers.py        # EPUB parser (Strategy Pattern)
│       ├── chunker.py        # Text chunking
│       ├── extractor.py      # LLM entity extraction (Instructor + DeepSeek)
│       ├── graph_builder.py  # NetworkX MultiDiGraph construction
│       ├── exporter.py       # Cytoscape.js JSON exporter
│       └── workflow.py       # LangGraph sequential pipeline
├── frontend/
│   └── app.py                # Streamlit visualization
├── scripts/
│   └── run_integration.py    # Pipeline runner
├── config.yaml               # Pipeline hyperparameters
├── .env                      # Secrets (API keys)
└── tests/                    # Pytest test suite