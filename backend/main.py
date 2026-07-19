"""
Main FastAPI Application Entry Point
MongoDB + Pinecone RAG Architecture
"""
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
from loguru import logger
import time

from app.core.config import settings
from app.core.database import connect_to_mongodb, close_mongodb_connection
from app.api.v1.api import api_router

# Configure logger
logger.add(
    "logs/app.log",
    rotation="500 MB",
    retention="10 days",
    level="INFO",
    format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {message}"
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events"""
    logger.info("Starting AI Study Assistant API with MongoDB + Pinecone...")
    
    # Connect to MongoDB
    await connect_to_mongodb()
    logger.info("MongoDB connected and Beanie initialized")
    
    # Initialize Pinecone (done in vector_store service)
    from app.services.rag.vector_store import vector_store
    logger.info(f"Pinecone connected: {vector_store.index_name}")
    
    yield
    
    logger.info("Shutting down AI Study Assistant API...")
    await close_mongodb_connection()


# Initialize FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    description="RAG-based Smart Exam Preparation Platform with MongoDB + Pinecone",
    version=settings.API_VERSION,
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    lifespan=lifespan
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Request timing middleware
@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    return response


# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Global exception: {exc}")
    return JSONResponse(
        status_code=500,
        content={
            "detail": "Internal server error",
            "message": str(exc) if settings.DEBUG else "Something went wrong"
        }
    )


# Include API routes
app.include_router(api_router, prefix=f"/api/{settings.API_VERSION}")


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "AI Study Assistant API",
        "version": settings.API_VERSION,
        "status": "running",
        "architecture": "MongoDB + Pinecone RAG",
        "docs": "/api/docs"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    from app.services.rag.vector_store import vector_store
    
    # Check Pinecone stats
    vector_stats = vector_store.get_stats()
    
    return {
        "status": "healthy",
        "version": settings.API_VERSION,
        "database": "MongoDB",
        "vector_db": "Pinecone",
        "vector_stats": vector_stats
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG
    )
