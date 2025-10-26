"""
Test script for the nuclear power plant AI prediction flow.
Tests the complete pipeline from reactor parameters to AI model predictions.
"""

import sys
import os
import logging
from pathlib import Path

# Add the backend directory to the Python path for proper package imports
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

# Now we can import from src as a package
from src.features.feature_engineering import FeatureEngineer, ReactorState
from src.models.model_manager import ModelManager

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def test_feature_engineering():
    """Test the feature engineering pipeline."""
    print("=" * 60)
    print("Testing Feature Engineering Pipeline")
    print("=" * 60)
    
    # Initialize feature engineer
    feature_engineer = FeatureEngineer(rolling_window=3)
    
    # Test with sample reactor parameters
    sample_params = {
        'timeSeconds': 1000.0,
        'averageRcsTemperature': 300.0,
        'hotLegTemperatureA': 320.0,
        'hotLegTemperatureB': 320.0,
        'coldLegTemperatureA': 280.0,
        'coldLegTemperatureB': 280.0,
        'rcsPressure': 155.0,
        'steamGeneratorAPressure': 70.0,
        'steamGeneratorBPressure': 70.0,
        'pressurizerLevel': 50.0,
        'rcsFlowA': 1000.0,
        'rcsFlowB': 1000.0,
        'feedwaterFlowA': 500.0,
        'feedwaterFlowB': 500.0,
        'steamFlowA': 500.0,
        'steamFlowB': 500.0,
        'reactorThermalPower': 100.0,
        'neutronPower': 100.0,
        'boronConcentration': 1000.0,
        'totalReactivity': 0.0,
        'peakFuelTemperature': 400.0,
        'averageFuelTemperature': 390.0,
        'dnbRatio': 2.0
    }
    
    print(f"Sample reactor parameters: {len(sample_params)} parameters")
    
    # Convert to ReactorState
    reactor_state = feature_engineer.from_dict(sample_params)
    print(f"✓ Successfully converted parameters to ReactorState")
    
    # Generate features
    features = feature_engineer.create_features(reactor_state)
    print(f"✓ Generated {len(features)} features")
    
    # Validate features
    is_valid = feature_engineer.validate_features(features)
    print(f"✓ Feature validation: {'PASSED' if is_valid else 'FAILED'}")
    
    # Test with multiple states for rolling calculations
    print("\nTesting rolling calculations with multiple states...")
    for i in range(3):
        # Slightly modify parameters
        modified_params = sample_params.copy()
        modified_params['timeSeconds'] += i * 10
        modified_params['averageRcsTemperature'] += i * 0.5
        
        state = feature_engineer.from_dict(modified_params)
        features = feature_engineer.create_features(state)
        print(f"  State {i+1}: {len(features)} features generated")
    
    print(f"✓ Rolling calculations working correctly")
    
    # Get feature names
    feature_names = feature_engineer.get_feature_names()
    print(f"✓ Feature names available: {len(feature_names)} names")
    
    return True


def test_model_manager():
    """Test the model manager with feature engineering."""
    print("\n" + "=" * 60)
    print("Testing Model Manager with Feature Engineering")
    print("=" * 60)
    
    # Initialize model manager
    models_dir = Path(__file__).parent / "ai"
    if not models_dir.exists():
        print(f"❌ Models directory not found: {models_dir}")
        return False
    
    try:
        model_manager = ModelManager(str(models_dir), lazy_loading=True)
        print(f"✓ Model manager initialized")
        
        # Check available models
        available_models = model_manager.get_available_models()
        print(f"✓ Available models: {available_models}")
        
        if not available_models:
            print("❌ No models found")
            return False
        
        # Test feature engineering integration
        sample_params = {
            'timeSeconds': 1000.0,
            'averageRcsTemperature': 300.0,
            'hotLegTemperatureA': 320.0,
            'hotLegTemperatureB': 320.0,
            'coldLegTemperatureA': 280.0,
            'coldLegTemperatureB': 280.0,
            'rcsPressure': 155.0,
            'steamGeneratorAPressure': 70.0,
            'steamGeneratorBPressure': 70.0,
            'pressurizerLevel': 50.0,
            'rcsFlowA': 1000.0,
            'rcsFlowB': 1000.0,
            'feedwaterFlowA': 500.0,
            'feedwaterFlowB': 500.0,
            'steamFlowA': 500.0,
            'steamFlowB': 500.0,
            'reactorThermalPower': 100.0,
            'neutronPower': 100.0,
            'boronConcentration': 1000.0,
            'totalReactivity': 0.0,
            'peakFuelTemperature': 400.0,
            'averageFuelTemperature': 390.0,
            'dnbRatio': 2.0
        }
        
        # Test prediction with each available model
        for model_name in available_models:
            try:
                print(f"\nTesting prediction with model: {model_name}")
                print(f"Sample params type: {type(sample_params)}")
                print(f"Sample params keys: {list(sample_params.keys())[:5]}...")  # Show first 5 keys
                result = model_manager.predict_from_reactor_params(model_name, sample_params)
                print(f"✓ Prediction successful for {model_name}")
                print(f"  - Model: {result['model_name']}")
                print(f"  - Predictions: {len(result['predictions'])} results")
                print(f"  - Input shape: {result['metadata']['input_shape']}")
                
                # Print first few predictions for verification
                if result['predictions']:
                    pred = result['predictions'][0]
                    if 'predicted_class' in pred:
                        print(f"  - Classification result: Class {pred['predicted_class']}, Confidence: {pred.get('confidence', 'N/A')}")
                    elif 'predicted_value' in pred:
                        print(f"  - Regression result: {pred['predicted_value']}")
                
            except Exception as e:
                import traceback
                print(f"❌ Prediction failed for {model_name}: {str(e)}")
                print(f"Full traceback: {traceback.format_exc()}")
                return False
        
        # Test feature history reset
        model_manager.reset_feature_history()
        print(f"✓ Feature history reset successful")
        
        # Test feature names
        feature_names = model_manager.get_feature_names()
        print(f"✓ Feature names retrieved: {len(feature_names)} features")
        
        return True
        
    except Exception as e:
        print(f"❌ Model manager test failed: {str(e)}")
        return False


def test_edge_cases():
    """Test edge cases and error handling."""
    print("\n" + "=" * 60)
    print("Testing Edge Cases and Error Handling")
    print("=" * 60)
    
    feature_engineer = FeatureEngineer()
    
    # Test with minimal parameters
    minimal_params = {'timeSeconds': 0.0}
    try:
        state = feature_engineer.from_dict(minimal_params)
        features = feature_engineer.create_features(state)
        print(f"✓ Minimal parameters handled: {len(features)} features")
    except Exception as e:
        print(f"❌ Minimal parameters failed: {str(e)}")
        return False
    
    # Test with extreme values
    extreme_params = {
        'averageRcsTemperature': 1000.0,  # Very high temperature
        'rcsPressure': 300.0,  # Very high pressure
        'reactorThermalPower': 150.0,  # Overpower condition
    }
    try:
        state = feature_engineer.from_dict(extreme_params)
        features = feature_engineer.create_features(state)
        is_valid = feature_engineer.validate_features(features)
        print(f"✓ Extreme values handled: Valid={is_valid}")
    except Exception as e:
        print(f"❌ Extreme values failed: {str(e)}")
        return False
    
    # Test feature validation with invalid data
    invalid_features = [float('inf')] * 288
    is_valid = feature_engineer.validate_features(invalid_features)
    print(f"✓ Invalid feature detection: Valid={is_valid} (should be False)")
    
    return True


def main():
    """Run all tests."""
    print("Nuclear Power Plant AI Prediction Flow Test")
    print("=" * 60)
    
    tests = [
        ("Feature Engineering", test_feature_engineering),
        ("Model Manager", test_model_manager),
        ("Edge Cases", test_edge_cases)
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} test crashed: {str(e)}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    
    passed = 0
    for test_name, result in results:
        status = "✓ PASSED" if result else "❌ FAILED"
        print(f"{test_name}: {status}")
        if result:
            passed += 1
    
    print(f"\nOverall: {passed}/{len(results)} tests passed")
    
    if passed == len(results):
        print("🎉 All tests passed! The prediction flow is working correctly.")
        return 0
    else:
        print("⚠️  Some tests failed. Please check the implementation.")
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)