# FLB Nuclear Power Plant AI Backend

A FastAPI-based backend service for nuclear power plant monitoring using AI models for classification and regression predictions.

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- pip package manager

### Installation

1. **Clone the repository and navigate to backend:**
   ```bash
   cd backend
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Start the API server:**
   ```bash
   python src/main.py
   ```

The API will be available at `http://localhost:8000`

## 📊 Available Models

### Version 2 Models (Latest)
- **clf_model_rf_v2.onnx** - Classification model (2.40 MB)
  - Input: 288 features
  - Outputs: predicted class and probabilities
  
- **reg_model_rf_v2.onnx** - Regression model (10.13 MB)
  - Input: 288 features
  - Output: continuous prediction values

## 🔧 API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v1/predict` | POST | Single prediction |
| `/api/v1/predict/batch` | POST | Batch predictions |
| `/api/v1/models` | GET | List available models |
| `/api/v1/models/versions` | GET | Models grouped by version |
| `/api/v1/models/{model_name}` | GET | Model information |
| `/api/v1/models/stats` | GET | Loading statistics |
| `/api/v1/models/preload` | POST | Preload all models |
| `/api/v1/health` | GET | Health check |

## 📖 Documentation

- **[API Documentation](API_DOCUMENTATION.md)** - Complete API reference
- **[API Examples](api_examples.py)** - Python examples for all endpoints

## 🧪 Testing

### Run API Examples
```bash
# Make sure the API server is running first
python api_examples.py
```

### Test Model Manager
```bash
python test_model_manager.py
```

### Analyze Models
```bash
python analyze_models.py
```

## 📁 Project Structure

```
backend/
├── src/
│   ├── main.py              # FastAPI application entry point
│   ├── model_manager.py     # Model loading and management
│   ├── prediction_routes.py # API route definitions
│   ├── prediction_schemas.py# Pydantic schemas for validation
│   └── utils.py            # Utility functions
├── models/                  # AI model files (.onnx)
├── requirements.txt         # Python dependencies
├── api_examples.py         # Usage examples
├── test_model_manager.py   # Model manager tests
├── analyze_models.py       # Model analysis script
├── API_DOCUMENTATION.md    # Complete API documentation
└── README.md              # This file
```

## 🔍 Model Analysis

To analyze model details:
```bash
python analyze_models.py
```

This will generate detailed reports about model inputs, outputs, and metadata.

## 🏥 Health Monitoring

Check API health:
```bash
curl http://localhost:8000/api/v1/health
```

## 🚨 Error Handling

The API provides comprehensive error responses with:
- HTTP status codes
- Error messages
- Request IDs for tracking
- Timestamps

## 📈 Performance

- **Lazy Loading**: Models are loaded on first use
- **Caching**: Loaded models remain in memory
- **Batch Processing**: Efficient batch prediction support
- **Async Support**: Non-blocking request handling

## 🔧 Configuration

The API can be configured through environment variables or by modifying `src/main.py`:

- **Host**: Default `0.0.0.0`
- **Port**: Default `8000`
- **Model Directory**: Default `./models`
- **Lazy Loading**: Default `True`

## 📝 License

This project is part of the FLB Nuclear Power Plant monitoring system.

## 🤝 Contributing

1. Ensure all tests pass
2. Follow the existing code style
3. Add appropriate documentation
4. Test with both v1 and v2 models

## 📞 Support

For issues or questions, please check the API documentation or run the health check endpoint to verify system status.