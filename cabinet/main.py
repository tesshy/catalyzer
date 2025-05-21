"""Main FastAPI application for Catalyzer::Cabinet."""

import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional

from .routers import catalogs

# Create FastAPI app
app = FastAPI(
    title="Catalyzer::Cabinet",
    description="Catalog System for Datalake",
    version="0.1.0",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
from .routers.catalogs import router as catalogs_router
app.include_router(catalogs_router)


@app.get("/")
async def root(url: Optional[str] = None):
    """Root endpoint.
    
    When url parameter is provided, it fetches content from the URL
    and creates a catalog markdown file.
    """
    # URLがない場合は通常のウェルカムメッセージを返す
    if url is None:
        return {"message": "Welcome to Catalyzer::Cabinet"}
        
    # URLが指定されている場合は、カタログルーターのurlから目録作成エンドポイントにリダイレクト
    from fastapi.responses import RedirectResponse
    return RedirectResponse(f"/from_url?url={url}")


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}


# Run the app with uvicorn if executed directly
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "cabinet.main:app",
        host="0.0.0.0",
        port=int(os.getenv("PORT", "8000")),
        reload=True,
    )