# MedPilot Backend (POC)

MedPilot is a clinical decision support system designed with an AI-first workflow. This repository contains the FastAPI backend responsible for receiving patient information, parsing transcripts through the FastAI evaluation layer, providing safety reviews, and making workflow decisions. 

## Architecture
- **FastAPI Core**: Standard REST app running on Uvicorn, separated into semantic routers (`/api/v1/cases`, `/api/v1/chat`, `/api/v1/rag`).
- **AI Services**: Clients to interface with local or remote fastAI and vLLM models to handle medical logic.
- **Data Persistence**: Uses a combination of `database.xlsx` for light metadata reporting and raw JSON files inside `data/cases/` for deep state storage, preventing memory bloat and mitigating write locks.
- **Environment Management**: Utilizes `pydantic-settings` to inject constants directly using `.env` values.

## Initial Setup

1. **Install Dependencies**  
   Ensure you have Python 3.10+ installed.
   ```bash
   pip install -r requirements.txt
   ```

2. **Environment Variables**  
   Create a `.env` file at the root to configure the application overrides. Example:
   ```env
   ENVIRONMENT=dev
   VLLM_BASE_URL=http://localhost:8001/v1
   ```

3. **Running the Server**  
   Start Uvicorn to run the internal app:
   ```bash
   python main.py
   ```
   Or standard:
   ```bash
   uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
   ```

## Development and Testing

- **Tests Folder:** Use `pytest` to run all integration endpoint checks.
  ```bash
  pytest
  ```
- **Error Handling:** The backend uses unified exception handlers (500s, 422s, etc.) that automatically resolve into the standardized standard `APIResponse` object:
  ```json
  {
    "success": false,
    "message": "...",
    "data": null
  }
  ```

## UI
Serving the integrated chat/form user interface natively at `http://127.0.0.1:8000/`.
