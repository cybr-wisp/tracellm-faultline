"""FastAPI backend for the faultline research dashboard.

TODO (Day 35): Implement endpoints for experiments, runs, metrics, traces, and comparisons.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="tracellm-faultline",
    description="API for the faultline agent reliability evaluation dashboard.",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # Vite dev server
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok", "version": "0.1.0"}
