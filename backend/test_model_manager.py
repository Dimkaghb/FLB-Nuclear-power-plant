#!/usr/bin/env python3
"""
Test script for the updated ModelManager to verify compatibility with v2 models.
"""

import os
import sys
import numpy as np
from pathlib import Path

# Add the src directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from models.model_manager import ModelManager

def test_model_manager():
    """
    Test the ModelManager with both old and new models.
    """
    print("=== Testing Updated ModelManager ===\n")
    
    # Initialize ModelManager
    models_dir = os.path.join(Path(__file__).parent, "ai")
    manager = ModelManager(models_dir=models_dir, lazy_loading=False)
    
    print("1. Testing model discovery and loading...")
    available_models = manager.get_available_models()
    print(f"Available models: {available_models}")
    
    # Test version grouping
    print("\n2. Testing model version grouping...")
    models_by_version = manager.get_models_by_version()
    for version, models in models_by_version.items():
        if models:
            print(f"  {version.upper()} models: {models}")
    
    # Test model loading
    print("\n3. Testing model loading...")
    loaded_models = manager.models
    print(f"Loaded models: {list(loaded_models.keys())}")
    
    # Test model metadata
    print("\n4. Testing model metadata...")
    for model_name in available_models:
        metadata = manager.get_model_info(model_name)
        version = manager.get_model_version(model_name)
        print(f"  {model_name} (version: {version}):")
        if metadata:
            print(f"    Type: {metadata.get('type', 'unknown')}")
            print(f"    Input shape: {metadata.get('input_shape', 'unknown')}")
            print(f"    Output names: {metadata.get('output_names', 'unknown')}")
        else:
            print("    Metadata not available")
    
    # Test predictions with dummy data
    print("\n5. Testing predictions...")
    
    # Create dummy input data (288 features as required by v2 models)
    dummy_input = np.random.rand(288).tolist()
    
    for model_name in available_models:
        try:
            print(f"\n  Testing {model_name}...")
            result = manager.predict(model_name, dummy_input)
            print(f"    Prediction successful!")
            print(f"    Result keys: {list(result.keys())}")
            
            # Print sample of result values (truncated for readability)
            for key, value in result.items():
                if isinstance(value, list) and len(value) > 5:
                    print(f"    {key}: [{value[0]:.4f}, {value[1]:.4f}, ..., {value[-1]:.4f}] (length: {len(value)})")
                else:
                    print(f"    {key}: {value}")
                    
        except Exception as e:
            print(f"    Error with {model_name}: {str(e)}")
    
    # Test health check
    print("\n6. Testing health check...")
    try:
        health_status = manager.health_check()
        print(f"Health check passed: {health_status}")
    except Exception as e:
        print(f"Health check failed: {str(e)}")
    
    # Test loading statistics
    print("\n7. Testing loading statistics...")
    stats = manager.get_loading_stats()
    print(f"Loading statistics: {stats}")
    
    print("\n=== Test completed ===")

if __name__ == "__main__":
    test_model_manager()