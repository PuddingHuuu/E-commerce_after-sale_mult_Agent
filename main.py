"""Optional convenience launcher.

The authoritative FastAPI application is defined in ``app/main.py``.
Run the project with ``uvicorn app.main:app`` or use a PyCharm FastAPI run
configuration. This file only exists so PyCharm can start the same app by
directly running the repository-root ``main.py``.
"""

from app.main import app

__all__ = ["app"]


if __name__ == "__main__":
    import uvicorn

    from app.core.config import settings

    uvicorn.run(
        "app.main:app",
        host=settings.api_host,
        port=settings.api_port,
    )

