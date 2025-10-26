# FLB Nuclear Power Plant AI API Documentation

## Overview

The FLB Nuclear Power Plant AI API provides endpoints for making predictions using machine learning models for nuclear power plant monitoring and analysis. The API supports both classification and regression models with version management capabilities.

## Base URL

```
http://localhost:8000/api/v1
```

## Available Models

### Version 2 Models (Current)

- **clf_model_rf_v2**: Classification model for nuclear power plant status prediction
  - Input features: 288 numerical values
  - Output: Classification results with probabilities
  - Model type: Random Forest Classifier

- **reg_model_rf_v2**: Regression model for nuclear power plant parameter prediction
  - Input features: 288 numerical values
  - Output: Continuous numerical predictions
  - Model type: Random Forest Regressor

## API Endpoints

### 1. Single Prediction

**POST** `/predict`

Make a prediction using a specified AI model.

#### Request Body

```json
{
  "model_name": "clf_model_rf_v2",
  "features": [1.2, 3.4, 5.6, ...], // 288 numerical values
  "request_id": "optional_request_id"
}
```

#### Response

```json
{
  "success": true,
  "model_name": "clf_model_rf_v2",
  "predictions": [
    {
      "type": "classification",
      "output_name": "output_label+output_probability",
      "predicted_class": 2,
      "probabilities": [0.421, 0.067, 0.511],
      "confidence": 0.511
    }
  ],
  "metadata": {
    "input_shape": [1, 288],
    "output_names": ["output_label", "output_probability"]
  },
  "request_id": "optional_request_id",
  "timestamp": "2024-01-15T10:30:00Z",
  "processing_time_ms": 45.2
}
```

#### Example cURL

```bash
curl -X POST "http://localhost:8000/api/v1/predict" \
  -H "Content-Type: application/json" \
  -d '{
    "model_name": "clf_model_rf_v2",
    "features": [1.2, 3.4, 5.6, 7.8, 9.0, ...], // 288 values total
    "request_id": "test_prediction_001"
  }'
```

### 2. Batch Prediction

**POST** `/predict/batch`

Make predictions for multiple samples using a specified AI model.

#### Request Body

```json
{
  "model_name": "reg_model_rf_v2",
  "batch_features": [
    [1.2, 3.4, 5.6, ...], // First sample (288 values)
    [2.1, 4.3, 6.5, ...], // Second sample (288 values)
    [3.0, 5.2, 7.4, ...]  // Third sample (288 values)
  ],
  "request_id": "batch_prediction_001"
}
```

#### Response

```json
{
  "success": true,
  "model_name": "reg_model_rf_v2",
  "batch_predictions": [
    [
      {
        "type": "regression",
        "output_name": "variable",
        "predicted_values": [509.17]
      }
    ],
    [
      {
        "type": "regression",
        "output_name": "variable",
        "predicted_values": [512.34]
      }
    ],
    [
      {
        "type": "regression",
        "output_name": "variable",
        "predicted_values": [498.76]
      }
    ]
  ],
  "batch_size": 3,
  "request_id": "batch_prediction_001",
  "timestamp": "2024-01-15T10:35:00Z",
  "processing_time_ms": 123.5
}
```

### 3. Get Available Models

**GET** `/models`

Get a list of all available AI models.

#### Response

```json
{
  "success": true,
  "models": ["clf_model_rf_v2", "reg_model_rf_v2"],
  "count": 2,
  "timestamp": "2024-01-15T10:40:00Z"
}
```

### 4. Get Models by Version

**GET** `/models/versions`

Get all available models grouped by their versions with detailed information.

#### Query Parameters

- `version` (optional): Filter by specific version (v1, v2, unknown)

#### Response

```json
{
  "success": true,
  "models_by_version": {
    "v2": [
      {
        "model_name": "clf_model_rf_v2",
        "version": "v2",
        "type": "classification",
        "features_count": 288,
        "output_names": ["output_label", "output_probability"]
      },
      {
        "model_name": "reg_model_rf_v2",
        "version": "v2",
        "type": "regression",
        "features_count": 288,
        "output_names": ["variable"]
      }
    ]
  },
  "total_models": 2,
  "timestamp": "2024-01-15T10:45:00Z"
}
```

#### Example cURL

```bash
# Get all models by version
curl "http://localhost:8000/api/v1/models/versions"

# Get only v2 models
curl "http://localhost:8000/api/v1/models/versions?version=v2"
```

### 5. Get Model Information

**GET** `/models/{model_name}`

Get detailed information about a specific AI model.

#### Response

```json
{
  "success": true,
  "model_info": {
    "name": "clf_model_rf_v2",
    "path": "/path/to/clf_model_rf_v2.onnx",
    "input_names": ["float_input"],
    "output_names": ["output_label", "output_probability"],
    "input_shapes": [[1, 288]],
    "output_shapes": [[1], []],
    "input_types": ["tensor(float)"],
    "output_types": ["tensor(int64)", "tensor(float)"]
  },
  "timestamp": "2024-01-15T10:50:00Z"
}
```

### 6. Model Loading Statistics

**GET** `/models/stats`

Get statistics about model loading status.

#### Response

```json
{
  "success": true,
  "stats": {
    "lazy_loading_enabled": false,
    "total_available": 2,
    "total_loaded": 2,
    "available_models": ["clf_model_rf_v2", "reg_model_rf_v2"],
    "loaded_models": ["clf_model_rf_v2", "reg_model_rf_v2"],
    "unloaded_models": []
  },
  "timestamp": 1705312200.123
}
```

### 7. Preload Models

**POST** `/models/preload`

Preload all available models into memory (useful for production environments).

#### Response

```json
{
  "success": true,
  "message": "Successfully preloaded 2 models",
  "stats": {
    "lazy_loading_enabled": true,
    "total_available": 2,
    "total_loaded": 2,
    "available_models": ["clf_model_rf_v2", "reg_model_rf_v2"],
    "loaded_models": ["clf_model_rf_v2", "reg_model_rf_v2"],
    "unloaded_models": []
  },
  "timestamp": 1705312300.456
}
```

### 8. Health Check

**GET** `/health`

Check the health status of the AI service and all loaded models.

#### Response

```json
{
  "success": true,
  "status": "healthy",
  "models_count": 2,
  "models": {
    "clf_model_rf_v2": "healthy",
    "reg_model_rf_v2": "healthy"
  },
  "timestamp": "2024-01-15T11:00:00Z"
}
```

## Model Input Requirements

### V2 Models (Current)

All V2 models require exactly **288 numerical features** as input. The features should be:

- Numerical values (integers or floats)
- Within reasonable bounds (-1e10 to 1e10)
- Provided as a list/array of exactly 288 values

#### Example Input Format

```json
{
  "features": [
    1.23, 4.56, 7.89, 0.12, 3.45, 6.78, 9.01, 2.34,
    5.67, 8.90, 1.23, 4.56, 7.89, 0.12, 3.45, 6.78,
    // ... continue for 288 total values
  ]
}
```

## Model Output Formats

### Classification Models (clf_model_rf_v2)

Classification models return:

- `predicted_class`: Integer representing the predicted class index
- `probabilities`: Array of probability values for each class
- `confidence`: Highest probability value (confidence score)

### Regression Models (reg_model_rf_v2)

Regression models return:

- `predicted_values`: Array containing the predicted numerical value(s)

## Error Handling

### Common Error Responses

#### 400 Bad Request

```json
{
  "success": false,
  "error": "Feature at index 5 must be a number",
  "error_type": "ValidationError",
  "request_id": "optional_request_id",
  "timestamp": "2024-01-15T11:05:00Z"
}
```

#### 404 Not Found

```json
{
  "success": false,
  "error": "Model 'invalid_model' not found",
  "error_type": "ModelNotFoundError",
  "request_id": "optional_request_id",
  "timestamp": "2024-01-15T11:05:00Z"
}
```

#### 500 Internal Server Error

```json
{
  "success": false,
  "error": "Internal server error during prediction",
  "error_type": "InternalServerError",
  "request_id": "optional_request_id",
  "timestamp": "2024-01-15T11:05:00Z"
}
```

## Rate Limiting and Performance

- **Batch Size Limit**: Maximum 100 samples per batch request
- **Feature Validation**: All features are validated for type and bounds
- **Processing Time**: Typical response times range from 10-100ms depending on model and batch size
- **Memory Usage**: Models are loaded into memory for fast inference

## Version Management

The API supports multiple model versions:

- **v2**: Current generation models with 288 input features
- **v1**: Legacy models (if present)
- **unknown**: Models without explicit version information

Use the `/models/versions` endpoint to discover available models and their versions.

## Getting Started

1. **Start the API server**:
   ```bash
   cd backend
   python -m uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
   ```

2. **Check health status**:
   ```bash
   curl http://localhost:8000/api/v1/health
   ```

3. **List available models**:
   ```bash
   curl http://localhost:8000/api/v1/models
   ```

4. **Make a test prediction**:
   ```bash
   curl -X POST "http://localhost:8000/api/v1/predict" \
     -H "Content-Type: application/json" \
     -d '{
       "model_name": "clf_model_rf_v2",
       "features": [/* 288 numerical values */]
     }'
   ```

## Support and Troubleshooting

- Ensure all input features are numerical and within valid bounds
- Check model availability using the `/models` endpoint
- Use the `/health` endpoint to verify model loading status
- Review server logs for detailed error information
- For batch predictions, ensure all samples have the same number of features

## API Versioning

Current API version: **v1**

All endpoints are prefixed with `/api/v1/` to support future API versioning.