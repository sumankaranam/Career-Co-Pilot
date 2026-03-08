from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .database import init_db
from .routers import alignment_router, job_router, outreach_router, resume_router

# Load environment variables from .env file
env_path = Path(__file__).resolve().parents[1] / ".env"
load_dotenv(env_path)


def create_app() -> FastAPI:
    app = FastAPI(title="Career Co-Pilot API", version="0.1.0")

    # CORS for local frontend dev
    origins = [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ]

    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(resume_router.router)
    app.include_router(job_router.router)
    app.include_router(alignment_router.router)
    app.include_router(outreach_router.router)

    @app.get("/")
    async def root() -> dict[str, str]:
        return {"status": "ok", "message": "Career Co-Pilot backend is running."}

    return app


init_db()
app = create_app()

