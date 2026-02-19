from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import os

from database import engine, Base
from routers import admin, raters

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Human Rating Platform", version="1.0.0")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routers
app.include_router(admin.router)
app.include_router(raters.router)


@app.get("/health")
def health():
    return {"status": "healthy"}


# Serve static files (React build)
static_dir = os.path.join(os.path.dirname(__file__), "static")
if os.path.exists(static_dir):
    app.mount("/assets", StaticFiles(directory=os.path.join(static_dir, "assets")), name="assets")

    @app.get("/{full_path:path}")
    async def serve_spa(request: Request, full_path: str):
        # Serve index.html for all non-API routes (SPA routing)
        return FileResponse(os.path.join(static_dir, "index.html"))
