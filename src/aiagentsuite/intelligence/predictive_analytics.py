"""
Predictive Analytics Module

Future state prediction and trend analysis using ML models
to anticipate needs and optimize proactively.
"""

from typing import Any, Optional
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import json
import heapq


class TrendDirection(Enum):
    """Direction of detected trends."""
    RISING = "rising"
    FALLING = "falling"
    STABLE = "stable"
    VOLATILE = "volatile"


class RiskLevel(Enum):
    """Risk assessment levels."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class TrendAnalysis:
    """Analysis of a detected trend."""
    metric: str
    direction: TrendDirection
    confidence: float
    velocity: float  # Rate of change
    predictions: list[tuple[datetime, float]] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class RiskAssessment:
    """Risk assessment result."""
    level: RiskLevel
    score: float  # 0-100
    factors: list[dict[str, Any]]
    recommendations: list[str]
    expires_at: datetime


@dataclass
class RecommendedAction:
    """A recommended action based on predictions."""
    id: str
    action: str
    reason: str
    priority: float
    expected_impact: float
    confidence: float
    metadata: dict[str, Any] = field(default_factory=dict)


class PredictiveAnalytics:
    """
    Predictive analytics engine for forecasting future states
    and recommending proactive actions.

    Provides:
    - Trend analysis and prediction
    - Risk assessment
    - Need prediction
    - Action recommendations
    """

    def __init__(
        self,
        prediction_window: int = 24,  # hours
        min_data_points: int = 5,
        confidence_threshold: float = 0.7,
    ):
        """
        Initialize predictive analytics.

        Args:
            prediction_window: Hours to predict ahead
            min_data_points: Minimum data points for prediction
            confidence_threshold: Minimum confidence for predictions
        """
        self.prediction_window = prediction_window
        self.min_data_points = min_data_points
        self.confidence_threshold = confidence_threshold
        self.historical_data: dict[str, list[tuple[datetime, float]]] = {}
        self.trends: dict[str, TrendAnalysis] = {}
        self.models: dict[str, Any] = {}

    def record_metric(
        self,
        metric_name: str,
        value: float,
        timestamp: Optional[datetime] = None,
    ) -> None:
        """
        Record a metric value for trend analysis.

        Args:
            metric_name: Name of the metric
            value: Metric value
            timestamp: Optional timestamp (defaults to now)
        """
        if timestamp is None:
            timestamp = datetime.now()

        if metric_name not in self.historical_data:
            self.historical_data[metric_name] = []

        self.historical_data[metric_name].append((timestamp, value))

        # Keep only recent data (last 30 days)
        cutoff = datetime.now() - timedelta(days=30)
        self.historical_data[metric_name] = [
            (ts, v) for ts, v in self.historical_data[metric_name]
            if ts >= cutoff
        ]

    def analyze_trends(
        self,
        metric_name: Optional[str] = None,
    ) -> dict[str, TrendAnalysis]:
        """
        Analyze trends in recorded metrics.

        Args:
            metric_name: Optional specific metric to analyze

        Returns:
            Dictionary of trend analyses by metric name
        """
        if metric_name:
            return {metric_name: self._analyze_single_trend(metric_name)}

        results = {}
        for metric in self.historical_data:
            results[metric] = self._analyze_single_trend(metric)
        return results

    def _analyze_single_trend(self, metric_name: str) -> TrendAnalysis:
        """Analyze trend for a single metric."""
        data = self.historical_data.get(metric_name, [])
        
        if len(data) < self.min_data_points:
            return TrendAnalysis(
                metric=metric_name,
                direction=TrendDirection.STABLE,
                confidence=0.0,
                velocity=0.0,
            )

        # Sort by timestamp
        sorted_data = sorted(data, key=lambda x: x[0])
        
        # Calculate basic trend
        values = [v for _, v in sorted_data]
        n = len(values)
        
        # Simple linear regression for trend
        x_mean = (n - 1) / 2
        y_mean = sum(values) / n
        
        numerator = sum((i - x_mean) * (values[i] - y_mean) for i in range(n))
        denominator = sum((i - x_mean) ** 2 for i in range(n))
        
        slope = numerator / denominator if denominator != 0 else 0
        
        # Calculate velocity (rate of change)
        velocity = abs(slope) / y_mean if y_mean != 0 else 0
        
        # Determine direction
        if velocity < 0.01:
            direction = TrendDirection.STABLE
        elif abs(slope) > (max(values) - min(values)) * 0.1:
            direction = TrendDirection.RISING if slope > 0 else TrendDirection.FALLING
        else:
            direction = TrendDirection.VOLATILE

        # Calculate confidence based on data quality
        confidence = min(n / 20.0, 1.0) * (1.0 - min(velocity, 1.0) * 0.3)
        
        # Generate predictions
        predictions = self._generate_predictions(slope, values[-1], sorted_data[-1][0])
        
        return TrendAnalysis(
            metric=metric_name,
            direction=direction,
            confidence=confidence,
            velocity=velocity,
            predictions=predictions,
        )

    def _generate_predictions(
        self,
        slope: float,
        last_value: float,
        last_timestamp: datetime,
    ) -> list[tuple[datetime, float]]:
        """Generate future value predictions."""
        predictions = []
        hours_ahead = [1, 2, 4, 8, 12, 24][:self.prediction_window // 4]
        
        for hours in hours_ahead:
            pred_time = last_timestamp + timedelta(hours=hours)
            pred_value = last_value + (slope * hours)
            predictions.append((pred_time, max(0, pred_value)))  # Ensure non-negative
        
        return predictions

    def predict_value(
        self,
        metric_name: str,
        hours_ahead: int = 1,
    ) -> Optional[tuple[float, float]]:
        """
        Predict future value for a metric.

        Args:
            metric_name: Name of metric to predict
            hours_ahead: Hours in the future to predict

        Returns:
            Tuple of (predicted_value, confidence) or None
        """
        data = self.historical_data.get(metric_name, [])
        
        if len(data) < self.min_data_points:
            return None

        sorted_data = sorted(data, key=lambda x: x[0])
        values = [v for _, v in sorted_data]
        
        # Simple linear extrapolation
        n = len(values)
        x_mean = (n - 1) / 2
        y_mean = sum(values) / n
        
        numerator = sum((i - x_mean) * (values[i] - y_mean) for i in range(n))
        denominator = sum((i - x_mean) ** 2 for i in range(n))
        
        slope = numerator / denominator if denominator != 0 else 0
        
        # Predict at x = n - 1 + hours_ahead
        pred_x = n - 1 + hours_ahead
        predicted_value = y_mean + slope * (pred_x - x_mean)
        
        # Confidence based on data points and extrapolation distance
        confidence = min(n / 20.0, 1.0) * max(0.5, 1.0 - (hours_ahead / 48.0))
        
        return max(0, predicted_value), confidence

    def predict_needs(
        self,
        current_state: dict[str, Any],
    ) -> dict[str, float]:
        """
        Predict likely needs based on current state.

        Args:
            current_state: Current system state

        Returns:
            Dictionary of predicted needs with probabilities
        """
        needs: dict[str, float] = {}
        
        # Analyze current metrics for predictive needs
        for metric, trend in self.trends.items():
            if trend.direction == TrendDirection.RISING:
                # Resource likely needed
                needs[f"increase_{metric}"] = min(trend.velocity * 10, 1.0)
            elif trend.direction == TrendDirection.FALLING:
                needs[f"decrease_{metric}"] = min(trend.velocity * 10, 1.0)
        
        # Analyze patterns for prediction
        for metric in self.historical_data:
            pred = self.predict_value(metric, hours_ahead=1)
            if pred:
                value, confidence = pred
                if confidence >= self.confidence_threshold:
                    # If predicted value is significantly different from recent
                    recent = self.historical_data[metric][-1][1] if self.historical_data[metric] else value
                    if value > recent * 1.2:
                        needs[f"prepare_increase_{metric}"] = confidence
                    elif value < recent * 0.8:
                        needs[f"prepare_decrease_{metric}"] = confidence
        
        return needs

    def identify_risks(
        self,
        context: dict[str, Any],
    ) -> RiskAssessment:
        """
        Identify potential risks based on current context and trends.

        Args:
            context: Current context information

        Returns:
            Risk assessment with level and recommendations
        """
        factors = []
        recommendations = []
        risk_score = 0.0

        # Check trend risks
        for metric, trend in self.trends.items():
            if trend.direction == TrendDirection.FALLING and trend.velocity > 0.5:
                factors.append({
                    "type": "declining_metric",
                    "metric": metric,
                    "velocity": trend.velocity,
                    "severity": "high" if trend.velocity > 0.8 else "medium",
                })
                risk_score += trend.velocity * 20
                recommendations.append(f"Monitor {metric} - significant decline detected")

            elif trend.direction == TrendDirection.VOLATILE:
                factors.append({
                    "type": "volatile_metric",
                    "metric": metric,
                    "velocity": trend.velocity,
                    "severity": "medium",
                })
                risk_score += trend.velocity * 10
                recommendations.append(f"Investigate {metric} volatility")

        # Check predictive risks
        for metric in self.historical_data:
            pred = self.predict_value(metric, hours_ahead=2)
            if pred:
                value, confidence = pred
                if confidence >= 0.8:
                    recent = self.historical_data[metric][-1][1] if self.historical_data[metric] else value
                    if value > recent * 2:
                        factors.append({
                            "type": "predicted_spike",
                            "metric": metric,
                            "predicted": value,
                            "recent": recent,
                            "confidence": confidence,
                            "severity": "high",
                        })
                        risk_score += confidence * 25
                        recommendations.append(f"Prepare for {metric} spike: {value:.1f}")

        # Determine risk level
        if risk_score >= 75:
            level = RiskLevel.CRITICAL
        elif risk_score >= 50:
            level = RiskLevel.HIGH
        elif risk_score >= 25:
            level = RiskLevel.MEDIUM
        else:
            level = RiskLevel.LOW

        return RiskAssessment(
            level=level,
            score=min(risk_score, 100),
            factors=factors,
            recommendations=recommendations,
            expires_at=datetime.now() + timedelta(minutes=30),
        )

    def recommend_actions(
        self,
        context: dict[str, Any],
    ) -> list[RecommendedAction]:
        """
        Recommend actions based on predictions and risks.

        Args:
            context: Current context information

        Returns:
            List of recommended actions sorted by priority
        """
        actions = []
        
        # Get risk assessment
        risk = self.identify_risks(context)
        
        # Generate actions from risks
        for i, rec in enumerate(risk.recommendations):
            action = RecommendedAction(
                id=f"risk_action_{i}",
                action=rec,
                reason="Risk mitigation based on trend analysis",
                priority=risk.score / 100.0 * (1.0 - i * 0.1),
                expected_impact=0.8,
                confidence=risk.score / 100.0,
            )
            actions.append(action)

        # Get predictive needs
        needs = self.predict_needs(context)
        for need_name, probability in needs.items():
            if probability >= self.confidence_threshold:
                action = RecommendedAction(
                    id=f"predictive_action_{need_name}",
                    action=f"Prepare for {need_name}",
                    reason=f"Predicted need with {probability:.0%} confidence",
                    priority=probability,
                    expected_impact=probability * 0.7,
                    confidence=probability,
                )
                actions.append(action)

        # Sort by priority
        actions.sort(key=lambda a: a.priority, reverse=True)
        
        return actions[:10]  # Return top 10 actions

    def get_trend(self, metric_name: str) -> Optional[TrendAnalysis]:
        """Get cached trend analysis for a metric."""
        if metric_name not in self.trends:
            self.trends[metric_name] = self._analyze_single_trend(metric_name)
        return self.trends.get(metric_name)

    def clear_trends(self) -> None:
        """Clear cached trend analyses."""
        self.trends.clear()

    def get_statistics(self) -> dict[str, Any]:
        """Get predictive analytics statistics."""
        return {
            "tracked_metrics": len(self.historical_data),
            "active_trends": len(self.trends),
            "total_data_points": sum(len(v) for v in self.historical_data.values()),
            "metrics": {
                name: len(data) for name, data in self.historical_data.items()
            },
        }

    def export_data(self) -> str:
        """Export historical data as JSON."""
        data = {
            metric: [
                {"timestamp": ts.isoformat(), "value": val}
                for ts, val in points
            ]
            for metric, points in self.historical_data.items()
        }
        return json.dumps(data, indent=2)

    def import_data(self, json_data: str) -> int:
        """Import historical data from JSON."""
        data = json.loads(json_data)
        imported = 0

        for metric, points in data.items():
            self.historical_data[metric] = []
            for point in points:
                ts = datetime.fromisoformat(point["timestamp"])
                val = point["value"]
                self.historical_data[metric].append((ts, val))
                imported += 1

        return imported
