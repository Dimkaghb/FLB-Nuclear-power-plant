"""
Enhanced Nuclear Reactor Analysis Module
Specifically designed for FLB Nuclear Power Plant AI Application

This module provides advanced functionality for:
- Real-time reactor parameter analysis
- Enhanced feature engineering for nuclear reactor data
- Safety system monitoring and alerting
- Predictive maintenance recommendations
- Advanced anomaly detection
"""

import os
import glob
import numpy as np
import pandas as pd
import joblib
from typing import Dict, List, Tuple, Optional, Any
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

from sklearn.model_selection import train_test_split, GridSearchCV, TimeSeriesSplit
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor, IsolationForest
from sklearn.preprocessing import StandardScaler, RobustScaler
from sklearn.metrics import classification_report, confusion_matrix, mean_absolute_error, roc_auc_score
from sklearn.feature_selection import SelectKBest, f_classif
import matplotlib.pyplot as plt
import seaborn as sns

class ReactorDataAnalyzer:
    """
    Advanced reactor data analyzer for nuclear power plant operations.
    
    Features:
    - Multi-model ensemble predictions
    - Real-time anomaly detection
    - Safety system monitoring
    - Predictive maintenance alerts
    - Advanced feature engineering
    """
    
    def __init__(self, config: Optional[Dict] = None):
        """
        Initialize the reactor data analyzer.
        
        Args:
            config: Configuration dictionary with analysis parameters
        """
        self.config = config or self._get_default_config()
        self.models = {}
        self.scalers = {}
        self.feature_columns = []
        self.safety_thresholds = self._get_safety_thresholds()
        self.anomaly_detector = None
        
    def _get_default_config(self) -> Dict:
        """Get default configuration for reactor analysis."""
        return {
            'rolling_window': 5,
            'pred_pre_event_seconds': 30,
            'anomaly_threshold': 0.1,
            'safety_margin': 0.15,
            'model_ensemble_size': 3,
            'feature_selection_k': 50,
            'use_time_series_cv': True,
            'n_estimators': 500,
            'max_depth': 25,
            'min_samples_split': 3
        }
    
    def _get_safety_thresholds(self) -> Dict:
        """Define safety thresholds for critical reactor parameters."""
        return {
            'temperature': {
                'peak_fuel_temp': {'warning': 450, 'critical': 500},
                'avg_rcs_temp': {'warning': 320, 'critical': 350},
                'pressurizer_temp': {'warning': 370, 'critical': 400}
            },
            'pressure': {
                'rcs_pressure': {'warning': 140, 'critical': 120},
                'pressurizer_pressure': {'warning': 140, 'critical': 120},
                'sg_pressure': {'warning': 60, 'critical': 50}
            },
            'flow': {
                'rcs_flow': {'warning': 800, 'critical': 600},
                'feedwater_flow': {'warning': 400, 'critical': 300}
            },
            'radiation': {
                'building_radiation': {'warning': 1.0, 'critical': 5.0},
                'rcs_activity': {'warning': 5000, 'critical': 10000}
            }
        }
    
    def enhanced_feature_engineering(self, df: pd.DataFrame, feature_cols: List[str]) -> pd.DataFrame:
        """
        Apply enhanced feature engineering for nuclear reactor data.
        
        Args:
            df: Input dataframe with reactor parameters
            feature_cols: List of feature column names
            
        Returns:
            DataFrame with engineered features
        """
        out = df.copy()
        
        # Ensure all feature columns exist
        for c in feature_cols:
            if c not in out.columns:
                out[c] = 0.0
        
        # 1. Rolling statistics (multiple windows)
        windows = [3, 5, 10, 20]
        for window in windows:
            for c in feature_cols:
                out[f"{c}_rm{window}"] = out[c].rolling(window=window, min_periods=1).mean()
                out[f"{c}_rstd{window}"] = out[c].rolling(window=window, min_periods=1).std().fillna(0)
                out[f"{c}_rmax{window}"] = out[c].rolling(window=window, min_periods=1).max()
                out[f"{c}_rmin{window}"] = out[c].rolling(window=window, min_periods=1).min()
        
        # 2. Differential features
        for c in feature_cols:
            out[f"{c}_d1"] = out[c].diff().fillna(0.0)
            out[f"{c}_d2"] = out[c].diff(2).fillna(0.0)
            out[f"{c}_pct_change"] = out[c].pct_change().fillna(0.0)
        
        # 3. Rate of change features
        for c in feature_cols:
            out[f"{c}_roc_5"] = (out[c] - out[c].shift(5)) / 5
            out[f"{c}_roc_10"] = (out[c] - out[c].shift(10)) / 10
            out[f"{c}_acceleration"] = out[f"{c}_d1"].diff().fillna(0.0)
        
        # 4. Cross-parameter relationships
        if 'TFPK' in feature_cols and 'P' in feature_cols:
            out['temp_pressure_ratio'] = out['TFPK'] / (out['P'] + 1e-6)
        
        if 'RC87' in feature_cols and 'LVCR' in feature_cols:
            out['flow_level_ratio'] = out['RC87'] / (out['LVCR'] + 1e-6)
        
        # 5. Safety system indicators
        emergency_indicators = []
        for c in feature_cols:
            if 'HPI' in c or 'ECCS' in c or 'SPRAY' in c:
                emergency_indicators.append(c)
        
        if emergency_indicators:
            out['emergency_systems_active'] = out[emergency_indicators].sum(axis=1)
        
        # 6. Anomaly scores for individual parameters
        for c in feature_cols:
            if c in out.columns:
                # Simple z-score based anomaly detection
                mean_val = out[c].rolling(window=50, min_periods=10).mean()
                std_val = out[c].rolling(window=50, min_periods=10).std()
                out[f"{c}_zscore"] = (out[c] - mean_val) / (std_val + 1e-6)
                out[f"{c}_anomaly"] = (np.abs(out[f"{c}_zscore"]) > 3).astype(int)
        
        return out
    
    def detect_event_time_advanced(self, df: pd.DataFrame, sensitive_columns: List[str], 
                                 method: str = 'gradient') -> float:
        """
        Advanced event detection using multiple methods.
        
        Args:
            df: Input dataframe
            sensitive_columns: List of sensitive parameter columns
            method: Detection method ('gradient', 'changepoint', 'ensemble')
            
        Returns:
            Detected event time
        """
        if "TIME" not in df.columns:
            return df.index[-1] if len(df) > 0 else 0.0
        
        if method == 'gradient':
            return self._detect_by_gradient(df, sensitive_columns)
        elif method == 'changepoint':
            return self._detect_by_changepoint(df, sensitive_columns)
        elif method == 'ensemble':
            # Use ensemble of methods
            grad_time = self._detect_by_gradient(df, sensitive_columns)
            cp_time = self._detect_by_changepoint(df, sensitive_columns)
            return min(grad_time, cp_time)
        else:
            raise ValueError(f"Unknown detection method: {method}")
    
    def _detect_by_gradient(self, df: pd.DataFrame, sensitive_columns: List[str]) -> float:
        """Detect event using gradient-based method."""
        grads = []
        for c in sensitive_columns:
            if c in df.columns:
                series = df[c].fillna(method="ffill").fillna(0).values.astype(float)
                g = np.abs(np.gradient(series))
                grads.append(g)
        
        if len(grads) == 0:
            return df["TIME"].max()
        
        total_grad = np.sum(grads, axis=0)
        # Adaptive threshold based on data distribution
        threshold = np.percentile(total_grad, 95) + 2 * np.std(total_grad)
        
        idxs = np.where(total_grad > threshold)[0]
        if len(idxs) == 0:
            return df["TIME"].max()
        
        return float(df["TIME"].iloc[idxs[0]])
    
    def _detect_by_changepoint(self, df: pd.DataFrame, sensitive_columns: List[str]) -> float:
        """Detect event using changepoint detection."""
        try:
            import ruptures as rpt
            
            # Combine sensitive columns
            data_matrix = []
            for c in sensitive_columns:
                if c in df.columns:
                    series = df[c].fillna(method="ffill").fillna(0).values
                    data_matrix.append(series)
            
            if len(data_matrix) == 0:
                return df["TIME"].max()
            
            signal = np.column_stack(data_matrix)
            
            # Use Pelt algorithm for changepoint detection
            algo = rpt.Pelt(model="rbf").fit(signal)
            changepoints = algo.predict(pen=10)
            
            if len(changepoints) > 1:  # First changepoint (excluding end)
                cp_idx = changepoints[0]
                return float(df["TIME"].iloc[min(cp_idx, len(df) - 1)])
            
        except ImportError:
            print("Warning: ruptures package not available, falling back to gradient method")
        except Exception as e:
            print(f"Warning: Changepoint detection failed: {e}, falling back to gradient method")
        
        return self._detect_by_gradient(df, sensitive_columns)
    
    def train_ensemble_models(self, data: pd.DataFrame, feature_cols: List[str], 
                            target_col: str = 'label') -> Dict[str, Any]:
        """
        Train ensemble of models for robust predictions.
        
        Args:
            data: Training data
            feature_cols: Feature column names
            target_col: Target column name
            
        Returns:
            Dictionary containing trained models and metrics
        """
        X = data[feature_cols].fillna(0)
        y = data[target_col].astype(int)
        
        # Feature selection
        selector = SelectKBest(f_classif, k=min(self.config['feature_selection_k'], len(feature_cols)))
        X_selected = selector.fit_transform(X, y)
        selected_features = [feature_cols[i] for i in selector.get_support(indices=True)]
        
        # Time series split for validation
        if self.config['use_time_series_cv']:
            tscv = TimeSeriesSplit(n_splits=5)
            cv_iterator = tscv
        else:
            cv_iterator = 5
        
        # Train multiple models
        models = {}
        
        # 1. Random Forest with different configurations
        rf_configs = [
            {'n_estimators': 300, 'max_depth': 20, 'min_samples_split': 2},
            {'n_estimators': 500, 'max_depth': 25, 'min_samples_split': 3},
            {'n_estimators': 200, 'max_depth': 15, 'min_samples_split': 5}
        ]
        
        for i, config in enumerate(rf_configs):
            rf = RandomForestClassifier(
                random_state=42 + i,
                class_weight='balanced',
                n_jobs=-1,
                **config
            )
            rf.fit(X_selected, y)
            models[f'rf_{i}'] = rf
        
        # 2. Train anomaly detector
        anomaly_detector = IsolationForest(
            contamination=self.config['anomaly_threshold'],
            random_state=42
        )
        anomaly_detector.fit(X_selected[y == 0])  # Train on normal data only
        
        return {
            'models': models,
            'feature_selector': selector,
            'selected_features': selected_features,
            'anomaly_detector': anomaly_detector,
            'scaler': StandardScaler().fit(X_selected)
        }
    
    def predict_with_ensemble(self, features: np.ndarray, models_dict: Dict) -> Dict[str, Any]:
        """
        Make predictions using ensemble of models.
        
        Args:
            features: Input features
            models_dict: Dictionary containing trained models
            
        Returns:
            Dictionary with ensemble predictions and confidence scores
        """
        # Feature selection and scaling
        features_selected = models_dict['feature_selector'].transform(features.reshape(1, -1))
        features_scaled = models_dict['scaler'].transform(features_selected)
        
        # Get predictions from all models
        predictions = []
        probabilities = []
        
        for model_name, model in models_dict['models'].items():
            pred = model.predict(features_scaled)[0]
            prob = model.predict_proba(features_scaled)[0]
            predictions.append(pred)
            probabilities.append(prob)
        
        # Ensemble prediction (majority vote)
        ensemble_pred = np.bincount(predictions).argmax()
        
        # Average probabilities
        avg_probabilities = np.mean(probabilities, axis=0)
        confidence = np.max(avg_probabilities)
        
        # Anomaly detection
        anomaly_score = models_dict['anomaly_detector'].decision_function(features_scaled)[0]
        is_anomaly = models_dict['anomaly_detector'].predict(features_scaled)[0] == -1
        
        return {
            'prediction': ensemble_pred,
            'confidence': confidence,
            'probabilities': avg_probabilities.tolist(),
            'individual_predictions': predictions,
            'anomaly_score': anomaly_score,
            'is_anomaly': is_anomaly
        }
    
    def generate_safety_alerts(self, current_params: Dict[str, float]) -> List[Dict[str, Any]]:
        """
        Generate safety alerts based on current reactor parameters.
        
        Args:
            current_params: Dictionary of current reactor parameters
            
        Returns:
            List of safety alerts
        """
        alerts = []
        
        for category, params in self.safety_thresholds.items():
            for param_name, thresholds in params.items():
                # Map parameter names to actual data columns
                param_key = self._map_param_name(param_name, current_params)
                
                if param_key and param_key in current_params:
                    value = current_params[param_key]
                    
                    if value >= thresholds['critical']:
                        alerts.append({
                            'level': 'CRITICAL',
                            'category': category,
                            'parameter': param_name,
                            'current_value': value,
                            'threshold': thresholds['critical'],
                            'message': f"CRITICAL: {param_name} ({value:.2f}) exceeds critical threshold ({thresholds['critical']})",
                            'timestamp': datetime.now().isoformat(),
                            'recommended_action': self._get_critical_action(param_name)
                        })
                    elif value >= thresholds['warning']:
                        alerts.append({
                            'level': 'WARNING',
                            'category': category,
                            'parameter': param_name,
                            'current_value': value,
                            'threshold': thresholds['warning'],
                            'message': f"WARNING: {param_name} ({value:.2f}) exceeds warning threshold ({thresholds['warning']})",
                            'timestamp': datetime.now().isoformat(),
                            'recommended_action': self._get_warning_action(param_name)
                        })
        
        return sorted(alerts, key=lambda x: {'CRITICAL': 0, 'WARNING': 1}[x['level']])
    
    def _map_param_name(self, param_name: str, current_params: Dict) -> Optional[str]:
        """Map safety threshold parameter names to actual data column names."""
        mapping = {
            'peak_fuel_temp': 'peakFuelTemperature',
            'avg_rcs_temp': 'averageRcsTemperature',
            'pressurizer_temp': 'pressurizerTemperature',
            'rcs_pressure': 'rcsPressure',
            'pressurizer_pressure': 'pressurizerPressureLevel',
            'sg_pressure': 'steamGeneratorPressureA',
            'rcs_flow': 'reactorCoolantFlowA',
            'feedwater_flow': 'steamGeneratorWaterFeedA',
            'building_radiation': 'radiationInBuilding',
            'rcs_activity': 'rcsActivity'
        }
        
        return mapping.get(param_name)
    
    def _get_critical_action(self, param_name: str) -> str:
        """Get recommended critical action for parameter."""
        actions = {
            'peak_fuel_temp': 'IMMEDIATE REACTOR SHUTDOWN - Fuel temperature critical',
            'avg_rcs_temp': 'Reduce reactor power immediately - Check cooling systems',
            'pressurizer_temp': 'Check pressurizer heaters - Verify pressure control',
            'rcs_pressure': 'EMERGENCY - Check for RCS breach - Activate ECCS',
            'pressurizer_pressure': 'EMERGENCY - Pressurizer pressure loss - Check safety valves',
            'sg_pressure': 'Steam generator pressure critical - Check feedwater systems',
            'rcs_flow': 'CRITICAL - RCS flow loss - Check reactor coolant pumps',
            'feedwater_flow': 'Steam generator feedwater critical - Check pumps',
            'building_radiation': 'RADIATION EMERGENCY - Evacuate area - Check containment',
            'rcs_activity': 'HIGH ACTIVITY - Check for fuel damage - Increase monitoring'
        }
        return actions.get(param_name, 'Immediate investigation required')
    
    def _get_warning_action(self, param_name: str) -> str:
        """Get recommended warning action for parameter."""
        actions = {
            'peak_fuel_temp': 'Monitor fuel temperature - Consider power reduction',
            'avg_rcs_temp': 'Check cooling system performance',
            'pressurizer_temp': 'Monitor pressurizer operation',
            'rcs_pressure': 'Monitor RCS pressure trend - Check for leaks',
            'pressurizer_pressure': 'Monitor pressurizer level and pressure',
            'sg_pressure': 'Check steam generator operation',
            'rcs_flow': 'Monitor coolant flow - Check pump performance',
            'feedwater_flow': 'Monitor feedwater system',
            'building_radiation': 'Increase radiation monitoring',
            'rcs_activity': 'Monitor RCS activity levels'
        }
        return actions.get(param_name, 'Increased monitoring recommended')
    
    def generate_maintenance_recommendations(self, historical_data: pd.DataFrame, 
                                           prediction_result: Dict) -> List[Dict[str, Any]]:
        """
        Generate predictive maintenance recommendations.
        
        Args:
            historical_data: Historical reactor data
            prediction_result: Current prediction result
            
        Returns:
            List of maintenance recommendations
        """
        recommendations = []
        
        # Analyze trends in critical parameters
        if len(historical_data) > 100:  # Need sufficient history
            for param in ['TFPK', 'P', 'RC87', 'LVCR']:
                if param in historical_data.columns:
                    trend = self._analyze_parameter_trend(historical_data[param])
                    
                    if trend['degradation_rate'] > 0.1:
                        recommendations.append({
                            'type': 'PREDICTIVE_MAINTENANCE',
                            'component': self._get_component_name(param),
                            'parameter': param,
                            'issue': 'Parameter showing degradation trend',
                            'urgency': 'HIGH' if trend['degradation_rate'] > 0.2 else 'MEDIUM',
                            'estimated_time_to_failure': trend['time_to_failure'],
                            'recommended_action': f"Schedule maintenance for {self._get_component_name(param)}",
                            'confidence': trend['confidence']
                        })
        
        # Check for anomalies that might indicate equipment issues
        if prediction_result.get('is_anomaly', False):
            recommendations.append({
                'type': 'ANOMALY_INVESTIGATION',
                'component': 'UNKNOWN',
                'issue': 'Anomalous behavior detected',
                'urgency': 'HIGH',
                'recommended_action': 'Investigate unusual parameter patterns',
                'anomaly_score': prediction_result.get('anomaly_score', 0)
            })
        
        return recommendations
    
    def _analyze_parameter_trend(self, series: pd.Series) -> Dict[str, float]:
        """Analyze trend in parameter series."""
        # Simple linear trend analysis
        x = np.arange(len(series))
        coeffs = np.polyfit(x, series.values, 1)
        slope = coeffs[0]
        
        # Calculate R-squared for confidence
        y_pred = np.polyval(coeffs, x)
        ss_res = np.sum((series.values - y_pred) ** 2)
        ss_tot = np.sum((series.values - np.mean(series.values)) ** 2)
        r_squared = 1 - (ss_res / ss_tot) if ss_tot > 0 else 0
        
        # Estimate time to failure (simplified)
        if slope > 0:
            # Assuming failure at 2 standard deviations above mean
            current_val = series.iloc[-1]
            failure_threshold = np.mean(series) + 2 * np.std(series)
            time_to_failure = (failure_threshold - current_val) / slope if slope > 0 else np.inf
        else:
            time_to_failure = np.inf
        
        return {
            'degradation_rate': abs(slope) / np.mean(series) if np.mean(series) != 0 else 0,
            'time_to_failure': max(0, time_to_failure),
            'confidence': r_squared
        }
    
    def _get_component_name(self, param: str) -> str:
        """Map parameter to component name."""
        mapping = {
            'TFPK': 'Fuel Assembly',
            'P': 'Pressure System',
            'RC87': 'Reactor Coolant System',
            'LVCR': 'Core Water Level System'
        }
        return mapping.get(param, 'Unknown Component')


def main():
    """
    Main function demonstrating the enhanced reactor analysis functionality.
    """
    print("🚀 Enhanced Nuclear Reactor Analysis System")
    print("=" * 50)
    
    # Initialize analyzer
    config = {
        'rolling_window': 5,
        'pred_pre_event_seconds': 30,
        'anomaly_threshold': 0.05,
        'feature_selection_k': 30
    }
    
    analyzer = ReactorDataAnalyzer(config)
    
    # Example usage with synthetic data
    print("📊 Generating example reactor data...")
    
    # Create synthetic reactor data for demonstration
    np.random.seed(42)
    n_samples = 1000
    time_points = np.linspace(0, 3600, n_samples)  # 1 hour of data
    
    # Simulate normal operation with some noise
    data = {
        'TIME': time_points,
        'TFPK': 300 + 20 * np.sin(time_points / 600) + np.random.normal(0, 5, n_samples),
        'P': 155 + 10 * np.cos(time_points / 800) + np.random.normal(0, 2, n_samples),
        'RC87': 1000 + 50 * np.sin(time_points / 400) + np.random.normal(0, 10, n_samples),
        'LVCR': 50 + 10 * np.cos(time_points / 300) + np.random.normal(0, 2, n_samples),
        'CNH2': 1000 + np.random.normal(0, 50, n_samples),
        'RM1': 0.1 + np.random.exponential(0.05, n_samples)
    }
    
    # Add event simulation in the last 200 samples
    event_start = n_samples - 200
    data['TFPK'][event_start:] += np.linspace(0, 100, 200)  # Temperature rise
    data['P'][event_start:] -= np.linspace(0, 30, 200)      # Pressure drop
    
    df = pd.DataFrame(data)
    
    # Apply enhanced feature engineering
    print("🔧 Applying enhanced feature engineering...")
    feature_cols = ['TFPK', 'P', 'RC87', 'LVCR', 'CNH2', 'RM1']
    df_enhanced = analyzer.enhanced_feature_engineering(df, feature_cols)
    
    print(f"✅ Original features: {len(feature_cols)}")
    print(f"✅ Enhanced features: {len([c for c in df_enhanced.columns if c not in ['TIME']])}")
    
    # Detect event time
    print("🔍 Detecting event time...")
    event_time = analyzer.detect_event_time_advanced(df, feature_cols, method='ensemble')
    print(f"✅ Detected event time: {event_time:.2f} seconds")
    
    # Create labels for training
    labels = []
    for t in df['TIME'].values:
        if t < event_time - 30:
            labels.append(0)  # Normal
        elif t < event_time:
            labels.append(1)  # Pre-event
        else:
            labels.append(2)  # Event
    
    df_enhanced['label'] = labels
    
    # Train ensemble models
    print("🤖 Training ensemble models...")
    enhanced_feature_cols = [c for c in df_enhanced.columns 
                           if c not in ['TIME', 'label'] and not c.endswith('_anomaly')]
    
    models_dict = analyzer.train_ensemble_models(df_enhanced, enhanced_feature_cols)
    print(f"✅ Trained {len(models_dict['models'])} models")
    print(f"✅ Selected {len(models_dict['selected_features'])} features")
    
    # Test prediction
    print("🔮 Testing ensemble prediction...")
    test_features = df_enhanced[enhanced_feature_cols].iloc[-1].values
    prediction_result = analyzer.predict_with_ensemble(test_features, models_dict)
    
    print(f"✅ Prediction: {prediction_result['prediction']}")
    print(f"✅ Confidence: {prediction_result['confidence']:.3f}")
    print(f"✅ Anomaly detected: {prediction_result['is_anomaly']}")
    
    # Generate safety alerts
    print("⚠️  Generating safety alerts...")
    current_params = {
        'peakFuelTemperature': 480,  # Critical level
        'averageRcsTemperature': 330,  # Warning level
        'rcsPressure': 145,  # Normal
        'radiationInBuilding': 0.5   # Normal
    }
    
    alerts = analyzer.generate_safety_alerts(current_params)
    print(f"✅ Generated {len(alerts)} alerts")
    
    for alert in alerts:
        print(f"   {alert['level']}: {alert['message']}")
    
    # Generate maintenance recommendations
    print("🔧 Generating maintenance recommendations...")
    recommendations = analyzer.generate_maintenance_recommendations(df, prediction_result)
    print(f"✅ Generated {len(recommendations)} recommendations")
    
    for rec in recommendations:
        print(f"   {rec['type']}: {rec.get('recommended_action', 'No action specified')}")
    
    print("\n🎉 Enhanced reactor analysis completed successfully!")
    print("💡 This system provides:")
    print("   • Advanced feature engineering with multiple time windows")
    print("   • Ensemble model predictions for robustness")
    print("   • Real-time anomaly detection")
    print("   • Safety threshold monitoring and alerting")
    print("   • Predictive maintenance recommendations")
    print("   • Enhanced event detection algorithms")


if __name__ == "__main__":
    main()