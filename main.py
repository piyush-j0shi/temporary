"""Main application file.

This file initializes the FastAPI application, includes the API router,
and defines the root and health check endpoints.
"""

import logging
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from dotenv import load_dotenv
from api.routes import router as api_router


load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="nemotron",
    description="70B Instruct",
)

# app.mount("/static", StaticFiles(directory="static"), name="static")
# templates = Jinja2Templates(directory="templates")
app.include_router(api_router, prefix="/api")


@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    """Serve the main chat interface.

    Args:
        request: The incoming request.

    Returns:
        The root path.
    """
    # return templates.TemplateResponse("index.html", {"request": request})
    return "/"


@app.get("/health")
async def health_check():
    """Health check endpoint.

    Returns:
        A dictionary with the status of the application.
    """
    return {"status": "healthy", "message": "AI Chat Assistant is running"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )