"""
FLB Nuclear Power Plant AI Service
Main FastAPI application for AI model inference and monitoring.

This service provides REST API endpoints for:
- AI model predictions (classification and regression)
- Batch predictions
- Model information and health checks
- Request logging and error handling

Author: FLB Nuclear Power Plant Team
Version: 1.0.0
"""

import os
import sys
import time
from contextlib import asynccontextmanager
from pathlib import Path

import fastapi
from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn

# Add src directory to Python path for imports
src_path = str(Path(__file__).parent)
if src_path not in sys.path:
    sys.path.insert(0, src_path)

from models.model_manager import ModelManager
from api.prediction_routes import router as prediction_router, set_model_manager
from utils.logging_config import setup_development_logging, get_logger
from schemas.prediction_schemas import ErrorResponse

# Global variables
model_manager: ModelManager = None
app_start_time: float = time.time()

# Setup logging
setup_development_logging()
logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan manager.
    Handles startup and shutdown events for the FastAPI application.
    
    Args:
        app: FastAPI application instance
    """
    # Startup
    logger.info("Starting FLB Nuclear Power Plant AI Service...")
    
    try:
        # Initialize model manager with lazy loading
        models_dir = os.path.join(Path(__file__).parent.parent, "ai")
        
        # Check environment variables for configuration
        # Changed default to false to enable eager loading by default
        lazy_loading = os.getenv("LAZY_LOADING", "false").lower() == "true"
        preload_models = os.getenv("PRELOAD_MODELS", "false").lower() == "true"
        
        global model_manager
        model_manager = ModelManager(models_dir, lazy_loading=lazy_loading)
        
        # Set model manager in API routes
        set_model_manager(model_manager)
        
        # Get loading statistics
        stats = model_manager.get_loading_stats()
        logger.info(f"Model Manager initialized with lazy loading: {stats['lazy_loading_enabled']}")
        logger.info(f"Found {stats['total_available']} available models: {stats['available_models']}")
        
        if lazy_loading:
            logger.info(f"Lazy loading enabled - models will be loaded on first request")
            if preload_models:
                logger.info("Preloading all models due to PRELOAD_MODELS=true")
                model_manager.preload_all_models()
                updated_stats = model_manager.get_loading_stats()
                logger.info(f"Preloaded {updated_stats['total_loaded']} models")
        else:
            logger.info(f"Lazy loading disabled - loaded {stats['total_loaded']} models immediately")
        
        # Perform initial health check
        health_status = model_manager.health_check()
        logger.info(f"Initial health check: {health_status['status']}")
        
        logger.info("FLB Nuclear Power Plant AI Service started successfully!")
        
    except Exception as e:
        logger.error(f"Failed to start application: {str(e)}")
        raise
    
    yield
    
    # Shutdown
    logger.info("Shutting down FLB Nuclear Power Plant AI Service...")
    logger.info("Application shutdown complete")


# Create FastAPI application
app = FastAPI(
    title="FLB Nuclear Power Plant AI Service",
    description="""
    AI-powered prediction service for nuclear power plant monitoring and analysis.
    
    This service provides machine learning capabilities for:
    - **Classification**: Anomaly detection and status classification
    - **Regression**: Parameter prediction and trend analysis
    - **Batch Processing**: Multiple sample predictions
    - **Health Monitoring**: Service and model health checks
    
    ## Features
    - Real-time AI model inference using ONNX Runtime
    - Comprehensive input validation with Pydantic
    - Structured logging with request tracking
    - Error handling and recovery
    - Scalable architecture ready for production
    
    ## Models
    The service automatically loads and manages AI models from the configured directory.
    Currently supported model types:
    - Classification models (clf_model_*)
    - Regression models (reg_model_*)
    """,
    version="1.0.0",
    contact={
        "name": "FLB Nuclear Power Plant Team",
        "email": "support@flb-nuclear.com"
    },
    license_info={
        "name": "Proprietary",
        "url": "https://flb-nuclear.com/license"
    },
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Request logging middleware
@app.middleware("http")
async def log_requests(request: Request, call_next):
    """
    Middleware to log all HTTP requests and responses.
    
    Args:
        request: HTTP request
        call_next: Next middleware/endpoint
        
    Returns:
        Response: HTTP response
    """
    start_time = time.time()
    
    # Generate request ID
    request_id = f"req_{int(time.time() * 1000)}"
    
    # Log request start
    logger.info(
        f"Request started - {request.method} {request.url.path}",
        extra={'request_id': request_id, 'model_name': 'N/A'}
    )
    
    try:
        # Process request
        response = await call_next(request)
        
        # Calculate processing time
        processing_time = (time.time() - start_time) * 1000
        
        # Log request completion
        logger.info(
            f"Request completed - {request.method} {request.url.path} - "
            f"Status: {response.status_code} - Time: {processing_time:.2f}ms",
            extra={'request_id': request_id, 'model_name': 'N/A'}
        )
        
        return response
        
    except Exception as e:
        # Calculate processing time
        processing_time = (time.time() - start_time) * 1000
        
        # Log request error
        logger.error(
            f"Request failed - {request.method} {request.url.path} - "
            f"Error: {str(e)} - Time: {processing_time:.2f}ms",
            extra={'request_id': request_id, 'model_name': 'N/A'},
            exc_info=True
        )
        
        # Return error response
        return JSONResponse(
            status_code=500,
            content=ErrorResponse(
                error="Internal server error",
                error_type="ServerError",
                request_id=request_id
            ).dict()
        )


# Include API routes
app.include_router(prediction_router)


# Root endpoint
@app.get(
    "/",
    summary="Service information",
    description="Get basic information about the FLB Nuclear Power Plant AI Service."
)
async def root():
    """
    Root endpoint providing service information.
    
    Returns:
        dict: Service information and status
    """
    uptime_seconds = time.time() - app_start_time
    
    return {
        "service": "FLB Nuclear Power Plant AI Service",
        "version": "1.0.0",
        "status": "running",
        "uptime_seconds": round(uptime_seconds, 2),
        "models_loaded": len(model_manager.get_available_models()) if model_manager else 0,
        "endpoints": {
            "predictions": "/api/v1/predict",
            "batch_predictions": "/api/v1/predict/batch",
            "models": "/api/v1/models",
            "health": "/api/v1/health",
            "docs": "/docs",
            "redoc": "/redoc"
        }
    }


# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """
    Global exception handler for unhandled errors.
    
    Args:
        request: HTTP request
        exc: Exception that occurred
        
    Returns:
        JSONResponse: Error response
    """
    logger.error(
        f"Unhandled exception in {request.method} {request.url.path}: {str(exc)}",
        exc_info=True
    )
    
    return JSONResponse(
        status_code=500,
        content=ErrorResponse(
            error="Internal server error",
            error_type="UnhandledException"
        ).dict()
    )


# Development server runner
if __name__ == "__main__":
    """
    Run the development server.
    
    For production deployment, use a proper ASGI server like:
    uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
    """
    logger.info("Starting development server...")
    
    uvicorn.run(
        "main:app",
        host="127.0.0.1",
        port=8000,
        reload=True,
        log_level="info",
        access_log=True,
        reload_excludes=["*.onnx", "*.pyc", "__pycache__"],
        reload_delay=0.25  # Add small delay to prevent rapid reloads
    )
