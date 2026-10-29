"""
Vercel Python runtime entry point.

Vercel's Python runtime looks for a root-level ``main.py`` exposing an ASGI
or WSGI ``app`` object. The FastAPI app lives in the ``app`` package
(``app.main:app``), so this shim simply re-exports it.

Run locally the same way:
    uvicorn main:app --reload
"""
from app.main import app  # noqa: F401  (re-export for the runtime)

__all__ = ["app"]