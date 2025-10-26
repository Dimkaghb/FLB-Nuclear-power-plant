"""
Pydantic schemas for API request and response validation
for FLB Nuclear Power Plant AI prediction service.
"""

from typing import List, Dict, Any, Optional, Union
from pydantic import BaseModel, Field, validator, ConfigDict
from datetime import datetime
      

class PredictionRequest(BaseModel):
    """
    Schema for prediction request containing input features.
    """
    model_config = ConfigDict(protected_namespaces=())
    
    model_name: str = Field(
        ..., 
        description="Name of the AI model to use for prediction",
        example="clf_model_rf_v2"
    )
    features: List[float] = Field(
        ..., 
        description="List of numerical features for prediction",
        min_items=1,
        example=[1.2, 3.4, 5.6, 7.8, 9.0]
    )
    request_id: Optional[str] = Field(
        None,
        description="Optional unique identifier for the request",
        example="req_123456789"
    )
    
    @validator('features')
    def validate_features(cls, v):
        """Validate that all features are finite numbers."""
        for i, feature in enumerate(v):
            if not isinstance(feature, (int, float)):
                raise ValueError(f"Feature at index {i} must be a number")
            if not (-1e10 <= feature <= 1e10):  # Reasonable bounds
                raise ValueError(f"Feature at index {i} is out of reasonable bounds")
        return v
    
    @validator('model_name')
    def validate_model_name(cls, v):
        """Validate model name format."""
        if not v or not isinstance(v, str):
            raise ValueError("Model name must be a non-empty string")
        if len(v) > 100:
            raise ValueError("Model name too long (max 100 characters)")
        return v.strip()


class ClassificationPrediction(BaseModel):
    """
    Schema for classification prediction results.
    """
    type: str = Field(default="classification", description="Type of prediction")
    output_name: str = Field(..., description="Name of the model output")
    predicted_class: int = Field(..., description="Predicted class index")
    probabilities: List[float] = Field(..., description="Class probabilities")
    confidence: float = Field(..., description="Confidence score (0-1)")


class BinaryClassificationPrediction(BaseModel):
    """
    Schema for binary classification prediction results.
    """
    type: str = Field(default="binary_classification", description="Type of prediction")
    output_name: str = Field(..., description="Name of the model output")
    predicted_class: int = Field(..., description="Predicted class (0 or 1)")
    probability: float = Field(..., description="Probability of positive class")
    confidence: float = Field(..., description="Confidence score (0-1)")


class RegressionPrediction(BaseModel):
    """
    Schema for regression prediction results.
    """
    type: str = Field(default="regression", description="Type of prediction")
    output_name: str = Field(..., description="Name of the model output")
    predicted_values: List[float] = Field(..., description="Predicted numerical values")


class PredictionMetadata(BaseModel):
    """
    Schema for prediction metadata.
    """
    input_shape: List[int] = Field(..., description="Shape of input data")
    output_names: List[str] = Field(..., description="Names of model outputs")


class PredictionResponse(BaseModel):
    """
    Schema for prediction response.
    """
    model_config = ConfigDict(protected_namespaces=())
    
    success: bool = Field(default=True, description="Whether prediction was successful")
    model_name: str = Field(..., description="Name of the model used")
    predictions: List[Union[ClassificationPrediction, BinaryClassificationPrediction, RegressionPrediction]] = Field(
        ..., description="List of prediction results"
    )
    metadata: PredictionMetadata = Field(..., description="Prediction metadata")
    request_id: Optional[str] = Field(None, description="Request identifier if provided")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Prediction timestamp")
    processing_time_ms: Optional[float] = Field(None, description="Processing time in milliseconds")


class ErrorResponse(BaseModel):
    """
    Schema for error responses.
    """
    success: bool = Field(default=False, description="Always false for error responses")
    error: str = Field(..., description="Error message")
    error_type: str = Field(..., description="Type of error")
    request_id: Optional[str] = Field(None, description="Request identifier if provided")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Error timestamp")


class ModelInfo(BaseModel):
    """
    Schema for model information.
    """
    name: str = Field(..., description="Model name")
    path: str = Field(..., description="Path to model file")
    input_names: List[str] = Field(..., description="Names of model inputs")
    output_names: List[str] = Field(..., description="Names of model outputs")
    input_shapes: List[List[int]] = Field(..., description="Shapes of model inputs")
    output_shapes: List[List[int]] = Field(..., description="Shapes of model outputs")
    input_types: List[str] = Field(..., description="Types of model inputs")
    output_types: List[str] = Field(..., description="Types of model outputs")


class ModelsListResponse(BaseModel):
    """
    Schema for available models list response.
    """
    success: bool = Field(default=True, description="Whether request was successful")
    models: List[str] = Field(..., description="List of available model names")
    count: int = Field(..., description="Number of available models")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Response timestamp")


class ModelInfoResponse(BaseModel):
    """
    Schema for model information response.
    """
    model_config = ConfigDict(protected_namespaces=())
    
    success: bool = Field(default=True, description="Whether request was successful")
    model_info: Optional[ModelInfo] = Field(None, description="Model information")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Response timestamp")


class HealthCheckResponse(BaseModel):
    """
    Schema for health check response.
    """
    success: bool = Field(default=True, description="Whether health check passed")
    status: str = Field(..., description="Overall health status")
    models_count: int = Field(..., description="Number of loaded models")
    models: Dict[str, str] = Field(..., description="Health status of each model")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Health check timestamp")
    uptime_seconds: Optional[float] = Field(None, description="Server uptime in seconds")


class ModelVersionInfo(BaseModel):
    """
    Schema for model version information.
    """
    model_name: str = Field(..., description="Name of the model")
    version: str = Field(..., description="Version of the model (v1, v2, unknown)")
    type: str = Field(..., description="Type of model (classification, regression)")
    features_count: int = Field(..., description="Number of input features required")
    output_names: List[str] = Field(..., description="Names of model outputs")


class ModelsVersionResponse(BaseModel):
    """
    Schema for models version information response.
    """
    success: bool = Field(default=True, description="Whether request was successful")
    models_by_version: Dict[str, List[ModelVersionInfo]] = Field(
        ..., description="Models grouped by version"
    )
    total_models: int = Field(..., description="Total number of models")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Response timestamp")


# Nuclear Reactor Prediction Schemas
class ReactorTemperatureParameters(BaseModel):
    """Temperature-related reactor parameters"""
    timeSeconds: Optional[float] = Field(default=0.0, description="Time in seconds")
    averageRcsTemperature: Optional[float] = Field(default=300.0, description="Average RCS temperature (°C)")
    hotLegTemperatureA: Optional[float] = Field(default=320.0, description="Hot leg temperature A (°C)")
    hotLegTemperatureB: Optional[float] = Field(default=320.0, description="Hot leg temperature B (°C)")
    coldLegTemperatureA: Optional[float] = Field(default=280.0, description="Cold leg temperature A (°C)")
    coldLegTemperatureB: Optional[float] = Field(default=280.0, description="Cold leg temperature B (°C)")
    pressurizerTemperature: Optional[float] = Field(default=350.0, description="Pressurizer temperature (°C)")
    reactorBuildingTemperature: Optional[float] = Field(default=25.0, description="Reactor building temperature (°C)")
    submergedFuelTemperature: Optional[float] = Field(default=400.0, description="Submerged fuel temperature (°C)")
    peakFuelTemperature: Optional[float] = Field(default=450.0, description="Peak fuel temperature (°C)")
    averageFuelTemperature: Optional[float] = Field(default=425.0, description="Average fuel temperature (°C)")
    peakFuelCladdingTemperature: Optional[float] = Field(default=380.0, description="Peak fuel cladding temperature (°C)")
    debrisTemperatureInCavity: Optional[float] = Field(default=0.0, description="Debris temperature in cavity (°C)")
    debrisTemperatureInLowerPlenum: Optional[float] = Field(default=0.0, description="Debris temperature in lower plenum (°C)")
    moltenConcreteTemperature: Optional[float] = Field(default=0.0, description="Molten concrete temperature (°C)")

class ReactorPressureParameters(BaseModel):
    """Pressure-related reactor parameters"""
    steamGeneratorPressureA: Optional[float] = Field(default=70.0, description="Steam generator pressure A (bar)")
    steamGeneratorPressureB: Optional[float] = Field(default=70.0, description="Steam generator pressure B (bar)")
    pressurizerPressureLevel: Optional[float] = Field(default=155.0, description="Pressurizer pressure level (bar)")
    reactorBuildingPressure: Optional[float] = Field(default=1.0, description="Reactor building pressure (bar)")
    partialAirPressureRB: Optional[float] = Field(default=1.0, description="Partial air pressure RB (bar)")
    rcsPressure: Optional[float] = Field(default=155.0, description="RCS pressure (bar)")

class ReactorFlowParameters(BaseModel):
    """Flow-related reactor parameters"""
    reactorCoolantFlowA: Optional[float] = Field(default=1000.0, description="Reactor coolant flow A (kg/s)")
    reactorCoolantFlowB: Optional[float] = Field(default=1000.0, description="Reactor coolant flow B (kg/s)")
    steamGeneratorWaterFeedA: Optional[float] = Field(default=500.0, description="Steam generator water feed A (kg/s)")
    steamGeneratorWaterFeedB: Optional[float] = Field(default=500.0, description="Steam generator water feed B (kg/s)")
    steamGeneratorSteamFlowA: Optional[float] = Field(default=500.0, description="Steam generator steam flow A (kg/s)")
    steamGeneratorSteamFlowB: Optional[float] = Field(default=500.0, description="Steam generator steam flow B (kg/s)")
    rcsWaterLeakage: Optional[float] = Field(default=0.0, description="RCS water leakage (kg/s)")
    hpiFlow: Optional[float] = Field(default=0.0, description="HPI flow (kg/s)")
    eccsFlow: Optional[float] = Field(default=0.0, description="ECCS flow (kg/s)")
    sgTubeLeakageA: Optional[float] = Field(default=0.0, description="SG tube leakage A (kg/s)")
    sgTubeLeakageB: Optional[float] = Field(default=0.0, description="SG tube leakage B (kg/s)")
    pressurizerSprayFlow: Optional[float] = Field(default=0.0, description="Pressurizer spray flow (kg/s)")
    containmentSprayFlow: Optional[float] = Field(default=0.0, description="Containment spray flow (kg/s)")
    accumulatorFlow: Optional[float] = Field(default=0.0, description="Accumulator flow (kg/s)")
    lpsiRhrFlow: Optional[float] = Field(default=0.0, description="LPSI RHR flow (kg/s)")
    makeupFlow: Optional[float] = Field(default=0.0, description="Makeup flow (kg/s)")
    letdownFlow: Optional[float] = Field(default=0.0, description="Letdown flow (kg/s)")

class ReactorReactivityParameters(BaseModel):
    """Reactivity-related reactor parameters"""
    boronAcidReactivity: Optional[float] = Field(default=0.0, description="Boron acid reactivity (pcm)")
    moderatorTemperatureReactivity: Optional[float] = Field(default=0.0, description="Moderator temperature reactivity (pcm)")
    fuelReactivityDoppler: Optional[float] = Field(default=0.0, description="Fuel reactivity Doppler (pcm)")
    rodReactivity: Optional[float] = Field(default=0.0, description="Rod reactivity (pcm)")
    totalReactivity: Optional[float] = Field(default=0.0, description="Total reactivity (pcm)")

class ReactorRadiationParameters(BaseModel):
    """Radiation-related reactor parameters"""
    radiationInBuilding: Optional[float] = Field(default=0.1, description="Radiation in building (mSv/h)")
    radiationInSteamLine: Optional[float] = Field(default=0.1, description="Radiation in steam line (mSv/h)")
    condenserRadiation: Optional[float] = Field(default=0.1, description="Condenser radiation (mSv/h)")
    auxiliaryBuildingRadiation: Optional[float] = Field(default=0.1, description="Auxiliary building radiation (mSv/h)")
    rcsActivity: Optional[float] = Field(default=1000.0, description="RCS activity (Bq/m³)")
    i131ConcentrationInRcs: Optional[float] = Field(default=100.0, description="I-131 concentration in RCS (Bq/m³)")

class ReactorOtherParameters(BaseModel):
    """Other reactor parameters"""
    reactorThermalPower: Optional[float] = Field(default=3000.0, description="Reactor thermal power (MW)")
    turbineLoad: Optional[float] = Field(default=1000.0, description="Turbine load (MW)")
    pressurizerHeaterPower: Optional[float] = Field(default=100.0, description="Pressurizer heater power (kW)")
    neutronFluxPower: Optional[float] = Field(default=100.0, description="Neutron flux power (%)")
    rcsLiquidVolume: Optional[float] = Field(default=300.0, description="RCS liquid volume (m³)")
    rcsAirVolume: Optional[float] = Field(default=50.0, description="RCS air volume (m³)")
    sgWaterLevelAWideRange: Optional[float] = Field(default=50.0, description="SG water level A wide range (%)")
    sgWaterLevelBWideRange: Optional[float] = Field(default=50.0, description="SG water level B wide range (%)")
    sgHeatRemovalA: Optional[float] = Field(default=1500.0, description="SG heat removal A (MW)")
    sgHeatRemovalB: Optional[float] = Field(default=1500.0, description="SG heat removal B (MW)")
    coreWaterLevel: Optional[float] = Field(default=100.0, description="Core water level (%)")
    claddingDamageFraction: Optional[float] = Field(default=0.0, description="Cladding damage fraction")
    departureFromNucleateBoilingRatio: Optional[float] = Field(default=2.0, description="Departure from nucleate boiling ratio")
    boronConcentrationInRCS: Optional[float] = Field(default=1000.0, description="Boron concentration in RCS (ppm)")

class ReactorPredictionRequest(BaseModel):
    """Request for nuclear reactor prediction"""
    temperature: ReactorTemperatureParameters = Field(default_factory=ReactorTemperatureParameters)
    pressure: ReactorPressureParameters = Field(default_factory=ReactorPressureParameters)
    flow: ReactorFlowParameters = Field(default_factory=ReactorFlowParameters)
    reactivity: ReactorReactivityParameters = Field(default_factory=ReactorReactivityParameters)
    radiation: ReactorRadiationParameters = Field(default_factory=ReactorRadiationParameters)
    other: ReactorOtherParameters = Field(default_factory=ReactorOtherParameters)
    request_id: Optional[str] = Field(default=None, description="Optional request identifier")
    model_name: Optional[str] = Field(default="clf_model_rf_v2", description="Model to use for prediction")
    include_feature_engineering: Optional[bool] = Field(default=True, description="Apply feature engineering (rolling mean, diff)")

class ReactorPredictionResult(BaseModel):
    """Result of reactor prediction"""
    scenario_prediction: str = Field(..., description="Predicted scenario (Normal, Pre-Event, Event)")
    scenario_confidence: float = Field(..., description="Confidence in scenario prediction")
    time_to_event_prediction: Optional[float] = Field(default=None, description="Predicted time to event (seconds)")
    risk_level: str = Field(..., description="Risk level (Low, Medium, High, Critical)")
    recommendations: List[str] = Field(default_factory=list, description="Safety recommendations")
    feature_importance: Optional[Dict[str, float]] = Field(default=None, description="Top feature importances")

class ReactorPredictionResponse(BaseModel):
    """Response for nuclear reactor prediction"""
    success: bool = Field(..., description="Whether prediction was successful")
    prediction: Optional[ReactorPredictionResult] = Field(default=None, description="Prediction result")
    processing_time_ms: float = Field(..., description="Processing time in milliseconds")
    request_id: Optional[str] = Field(default=None, description="Request identifier")
    timestamp: str = Field(..., description="Response timestamp")
    error: Optional[str] = Field(default=None, description="Error message if prediction failed")


class BatchPredictionRequest(BaseModel):
    """
    Schema for batch prediction request.
    """
    model_config = ConfigDict(protected_namespaces=())
    
    model_name: str = Field(
        ..., 
        description="Name of the AI model to use for prediction",
        example="clf_model_rf_v2"
    )
    batch_features: List[List[float]] = Field(
        ..., 
        description="List of feature vectors for batch prediction",
        min_items=1,
        max_items=100,  # Limit batch size
        example=[[1.2, 3.4, 5.6], [7.8, 9.0, 1.1]]
    )
    request_id: Optional[str] = Field(
        None,
        description="Optional unique identifier for the request",
        example="batch_req_123456789"
    )
    
    @validator('batch_features')
    def validate_batch_features(cls, v):
        """Validate batch features."""
        if len(v) > 100:
            raise ValueError("Batch size cannot exceed 100 samples")
        
        # Check that all feature vectors have the same length
        if v:
            first_length = len(v[0])
            for i, features in enumerate(v):
                if len(features) != first_length:
                    raise ValueError(f"All feature vectors must have the same length. "
                                   f"Vector at index {i} has length {len(features)}, "
                                   f"expected {first_length}")
                
                # Validate individual features
                for j, feature in enumerate(features):
                    if not isinstance(feature, (int, float)):
                        raise ValueError(f"Feature at batch index {i}, feature index {j} must be a number")
                    if not (-1e10 <= feature <= 1e10):
                        raise ValueError(f"Feature at batch index {i}, feature index {j} is out of bounds")
        
        return v


class BatchPredictionResponse(BaseModel):
    """
    Schema for batch prediction response.
    """
    model_config = ConfigDict(protected_namespaces=())
    
    success: bool = Field(default=True, description="Whether batch prediction was successful")
    model_name: str = Field(..., description="Name of the model used")
    batch_predictions: List[List[Union[ClassificationPrediction, BinaryClassificationPrediction, RegressionPrediction]]] = Field(
        ..., description="List of prediction results for each input"
    )
    batch_size: int = Field(..., description="Number of samples in the batch")
    request_id: Optional[str] = Field(None, description="Request identifier if provided")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Prediction timestamp")
    processing_time_ms: Optional[float] = Field(None, description="Total processing time in milliseconds")