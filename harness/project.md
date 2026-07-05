# RAGraph — Project Identity

## Goal

Build "RAGraph", a production-grade AI application that:

- Extracts text from Agatha Christie EPUB files.
- Analyzes and visualizes character relationships and timelines.
- Provides a stateful "anti-spoiler" chat UI with a human-in-the-loop correction mechanism.

## Tech Stack

| Layer          | Technology                                           |
|----------------|------------------------------------------------------|
| UI             | Streamlit                                            |
| Backend        | FastAPI                                              |
| Workflow       | LangGraph                                            |
| LLM API        | DeepSeek API                                         |
| Graph Analysis | NetworkX                                             |
| Observability  | LangSmith                                            |
| Testing        | Pytest                                               |
| Container      | Docker                                               |
| Infrastructure | Terraform                                            |
| Deployment     | GCP Cloud Run                                        |
| CI/CD          | GitHub Actions                                       |

## Architecture Principle

**Strict Decoupling.**

- UI logic is isolated entirely in the Streamlit frontend layer.
- Business logic, LangGraph state management, and LLM API calls are isolated entirely in the FastAPI backend layer.
- No Streamlit import or dependency shall appear in backend code.
- No direct business logic shall be embedded in Streamlit callbacks.
- Communication between frontend and backend occurs exclusively via REST API calls.