"""
Predictive Analytics Service
Provides forecasting and predictive insights for organizational patterns and trends
"""

import asyncio
import logging
import uuid
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
import structlog
from collections import defaultdict, deque
import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import PolynomialFeatures
from sklearn.metrics import mean_squared_error, r2_score
import warnings
warnings.filterwarnings('ignore')

logger = structlog.get_logger(__name__)

class ForecastType(Enum):
    """Types of forecasts"""
    PATTERN_FREQUENCY = "pattern_frequency"
    TREND_CONTINUATION = "trend_continuation"
    SEASONAL_PATTERN = "seasonal_pattern"
    ANOMALY_DETECTION = "anomaly_detection"
    INTERVENTION_IMPACT = "intervention_impact"
    RISK_PROBABILITY = "risk_probability"
    OPPORTUNITY_EMERGENCE = "opportunity_emergence"
    PERFORMANCE_TRAJECTORY = "performance_trajectory"

class ForecastHorizon(Enum):
    """Forecast time horizons"""
    SHORT_TERM = "short_term"      # 1-4 weeks
    MEDIUM_TERM = "medium_term"    # 1-3 months
    LONG_TERM = "long_term"        # 3-12 months
    STRATEGIC = "strategic"        # 1+ years

class ConfidenceLevel(Enum):
    """Confidence levels for predictions"""
    VERY_LOW = "very_low"      # < 50%
    LOW = "low"                # 50-65%
    MEDIUM = "medium"          # 65-80%
    HIGH = "high"              # 80-90%
    VERY_HIGH = "very_high"    # > 90%

@dataclass
class TimeSeriesData:
    """Time series data for forecasting"""
    timestamps: List[datetime]
    values: List[float]
    metadata: Dict[str, Any]
    data_quality_score: float
    seasonality_detected: bool
    trend_detected: bool

@dataclass
class ForecastResult:
    """Result of a forecast analysis"""
    id: str
    forecast_type: ForecastType
    target_variable: str
    forecast_horizon: ForecastHorizon
    predicted_values: List[float]
    prediction_timestamps: List[datetime]
    confidence_intervals: List[Tuple[float, float]]
    confidence_level: ConfidenceLevel
    model_accuracy: float
    trend_direction: str  # increasing, decreasing, stable
    seasonal_components: Optional[Dict[str, Any]]
    key_insights: List[str]
    risk_factors: List[str]
    recommendations: List[str]
    created_at: datetime = field(default_factory=datetime.utcnow)

@dataclass
class TrendAnalysis:
    """Analysis of trends in organizational data"""
    id: str
    variable_name: str
    trend_strength: float  # -1 to 1
    trend_direction: str
    trend_significance: float
    change_rate: float  # rate of change per time unit
    acceleration: float  # second derivative
    turning_points: List[datetime]
    trend_stability: float
    forecast_reliability: float

@dataclass
class AnomalyDetection:
    """Anomaly detection results"""
    id: str
    timestamp: datetime
    variable_name: str
    observed_value: float
    expected_value: float
    anomaly_score: float
    anomaly_type: str  # spike, dip, shift, trend_change
    severity: str  # low, medium, high, critical
    potential_causes: List[str]
    impact_assessment: str
    recommended_actions: List[str]

@dataclass
class RiskForecast:
    """Risk probability forecast"""
    id: str
    risk_type: str
    risk_description: str
    probability_forecast: List[float]
    forecast_timestamps: List[datetime]
    risk_factors: List[str]
    mitigation_strategies: List[str]
    impact_severity: str
    confidence_score: float

class PredictiveAnalyticsService:
    """Service for predictive analytics and forecasting"""
    
    def __init__(self):
        self.forecast_results = {}  # forecast_id -> ForecastResult
        self.trend_analyses = {}  # analysis_id -> TrendAnalysis
        self.anomaly_detections = {}  # anomaly_id -> AnomalyDetection
        self.risk_forecasts = {}  # risk_id -> RiskForecast
        
        # Historical data storage for forecasting
        self.time_series_data = defaultdict(lambda: deque(maxlen=1000))  # variable -> time series
        
        # Forecasting models
        self.models = {}
        
        # Configuration
        self.config = {
            'min_data_points_for_forecast': 10,
            'forecast_confidence_threshold': 0.6,
            'anomaly_detection_threshold': 2.0,  # standard deviations
            'trend_significance_threshold': 0.05,
            'seasonal_detection_min_periods': 4,
            'max_forecast_horizon_days': 365
        }
    
    async def add_time_series_data(self, variable_name: str, timestamp: datetime, value: float,
                                 metadata: Optional[Dict[str, Any]] = None):
        """Add new data point to time series"""
        try:
            data_point = {
                'timestamp': timestamp,
                'value': value,
                'metadata': metadata or {}
            }
            
            self.time_series_data[variable_name].append(data_point)
            
            # Trigger analysis if we have enough data
            if len(self.time_series_data[variable_name]) >= self.config['min_data_points_for_forecast']:
                await self._update_forecasts(variable_name)
            
        except Exception as e:
            logger.error("Time series data addition failed", error=str(e))
    
    async def generate_pattern_frequency_forecast(self, pattern_id: str, 
                                                forecast_horizon: ForecastHorizon) -> ForecastResult:
        """Generate forecast for pattern frequency"""
        try:
            # Get historical pattern data
            time_series = await self._get_pattern_time_series(pattern_id)
            
            if len(time_series.timestamps) < self.config['min_data_points_for_forecast']:
                raise ValueError(f"Insufficient data for forecasting pattern {pattern_id}")
            
            # Prepare data for forecasting
            X, y = self._prepare_time_series_data(time_series)
            
            # Choose appropriate model based on data characteristics
            model = self._select_forecasting_model(time_series)
            
            # Train model
            model.fit(X, y)
            
            # Generate forecast
            forecast_periods = self._get_forecast_periods(forecast_horizon)
            future_X = self._generate_future_features(X, forecast_periods)
            predictions = model.predict(future_X)
            
            # Calculate confidence intervals
            confidence_intervals = self._calculate_confidence_intervals(model, future_X, y)
            
            # Generate prediction timestamps
            last_timestamp = time_series.timestamps[-1]
            prediction_timestamps = [
                last_timestamp + timedelta(days=i+1) for i in range(forecast_periods)
            ]
            
            # Assess model accuracy
            model_accuracy = self._assess_model_accuracy(model, X, y)
            
            # Determine confidence level
            confidence_level = self._determine_confidence_level(model_accuracy, len(time_series.values))
            
            # Analyze trend
            trend_direction = self._analyze_trend_direction(predictions)
            
            # Generate insights
            insights = self._generate_forecast_insights(time_series, predictions, trend_direction)
            
            # Identify risk factors
            risk_factors = self._identify_forecast_risks(time_series, predictions)
            
            # Generate recommendations
            recommendations = self._generate_forecast_recommendations(predictions, trend_direction, risk_factors)
            
            forecast_result = ForecastResult(
                id=str(uuid.uuid4()),
                forecast_type=ForecastType.PATTERN_FREQUENCY,
                target_variable=f"pattern_{pattern_id}_frequency",
                forecast_horizon=forecast_horizon,
                predicted_values=predictions.tolist(),
                prediction_timestamps=prediction_timestamps,
                confidence_intervals=confidence_intervals,
                confidence_level=confidence_level,
                model_accuracy=model_accuracy,
                trend_direction=trend_direction,
                seasonal_components=self._detect_seasonality(time_series),
                key_insights=insights,
                risk_factors=risk_factors,
                recommendations=recommendations
            )
            
            self.forecast_results[forecast_result.id] = forecast_result
            
            logger.info("Pattern frequency forecast generated",
                       pattern_id=pattern_id,
                       forecast_horizon=forecast_horizon.value,
                       model_accuracy=model_accuracy)
            
            return forecast_result
            
        except Exception as e:
            logger.error("Pattern frequency forecast generation failed", error=str(e))
            raise
    
    async def detect_anomalies(self, variable_name: str, 
                             detection_window_days: int = 30) -> List[AnomalyDetection]:
        """Detect anomalies in time series data"""
        try:
            # Get recent time series data
            time_series = await self._get_variable_time_series(variable_name, detection_window_days)
            
            if len(time_series.values) < 5:
                return []  # Need minimum data for anomaly detection
            
            anomalies = []
            
            # Statistical anomaly detection
            statistical_anomalies = self._detect_statistical_anomalies(time_series)
            anomalies.extend(statistical_anomalies)
            
            # Trend-based anomaly detection
            trend_anomalies = self._detect_trend_anomalies(time_series)
            anomalies.extend(trend_anomalies)
            
            # Seasonal anomaly detection (if seasonality detected)
            if time_series.seasonality_detected:
                seasonal_anomalies = self._detect_seasonal_anomalies(time_series)
                anomalies.extend(seasonal_anomalies)
            
            # Store anomalies
            for anomaly in anomalies:
                self.anomaly_detections[anomaly.id] = anomaly
            
            logger.info("Anomaly detection completed",
                       variable_name=variable_name,
                       anomalies_detected=len(anomalies))
            
            return anomalies
            
        except Exception as e:
            logger.error("Anomaly detection failed", error=str(e))
            return []
    
    async def analyze_trends(self, variable_name: str, 
                           analysis_window_days: int = 90) -> TrendAnalysis:
        """Analyze trends in time series data"""
        try:
            # Get time series data
            time_series = await self._get_variable_time_series(variable_name, analysis_window_days)
            
            if len(time_series.values) < self.config['min_data_points_for_forecast']:
                raise ValueError(f"Insufficient data for trend analysis of {variable_name}")
            
            # Calculate trend metrics
            trend_strength = self._calculate_trend_strength(time_series.values)
            trend_direction = self._determine_trend_direction(time_series.values)
            trend_significance = self._test_trend_significance(time_series.values)
            change_rate = self._calculate_change_rate(time_series.values, time_series.timestamps)
            acceleration = self._calculate_acceleration(time_series.values)
            turning_points = self._identify_turning_points(time_series.timestamps, time_series.values)
            trend_stability = self._assess_trend_stability(time_series.values)
            forecast_reliability = self._assess_forecast_reliability(time_series)
            
            trend_analysis = TrendAnalysis(
                id=str(uuid.uuid4()),
                variable_name=variable_name,
                trend_strength=trend_strength,
                trend_direction=trend_direction,
                trend_significance=trend_significance,
                change_rate=change_rate,
                acceleration=acceleration,
                turning_points=turning_points,
                trend_stability=trend_stability,
                forecast_reliability=forecast_reliability
            )
            
            self.trend_analyses[trend_analysis.id] = trend_analysis
            
            logger.info("Trend analysis completed",
                       variable_name=variable_name,
                       trend_direction=trend_direction,
                       trend_strength=trend_strength)
            
            return trend_analysis
            
        except Exception as e:
            logger.error("Trend analysis failed", error=str(e))
            raise
    
    async def forecast_intervention_impact(self, intervention_id: str,
                                         target_metrics: List[str]) -> Dict[str, ForecastResult]:
        """Forecast the impact of an intervention on target metrics"""
        try:
            impact_forecasts = {}
            
            for metric in target_metrics:
                # Get baseline time series for the metric
                baseline_series = await self._get_variable_time_series(metric, 60)  # 60 days baseline
                
                if len(baseline_series.values) < self.config['min_data_points_for_forecast']:
                    continue
                
                # Model intervention impact
                impact_model = self._create_intervention_impact_model(baseline_series, intervention_id)
                
                # Generate forecast with intervention
                forecast_periods = 30  # 30 days post-intervention
                intervention_forecast = self._forecast_with_intervention(
                    impact_model, baseline_series, forecast_periods
                )
                
                # Create forecast result
                forecast_result = ForecastResult(
                    id=str(uuid.uuid4()),
                    forecast_type=ForecastType.INTERVENTION_IMPACT,
                    target_variable=metric,
                    forecast_horizon=ForecastHorizon.SHORT_TERM,
                    predicted_values=intervention_forecast['values'],
                    prediction_timestamps=intervention_forecast['timestamps'],
                    confidence_intervals=intervention_forecast['confidence_intervals'],
                    confidence_level=intervention_forecast['confidence_level'],
                    model_accuracy=intervention_forecast['accuracy'],
                    trend_direction=intervention_forecast['trend_direction'],
                    seasonal_components=None,
                    key_insights=intervention_forecast['insights'],
                    risk_factors=intervention_forecast['risks'],
                    recommendations=intervention_forecast['recommendations']
                )
                
                impact_forecasts[metric] = forecast_result
                self.forecast_results[forecast_result.id] = forecast_result
            
            logger.info("Intervention impact forecast completed",
                       intervention_id=intervention_id,
                       metrics_forecasted=len(impact_forecasts))
            
            return impact_forecasts
            
        except Exception as e:
            logger.error("Intervention impact forecasting failed", error=str(e))
            return {}
    
    def _prepare_time_series_data(self, time_series: TimeSeriesData) -> Tuple[np.ndarray, np.ndarray]:
        """Prepare time series data for machine learning models"""
        try:
            # Convert timestamps to numeric features
            timestamps = np.array([ts.timestamp() for ts in time_series.timestamps])
            values = np.array(time_series.values)
            
            # Normalize timestamps to start from 0
            timestamps = timestamps - timestamps[0]
            
            # Create feature matrix
            X = timestamps.reshape(-1, 1)
            
            # Add polynomial features if trend is non-linear
            if self._is_nonlinear_trend(values):
                poly_features = PolynomialFeatures(degree=2)
                X = poly_features.fit_transform(X)
            
            return X, values
            
        except Exception as e:
            logger.error("Time series data preparation failed", error=str(e))
            raise
    
    def _select_forecasting_model(self, time_series: TimeSeriesData):
        """Select appropriate forecasting model based on data characteristics"""
        try:
            # For now, use linear regression as the base model
            # In a production system, this would include more sophisticated model selection
            model = LinearRegression()
            
            return model
            
        except Exception as e:
            logger.error("Forecasting model selection failed", error=str(e))
            return LinearRegression()
    
    def _calculate_confidence_intervals(self, model, X_future: np.ndarray, 
                                      y_train: np.ndarray) -> List[Tuple[float, float]]:
        """Calculate confidence intervals for predictions"""
        try:
            # Simple approach using training error
            # In production, would use more sophisticated methods
            predictions = model.predict(X_future)
            
            # Calculate prediction error from training data
            X_train = X_future[:len(y_train)] if len(X_future) >= len(y_train) else X_future
            if len(X_train) > 0:
                train_predictions = model.predict(X_train[:len(y_train)])
                mse = mean_squared_error(y_train, train_predictions)
                std_error = np.sqrt(mse)
            else:
                std_error = np.std(y_train) * 0.1  # Conservative estimate
            
            # 95% confidence intervals
            confidence_intervals = []
            for pred in predictions:
                lower = pred - 1.96 * std_error
                upper = pred + 1.96 * std_error
                confidence_intervals.append((lower, upper))
            
            return confidence_intervals
            
        except Exception as e:
            logger.error("Confidence interval calculation failed", error=str(e))
            # Return wide intervals as fallback
            return [(pred - abs(pred) * 0.5, pred + abs(pred) * 0.5) for pred in model.predict(X_future)]
    
    def _assess_model_accuracy(self, model, X: np.ndarray, y: np.ndarray) -> float:
        """Assess model accuracy using cross-validation or holdout"""
        try:
            if len(y) < 5:
                return 0.5  # Default for insufficient data
            
            # Simple holdout validation
            split_point = int(len(y) * 0.8)
            X_train, X_test = X[:split_point], X[split_point:]
            y_train, y_test = y[:split_point], y[split_point:]
            
            if len(y_test) == 0:
                # Use R² score on training data
                predictions = model.predict(X)
                r2 = r2_score(y, predictions)
                return max(0, r2)  # Ensure non-negative
            
            # Train on subset and test
            model.fit(X_train, y_train)
            test_predictions = model.predict(X_test)
            r2 = r2_score(y_test, test_predictions)
            
            return max(0, r2)  # Ensure non-negative
            
        except Exception as e:
            logger.error("Model accuracy assessment failed", error=str(e))
            return 0.5
    
    def _determine_confidence_level(self, model_accuracy: float, data_points: int) -> ConfidenceLevel:
        """Determine confidence level based on model accuracy and data quantity"""
        try:
            # Adjust confidence based on both accuracy and data quantity
            data_factor = min(data_points / 50, 1.0)  # More data = higher confidence
            combined_score = model_accuracy * data_factor
            
            if combined_score >= 0.9:
                return ConfidenceLevel.VERY_HIGH
            elif combined_score >= 0.8:
                return ConfidenceLevel.HIGH
            elif combined_score >= 0.65:
                return ConfidenceLevel.MEDIUM
            elif combined_score >= 0.5:
                return ConfidenceLevel.LOW
            else:
                return ConfidenceLevel.VERY_LOW
                
        except Exception as e:
            logger.error("Confidence level determination failed", error=str(e))
            return ConfidenceLevel.MEDIUM
    
    def _analyze_trend_direction(self, predictions: np.ndarray) -> str:
        """Analyze trend direction from predictions"""
        try:
            if len(predictions) < 2:
                return "stable"
            
            # Calculate overall trend
            start_value = predictions[0]
            end_value = predictions[-1]
            change_percentage = (end_value - start_value) / abs(start_value) if start_value != 0 else 0
            
            if change_percentage > 0.05:  # 5% increase
                return "increasing"
            elif change_percentage < -0.05:  # 5% decrease
                return "decreasing"
            else:
                return "stable"
                
        except Exception as e:
            logger.error("Trend direction analysis failed", error=str(e))
            return "stable"
    
    async def get_predictive_dashboard_data(self) -> Dict[str, Any]:
        """Get comprehensive data for predictive analytics dashboard"""
        try:
            # Get recent forecasts
            recent_forecasts = [
                f for f in self.forecast_results.values()
                if f.created_at > datetime.utcnow() - timedelta(days=7)
            ]
            
            # Get recent anomalies
            recent_anomalies = [
                a for a in self.anomaly_detections.values()
                if a.timestamp > datetime.utcnow() - timedelta(days=7)
            ]
            
            # Get trend analyses
            recent_trends = [
                t for t in self.trend_analyses.values()
            ]
            
            # Calculate summary statistics
            forecast_accuracy_avg = np.mean([f.model_accuracy for f in recent_forecasts]) if recent_forecasts else 0
            high_confidence_forecasts = len([f for f in recent_forecasts if f.confidence_level in [ConfidenceLevel.HIGH, ConfidenceLevel.VERY_HIGH]])
            critical_anomalies = len([a for a in recent_anomalies if a.severity == 'critical'])
            
            return {
                'summary_stats': {
                    'total_forecasts': len(recent_forecasts),
                    'average_forecast_accuracy': forecast_accuracy_avg,
                    'high_confidence_forecasts': high_confidence_forecasts,
                    'recent_anomalies': len(recent_anomalies),
                    'critical_anomalies': critical_anomalies,
                    'trend_analyses': len(recent_trends)
                },
                'recent_forecasts': [self._serialize_forecast_result(f) for f in recent_forecasts[:10]],
                'recent_anomalies': [self._serialize_anomaly_detection(a) for a in recent_anomalies[:10]],
                'trend_summaries': [self._serialize_trend_analysis(t) for t in recent_trends[:10]],
                'forecast_accuracy_trend': self._calculate_forecast_accuracy_trend(),
                'prediction_confidence_distribution': self._calculate_confidence_distribution(recent_forecasts),
                'last_updated': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error("Predictive dashboard data generation failed", error=str(e))
            return {'error': 'Dashboard data generation failed'}
    
    def _serialize_forecast_result(self, forecast: ForecastResult) -> Dict[str, Any]:
        """Serialize forecast result for API response"""
        return {
            'id': forecast.id,
            'forecast_type': forecast.forecast_type.value,
            'target_variable': forecast.target_variable,
            'forecast_horizon': forecast.forecast_horizon.value,
            'predicted_values': forecast.predicted_values,
            'prediction_timestamps': [ts.isoformat() for ts in forecast.prediction_timestamps],
            'confidence_level': forecast.confidence_level.value,
            'model_accuracy': forecast.model_accuracy,
            'trend_direction': forecast.trend_direction,
            'key_insights': forecast.key_insights,
            'risk_factors': forecast.risk_factors,
            'recommendations': forecast.recommendations,
            'created_at': forecast.created_at.isoformat()
        }

# Global service instance
predictive_analytics_service = PredictiveAnalyticsService()