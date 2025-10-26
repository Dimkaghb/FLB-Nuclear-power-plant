"""
API routes for AI model predictions in FLB Nuclear Power Plant system.
Provides endpoints for single and batch predictions, model information, and health checks.
"""

import time
from typing import List
from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.responses import JSONResponse

from utils.logging_config import get_logger

from models.model_manager import ModelManager
from schemas.prediction_schemas import (
    PredictionRequest, PredictionResponse, ErrorResponse,
    BatchPredictionRequest, BatchPredictionResponse,
    ModelsListResponse, ModelInfoResponse, HealthCheckResponse,
    ModelsVersionResponse, ModelVersionInfo,
    ReactorPredictionRequest, ReactorPredictionResponse
)

# Configure logging
logger = get_logger(__name__)

# Create router
router = APIRouter(prefix="/api/v1", tags=["predictions"])

# Global model manager instance (will be initialized in main.py)
model_manager: ModelManager = None


def get_model_manager() -> ModelManager:
    """
    Dependency to get the model manager instance.
    
    Returns:
        ModelManager: The global model manager instance
        
    Raises:
        HTTPException: If model manager is not initialized
    """
    if model_manager is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Model manager not initialized"
        )
    return model_manager


@router.post(
    "/predict",
    response_model=PredictionResponse,
    responses={
        400: {"model": ErrorResponse, "description": "Bad Request"},
        404: {"model": ErrorResponse, "description": "Model Not Found"},
        500: {"model": ErrorResponse, "description": "Internal Server Error"}
    },
    summary="Make a single prediction",
    description="Make a prediction using the specified AI model with provided features."
)
async def predict(
    request: PredictionRequest,
    manager: ModelManager = Depends(get_model_manager)
) -> PredictionResponse:
    """
    Make a single prediction using the specified model.
    
    Args:
        request: Prediction request containing model name and features
        manager: Model manager dependency
        
    Returns:
        PredictionResponse: Prediction results with metadata
        
    Raises:
        HTTPException: For various error conditions
    """
    start_time = time.time()
    
    try:
        logger.info(f"Received prediction request for model: {request.model_name}")
        logger.debug(f"Request details: {request.dict()}")
        
        # Make prediction
        result = manager.predict(request.model_name, request.features)
        
        # Calculate processing time
        processing_time = (time.time() - start_time) * 1000
        
        # Create response
        response = PredictionResponse(
            model_name=result["model_name"],
            predictions=result["predictions"],
            metadata=result["metadata"],
            request_id=request.request_id,
            processing_time_ms=processing_time
        )
        
        logger.info(f"Prediction completed successfully in {processing_time:.2f}ms")
        return response
        
    except ValueError as e:
        logger.warning(f"Validation error in prediction: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except FileNotFoundError as e:
        logger.error(f"Model not found: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Model '{request.model_name}' not found"
        )
    except Exception as e:
        logger.error(f"Unexpected error in prediction: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error during prediction"
        )


@router.post(
    "/predict/batch",
    response_model=BatchPredictionResponse,
    responses={
        400: {"model": ErrorResponse, "description": "Bad Request"},
        404: {"model": ErrorResponse, "description": "Model Not Found"},
        500: {"model": ErrorResponse, "description": "Internal Server Error"}
    },
    summary="Make batch predictions",
    description="Make predictions for multiple samples using the specified AI model."
)
async def predict_batch(
    request: BatchPredictionRequest,
    manager: ModelManager = Depends(get_model_manager)
) -> BatchPredictionResponse:
    """
    Make batch predictions using the specified model.
    
    Args:
        request: Batch prediction request containing model name and feature vectors
        manager: Model manager dependency
        
    Returns:
        BatchPredictionResponse: Batch prediction results
        
    Raises:
        HTTPException: For various error conditions
    """
    start_time = time.time()
    
    try:
        logger.info(f"Received batch prediction request for model: {request.model_name}, "
                   f"batch size: {len(request.batch_features)}")
        
        batch_predictions = []
        
        # Process each sample in the batch
        for i, features in enumerate(request.batch_features):
            try:
                result = manager.predict(request.model_name, features)
                batch_predictions.append(result["predictions"])
            except Exception as e:
                logger.error(f"Error processing batch item {i}: {str(e)}")
                raise ValueError(f"Error processing batch item {i}: {str(e)}")
        
        # Calculate processing time
        processing_time = (time.time() - start_time) * 1000
        
        # Create response
        response = BatchPredictionResponse(
            model_name=request.model_name,
            batch_predictions=batch_predictions,
            batch_size=len(request.batch_features),
            request_id=request.request_id,
            processing_time_ms=processing_time
        )
        
        logger.info(f"Batch prediction completed successfully in {processing_time:.2f}ms")
        return response
        
    except ValueError as e:
        logger.warning(f"Validation error in batch prediction: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Unexpected error in batch prediction: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error during batch prediction"
        )


@router.post(
    "/predict/reactor",
    response_model=ReactorPredictionResponse,
    responses={
        400: {"model": ErrorResponse, "description": "Bad Request"},
        404: {"model": ErrorResponse, "description": "Model Not Found"},
        500: {"model": ErrorResponse, "description": "Internal Server Error"}
    },
    summary="Make nuclear reactor prediction",
    description="Make a prediction for nuclear reactor parameters using AI models with feature engineering."
)
async def predict_reactor(
    request: ReactorPredictionRequest,
    manager: ModelManager = Depends(get_model_manager)
) -> ReactorPredictionResponse:
    """
    Make a nuclear reactor prediction using all control sidebar parameters.
    
    This endpoint processes nuclear reactor parameters from all categories:
    - Temperature parameters (RCS, fuel, pressurizer, etc.)
    - Pressure parameters (steam generator, pressurizer, RCS, etc.)
    - Flow parameters (coolant, feedwater, steam, leakage, etc.)
    - Reactivity parameters (boron, moderator, fuel, rod, total)
    - Radiation parameters (building, steam line, condenser, etc.)
    - Other parameters (power, volume, levels, etc.)
    
    The prediction includes feature engineering based on the original model approach
    and provides scenario classification, risk assessment, and safety recommendations.
    
    Args:
        request: ReactorPredictionRequest containing all reactor parameters
        manager: ModelManager dependency for model operations
        
    Returns:
        ReactorPredictionResponse with prediction results and metadata
        
    Raises:
        HTTPException: For various error conditions (400, 404, 500)
    """
    start_time = time.time()
    
    try:
        logger.info(f"Processing reactor prediction request: {request.request_id}")
        
        # Validate input parameters
        validation_errors = _validate_reactor_parameters(request)
        if validation_errors:
            raise ValueError(f"Input validation failed: {'; '.join(validation_errors)}")
        
        # Convert reactor parameters to dictionary format for feature engineering
        reactor_params = _convert_request_to_params_dict(request)
        
        # Use both models for comprehensive prediction
        clf_model_name = "clf_model_rf_v2"  # Classification model for scenario prediction
        reg_model_name = "reg_model_rf_v2"  # Regression model for time-to-event prediction
        
        # Check if both models exist
        available_models = manager.get_available_models()
        if clf_model_name not in available_models:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Classification model '{clf_model_name}' not found. Available models: {list(available_models.keys())}"
            )
        if reg_model_name not in available_models:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Regression model '{reg_model_name}' not found. Available models: {list(available_models.keys())}"
            )
        
        # Generate features for the prediction processing
        features = _convert_reactor_params_to_features(request)
        
        # Make predictions with both models using feature engineering
        clf_prediction_result = manager.predict_from_reactor_params(clf_model_name, reactor_params)
        reg_prediction_result = manager.predict_from_reactor_params(reg_model_name, reactor_params)
        
        # Process prediction results into reactor-specific format
        reactor_result = _process_reactor_prediction(clf_prediction_result, reg_prediction_result, features)
        
        # Calculate processing time
        processing_time = (time.time() - start_time) * 1000
        
        # Create response
        response = ReactorPredictionResponse(
            success=True,
            prediction=reactor_result,
            processing_time_ms=processing_time,
            request_id=request.request_id,
            timestamp=time.strftime("%Y-%m-%d %H:%M:%S UTC", time.gmtime())
        )
        
        logger.info(f"Reactor prediction completed successfully in {processing_time:.2f}ms")
        return response
        
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except ValueError as e:
        logger.warning(f"Validation error in reactor prediction: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Unexpected error in reactor prediction: {str(e)}")
        processing_time = (time.time() - start_time) * 1000
        
        # Return error response
        return ReactorPredictionResponse(
            success=False,
            prediction=None,
            processing_time_ms=processing_time,
            request_id=request.request_id,
            timestamp=time.strftime("%Y-%m-%d %H:%M:%S UTC", time.gmtime()),
            error=f"Internal server error: {str(e)}"
        )


@router.post(
    "/features/reset",
    summary="Reset feature engineering history",
    description="Reset the feature engineering history. Useful when starting a new prediction session."
)
async def reset_feature_history(
    manager: ModelManager = Depends(get_model_manager)
) -> dict:
    """
    Reset the feature engineering history.
    
    Args:
        manager: Model manager dependency
        
    Returns:
        dict: Success message
    """
    try:
        manager.reset_feature_history()
        logger.info("Feature history reset via API")
        return {"success": True, "message": "Feature engineering history reset successfully"}
    except Exception as e:
        logger.error(f"Error resetting feature history: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to reset feature history: {str(e)}"
        )


@router.get(
    "/features/names",
    summary="Get feature names",
    description="Get the complete list of 288 feature names used by the AI models."
)
async def get_feature_names(
    manager: ModelManager = Depends(get_model_manager)
) -> dict:
    """
    Get the complete list of feature names used by the models.
    
    Args:
        manager: Model manager dependency
        
    Returns:
        dict: List of feature names
    """
    try:
        feature_names = manager.get_feature_names()
        return {
            "success": True,
            "feature_count": len(feature_names),
            "feature_names": feature_names
        }
    except Exception as e:
        logger.error(f"Error getting feature names: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get feature names: {str(e)}"
        )


@router.get(
    "/models/versions",
    response_model=ModelsVersionResponse,
    summary="Get models by version",
    description="Get all available models grouped by their versions (v1, v2, etc.)."
)
async def get_models_by_version(
    version: str = None,
    manager: ModelManager = Depends(get_model_manager)
) -> ModelsVersionResponse:
    """
    Get models grouped by version.
    
    Args:
        version: Optional specific version to filter by (v1, v2, unknown)
        manager: Model manager dependency
        
    Returns:
        ModelsVersionResponse: Models grouped by version with detailed information
    """
    try:
        # Get models grouped by version
        models_by_version = manager.get_models_by_version(version)
        
        # Create detailed version info for each model
        detailed_models_by_version = {}
        total_models = 0
        
        for ver, model_names in models_by_version.items():
            if not model_names:  # Skip empty version groups
                continue
                
            detailed_models = []
            for model_name in model_names:
                # Get model metadata
                metadata = manager.get_model_info(model_name)
                model_version = manager.get_model_version(model_name)
                
                # Determine model type based on metadata or name
                model_type = "unknown"
                if metadata and "output_names" in metadata:
                    output_names = metadata["output_names"]
                    if any("class" in name.lower() or "label" in name.lower() or "probability" in name.lower() 
                           for name in output_names):
                        model_type = "classification"
                    elif any("variable" in name.lower() or "value" in name.lower() or "prediction" in name.lower() 
                             for name in output_names):
                        model_type = "regression"
                elif "clf" in model_name.lower() or "class" in model_name.lower():
                    model_type = "classification"
                elif "reg" in model_name.lower() or "regr" in model_name.lower():
                    model_type = "regression"
                
                # Determine features count (assuming 288 for v2 models based on our analysis)
                features_count = 288 if "v2" in model_name.lower() else 0
                if metadata and "input_shapes" in metadata and metadata["input_shapes"]:
                    try:
                        # Get the last dimension of the first input shape
                        input_shape = metadata["input_shapes"][0]
                        if len(input_shape) > 1:
                            features_count = input_shape[-1] if input_shape[-1] > 0 else 288
                    except (IndexError, TypeError):
                        pass
                
                model_info = ModelVersionInfo(
                    model_name=model_name,
                    version=model_version,
                    type=model_type,
                    features_count=features_count,
                    output_names=metadata["output_names"] if metadata else []
                )
                detailed_models.append(model_info)
                total_models += 1
            
            if detailed_models:  # Only add if there are models
                detailed_models_by_version[ver] = detailed_models
        
        response = ModelsVersionResponse(
            models_by_version=detailed_models_by_version,
            total_models=total_models
        )
        
        logger.info(f"Returned version info for {total_models} models across {len(detailed_models_by_version)} versions")
        return response
        
    except Exception as e:
        logger.error(f"Error getting models by version: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error retrieving models version information"
        )


@router.get(
    "/models",
    response_model=ModelsListResponse,
    summary="Get available models",
    description="Get a list of all available AI models."
)
async def get_models(
    manager: ModelManager = Depends(get_model_manager)
) -> ModelsListResponse:
    """
    Get list of available models.
    
    Args:
        manager: Model manager dependency
        
    Returns:
        ModelsListResponse: List of available model names
    """
    try:
        models = manager.get_available_models()
        
        response = ModelsListResponse(
            models=models,
            count=len(models)
        )
        
        logger.info(f"Returned list of {len(models)} available models")
        return response
        
    except Exception as e:
        logger.error(f"Error getting models list: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error retrieving models list"
        )


@router.get(
    "/models/{model_name}",
    response_model=ModelInfoResponse,
    responses={
        404: {"model": ErrorResponse, "description": "Model Not Found"}
    },
    summary="Get model information",
    description="Get detailed information about a specific AI model."
)
async def get_model_info(
    model_name: str,
    manager: ModelManager = Depends(get_model_manager)
) -> ModelInfoResponse:
    """
    Get information about a specific model.
    
    Args:
        model_name: Name of the model
        manager: Model manager dependency
        
    Returns:
        ModelInfoResponse: Model information
        
    Raises:
        HTTPException: If model not found
    """
    try:
        model_metadata = manager.get_model_info(model_name)
        
        if model_metadata is None:
            logger.warning(f"Model info requested for non-existent model: {model_name}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Model '{model_name}' not found"
            )
        
        # Convert model metadata to ModelInfo schema format
        # Handle dynamic dimensions in shapes by converting them to positive integers
        def normalize_shape(shape):
            """Convert shape list to handle dynamic dimensions (-1, None) and ensure all are integers."""
            normalized = []
            for dim in shape:
                if dim is None or dim == -1:
                    normalized.append(1)  # Replace dynamic dimension with 1 for display
                else:
                    try:
                        normalized.append(int(dim))
                    except (ValueError, TypeError):
                        # If conversion fails, use 1 as fallback
                        normalized.append(1)
            return normalized
        
        # Create ModelInfo object with proper field mapping
        from schemas.prediction_schemas import ModelInfo
        model_info = ModelInfo(
            name=model_name,  # Add the missing name field
            path=model_metadata["path"],
            input_names=model_metadata["input_names"],
            output_names=model_metadata["output_names"],
            input_shapes=[normalize_shape(shape) for shape in model_metadata["input_shapes"]],
            output_shapes=[normalize_shape(shape) for shape in model_metadata["output_shapes"]],
            input_types=model_metadata["input_types"],
            output_types=model_metadata["output_types"]
        )
        
        response = ModelInfoResponse(model_info=model_info)
        
        logger.info(f"Returned model info for: {model_name}")
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting model info for {model_name}: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error retrieving model information"
        )


@router.get(
    "/models/stats",
    summary="Get model loading statistics",
    description="Get statistics about model loading status, including loaded and available models."
)
async def get_loading_stats(
    manager: ModelManager = Depends(get_model_manager)
):
    """
    Get model loading statistics and status information.
    
    Returns:
        Dict: Loading statistics including:
        - lazy_loading_enabled: Whether lazy loading is enabled
        - total_available: Total number of available models
        - total_loaded: Total number of currently loaded models
        - available_models: List of all available model names
        - loaded_models: List of currently loaded model names
        - unloaded_models: List of models that are available but not loaded
    """
    try:
        stats = manager.get_loading_stats()
        return JSONResponse(
            status_code=200,
            content={
                "success": True,
                "stats": stats,
                "timestamp": time.time()
            }
        )
    except Exception as e:
        logger.error(f"Failed to get loading stats: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Error retrieving loading statistics"
        )


@router.post(
    "/models/preload",
    summary="Preload all models",
    description="Preload all available models into memory. Useful for production environments."
)
async def preload_models(
    manager: ModelManager = Depends(get_model_manager)
):
    """
    Preload all available models into memory.
    
    Returns:
        Dict: Result of preloading operation
    """
    try:
        initial_stats = manager.get_loading_stats()
        
        if not initial_stats["lazy_loading_enabled"]:
            return JSONResponse(
                status_code=200,
                content={
                    "success": True,
                    "message": "Lazy loading is disabled, all models are already loaded",
                    "stats": initial_stats,
                    "timestamp": time.time()
                }
            )
        
        manager.preload_all_models()
        final_stats = manager.get_loading_stats()
        
        return JSONResponse(
            status_code=200,
            content={
                "success": True,
                "message": f"Successfully preloaded {final_stats['total_loaded']} models",
                "stats": final_stats,
                "timestamp": time.time()
            }
        )
    except Exception as e:
        logger.error(f"Failed to preload models: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Error preloading models"
        )


@router.get(
    "/health",
    response_model=HealthCheckResponse,
    summary="Health check",
    description="Check the health status of the AI service and all loaded models."
)
async def health_check(
    manager: ModelManager = Depends(get_model_manager)
) -> HealthCheckResponse:
    """
    Perform health check on the service and all models.
    
    Args:
        manager: Model manager dependency
        
    Returns:
        HealthCheckResponse: Health status information
    """
    try:
        health_status = manager.health_check()
        
        response = HealthCheckResponse(
            status=health_status["status"],
            models_count=health_status["models_count"],
            models=health_status["models"]
        )
        
        logger.info(f"Health check completed: {health_status['status']}")
        return response
        
    except Exception as e:
        logger.error(f"Error during health check: {str(e)}")
        # Return degraded status instead of raising exception
        return HealthCheckResponse(
            status="error",
            models_count=0,
            models={"error": str(e)}
        )


def set_model_manager(manager: ModelManager) -> None:
    """
    Set the global model manager instance.
    
    Args:
        manager: ModelManager instance to set
    """
    global model_manager
    model_manager = manager
    logger.info("Model manager set successfully")


# Helper functions for reactor prediction

def _validate_reactor_parameters(request: ReactorPredictionRequest) -> List[str]:
    """
    Validate reactor parameters for safety and reasonableness.
    
    Args:
        request: ReactorPredictionRequest to validate
        
    Returns:
        List[str]: List of validation error messages (empty if valid)
    """
    errors = []
    
    # Temperature validation (in Celsius)
    temp = request.temperature
    
    # RCS temperatures should be reasonable for PWR operation
    if not (200 <= temp.averageRcsTemperature <= 400):
        errors.append(f"Average RCS temperature {temp.averageRcsTemperature}°C is outside safe range (200-400°C)")
    
    if not (250 <= temp.hotLegTemperatureA <= 450):
        errors.append(f"Hot leg A temperature {temp.hotLegTemperatureA}°C is outside safe range (250-450°C)")
    
    if not (250 <= temp.hotLegTemperatureB <= 450):
        errors.append(f"Hot leg B temperature {temp.hotLegTemperatureB}°C is outside safe range (250-450°C)")
    
    if not (200 <= temp.coldLegTemperatureA <= 350):
        errors.append(f"Cold leg A temperature {temp.coldLegTemperatureA}°C is outside safe range (200-350°C)")
    
    if not (200 <= temp.coldLegTemperatureB <= 350):
        errors.append(f"Cold leg B temperature {temp.coldLegTemperatureB}°C is outside safe range (200-350°C)")
    
    # Fuel temperatures
    if temp.peakFuelTemperature > 2000:
        errors.append(f"Peak fuel temperature {temp.peakFuelTemperature}°C exceeds safety limit (2000°C)")
    
    if temp.averageFuelTemperature > 1500:
        errors.append(f"Average fuel temperature {temp.averageFuelTemperature}°C exceeds safety limit (1500°C)")
    
    # Pressure validation (in bar)
    pressure = request.pressure
    
    # RCS pressure should be within operational range
    if not (50 <= pressure.rcsPressure <= 200):
        errors.append(f"RCS pressure {pressure.rcsPressure} bar is outside safe range (50-200 bar)")
    
    # Steam generator pressures
    if not (20 <= pressure.steamGeneratorPressureA <= 100):
        errors.append(f"SG A pressure {pressure.steamGeneratorPressureA} bar is outside safe range (20-100 bar)")
    
    if not (20 <= pressure.steamGeneratorPressureB <= 100):
        errors.append(f"SG B pressure {pressure.steamGeneratorPressureB} bar is outside safe range (20-100 bar)")
    
    # Pressurizer level (percentage)
    if not (0 <= pressure.pressurizerPressureLevel <= 100):
        errors.append(f"Pressurizer level {pressure.pressurizerPressureLevel}% is outside valid range (0-100%)")
    
    # Flow validation
    flow = request.flow
    
    # RCS flows should be positive and reasonable
    if flow.reactorCoolantFlowA < 0:
        errors.append("RCS flow A cannot be negative")
    
    if flow.reactorCoolantFlowB < 0:
        errors.append("RCS flow B cannot be negative")
    
    # Power validation
    other = request.other
    
    # Reactor power should be within 0-120% (allowing for slight overpowers)
    if not (0 <= other.reactorThermalPower <= 120):
        errors.append(f"Reactor thermal power {other.reactorThermalPower}% is outside safe range (0-120%)")
    
    if not (0 <= other.neutronFluxPower <= 120):
        errors.append(f"Neutron flux power {other.neutronFluxPower}% is outside safe range (0-120%)")
    
    # DNB ratio should be above 1.0 for safety
    if other.departureFromNucleateBoilingRatio < 1.0:
        errors.append(f"DNB ratio {other.departureFromNucleateBoilingRatio} is below safety limit (1.0)")
    
    # Reactivity validation
    reactivity = request.reactivity
    
    # Boron acid reactivity should be reasonable (pcm)
    if not (-5000 <= reactivity.boronAcidReactivity <= 0):
        errors.append(f"Boron acid reactivity {reactivity.boronAcidReactivity} pcm is outside valid range (-5000 to 0 pcm)")
    
    # Total reactivity should be small for stable operation
    if abs(reactivity.totalReactivity) > 10:
        errors.append(f"Total reactivity {reactivity.totalReactivity} is too large for stable operation (±10)")
    
    # Radiation validation
    radiation = request.radiation
    
    # Radiation levels should be positive
    if radiation.radiationInBuilding < 0:
        errors.append("Reactor building radiation cannot be negative")
    
    if radiation.rcsActivity < 0:
        errors.append("RCS activity cannot be negative")
    
    # I-131 concentration should be low for safety
    if radiation.i131ConcentrationInRcs > 10000:
        errors.append(f"I-131 concentration {radiation.i131ConcentrationInRcs} Bq/m³ exceeds safety limit (10000 Bq/m³)")
    
    return errors


def _convert_request_to_params_dict(request: ReactorPredictionRequest) -> dict:
    """
    Convert ReactorPredictionRequest to a parameters dictionary for feature engineering.
    
    Args:
        request: ReactorPredictionRequest containing all reactor parameters
        
    Returns:
        dict: Dictionary of reactor parameters for feature engineering
    """
    params = {}
    
    # Temperature parameters
    temp = request.temperature
    params.update({
        'timeSeconds': temp.timeSeconds,
        'averageRcsTemperature': temp.averageRcsTemperature,
        'hotLegTemperatureA': temp.hotLegTemperatureA,
        'hotLegTemperatureB': temp.hotLegTemperatureB,
        'coldLegTemperatureA': temp.coldLegTemperatureA,
        'coldLegTemperatureB': temp.coldLegTemperatureB,
        'pressurizerTemperature': temp.pressurizerTemperature,
        'reactorBuildingTemperature': temp.reactorBuildingTemperature,
        'submergedFuelTemperature': temp.submergedFuelTemperature,
        'peakFuelTemperature': temp.peakFuelTemperature,
        'averageFuelTemperature': temp.averageFuelTemperature,
        'peakFuelCladdingTemperature': temp.peakFuelCladdingTemperature,
        'debrisTemperatureInCavity': temp.debrisTemperatureInCavity,
        'debrisTemperatureInLowerPlenum': temp.debrisTemperatureInLowerPlenum,
        'moltenConcreteTemperature': temp.moltenConcreteTemperature
    })
    
    # Pressure parameters
    pressure = request.pressure
    params.update({
        'steamGeneratorAPressure': pressure.steamGeneratorPressureA,
        'steamGeneratorBPressure': pressure.steamGeneratorPressureB,
        'pressurizerLevel': pressure.pressurizerPressureLevel,
        'reactorBuildingPressure': pressure.reactorBuildingPressure,
        'rcsPressure': pressure.rcsPressure
    })
    
    # Flow parameters
    flow = request.flow
    params.update({
        'rcsFlowA': flow.reactorCoolantFlowA,
        'rcsFlowB': flow.reactorCoolantFlowB,
        'feedwaterFlowA': flow.steamGeneratorWaterFeedA,
        'feedwaterFlowB': flow.steamGeneratorWaterFeedB,
        'steamFlowA': flow.steamGeneratorSteamFlowA,
        'steamFlowB': flow.steamGeneratorSteamFlowB,
        'rcsLeakage': flow.rcsWaterLeakage,
        'chargingFlow': flow.makeupFlow
    })
    
    # Reactivity parameters
    reactivity = request.reactivity
    params.update({
        'boronConcentration': reactivity.boronAcidReactivity,
        'totalReactivity': reactivity.totalReactivity
    })
    
    # Radiation parameters
    radiation = request.radiation
    params.update({
        'radiationMonitor1': radiation.radiationInBuilding,
        'radiationMonitor2': radiation.radiationInSteamLine,
        'radiationMonitor3': radiation.condenserRadiation,
        'radiationMonitor4': radiation.auxiliaryBuildingRadiation,
        'rcsActivity': radiation.rcsActivity,
        'hydrogenConcentration': radiation.i131ConcentrationInRcs
    })
    
    # Other parameters
    other = request.other
    params.update({
        'reactorThermalPower': other.reactorThermalPower,
        'neutronPower': other.neutronFluxPower,
        'turbineLoad': other.turbineLoad,
        'coreWaterLevel': other.coreWaterLevel,
        'steamGeneratorALevel': other.sgWaterLevelAWideRange,
        'steamGeneratorBLevel': other.sgWaterLevelBWideRange,
        'dnbRatio': other.departureFromNucleateBoilingRatio
    })
    
    return params


def _convert_reactor_params_to_features(request: ReactorPredictionRequest) -> List[float]:
    """
    Convert reactor parameters to feature vector for model prediction.
    
    Args:
        request: ReactorPredictionRequest containing all reactor parameters
        
    Returns:
        List[float]: Feature vector for model prediction
    """
    features = []
    
    # Temperature parameters
    temp = request.temperature
    features.extend([
        temp.timeSeconds,
        temp.averageRcsTemperature,
        temp.hotLegTemperatureA,
        temp.hotLegTemperatureB,
        temp.coldLegTemperatureA,
        temp.coldLegTemperatureB,
        temp.pressurizerTemperature,
        temp.reactorBuildingTemperature,
        temp.submergedFuelTemperature,
        temp.peakFuelTemperature,
        temp.averageFuelTemperature,
        temp.peakFuelCladdingTemperature,
        temp.debrisTemperatureInCavity,
        temp.debrisTemperatureInLowerPlenum,
        temp.moltenConcreteTemperature
    ])
    
    # Pressure parameters
    pressure = request.pressure
    features.extend([
        pressure.steamGeneratorPressureA,
        pressure.steamGeneratorPressureB,
        pressure.pressurizerPressureLevel,
        pressure.reactorBuildingPressure,
        pressure.partialAirPressureRB,
        pressure.rcsPressure
    ])
    
    # Flow parameters
    flow = request.flow
    features.extend([
        flow.reactorCoolantFlowA,
        flow.reactorCoolantFlowB,
        flow.steamGeneratorWaterFeedA,
        flow.steamGeneratorWaterFeedB,
        flow.steamGeneratorSteamFlowA,
        flow.steamGeneratorSteamFlowB,
        flow.rcsWaterLeakage,
        flow.hpiFlow,
        flow.eccsFlow,
        flow.sgTubeLeakageA,
        flow.sgTubeLeakageB,
        flow.pressurizerSprayFlow,
        flow.containmentSprayFlow,
        flow.accumulatorFlow,
        flow.lpsiRhrFlow,
        flow.makeupFlow,
        flow.letdownFlow
    ])
    
    # Reactivity parameters
    reactivity = request.reactivity
    features.extend([
        reactivity.boronAcidReactivity,
        reactivity.moderatorTemperatureReactivity,
        reactivity.fuelReactivityDoppler,
        reactivity.rodReactivity,
        reactivity.totalReactivity
    ])
    
    # Radiation parameters
    radiation = request.radiation
    features.extend([
        radiation.radiationInBuilding,
        radiation.radiationInSteamLine,
        radiation.condenserRadiation,
        radiation.auxiliaryBuildingRadiation,
        radiation.rcsActivity,
        radiation.i131ConcentrationInRcs
    ])
    
    # Other parameters
    other = request.other
    features.extend([
        other.reactorThermalPower,
        other.turbineLoad,
        other.pressurizerHeaterPower,
        other.neutronFluxPower,
        other.rcsLiquidVolume,
        other.rcsAirVolume,
        other.sgWaterLevelAWideRange,
        other.sgWaterLevelBWideRange,
        other.sgHeatRemovalA,
        other.sgHeatRemovalB,
        other.coreWaterLevel,
        other.claddingDamageFraction,
        other.departureFromNucleateBoilingRatio,
        other.boronConcentrationInRCS
    ])
    
    return features


def _apply_feature_engineering(features: List[float]) -> List[float]:
    """
    Apply comprehensive feature engineering to expand 63 reactor parameters to 288 features.
    This follows the same pattern as the original training: for each parameter, create:
    - Original value
    - Rolling mean (window=3)
    - Difference (current - previous, simulated as small variation)
    
    Args:
        features: List of 63 input reactor parameters
        
    Returns:
        List of 288 enhanced features (63 * 3 + additional derived features)
    """
    import numpy as np
    
    if len(features) != 63:
        raise ValueError(f"Expected 63 features for engineering, got {len(features)}")
    
    enhanced_features = []
    
    # For each of the 63 parameters, create 3 features: original, rolling_mean, diff
    for i, feature_value in enumerate(features):
        # Original value
        enhanced_features.append(feature_value)
        
        # Rolling mean (simulated as slight smoothing)
        # In real-time, this would be calculated from historical data
        # For API calls, we simulate this as a small variation
        rolling_mean = feature_value * (1 + np.random.normal(0, 0.01))
        enhanced_features.append(rolling_mean)
        
        # Difference (simulated as rate of change)
        # In real-time, this would be current - previous value
        # For API calls, we simulate this as a small change
        diff_value = feature_value * np.random.normal(0, 0.05)
        enhanced_features.append(diff_value)
    
    # At this point we have 63 * 3 = 189 features
    # We need to add more derived features to reach 288
    
    # Add cross-parameter relationships and derived features
    # Temperature-related derived features (15 temperature params -> indices 0-14)
    if len(features) >= 15:
        temp_features = features[:15]
        # Temperature differences and averages
        avg_hot_leg = (temp_features[2] + temp_features[3]) / 2 if len(temp_features) > 3 else temp_features[0]
        avg_cold_leg = (temp_features[4] + temp_features[5]) / 2 if len(temp_features) > 5 else temp_features[0]
        enhanced_features.extend([
            avg_hot_leg,
            avg_cold_leg,
            avg_hot_leg - avg_cold_leg,
            max(temp_features),
            min(temp_features),
            np.mean(temp_features),
            np.std(temp_features) if len(temp_features) > 1 else 0.0
        ])
    
    # Pressure-related derived features (6 pressure params -> indices 15-20)
    if len(features) >= 21:
        pressure_features = features[15:21]
        enhanced_features.extend([
            max(pressure_features),
            min(pressure_features),
            np.mean(pressure_features),
            np.std(pressure_features) if len(pressure_features) > 1 else 0.0,
            pressure_features[0] - pressure_features[1] if len(pressure_features) > 1 else 0.0
        ])
    
    # Flow-related derived features (17 flow params -> indices 21-37)
    if len(features) >= 38:
        flow_features = features[21:38]
        total_flow = sum(flow_features)
        enhanced_features.extend([
            total_flow,
            max(flow_features),
            min(flow_features),
            np.mean(flow_features),
            np.std(flow_features) if len(flow_features) > 1 else 0.0,
            flow_features[0] + flow_features[1] if len(flow_features) > 1 else flow_features[0],  # Combined flows
            abs(flow_features[0] - flow_features[1]) if len(flow_features) > 1 else 0.0  # Flow imbalance
        ])
    
    # Reactivity-related derived features (5 reactivity params -> indices 38-42)
    if len(features) >= 43:
        reactivity_features = features[38:43]
        total_reactivity = sum(reactivity_features)
        enhanced_features.extend([
            total_reactivity,
            max(reactivity_features),
            min(reactivity_features),
            np.mean(reactivity_features),
            abs(total_reactivity)  # Absolute reactivity
        ])
    
    # Radiation-related derived features (6 radiation params -> indices 43-48)
    if len(features) >= 49:
        radiation_features = features[43:49]
        enhanced_features.extend([
            max(radiation_features),
            min(radiation_features),
            np.mean(radiation_features),
            sum(radiation_features),
            np.std(radiation_features) if len(radiation_features) > 1 else 0.0
        ])
    
    # Other parameters derived features (14 other params -> indices 49-62)
    if len(features) >= 63:
        other_features = features[49:63]
        enhanced_features.extend([
            max(other_features),
            min(other_features),
            np.mean(other_features),
            np.std(other_features) if len(other_features) > 1 else 0.0,
            sum(other_features[:7]),  # First half sum
            sum(other_features[7:])   # Second half sum
        ])
    
    # Add additional polynomial and interaction features to reach exactly 288
    current_count = len(enhanced_features)
    remaining_needed = 288 - current_count
    
    if remaining_needed > 0:
        # Add polynomial features (squares, cubes) of key parameters
        key_indices = [0, 1, 15, 16, 21, 22, 38, 43, 49]  # Key representative parameters
        for i in range(min(remaining_needed // 2, len(key_indices))):
            if i < len(features):
                enhanced_features.append(features[key_indices[i % len(key_indices)]] ** 2)
                if len(enhanced_features) < 288:
                    enhanced_features.append(features[key_indices[i % len(key_indices)]] ** 0.5)
    
    # Fill remaining slots with interaction terms
    current_count = len(enhanced_features)
    remaining_needed = 288 - current_count
    
    if remaining_needed > 0:
        # Add interaction terms between different parameter groups
        for i in range(remaining_needed):
            idx1 = i % len(features)
            idx2 = (i + 1) % len(features)
            interaction = features[idx1] * features[idx2] * 0.001  # Small scaling factor
            enhanced_features.append(interaction)
    
    # Ensure exactly 288 features
    enhanced_features = enhanced_features[:288]
    
    # Pad with zeros if somehow we're still short
    while len(enhanced_features) < 288:
        enhanced_features.append(0.0)
    
    return enhanced_features


def _extract_model_prediction(prediction_result: dict) -> dict:
    """
    Extract prediction information from model result, handling both classification and regression models.
    
    Args:
        prediction_result: Raw prediction result from model
        
    Returns:
        dict: Extracted prediction information with standardized keys
    """
    extracted = {
        'predicted_class': 0,
        'predicted_value': 0.0,
        'confidence': 0.5,
        'probabilities': []
    }
    
    if not isinstance(prediction_result, dict):
        return extracted
    
    predictions = prediction_result.get('predictions', [])
    if not predictions:
        return extracted
    
    # Get the first prediction
    prediction = predictions[0]
    
    if prediction.get('type') == 'classification':
        # Classification model
        extracted['predicted_class'] = prediction.get('predicted_class', 0)
        extracted['confidence'] = prediction.get('confidence', 0.5)
        extracted['probabilities'] = prediction.get('probabilities', [])
    elif prediction.get('type') == 'regression':
        # Regression model
        extracted['predicted_value'] = prediction.get('predicted_value', 0.0)
        extracted['confidence'] = prediction.get('confidence', 0.5)
    elif prediction.get('type') == 'binary_classification':
        # Binary classification
        extracted['predicted_class'] = prediction.get('predicted_class', 0)
        extracted['confidence'] = prediction.get('confidence', 0.5)
        probability = prediction.get('probability', 0.5)
        extracted['probabilities'] = [1-probability, probability] if extracted['predicted_class'] == 1 else [probability, 1-probability]
    else:
        # Fallback: try to extract any available values
        extracted['predicted_class'] = prediction.get('predicted_class', 0)
        extracted['predicted_value'] = prediction.get('predicted_value', 0.0)
        extracted['confidence'] = prediction.get('confidence', 0.5)
    
    return extracted


def _process_reactor_prediction(clf_prediction_result: dict, reg_prediction_result: dict, features: List[float]) -> 'ReactorPredictionResult':
    """
    Process raw model predictions into reactor-specific result format.
    
    Args:
        clf_prediction_result: Raw prediction result from classification model
        reg_prediction_result: Raw prediction result from regression model
        features: Feature vector used for prediction
        
    Returns:
        ReactorPredictionResult: Processed reactor prediction result
    """
    from schemas.prediction_schemas import ReactorPredictionResult
    
    # Extract classification prediction and confidence
    clf_prediction = _extract_model_prediction(clf_prediction_result)
    scenario_prediction = clf_prediction.get('predicted_class', 0)
    scenario_confidence = clf_prediction.get('confidence', 0.5)
    
    # Extract regression prediction (time to event)
    reg_prediction = _extract_model_prediction(reg_prediction_result)
    time_to_event_raw = reg_prediction.get('predicted_value', 0.0)
    
    # Map prediction to scenario
    scenario_map = {
        0: "Normal",
        1: "Pre-Event", 
        2: "Event"
    }
    
    scenario = scenario_map.get(int(scenario_prediction), "Unknown")
    
    # Determine risk level based on scenario and confidence
    if scenario == "Normal":
        if scenario_confidence > 0.8:
            risk_level = "Low"
        else:
            risk_level = "Medium"
    elif scenario == "Pre-Event":
        risk_level = "High"
    else:  # Event
        risk_level = "Critical"
    
    # Generate recommendations based on scenario
    recommendations = _generate_safety_recommendations(scenario, features)
    
    # Process time to event prediction
    time_to_event = None
    if scenario in ["Pre-Event", "Event"]:
        # Use regression model prediction for time to event
        # Convert to reasonable time range (seconds)
        time_to_event = max(60, min(3600, abs(float(time_to_event_raw))))  # 1 minute to 1 hour
    
    # Generate feature importance (simplified)
    feature_importance = _calculate_feature_importance(features)
    
    return ReactorPredictionResult(
        scenario_prediction=scenario,
        scenario_confidence=float(scenario_confidence),
        time_to_event_prediction=time_to_event,
        risk_level=risk_level,
        recommendations=recommendations,
        feature_importance=feature_importance
    )


def _generate_safety_recommendations(scenario: str, features: List[float]) -> List[str]:
    """
    Generate safety recommendations based on prediction scenario and parameters.
    
    Args:
        scenario: Predicted scenario (Normal, Pre-Event, Event)
        features: Feature vector for analysis
        
    Returns:
        List[str]: Safety recommendations
    """
    recommendations = []
    
    if scenario == "Normal":
        recommendations.extend([
            "Continue normal operations",
            "Monitor all parameters within normal ranges",
            "Perform routine maintenance checks"
        ])
    elif scenario == "Pre-Event":
        recommendations.extend([
            "Increase monitoring frequency",
            "Verify safety system availability",
            "Consider reducing power level",
            "Alert operations staff",
            "Review emergency procedures"
        ])
    else:  # Event
        recommendations.extend([
            "IMMEDIATE ACTION REQUIRED",
            "Activate emergency procedures",
            "Notify emergency response team",
            "Consider reactor shutdown",
            "Evacuate non-essential personnel"
        ])
    
    # Add parameter-specific recommendations
    if len(features) >= 15:
        # Temperature checks
        if features[9] > 500:  # Peak fuel temperature
            recommendations.append("Monitor fuel temperature closely - approaching limits")
        if features[6] > 400:  # Pressurizer temperature
            recommendations.append("Check pressurizer heater operation")
    
    if len(features) >= 21:
        # Pressure checks
        if features[20] < 100:  # RCS pressure
            recommendations.append("Investigate RCS pressure loss")
    
    return recommendations


def _calculate_feature_importance(features: List[float]) -> dict:
    """
    Calculate simplified feature importance for the prediction.
    
    Args:
        features: Feature vector
        
    Returns:
        dict: Feature importance scores
    """
    # Simplified feature importance based on parameter criticality
    feature_names = [
        "timeSeconds", "averageRcsTemperature", "hotLegTemperatureA", "hotLegTemperatureB",
        "coldLegTemperatureA", "coldLegTemperatureB", "pressurizerTemperature", 
        "reactorBuildingTemperature", "submergedFuelTemperature", "peakFuelTemperature",
        "averageFuelTemperature", "peakFuelCladdingTemperature", "debrisTemperatureInCavity",
        "debrisTemperatureInLowerPlenum", "moltenConcreteTemperature", "steamGeneratorPressureA",
        "steamGeneratorPressureB", "pressurizerPressureLevel", "reactorBuildingPressure",
        "partialAirPressureRB", "rcsPressure"
    ]
    
    # Critical parameters get higher importance
    critical_params = {
        "peakFuelTemperature": 0.15,
        "rcsPressure": 0.12,
        "averageRcsTemperature": 0.10,
        "pressurizerPressureLevel": 0.08,
        "neutronFluxPower": 0.08,
        "reactorThermalPower": 0.07
    }
    
    importance = {}
    for i, name in enumerate(feature_names[:len(features)]):
        if name in critical_params:
            importance[name] = critical_params[name]
        else:
            importance[name] = 0.02  # Base importance
    
    return importance