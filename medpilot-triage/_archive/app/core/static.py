import os
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

def setup_static_serving(app: FastAPI):
    # Serve static files (frontend)
    # Move up one level from app/core to app/ then one more to backend_AI
    static_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
    
    app.mount("/static", StaticFiles(directory=static_dir), name="static")

    @app.get("/")
    async def serve_frontend():
        return FileResponse(os.path.join(static_dir, "index.html"))
        
    @app.get("/index.html")
    async def serve_frontend_index():
        return FileResponse(os.path.join(static_dir, "index.html"))
