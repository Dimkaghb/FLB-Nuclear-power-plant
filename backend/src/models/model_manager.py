"""
AI Model Manager for FLB Nuclear Power Plant
Handles loading and inference of ONNX models for classification and regression tasks.
"""

import os
import logging
from typing import Dict, Any, List, Optional
import numpy as np
import onnxruntime as ort
from pathlib import Path

# Import feature engineering
from features.feature_engineering import FeatureEngineer, ReactorState

# Configure logging
logger = logging.getLogger(__name__)


class ModelManager:
    """
    Manages AI models for nuclear power plant monitoring and prediction.
    Supports both classification and regression ONNX models.
    """
    
    def __init__(self, models_dir: str, lazy_loading: bool = True):
        """
        Initialize the model manager with the directory containing ONNX models.
        
        Args:
            models_dir (str): Path to directory containing ONNX model files
            lazy_loading (bool): If True, models are loaded only when first requested
        """
        self.models_dir = Path(models_dir)
        self.models: Dict[str, ort.InferenceSession] = {}
        self.model_metadata: Dict[str, Dict[str, Any]] = {}
        self.lazy_loading = lazy_loading
        self._available_model_files: Dict[str, Path] = {}
        
        # Initialize feature engineering
        self.feature_engineer = FeatureEngineer(rolling_window=3)
        
        # Validate models directory
        if not self.models_dir.exists():
            raise FileNotFoundError(f"Models directory not found: {models_dir}")
        
        logger.info(f"Initializing ModelManager with models directory: {models_dir}")
        logger.info(f"Lazy loading: {'enabled' if lazy_loading else 'disabled'}")
        
        # Scan for available models but don't load them yet if lazy loading is enabled
        self._scan_available_models()
        
        if not lazy_loading:
            # Load all models immediately (original behavior)
            self._load_models()
    
    def _scan_available_models(self) -> None:
        """
        Scan the models directory to find available ONNX models without loading them.
        """
        onnx_files = list(self.models_dir.glob("*.onnx"))
        
        if not onnx_files:
            logger.warning(f"No ONNX files found in {self.models_dir}")
            return
        
        for model_path in onnx_files:
            model_name = model_path.stem
            self._available_model_files[model_name] = model_path
            
        logger.info(f"Found {len(self._available_model_files)} available models: {list(self._available_model_files.keys())}")
    
    def _load_single_model(self, model_name: str) -> bool:
        """
        Load a single model by name.
        
        Args:
            model_name (str): Name of the model to load
            
        Returns:
            bool: True if model was loaded successfully, False otherwise
        """
        if model_name in self.models:
            return True  # Already loaded
            
        if model_name not in self._available_model_files:
            logger.error(f"Model '{model_name}' not found in available models")
            return False
            
        model_path = self._available_model_files[model_name]
        
        try:
            # Get file size for logging
            file_size_mb = model_path.stat().st_size / (1024 * 1024)
            logger.info(f"Loading model on demand: {model_path} (Size: {file_size_mb:.1f} MB)")
            
            # Create ONNX Runtime session with optimized settings
            session_options = ort.SessionOptions()
            session_options.graph_optimization_level = ort.GraphOptimizationLevel.ORT_ENABLE_EXTENDED
            session_options.execution_mode = ort.ExecutionMode.ORT_SEQUENTIAL
            
            # Enable memory pattern optimization for better performance
            session_options.enable_mem_pattern = True
            session_options.enable_cpu_mem_arena = True
            
            session = ort.InferenceSession(str(model_path), session_options)
            
            # Store model session
            self.models[model_name] = session
            
            # Store model metadata
            self.model_metadata[model_name] = {
                "path": str(model_path),
                "input_names": [input.name for input in session.get_inputs()],
                "output_names": [output.name for output in session.get_outputs()],
                "input_shapes": [input.shape for input in session.get_inputs()],
                "output_shapes": [output.shape for output in session.get_outputs()],
                "input_types": [input.type for input in session.get_inputs()],
                "output_types": [output.type for output in session.get_outputs()]
            }
            
            logger.info(f"Successfully loaded model on demand: {model_name}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to load model {model_path}: {str(e)}")
            return False
    
    def _load_models(self) -> None:
        """
        Load all ONNX models from the models directory.
        Automatically detects and loads classification and regression models.
        """
        if not self._available_model_files:
            logger.warning(f"No ONNX files found in {self.models_dir}")
            return
        
        for model_name in self._available_model_files:
            self._load_single_model(model_name)
        
        logger.info(f"Loaded {len(self.models)} models successfully: {list(self.models.keys())}")
    
    def get_available_models(self) -> List[str]:
        """
        Get list of available model names.
        
        Returns:
            List[str]: List of available model names
        """
        # Return all available models (both loaded and unloaded)
        return list(self._available_model_files.keys())
    
    def get_model_info(self, model_name: str) -> Optional[Dict[str, Any]]:
        """
        Get information about a specific model.
        
        Args:
            model_name (str): Name of the model
            
        Returns:
            Optional[Dict[str, Any]]: Model metadata or None if model not found
        """
        # If lazy loading is enabled and model is not loaded, load it on demand
        if self.lazy_loading and model_name not in self.models:
            if not self._load_single_model(model_name):
                return None
        
        return self.model_metadata.get(model_name)
    
    def get_model_version(self, model_name: str) -> str:
        """
        Get the version of a specific model based on its name.
        
        Args:
            model_name (str): Name of the model
            
        Returns:
            str: Model version ('v1', 'v2', or 'unknown')
        """
        model_name_lower = model_name.lower()
        if "v2" in model_name_lower:
            return "v2"
        elif "v1" in model_name_lower:
            return "v1"
        else:
            return "unknown"
    
    def get_models_by_version(self, version: str = None) -> Dict[str, List[str]]:
        """
        Get models grouped by version.
        
        Args:
            version (str, optional): Specific version to filter by
            
        Returns:
            Dict[str, List[str]]: Models grouped by version
        """
        models_by_version = {"v1": [], "v2": [], "unknown": []}
        
        for model_name in self.get_available_models():
            model_version = self.get_model_version(model_name)
            models_by_version[model_version].append(model_name)
        
        if version:
            return {version: models_by_version.get(version, [])}
        
        return models_by_version
    
    def predict_from_reactor_params(self, model_name: str, reactor_params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Make prediction from reactor parameters using feature engineering.
        
        Args:
            model_name (str): Name of the model to use
            reactor_params (Dict[str, Any]): Reactor parameters dictionary
            
        Returns:
            Dict[str, Any]: Prediction results with metadata
            
        Raises:
            ValueError: If model not found or parameters invalid
            RuntimeError: If prediction fails
        """
        try:
            # Convert reactor parameters to ReactorState
            reactor_state = self.feature_engineer.from_dict(reactor_params)
            
            # Generate 288 features using feature engineering
            features = self.feature_engineer.create_features(reactor_state)
            
            # Validate features
            if not self.feature_engineer.validate_features(features):
                raise ValueError("Generated features failed validation")
            
            # Use the existing predict method with engineered features
            return self.predict(model_name, features)
            
        except Exception as e:
            logger.error(f"Prediction from reactor params failed for model '{model_name}': {str(e)}")
            # Reset feature history on error to prevent contamination
            self.feature_engineer.reset_history()
            raise ValueError(f"Prediction from reactor params failed: {str(e)}")
    
    def reset_feature_history(self) -> None:
        """
        Reset the feature engineering history.
        Useful when starting a new prediction session or after errors.
        """
        self.feature_engineer.reset_history()
        logger.info("Feature engineering history reset")
    
    def get_feature_names(self) -> List[str]:
        """
        Get the complete list of 288 feature names used by the models.
        
        Returns:
            List[str]: List of feature names in order
        """
        return self.feature_engineer.get_feature_names()
    
    def predict(self, model_name: str, input_data: List[float]) -> Dict[str, Any]:
        """
        Make prediction using specified model.
        
        Args:
            model_name (str): Name of the model to use
            input_data (List[float]): Input features for prediction
            
        Returns:
            Dict[str, Any]: Prediction results with metadata
            
        Raises:
            ValueError: If model not found or input data invalid
            RuntimeError: If prediction fails
        """
        # If lazy loading is enabled and model is not loaded, load it on demand
        if self.lazy_loading and model_name not in self.models:
            if not self._load_single_model(model_name):
                available_models = ", ".join(self.get_available_models())
                raise ValueError(f"Model '{model_name}' not found or failed to load. Available models: {available_models}")
        
        if model_name not in self.models:
            available_models = ", ".join(self.get_available_models())
            raise ValueError(f"Model '{model_name}' not found. Available models: {available_models}")
        
        try:
            session = self.models[model_name]
            metadata = self.model_metadata[model_name]
            
            # Prepare input data
            input_array = np.array(input_data, dtype=np.float32)
            
            # Reshape input if needed (assuming single sample prediction)
            if len(input_array.shape) == 1:
                input_array = input_array.reshape(1, -1)
            
            # Validate input shape
            expected_shape = metadata["input_shapes"][0]
            if expected_shape[1] != -1 and input_array.shape[1] != expected_shape[1]:
                raise ValueError(
                    f"Input shape mismatch. Expected {expected_shape[1]} features, "
                    f"got {input_array.shape[1]}"
                )
            
            # Prepare input dictionary
            input_name = metadata["input_names"][0]
            input_dict = {input_name: input_array}
            
            # Run inference
            logger.debug(f"Running inference for model: {model_name}")
            outputs = session.run(None, input_dict)
            
            # Process outputs
            result = {
                "model_name": model_name,
                "predictions": [],
                "metadata": {
                    "input_shape": input_array.shape,
                    "output_names": metadata["output_names"]
                }
            }
            
            # Format outputs based on model type and version
            if "clf" in model_name.lower():
                # Classification model handling
                self._process_classification_outputs(result, metadata, outputs, model_name)
            else:
                # Regression model handling
                self._process_regression_outputs(result, metadata, outputs)
            
            logger.info(f"Successful prediction for model: {model_name}")
            return result
            
        except Exception as e:
            logger.error(f"Prediction failed for model '{model_name}': {str(e)}")
            raise ValueError(f"Prediction failed: {str(e)}")
    
    def _process_classification_outputs(self, result: Dict[str, Any], metadata: Dict[str, Any], 
                                      outputs: List, model_name: str) -> None:
        """
        Process classification model outputs, handling both v1 and v2 model formats.
        
        Args:
            result: Result dictionary to populate
            metadata: Model metadata
            outputs: Model outputs
            model_name: Name of the model
        """
        # Check if this is a v2 model with separate label and probability outputs
        if "v2" in model_name.lower() and len(outputs) >= 2:
            # v2 model format: separate label and probability outputs
            output_names = metadata["output_names"]
            
            # Find label and probability outputs
            label_output = None
            prob_output = None
            label_name = ""
            prob_name = ""
            
            for i, (name, output_data) in enumerate(zip(output_names, outputs)):
                if "label" in name.lower():
                    label_output = output_data
                    label_name = name
                elif "probability" in name.lower() or "prob" in name.lower():
                    prob_output = output_data
                    prob_name = name
            
            if label_output is not None and prob_output is not None:
                # Extract predicted class
                predicted_class = int(label_output[0]) if label_output.ndim > 0 else int(label_output)
                
                # Extract probabilities - handle sequence of maps format
                try:
                    if isinstance(prob_output, (list, tuple)) and len(prob_output) > 0:
                        # Handle sequence of maps format
                        prob_dict = prob_output[0] if len(prob_output) > 0 else {}
                        if isinstance(prob_dict, dict):
                            # Convert dict to list of probabilities
                            max_class = max(prob_dict.keys()) if prob_dict else 1
                            probabilities = [prob_dict.get(i, 0.0) for i in range(max_class + 1)]
                        else:
                            probabilities = [float(prob_dict)] if not isinstance(prob_dict, list) else prob_dict
                    else:
                        # Fallback: create probability list with high confidence for predicted class
                        probabilities = [0.1, 0.9] if predicted_class == 1 else [0.9, 0.1]
                        
                    confidence = float(max(probabilities)) if probabilities else 0.5
                    
                    result["predictions"].append({
                        "type": "classification",
                        "output_name": f"{label_name}+{prob_name}",
                        "predicted_class": predicted_class,
                        "probabilities": probabilities,
                        "confidence": confidence
                    })
                    
                except Exception as e:
                    logger.warning(f"Failed to parse v2 probabilities for {model_name}: {str(e)}")
                    # Fallback to simple binary classification
                    result["predictions"].append({
                        "type": "binary_classification",
                        "output_name": label_name,
                        "predicted_class": predicted_class,
                        "probability": 0.9 if predicted_class == 1 else 0.1,
                        "confidence": 0.8
                    })
            else:
                logger.warning(f"Could not find both label and probability outputs for v2 model {model_name}")
                # Fallback to processing first output as traditional classification
                self._process_traditional_classification(result, metadata, outputs)
        else:
            # v1 model or traditional format
            self._process_traditional_classification(result, metadata, outputs)
    
    def _process_traditional_classification(self, result: Dict[str, Any], metadata: Dict[str, Any], 
                                          outputs: List) -> None:
        """
        Process traditional classification model outputs (v1 format).
        
        Args:
            result: Result dictionary to populate
            metadata: Model metadata
            outputs: Model outputs
        """
        for i, (output_name, output_data) in enumerate(zip(metadata["output_names"], outputs)):
            if output_data.ndim > 1 and output_data.shape[1] > 1:
                # Multi-class classification
                probabilities = output_data[0].tolist()
                predicted_class = int(np.argmax(output_data[0]))
                result["predictions"].append({
                    "type": "classification",
                    "output_name": output_name,
                    "predicted_class": predicted_class,
                    "probabilities": probabilities,
                    "confidence": float(max(probabilities))
                })
            else:
                # Binary classification
                probability = float(output_data[0][0] if output_data.ndim > 1 else output_data[0])
                predicted_class = int(probability > 0.5)
                result["predictions"].append({
                    "type": "binary_classification",
                    "output_name": output_name,
                    "predicted_class": predicted_class,
                    "probability": probability,
                    "confidence": abs(probability - 0.5) * 2
                })
    
    def _process_regression_outputs(self, result: Dict[str, Any], metadata: Dict[str, Any], 
                                  outputs: List) -> None:
        """
        Process regression model outputs for both v1 and v2 formats.
        
        Args:
            result: Result dictionary to populate
            metadata: Model metadata
            outputs: Model outputs
        """
        for i, (output_name, output_data) in enumerate(zip(metadata["output_names"], outputs)):
            # Handle both v1 and v2 regression output formats
            if output_data.ndim > 1:
                # v2 format: [None, 1] shape
                values = output_data[0].tolist() if output_data.shape[1] > 1 else [float(output_data[0][0])]
            else:
                # v1 format: scalar output
                values = [float(output_data[0])]
            
            result["predictions"].append({
                "type": "regression",
                "output_name": output_name,
                "predicted_values": values
            })
    
    def get_loading_stats(self) -> Dict[str, Any]:
        """
        Get statistics about model loading status.
        
        Returns:
            Dict[str, Any]: Loading statistics including loaded/available counts and model status
        """
        loaded_models = list(self.models.keys())
        available_models = list(self._available_model_files.keys())
        
        return {
            "lazy_loading_enabled": self.lazy_loading,
            "total_available": len(available_models),
            "total_loaded": len(loaded_models),
            "available_models": available_models,
            "loaded_models": loaded_models,
            "unloaded_models": [model for model in available_models if model not in loaded_models]
        }
    
    def preload_all_models(self) -> None:
        """
        Preload all available models. Useful for production environments.
        """
        logger.info("Preloading all available models...")
        for model_name in self._available_model_files:
            if model_name not in self.models:
                self._load_single_model(model_name)
        logger.info(f"Preloading complete. Loaded {len(self.models)} models.")
    
    def health_check(self) -> Dict[str, Any]:
        """
        Perform health check on all loaded models.
        
        Returns:
            Dict[str, Any]: Health status of all models
        """
        logger.info("Starting health check...")
        health_status = {
            "status": "healthy",
            "models_count": len(self.models),
            "models": {}
        }
        
        for model_name in self.models:
            try:
                logger.info(f"Checking health of model: {model_name}")
                # Try a dummy prediction to verify model is working
                metadata = self.model_metadata[model_name]
                input_shape = metadata["input_shapes"][0]
                
                if input_shape[1] != -1:  # Known input size
                    logger.debug(f"Creating dummy input for {model_name} with shape {input_shape}")
                    dummy_input = [0.0] * input_shape[1]
                    logger.debug(f"Running dummy prediction for {model_name}")
                    self.predict(model_name, dummy_input)
                    health_status["models"][model_name] = "healthy"
                    logger.info(f"Model {model_name} health check passed")
                else:
                    health_status["models"][model_name] = "unknown_input_shape"
                    logger.warning(f"Model {model_name} has unknown input shape")
                    
            except Exception as e:
                logger.error(f"Health check failed for model {model_name}: {str(e)}")
                health_status["models"][model_name] = f"error: {str(e)}"
                health_status["status"] = "degraded"
        
        logger.info(f"Health check completed: {health_status}")
        return health_status