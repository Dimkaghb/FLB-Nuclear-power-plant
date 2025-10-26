#!/usr/bin/env python3
"""
Example usage of the FLB Nuclear Power Plant AI API with v2 models.
This script demonstrates how to interact with the API endpoints.
"""

import requests
import json
import numpy as np
from typing import List, Dict, Any

# API Configuration
API_BASE_URL = "http://localhost:8000/api/v1"

def generate_sample_features(num_features: int = 288) -> List[float]:
    """
    Generate sample features for testing purposes.
    
    Args:
        num_features (int): Number of features to generate (default: 288 for v2 models)
        
    Returns:
        List[float]: List of random numerical features
    """
    # Generate realistic-looking features for nuclear power plant monitoring
    np.random.seed(42)  # For reproducible results
    features = []
    
    # Simulate different types of measurements
    for i in range(num_features):
        if i < 50:  # Temperature readings (°C)
            features.append(np.random.normal(300, 50))
        elif i < 100:  # Pressure readings (bar)
            features.append(np.random.normal(150, 20))
        elif i < 150:  # Flow rates (m³/h)
            features.append(np.random.normal(1000, 200))
        elif i < 200:  # Neutron flux readings
            features.append(np.random.normal(0.8, 0.1))
        elif i < 250:  # Control rod positions (%)
            features.append(np.random.uniform(0, 100))
        else:  # Other sensor readings
            features.append(np.random.normal(0, 1))
    
    return [round(f, 4) for f in features]

def check_api_health() -> Dict[str, Any]:
    """
    Check the health status of the API.
    
    Returns:
        Dict[str, Any]: Health check response
    """
    print("🔍 Checking API health...")
    try:
        response = requests.get(f"{API_BASE_URL}/health")
        response.raise_for_status()
        result = response.json()
        print(f"✅ API Status: {result['status']}")
        print(f"📊 Models loaded: {result['models_count']}")
        return result
    except requests.exceptions.RequestException as e:
        print(f"❌ Health check failed: {e}")
        return {}

def get_available_models() -> List[str]:
    """
    Get list of available models.
    
    Returns:
        List[str]: List of available model names
    """
    print("\n📋 Getting available models...")
    try:
        response = requests.get(f"{API_BASE_URL}/models")
        response.raise_for_status()
        result = response.json()
        models = result['models']
        print(f"✅ Found {len(models)} models: {models}")
        return models
    except requests.exceptions.RequestException as e:
        print(f"❌ Failed to get models: {e}")
        return []

def get_models_by_version() -> Dict[str, Any]:
    """
    Get models grouped by version.
    
    Returns:
        Dict[str, Any]: Models grouped by version
    """
    print("\n🏷️ Getting models by version...")
    try:
        response = requests.get(f"{API_BASE_URL}/models/versions")
        response.raise_for_status()
        result = response.json()
        
        print(f"✅ Total models: {result['total_models']}")
        for version, models in result['models_by_version'].items():
            print(f"  📦 {version.upper()}: {len(models)} models")
            for model in models:
                print(f"    - {model['model_name']} ({model['type']}, {model['features_count']} features)")
        
        return result
    except requests.exceptions.RequestException as e:
        print(f"❌ Failed to get models by version: {e}")
        return {}

def make_single_prediction(model_name: str, features: List[float]) -> Dict[str, Any]:
    """
    Make a single prediction using the specified model.
    
    Args:
        model_name (str): Name of the model to use
        features (List[float]): Input features for prediction
        
    Returns:
        Dict[str, Any]: Prediction response
    """
    print(f"\n🎯 Making single prediction with {model_name}...")
    
    payload = {
        "model_name": model_name,
        "features": features,
        "request_id": f"example_single_{model_name}"
    }
    
    try:
        response = requests.post(
            f"{API_BASE_URL}/predict",
            json=payload,
            headers={"Content-Type": "application/json"}
        )
        response.raise_for_status()
        result = response.json()
        
        print(f"✅ Prediction successful!")
        print(f"⏱️ Processing time: {result['processing_time_ms']:.2f}ms")
        
        for prediction in result['predictions']:
            print(f"📊 Prediction type: {prediction['type']}")
            if prediction['type'] == 'classification':
                print(f"🎯 Predicted class: {prediction['predicted_class']}")
                print(f"🎲 Confidence: {prediction['confidence']:.4f}")
                print(f"📈 Probabilities: {[round(p, 4) for p in prediction['probabilities']]}")
            elif prediction['type'] == 'regression':
                print(f"📏 Predicted values: {prediction['predicted_values']}")
        
        return result
    except requests.exceptions.RequestException as e:
        print(f"❌ Prediction failed: {e}")
        return {}

def make_batch_prediction(model_name: str, batch_features: List[List[float]]) -> Dict[str, Any]:
    """
    Make batch predictions using the specified model.
    
    Args:
        model_name (str): Name of the model to use
        batch_features (List[List[float]]): List of feature vectors for batch prediction
        
    Returns:
        Dict[str, Any]: Batch prediction response
    """
    print(f"\n📦 Making batch prediction with {model_name} (batch size: {len(batch_features)})...")
    
    payload = {
        "model_name": model_name,
        "batch_features": batch_features,
        "request_id": f"example_batch_{model_name}"
    }
    
    try:
        response = requests.post(
            f"{API_BASE_URL}/predict/batch",
            json=payload,
            headers={"Content-Type": "application/json"}
        )
        response.raise_for_status()
        result = response.json()
        
        print(f"✅ Batch prediction successful!")
        print(f"⏱️ Processing time: {result['processing_time_ms']:.2f}ms")
        print(f"📊 Batch size: {result['batch_size']}")
        
        # Show summary of results
        for i, predictions in enumerate(result['batch_predictions']):
            print(f"  Sample {i+1}:")
            for prediction in predictions:
                if prediction['type'] == 'classification':
                    print(f"    🎯 Class: {prediction['predicted_class']}, Confidence: {prediction['confidence']:.4f}")
                elif prediction['type'] == 'regression':
                    print(f"    📏 Value: {prediction['predicted_values'][0]:.4f}")
        
        return result
    except requests.exceptions.RequestException as e:
        print(f"❌ Batch prediction failed: {e}")
        return {}

def get_model_info(model_name: str) -> Dict[str, Any]:
    """
    Get detailed information about a specific model.
    
    Args:
        model_name (str): Name of the model
        
    Returns:
        Dict[str, Any]: Model information response
    """
    print(f"\n📋 Getting model information for {model_name}...")
    
    try:
        response = requests.get(f"{API_BASE_URL}/models/{model_name}")
        response.raise_for_status()
        result = response.json()
        
        model_info = result['model_info']
        print(f"✅ Model information retrieved:")
        print(f"  📁 Name: {model_info['name']}")
        print(f"  📂 Path: {model_info['path']}")
        print(f"  📥 Input names: {model_info['input_names']}")
        print(f"  📤 Output names: {model_info['output_names']}")
        print(f"  📐 Input shapes: {model_info['input_shapes']}")
        print(f"  📏 Output shapes: {model_info['output_shapes']}")
        
        return result
    except requests.exceptions.RequestException as e:
        print(f"❌ Failed to get model info: {e}")
        return {}

def main():
    """
    Main function demonstrating API usage with v2 models.
    """
    print("🚀 FLB Nuclear Power Plant AI API Examples")
    print("=" * 50)
    
    # Check API health
    health = check_api_health()
    if not health or health.get('status') != 'healthy':
        print("❌ API is not healthy. Please check the server.")
        return
    
    # Get available models
    models = get_available_models()
    if not models:
        print("❌ No models available. Please check the server.")
        return
    
    # Get models by version
    version_info = get_models_by_version()
    
    # Generate sample features for v2 models (288 features)
    sample_features = generate_sample_features(288)
    print(f"\n🔢 Generated {len(sample_features)} sample features")
    
    # Test each available model
    for model_name in models:
        print(f"\n{'='*60}")
        print(f"🧪 Testing model: {model_name}")
        print(f"{'='*60}")
        
        # Get model information
        get_model_info(model_name)
        
        # Make single prediction
        single_result = make_single_prediction(model_name, sample_features)
        
        # Make batch prediction with 3 samples
        batch_features = [
            generate_sample_features(288),
            generate_sample_features(288),
            generate_sample_features(288)
        ]
        batch_result = make_batch_prediction(model_name, batch_features)
    
    print(f"\n{'='*60}")
    print("🎉 All API examples completed successfully!")
    print("📚 Check the API_DOCUMENTATION.md file for more details.")
    print(f"{'='*60}")

if __name__ == "__main__":
    main()