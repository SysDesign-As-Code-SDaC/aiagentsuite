"""
Adaptive Decision Engine Module

AI-assisted dynamic decision making that learns from
outcomes and improves decision quality over time.
"""

from typing import Any, Callable, Optional
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import json
import hashlib


class DecisionStrategy(Enum):
    """Strategies for making decisions."""
    EXPLORE = "explore"  # Try new approaches
    EXPLOIT = "exploit"  # Use proven approaches
    BALANCED = "balanced"  # Mix of exploration and exploitation
    CONSERVATIVE = "conservative"  # Minimize risk
    AGGRESSIVE = "maximize"  # Maximize reward


class DecisionOutcome(Enum):
    """Possible outcomes of a decision."""
    SUCCESS = "success"
    PARTIAL_SUCCESS = "partial_success"
    FAILURE = "failure"
    UNKNOWN = "unknown"


@dataclass
class DecisionOption:
    """A single option in a decision."""
    id: str
    name: str
    description: str
    pros: list[str] = field(default_factory=list)
    cons: list[str] = field(default_factory=list)
    estimated_value: float = 0.0
    estimated_risk: float = 0.0
    metadata: dict[str, Any] = field(default_factory=dict)

    def score(self, strategy: DecisionStrategy) -> float:
        """Calculate score based on strategy."""
        if strategy == DecisionStrategy.CONSERVATIVE:
            # Minimize risk
            return self.estimated_value * (1 - self.estimated_risk)
        elif strategy == DecisionStrategy.AGGRESSIVE:
            # Maximize value regardless of risk
            return self.estimated_value * (1 + self.estimated_risk)
        elif strategy == DecisionStrategy.EXPLORE:
            # Prefer less tried options
            tried_count = self.metadata.get("tried_count", 0)
            exploration_bonus = 1.0 / (tried_count + 1)
            return self.estimated_value * (1 - self.estimated_risk) + exploration_bonus
        elif strategy == DecisionStrategy.EXPLOIT:
            # Prefer proven options
            success_rate = self.metadata.get("success_rate", 0.5)
            return self.estimated_value * success_rate
        else:  # BALANCED
            return self.estimated_value * (1 - self.estimated_risk * 0.5)


@dataclass
class Decision:
    """A decision that was made."""
    id: str
    context: dict[str, Any]
    options: list[DecisionOption]
    selected_option_id: str
    strategy: DecisionStrategy
    timestamp: datetime = field(default_factory=datetime.now)
    reasoning: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        if not self.id:
            content = f"{self.selected_option_id}:{self.timestamp.isoformat()}"
            self.id = hashlib.sha256(content.encode()).hexdigest()[:16]


@dataclass
class DecisionOutcomeRecord:
    """Record of a decision's outcome."""
    decision_id: str
    outcome: DecisionOutcome
    actual_value: float
    actual_risk: float
    feedback: str = ""
    timestamp: datetime = field(default_factory=datetime.now)
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class ContextAnalysis:
    """Analysis of current context for decision making."""
    summary: str
    key_factors: list[str]
    constraints: list[str]
    opportunities: list[str]
    confidence: float
    recommendations: list[str]


class AdaptiveDecisionEngine:
    """
    Adaptive decision engine that uses AI to assist with decisions
    and learns from outcomes to improve future decisions.

    Provides:
    - Context-aware decision analysis
    - Multi-criteria option evaluation
    - Learning from decision outcomes
    - Strategy adaptation
    """

    def __init__(
        self,
        default_strategy: DecisionStrategy = DecisionStrategy.BALANCED,
        exploration_rate: float = 0.2,
        learning_rate: float = 0.1,
    ):
        """
        Initialize adaptive decision engine.

        Args:
            default_strategy: Default strategy for making decisions
            exploration_rate: Probability of exploring new options
            learning_rate: Rate at which the system learns from outcomes
        """
        self.default_strategy = default_strategy
        self.exploration_rate = exploration_rate
        self.learning_rate = learning_rate
        
        self.decisions: list[Decision] = []
        self.outcomes: dict[str, DecisionOutcomeRecord] = {}
        self.option_performance: dict[str, dict[str, Any]] = {}
        self.strategy_performance: dict[DecisionStrategy, dict[str, float]] = {
            ds: {"success": 0, "total": 0} for ds in DecisionStrategy
        }

    def analyze_context(
        self,
        context: dict[str, Any],
    ) -> ContextAnalysis:
        """
        Analyze current context for decision making.

        Args:
            context: Current context information

        Returns:
            Context analysis with key factors and recommendations
        """
        key_factors = []
        constraints = []
        opportunities = []
        recommendations = []

        # Extract key factors from context
        if "task" in context:
            key_factors.append(f"Task: {context['task']}")
        if "resources" in context:
            resources = context["resources"]
            key_factors.append(f"Available resources: {len(resources) if isinstance(resources, list) else 'unknown'}")
        if "deadline" in context:
            key_factors.append(f"Deadline: {context['deadline']}")

        # Identify constraints
        if context.get("budget"):
            constraints.append(f"Budget limit: {context['budget']}")
        if context.get("time_limit"):
            constraints.append(f"Time limit: {context['time_limit']}")
        if context.get("team_size"):
            constraints.append(f"Team size: {context['team_size']}")

        # Identify opportunities
        if context.get("has_ai"):
            opportunities.append("AI assistance available")
        if context.get("has_template"):
            opportunities.append("Templates available")
        if context.get("reuse_possible"):
            opportunities.append("Code reuse possible")

        # Generate recommendations
        if constraints and not opportunities:
            recommendations.append("Consider requesting additional resources")
        if context.get("complexity", 0) > 0.7:
            recommendations.append("High complexity - consider breaking down the task")
        if context.get("urgency", 0) > 0.8:
            recommendations.append("High urgency - prioritize speed over optimization")

        # Calculate confidence based on context completeness
        expected_keys = ["task", "resources", "deadline"]
        confidence = sum(1 for k in expected_keys if k in context) / len(expected_keys)

        return ContextAnalysis(
            summary=self._generate_context_summary(context),
            key_factors=key_factors,
            constraints=constraints,
            opportunities=opportunities,
            confidence=confidence,
            recommendations=recommendations,
        )

    def _generate_context_summary(self, context: dict[str, Any]) -> str:
        """Generate a human-readable summary of the context."""
        parts = []
        if "task" in context:
            parts.append(f"Working on: {context['task']}")
        if "goal" in context:
            parts.append(f"Goal: {context['goal']}")
        return " | ".join(parts) if parts else "General context"

    def evaluate_options(
        self,
        options: list[DecisionOption],
        context: dict[str, Any],
        strategy: Optional[DecisionStrategy] = None,
    ) -> list[tuple[DecisionOption, float]]:
        """
        Evaluate and score decision options.

        Args:
            options: List of options to evaluate
            context: Current context
            strategy: Optional strategy override

        Returns:
            List of (option, score) tuples sorted by score
        """
        if strategy is None:
            strategy = self._select_strategy(context)

        # Score each option
        scored_options = []
        for option in options:
            # Adjust based on historical performance
            adjustment = self._get_option_adjustment(option.id)
            base_score = option.score(strategy)
            adjusted_score = base_score * (1 + adjustment)
            scored_options.append((option, adjusted_score))

        # Sort by score
        scored_options.sort(key=lambda x: x[1], reverse=True)
        return scored_options

    def make_decision(
        self,
        options: list[DecisionOption],
        context: dict[str, Any],
        strategy: Optional[DecisionStrategy] = None,
        reasoning: str = "",
    ) -> Decision:
        """
        Make a decision from available options.

        Args:
            options: List of decision options
            context: Current context
            strategy: Optional strategy override
            reasoning: Explanation of the decision

        Returns:
            The made decision
        """
        if not options:
            raise ValueError("Cannot make decision with no options")

        if strategy is None:
            strategy = self._select_strategy(context)

        # Evaluate options
        scored = self.evaluate_options(options, context, strategy)

        # Sometimes explore (try new options) instead of exploiting best
        if strategy == DecisionStrategy.EXPLORE or (
            strategy == DecisionStrategy.BALANCED and 
            np_random() < self.exploration_rate
        ):
            # Pick a random non-worst option
            selected = scored[np_random(len(scored)) if len(scored) > 1 else 0][0]
        else:
            # Pick the best option
            selected = scored[0][0]

        # Create decision record
        decision = Decision(
            id="",
            context=context,
            options=options,
            selected_option_id=selected.id,
            strategy=strategy,
            reasoning=reasoning or f"Selected '{selected.name}' using {strategy.value} strategy",
        )

        # Track decision
        self.decisions.append(decision)
        
        # Update strategy performance tracking
        self.strategy_performance[strategy]["total"] += 1

        return decision

    def record_outcome(
        self,
        decision: Decision,
        outcome: DecisionOutcome,
        actual_value: float,
        actual_risk: float,
        feedback: str = "",
    ) -> None:
        """
        Record the outcome of a decision for learning.

        Args:
            decision: The decision that was made
            outcome: The outcome of the decision
            actual_value: Actual value delivered
            actual_risk: Actual risk realized
            feedback: Additional feedback
        """
        # Create outcome record
        outcome_record = DecisionOutcomeRecord(
            decision_id=decision.id,
            outcome=outcome,
            actual_value=actual_value,
            actual_risk=actual_risk,
            feedback=feedback,
        )

        # Store outcome
        self.outcomes[decision.id] = outcome_record

        # Update option performance
        option_id = decision.selected_option_id
        if option_id not in self.option_performance:
            self.option_performance[option_id] = {
                "successes": 0,
                "failures": 0,
                "total_value": 0.0,
                "total_risk": 0.0,
                "count": 0,
            }

        perf = self.option_performance[option_id]
        perf["count"] += 1
        perf["total_value"] += actual_value
        perf["total_risk"] += actual_risk

        if outcome == DecisionOutcome.SUCCESS:
            perf["successes"] += 1
            self.strategy_performance[decision.strategy]["success"] += 1
        elif outcome == DecisionOutcome.FAILURE:
            perf["failures"] += 1

    def _select_strategy(self, context: dict[str, Any]) -> DecisionStrategy:
        """Select the best strategy based on context and history."""
        # Check if there's a clear winner strategy
        best_strategy = self.default_strategy
        best_success_rate = 0.0

        for strategy, perf in self.strategy_performance.items():
            if perf["total"] > 0:
                success_rate = perf["success"] / perf["total"]
                if success_rate > best_success_rate:
                    best_success_rate = success_rate
                    best_strategy = strategy

        # Adjust based on context
        if context.get("high_stakes"):
            # Be more conservative for high-stakes decisions
            return DecisionStrategy.CONSERVATIVE
        elif context.get("need_experimentation"):
            return DecisionStrategy.EXPLORE
        elif context.get("speed_important") and context.get("urgency", 0) > 0.7:
            return DecisionStrategy.AGGRESSIVE

        return best_strategy

    def _get_option_adjustment(self, option_id: str) -> float:
        """Get performance adjustment for an option based on history."""
        if option_id not in self.option_performance:
            return 0.0

        perf = self.option_performance[option_id]
        if perf["count"] == 0:
            return 0.0

        success_rate = perf["successes"] / perf["count"]
        avg_value = perf["total_value"] / perf["count"]
        avg_risk = perf["total_risk"] / perf["count"]

        # Adjustment based on historical performance
        # Positive for good performance, negative for poor
        adjustment = (success_rate - 0.5) * self.learning_rate
        adjustment += (avg_value - 0.5) * self.learning_rate * 0.5
        adjustment -= avg_risk * self.learning_rate * 0.3

        return max(-0.5, min(0.5, adjustment))  # Clamp to [-0.5, 0.5]

    def get_recommended_options(
        self,
        context: dict[str, Any],
        count: int = 3,
    ) -> list[DecisionOption]:
        """
        Get recommended options based on historical performance.

        Args:
            context: Current context
            count: Number of options to return

        Returns:
            List of recommended options
        """
        # Get best performing options
        options_by_perf = [
            (oid, perf)
            for oid, perf in self.option_performance.items()
            if perf["count"] >= 2
        ]

        if not options_by_perf:
            return []

        # Sort by success rate
        options_by_perf.sort(
            key=lambda x: x[1]["successes"] / x[1]["count"] if x[1]["count"] > 0 else 0,
            reverse=True,
        )

        return [oid for oid, _ in options_by_perf[:count]]

    def get_decision_history(
        self,
        limit: int = 10,
    ) -> list[Decision]:
        """Get recent decision history."""
        return self.decisions[-limit:]

    def get_statistics(self) -> dict[str, Any]:
        """Get decision engine statistics."""
        total_decisions = len(self.decisions)
        total_outcomes = len(self.outcomes)

        success_count = sum(
            1 for o in self.outcomes.values()
            if o.outcome == DecisionOutcome.SUCCESS
        )

        return {
            "total_decisions": total_decisions,
            "total_outcomes": total_outcomes,
            "success_rate": success_count / total_outcomes if total_outcomes > 0 else 0,
            "tracked_options": len(self.option_performance),
            "strategy_performance": {
                str(k): {
                    "successes": v["success"],
                    "total": v["total"],
                    "rate": v["success"] / v["total"] if v["total"] > 0 else 0,
                }
                for k, v in self.strategy_performance.items()
            },
        }

    def export_data(self) -> str:
        """Export decision history as JSON."""
        data = {
            "decisions": [
                {
                    "id": d.id,
                    "context": d.context,
                    "selected_option": d.selected_option_id,
                    "strategy": d.strategy.value,
                    "timestamp": d.timestamp.isoformat(),
                    "reasoning": d.reasoning,
                }
                for d in self.decisions
            ],
            "outcomes": {
                oid: {
                    "decision_id": o.decision_id,
                    "outcome": o.outcome.value,
                    "actual_value": o.actual_value,
                    "actual_risk": o.actual_risk,
                    "feedback": o.feedback,
                    "timestamp": o.timestamp.isoformat(),
                }
                for oid, o in self.outcomes.items()
            },
        }
        return json.dumps(data, indent=2)


def np_random(max_val: Optional[int] = None) -> float:
    """Simple random number generator (placeholder for numpy)."""
    import random
    if max_val is None:
        return random.random()
    return random.randint(0, max_val - 1)
