"""
Feedback Loop System Module

Continuous improvement system that learns from outcomes
and feeds learnings back into the system for optimization.
"""

from typing import Any, Callable, Optional
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import json


class FeedbackType(Enum):
    """Types of feedback that can be collected."""
    SUCCESS = "success"
    FAILURE = "failure"
    PERFORMANCE = "performance"
    USER_SATISFACTION = "user_satisfaction"
    EFFICIENCY = "efficiency"
    QUALITY = "quality"


class ImprovementCategory(Enum):
    """Categories for improvements."""
    SPEED = "speed"
    ACCURACY = "accuracy"
    RESOURCE_USAGE = "resource_usage"
    USER_EXPERIENCE = "user_experience"
    RELIABILITY = "reliability"
    SECURITY = "security"


@dataclass
class Feedback:
    """A piece of feedback about system behavior."""
    id: str
    feedback_type: FeedbackType
    source: str  # What generated this feedback
    context: dict[str, Any]
    rating: float  # -1 to 1 (negative to positive)
    description: str
    timestamp: datetime = field(default_factory=datetime.now)
    tags: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class Learning:
    """A learned insight from feedback analysis."""
    id: str
    category: ImprovementCategory
    insight: str
    evidence: list[str]  # Supporting evidence
    confidence: float  # How confident we are in this learning
    impact: float  # Estimated impact if applied
    actionable: bool
    recommendations: list[str]
    created_at: datetime = field(default_factory=datetime.now)
    last_validated: datetime = field(default_factory=datetime.now)
    validation_count: int = 0


@dataclass
class Improvement:
    """A proposed improvement based on learnings."""
    id: str
    title: str
    description: str
    category: ImprovementCategory
    expected_impact: float
    implementation_effort: float  # 0-1 (easy to hard)
    risks: list[str]
    prerequisites: list[str]
    success_metrics: list[str]
    status: str = "proposed"  # proposed, approved, implemented, rejected
    implemented_at: Optional[datetime] = None


class FeedbackLoopSystem:
    """
    Feedback loop system for continuous improvement.

    Provides:
    - Feedback collection and analysis
    - Pattern detection in feedback
    - Learning extraction
    - Improvement generation
    - Feedback-driven optimization
    """

    def __init__(
        self,
        feedback_window: int = 1000,  # Number of feedback items to keep
        learning_threshold: float = 0.7,  # Confidence threshold for learnings
        improvement_threshold: float = 0.5,  # Impact threshold for improvements
    ):
        """
        Initialize feedback loop system.

        Args:
            feedback_window: Maximum feedback items to retain
            learning_threshold: Minimum confidence for learnings
            improvement_threshold: Minimum impact for improvements
        """
        self.feedback_window = feedback_window
        self.learning_threshold = learning_threshold
        self.improvement_threshold = improvement_threshold

        self.feedback: list[Feedback] = []
        self.learnings: dict[str, Learning] = {}
        self.improvements: dict[str, Improvement] = {}
        self.feedback_by_type: dict[FeedbackType, list[str]] = {
            ft: [] for ft in FeedbackType
        }

        # Callbacks for external integration
        self._optimization_callbacks: list[Callable] = []

    def add_feedback(
        self,
        feedback_type: FeedbackType,
        source: str,
        context: dict[str, Any],
        rating: float,
        description: str,
        tags: Optional[list[str]] = None,
    ) -> Feedback:
        """
        Add new feedback to the system.

        Args:
            feedback_type: Type of feedback
            source: Source of feedback
            context: Context information
            rating: Rating from -1 to 1
            description: Description of feedback
            tags: Optional tags

        Returns:
            The created feedback object
        """
        # Generate ID
        feedback_id = f"fb_{len(self.feedback)}_{datetime.now().timestamp()}"

        feedback = Feedback(
            id=feedback_id,
            feedback_type=feedback_type,
            source=source,
            context=context,
            rating=max(-1.0, min(1.0, rating)),  # Clamp to [-1, 1]
            description=description,
            tags=tags or [],
        )

        # Add to collection
        self.feedback.append(feedback)
        self.feedback_by_type[feedback_type].append(feedback_id)

        # Trim if over window
        if len(self.feedback) > self.feedback_window:
            self._trim_feedback()

        # Check if this triggers new learning
        self._analyze_feedback(feedback)

        return feedback

    def _trim_feedback(self) -> None:
        """Trim old feedback to maintain window size."""
        # Remove oldest feedback
        to_remove = len(self.feedback) - self.feedback_window
        removed = self.feedback[:to_remove]

        self.feedback = self.feedback[to_remove:]

        # Update type index
        for fb in removed:
            if fb.id in self.feedback_by_type[fb.feedback_type]:
                self.feedback_by_type[fb.feedback_type].remove(fb.id)

    def _analyze_feedback(self, feedback: Feedback) -> None:
        """Analyze new feedback for potential learnings."""
        # Find similar recent feedback
        similar = self._find_similar_feedback(feedback)

        if len(similar) >= 3:
            # Check if pattern is consistent
            ratings = [fb.rating for fb in similar + [feedback]]
            avg_rating = sum(ratings) / len(ratings)

            # If consistent negative or positive feedback
            if abs(avg_rating) >= 0.5:
                self._extract_learning(feedback, similar, avg_rating)

    def _find_similar_feedback(
        self,
        feedback: Feedback,
        limit: int = 10,
    ) -> list[Feedback]:
        """Find similar feedback based on context and type."""
        similar = []

        for fb in self.feedback[-50:]:  # Check recent feedback
            if fb.id == feedback.id:
                continue
            if fb.feedback_type != feedback.feedback_type:
                continue

            # Check context similarity
            similarity = self._calculate_context_similarity(
                feedback.context, fb.context
            )
            if similarity >= 0.5:
                similar.append(fb)

        return similar[:limit]

    def _calculate_context_similarity(
        self,
        ctx1: dict[str, Any],
        ctx2: dict[str, Any],
    ) -> float:
        """Calculate similarity between two contexts."""
        if not ctx1 or not ctx2:
            return 0.0

        keys1 = set(ctx1.keys())
        keys2 = set(ctx2.keys())

        if not keys1 or not keys2:
            return 0.0

        intersection = len(keys1 & keys2)
        union = len(keys1 | keys2)

        return intersection / union if union > 0 else 0.0

    def _extract_learning(
        self,
        feedback: Feedback,
        similar: list[Feedback],
        avg_rating: float,
    ) -> Optional[Learning]:
        """Extract a learning from feedback pattern."""
        # Determine category
        category = self._determine_category(feedback, similar)

        # Generate insight
        insight = self._generate_insight(feedback, similar, avg_rating)

        # Check if we already have similar learning
        for existing in self.learnings.values():
            if existing.insight == insight:
                # Update existing learning
                existing.validation_count += 1
                existing.last_validated = datetime.now()
                return None

        # Create new learning
        learning_id = f"learn_{len(self.learnings)}_{datetime.now().timestamp()}"
        
        learning = Learning(
            id=learning_id,
            category=category,
            insight=insight,
            evidence=[fb.description for fb in similar[:5]],
            confidence=min(0.5 + (len(similar) * 0.1), 1.0),
            impact=abs(avg_rating),
            actionable=abs(avg_rating) >= self.learning_threshold,
            recommendations=self._generate_recommendations(feedback, similar, avg_rating),
        )

        self.learnings[learning_id] = learning

        # Check if should create improvement
        if learning.actionable and learning.impact >= self.improvement_threshold:
            self._generate_improvement(learning)

        return learning

    def _determine_category(
        self,
        feedback: Feedback,
        similar: list[Feedback],
    ) -> ImprovementCategory:
        """Determine the improvement category from feedback."""
        # Analyze context for category hints
        context = feedback.context

        if any(k in str(context).lower() for k in ["time", "speed", "fast", "slow"]):
            return ImprovementCategory.SPEED
        elif any(k in str(context).lower() for k in ["error", "bug", "fail"]):
            return ImprovementCategory.RELIABILITY
        elif any(k in str(context).lower() for k in ["memory", "cpu", "resource"]):
            return ImprovementCategory.RESOURCE_USAGE
        elif any(k in str(context).lower() for k in ["user", "ui", "interface"]):
            return ImprovementCategory.USER_EXPERIENCE

        return ImprovementCategory.ACCURACY

    def _generate_insight(
        self,
        feedback: Feedback,
        similar: list[Feedback],
        avg_rating: float,
    ) -> str:
        """Generate an insight from feedback pattern."""
        sentiment = "positive" if avg_rating > 0 else "negative"
        feedback_type = feedback.feedback_type.value

        return (
            f"System shows {sentiment} {feedback_type} feedback "
            f"({len(similar) + 1} instances) - {feedback.description[:100]}"
        )

    def _generate_recommendations(
        self,
        feedback: Feedback,
        similar: list[Feedback],
        avg_rating: float,
    ) -> list[str]:
        """Generate recommendations based on feedback pattern."""
        recommendations = []

        if avg_rating < 0:
            recommendations.append("Investigate root cause of negative feedback")
            recommendations.append("Consider rolling back recent changes")

            # Check for specific issues
            contexts = [fb.context for fb in similar]
            if any("timeout" in str(ctx).lower() for ctx in contexts):
                recommendations.append("Optimize timeout handling")
            if any("memory" in str(ctx).lower() for ctx in contexts):
                recommendations.append("Review memory management")
        else:
            recommendations.append("Document successful patterns")
            recommendations.append("Consider applying similar approach elsewhere")

        return recommendations

    def _generate_improvement(self, learning: Learning) -> None:
        """Generate an improvement proposal from a learning."""
        improvement_id = f"imp_{len(self.improvements)}_{datetime.now().timestamp()}"

        improvement = Improvement(
            id=improvement_id,
            title=f"Improve {learning.category.value} based on feedback",
            description=learning.insight,
            category=learning.category,
            expected_impact=learning.impact,
            implementation_effort=0.5,  # Default estimate
            risks=["Potential unintended consequences"],
            prerequisites=[],
            success_metrics=["Feedback rating improvement", "Reduced error rate"],
        )

        self.improvements[improvement_id] = improvement

        # Trigger optimization callbacks
        for callback in self._optimization_callbacks:
            try:
                callback(improvement)
            except Exception:
                pass  # Ignore callback errors

    def register_optimization_callback(
        self,
        callback: Callable[[Improvement], None],
    ) -> None:
        """Register a callback to be called when improvements are generated."""
        self._optimization_callbacks.append(callback)

    def get_recent_feedback(
        self,
        feedback_type: Optional[FeedbackType] = None,
        limit: int = 10,
    ) -> list[Feedback]:
        """Get recent feedback, optionally filtered by type."""
        if feedback_type:
            ids = self.feedback_by_type.get(feedback_type, [])
            return [fb for fb in self.feedback if fb.id in ids][-limit:]
        return self.feedback[-limit:]

    def get_active_learnings(self) -> list[Learning]:
        """Get learnings that are still valid."""
        cutoff = datetime.now() - timedelta(days=7)
        return [
            l for l in self.learnings.values()
            if l.last_validated >= cutoff
        ]

    def get_pending_improvements(self) -> list[Improvement]:
        """Get improvements that are proposed but not implemented."""
        return [
            imp for imp in self.improvements.values()
            if imp.status == "proposed"
        ]

    def approve_improvement(self, improvement_id: str) -> bool:
        """Approve an improvement for implementation."""
        improvement = self.improvements.get(improvement_id)
        if not improvement:
            return False

        improvement.status = "approved"
        return True

    def implement_improvement(self, improvement_id: str) -> bool:
        """Mark an improvement as implemented."""
        improvement = self.improvements.get(improvement_id)
        if not improvement:
            return False

        improvement.status = "implemented"
        improvement.implemented_at = datetime.now()
        return True

    def get_feedback_statistics(self) -> dict[str, Any]:
        """Get feedback statistics."""
        if not self.feedback:
            return {
                "total_feedback": 0,
                "average_rating": 0.0,
                "by_type": {},
            }

        by_type = {}
        for ft in FeedbackType:
            type_feedback = [
                fb for fb in self.feedback
                if fb.feedback_type == ft
            ]
            if type_feedback:
                by_type[ft.value] = {
                    "count": len(type_feedback),
                    "avg_rating": sum(fb.rating for fb in type_feedback) / len(type_feedback),
                }

        return {
            "total_feedback": len(self.feedback),
            "average_rating": sum(fb.rating for fb in self.feedback) / len(self.feedback),
            "by_type": by_type,
            "total_learnings": len(self.learnings),
            "actionable_learnings": sum(1 for l in self.learnings.values() if l.actionable),
            "pending_improvements": len(self.get_pending_improvements()),
            "implemented_improvements": sum(
                1 for imp in self.improvements.values()
                if imp.status == "implemented"
            ),
        }

    def export_data(self) -> str:
        """Export feedback loop data as JSON."""
        data = {
            "feedback": [
                {
                    "id": fb.id,
                    "type": fb.feedback_type.value,
                    "source": fb.source,
                    "rating": fb.rating,
                    "description": fb.description,
                    "timestamp": fb.timestamp.isoformat(),
                    "tags": fb.tags,
                }
                for fb in self.feedback
            ],
            "learnings": {
                lid: {
                    "category": l.category.value,
                    "insight": l.insight,
                    "confidence": l.confidence,
                    "impact": l.impact,
                    "actionable": l.actionable,
                    "created_at": l.created_at.isoformat(),
                }
                for lid, l in self.learnings.items()
            },
            "improvements": {
                iid: {
                    "title": imp.title,
                    "category": imp.category.value,
                    "status": imp.status,
                    "expected_impact": imp.expected_impact,
                }
                for iid, imp in self.improvements.items()
            },
        }
        return json.dumps(data, indent=2)

    def import_data(self, json_data: str) -> int:
        """Import feedback loop data from JSON."""
        data = json.loads(json_data)
        imported = 0

        # Import feedback
        for fb_data in data.get("feedback", []):
            self.add_feedback(
                feedback_type=FeedbackType(fb_data["type"]),
                source=fb_data["source"],
                context={},
                rating=fb_data["rating"],
                description=fb_data["description"],
                tags=fb_data.get("tags", []),
            )
            imported += 1

        return imported
