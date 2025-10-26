"""
Nuclear Reactor Integration Example
Demonstrates how to use the new reactor prediction endpoint with control sidebar data

This example shows:
1. How to format control sidebar data for the API
2. How to call the new /predict/reactor endpoint
3. How to interpret the prediction results
4. How to handle safety alerts and recommendations
"""

import requests
import json
from typing import Dict, Any, List
from datetime import datetime
import time

# API Configuration
API_BASE_URL = "http://localhost:8000/api/v1"
REACTOR_PREDICT_ENDPOINT = f"{API_BASE_URL}/predict/reactor"

def create_sample_reactor_data() -> Dict[str, Any]:
    """
    Create sample reactor data matching the control sidebar structure.
    This simulates data that would come from the control-sidebar.tsx component.
    
    Returns:
        Dictionary with reactor parameters organized by category
    """
    return {
        "temperature": {
            "peakFuelTemperature": 425.5,
            "averageRcsTemperature": 315.2,
            "pressurizerTemperature": 345.8,
            "steamGeneratorTemperatureA": 285.3,
            "steamGeneratorTemperatureB": 287.1,
            "containmentTemperature": 35.2
        },
        "pressure": {
            "rcsPressure": 155.2,
            "pressurizerPressureLevel": 152.8,
            "steamGeneratorPressureA": 65.4,
            "steamGeneratorPressureB": 66.1,
            "containmentPressure": 1.02
        },
        "flow": {
            "reactorCoolantFlowA": 950.3,
            "reactorCoolantFlowB": 948.7,
            "steamGeneratorWaterFeedA": 420.5,
            "steamGeneratorWaterFeedB": 418.9,
            "pressurizerSprayFlow": 12.3
        },
        "reactivity": {
            "reactorPower": 85.2,
            "neutronFlux": 1.15,
            "controlRodPosition": 75.8,
            "boronConcentration": 1250.0,
            "reactivityWorth": -0.05
        },
        "radiation": {
            "radiationInBuilding": 0.8,
            "rcsActivity": 3500.0,
            "containmentRadiation": 0.12,
            "steamLineRadiation": 0.05
        },
        "other": {
            "coreWaterLevel": 48.5,
            "emergencySystemsStatus": 0,
            "auxiliaryFeedwaterFlow": 0.0,
            "chargingFlow": 25.3,
            "letdownFlow": 23.8
        }
    }

def create_emergency_scenario_data() -> Dict[str, Any]:
    """
    Create reactor data simulating an emergency scenario.
    This demonstrates how the system responds to critical conditions.
    
    Returns:
        Dictionary with reactor parameters showing emergency conditions
    """
    return {
        "temperature": {
            "peakFuelTemperature": 520.0,  # Critical level
            "averageRcsTemperature": 340.0,  # High
            "pressurizerTemperature": 380.0,  # High
            "steamGeneratorTemperatureA": 295.0,
            "steamGeneratorTemperatureB": 298.0,
            "containmentTemperature": 45.0
        },
        "pressure": {
            "rcsPressure": 115.0,  # Low - potential LOCA
            "pressurizerPressureLevel": 110.0,  # Low
            "steamGeneratorPressureA": 45.0,  # Low
            "steamGeneratorPressureB": 47.0,
            "containmentPressure": 1.8  # High
        },
        "flow": {
            "reactorCoolantFlowA": 650.0,  # Reduced
            "reactorCoolantFlowB": 680.0,  # Reduced
            "steamGeneratorWaterFeedA": 200.0,  # Low
            "steamGeneratorWaterFeedB": 210.0,
            "pressurizerSprayFlow": 0.0
        },
        "reactivity": {
            "reactorPower": 25.0,  # Reduced due to emergency
            "neutronFlux": 0.35,
            "controlRodPosition": 15.0,  # Inserted for shutdown
            "boronConcentration": 2500.0,  # High for shutdown
            "reactivityWorth": -5.0  # Highly negative
        },
        "radiation": {
            "radiationInBuilding": 8.5,  # Critical level
            "rcsActivity": 25000.0,  # High
            "containmentRadiation": 2.5,  # High
            "steamLineRadiation": 1.2  # Elevated
        },
        "other": {
            "coreWaterLevel": 35.0,  # Low
            "emergencySystemsStatus": 1,  # Active
            "auxiliaryFeedwaterFlow": 150.0,  # Emergency cooling
            "chargingFlow": 45.0,  # High injection
            "letdownFlow": 0.0  # Isolated
        }
    }

def call_reactor_prediction_api(reactor_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Call the reactor prediction API endpoint.
    
    Args:
        reactor_data: Reactor parameters organized by category
        
    Returns:
        API response with prediction results
    """
    try:
        print(f"🔗 Calling API: {REACTOR_PREDICT_ENDPOINT}")
        
        response = requests.post(
            REACTOR_PREDICT_ENDPOINT,
            json=reactor_data,
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        if response.status_code == 200:
            return response.json()
        else:
            print(f"❌ API Error: {response.status_code}")
            print(f"Response: {response.text}")
            return {"error": f"API returned status {response.status_code}"}
            
    except requests.exceptions.ConnectionError:
        print("❌ Connection Error: Could not connect to the API server")
        print("💡 Make sure the backend server is running on http://localhost:8000")
        return {"error": "Connection failed"}
    except requests.exceptions.Timeout:
        print("❌ Timeout Error: API request timed out")
        return {"error": "Request timeout"}
    except Exception as e:
        print(f"❌ Unexpected Error: {e}")
        return {"error": str(e)}

def interpret_prediction_results(results: Dict[str, Any]) -> None:
    """
    Interpret and display prediction results in a user-friendly format.
    
    Args:
        results: API response with prediction results
    """
    if "error" in results:
        print(f"❌ Error in prediction: {results['error']}")
        return
    
    print("\n" + "="*60)
    print("🔮 REACTOR PREDICTION RESULTS")
    print("="*60)
    
    # Overall prediction
    prediction = results.get("prediction", {})
    print(f"🎯 Overall Risk Level: {prediction.get('risk_level', 'Unknown')}")
    print(f"📊 Confidence Score: {prediction.get('confidence', 0):.3f}")
    print(f"🔢 Prediction Class: {prediction.get('class', 'Unknown')}")
    
    # Safety status
    safety = results.get("safety_status", {})
    print(f"\n🛡️ Safety Status: {safety.get('overall_status', 'Unknown')}")
    print(f"⚠️ Critical Alerts: {safety.get('critical_alerts', 0)}")
    print(f"⚡ Warning Alerts: {safety.get('warning_alerts', 0)}")
    
    # Detailed alerts
    alerts = safety.get("alerts", [])
    if alerts:
        print(f"\n🚨 ACTIVE ALERTS ({len(alerts)}):")
        for i, alert in enumerate(alerts[:5], 1):  # Show top 5 alerts
            level_emoji = "🔴" if alert.get("level") == "CRITICAL" else "🟡"
            print(f"   {level_emoji} {alert.get('parameter', 'Unknown')}: {alert.get('message', 'No message')}")
    
    # Recommendations
    recommendations = results.get("recommendations", [])
    if recommendations:
        print(f"\n💡 RECOMMENDATIONS ({len(recommendations)}):")
        for i, rec in enumerate(recommendations[:3], 1):  # Show top 3 recommendations
            print(f"   {i}. {rec.get('action', 'No action specified')}")
            if rec.get("urgency"):
                print(f"      Urgency: {rec['urgency']}")
    
    # Feature importance (if available)
    feature_importance = results.get("feature_importance", {})
    if feature_importance:
        print(f"\n📈 KEY INFLUENCING FACTORS:")
        for param, importance in list(feature_importance.items())[:5]:
            print(f"   • {param}: {importance:.3f}")
    
    print("="*60)

def demonstrate_normal_operation():
    """Demonstrate API usage with normal reactor operation data."""
    print("\n🟢 SCENARIO 1: Normal Operation")
    print("-" * 40)
    
    normal_data = create_sample_reactor_data()
    print("📤 Sending normal operation data to API...")
    
    results = call_reactor_prediction_api(normal_data)
    interpret_prediction_results(results)

def demonstrate_emergency_scenario():
    """Demonstrate API usage with emergency scenario data."""
    print("\n🔴 SCENARIO 2: Emergency Conditions")
    print("-" * 40)
    
    emergency_data = create_emergency_scenario_data()
    print("📤 Sending emergency scenario data to API...")
    
    results = call_reactor_prediction_api(emergency_data)
    interpret_prediction_results(results)

def test_api_health():
    """Test if the API server is running and healthy."""
    try:
        health_url = f"{API_BASE_URL}/health"
        response = requests.get(health_url, timeout=5)
        
        if response.status_code == 200:
            print("✅ API server is healthy and running")
            return True
        else:
            print(f"⚠️ API server responded with status: {response.status_code}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to API server")
        print("💡 Please start the backend server with: python main.py")
        return False
    except Exception as e:
        print(f"❌ Health check failed: {e}")
        return False

def show_api_integration_guide():
    """Show how to integrate this with the frontend control sidebar."""
    print("\n" + "="*60)
    print("🔧 FRONTEND INTEGRATION GUIDE")
    print("="*60)
    print("To integrate with control-sidebar.tsx:")
    print()
    print("1. Collect parameter values from the sidebar controls:")
    print("   const reactorData = {")
    print("     temperature: {")
    print("       peakFuelTemperature: temperatureValues.peakFuelTemperature,")
    print("       averageRcsTemperature: temperatureValues.averageRcsTemperature,")
    print("       // ... other temperature parameters")
    print("     },")
    print("     pressure: { /* pressure parameters */ },")
    print("     flow: { /* flow parameters */ },")
    print("     reactivity: { /* reactivity parameters */ },")
    print("     radiation: { /* radiation parameters */ },")
    print("     other: { /* other parameters */ }")
    print("   };")
    print()
    print("2. Send to the prediction API:")
    print("   const response = await fetch('/api/v1/predict/reactor', {")
    print("     method: 'POST',")
    print("     headers: { 'Content-Type': 'application/json' },")
    print("     body: JSON.stringify(reactorData)")
    print("   });")
    print()
    print("3. Handle the response:")
    print("   const result = await response.json();")
    print("   // Update UI with prediction results")
    print("   // Show safety alerts")
    print("   // Display recommendations")
    print("="*60)

def main():
    """
    Main function demonstrating the reactor prediction API integration.
    """
    print("🚀 Nuclear Reactor Prediction API Integration Example")
    print("=" * 60)
    print("This example demonstrates how to use the new reactor prediction endpoint")
    print("with data from the control-sidebar.tsx component.")
    print()
    
    # Test API health first
    if not test_api_health():
        print("\n⚠️ API server is not available. Please start the backend server first.")
        print("Run: python main.py")
        return
    
    # Demonstrate normal operation
    demonstrate_normal_operation()
    
    # Wait a moment between requests
    time.sleep(1)
    
    # Demonstrate emergency scenario
    demonstrate_emergency_scenario()
    
    # Show integration guide
    show_api_integration_guide()
    
    print("\n🎉 Integration example completed!")
    print("💡 Use this pattern to integrate reactor predictions with your frontend.")

if __name__ == "__main__":
    main()