"""
Learning Engine Module

Experience-based optimization system that learns from
past experiences and improves over time.
"""

from typing import Any, Callable, Dict, List, Optional
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import json
import hashlib
from collections import deque


class ExperienceType(Enum):
    """Types of experiences."""
    SUCCESS = "success"
    FAILURE = "failure"
    EXPLORATION = "exploration"
    OPTIMIZATION = "optimization"
    ADAPTATION = "adaptation"


class LearningStrategy(Enum):
    """Learning strategies."""
    SUPERVISED = "supervised"
    REINFORCEMENT = "reinforcement"
    UNSUPERVISED = "unsupervised"
    META_LEARNING = "meta_learning"


@dataclass
class Experience:
    """A single experience record."""
    id: str
    experience_type: ExperienceType
    context: Dict[str, Any]
    action: str
    outcome: Any
    reward: float  # -1 to 1
    timestamp: datetime = field(default_factory=datetime.now)
    duration_ms: int = 0
    metadata: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        if not self.id:
            content = f"{self.action}:{self.timestamp.isoformat()}"
            self.id = hashlib.sha256(content.encode()).hexdigest()[:16]


@dataclass
class LearnedPattern:
    """A pattern learned from experiences."""
    id: str
    pattern_type: str
    description: str
    evidence: List[str]
    confidence: float
    applicability: Dict[str, Any]
    created_at: datetime = field(default_factory=datetime.now)
    validated_count: int = 0


@dataclass
class Optimization:
    """An optimization derived from learning."""
    id: str
    name: str
    description: str
    target: str  # What to optimize
    expected_improvement: float
    implementation: str
    status: str = "proposed"  # proposed, approved, implemented
    tested_at: Optional[datetime] = None
    results: Dict[str, Any] = field(default_factory=dict)


class LearningEngine:
    """
    Learning engine for experience-based optimization.

    Provides:
    - Experience recording and storage
    - Pattern extraction from experiences
    - Optimization generation
    - Learning strategy adaptation
    """

    def __init__(
        self,
        max_experiences: int = 10000,
        pattern_threshold: float = 0.7,
        learning_rate: float = 0.1,
    ):
        """
        Initialize learning engine.

        Args:
            max_experiences: Maximum experiences to store
            pattern_threshold: Confidence threshold for patterns
            learning_rate: Rate of learning from experiences
        """
        self.max_experiences = max_experiences
        self.pattern_threshold = pattern_threshold
        self.learning_rate = learning_rate

        # Experience storage
        self.experiences: deque = deque(maxlen=max_experiences)
        
        # Learned patterns
        self.patterns: Dict[str, LearnedPattern] = {}
        
        # Optimizations
        self.optimizations: Dict[str, Optimization] = {}
        
        # Statistics
        self.total_rewards: float = 0.0
        self.experience_count: int = 0
        
        # Callbacks
        self._pattern_callbacks: List[Callable[[LearnedPattern], None]] = []
        self._optimization_callbacks: List[Callable[[Optimization], None]] = []

    def record_experience(
        self,
        experience_type: ExperienceType,
        context: Dict[str, Any],
        action: str,
        outcome: Any,
        reward: float,
        duration_ms: int = 0,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Experience:
        """
        Record a new experience.

        Args:
            type: Type of experience
            context: Context of the experience
            action: Action that was taken
            outcome: Outcome of the action
            reward: Reward value (-1 to 1)
            duration_ms: Duration of the action
            metadata: Additional metadata

        Returns:
            The recorded experience
        """
        experience = Experience(
            id="",
            experience_type=experience_type,
            context=context,
            action=action,
            outcome=outcome,
            reward=reward,
            duration_ms=duration_ms,
            metadata=metadata or {},
        )

        self.experiences.append(experience)
        self.experience_count += 1
        self.total_rewards += reward

        # Extract patterns if enough experiences
        if len(self.experiences) >= 10:
            self._extract_patterns()

        return experience

    def get_recent_experiences(
        self,
        experience_type: Optional[ExperienceType] = None,
        limit: int = 10,
    ) -> List[Experience]:
        """Get recent experiences."""
        experiences = list(self.experiences)
        
        if experience_type:
            experiences = [
                e for e in experiences
                if e.experience_type == experience_type
            ]
        
        return experiences[-limit:]

    def get_experiences_by_context(
        self,
        context_filter: Dict[str, Any],
        limit: int = 10,
    ) -> List[Experience]:
        """Get experiences matching context filter."""
        results = []
        
        for exp in reversed(self.experiences):
            match = True
            for key, value in context_filter.items():
                if exp.context.get(key) != value:
                    match = False
                    break
            
            if match:
                results.append(exp)
            
            if len(results) >= limit:
                break
        
        return results

    # Pattern Learning

    def _extract_patterns(self) -> None:
        """Extract patterns from recent experiences."""
        experiences = list(self.experiences)
        
        # Group by action
        action_experiences: Dict[str, List[Experience]] = {}
        for exp in experiences[-100:]:  # Use recent experiences
            if exp.action not in action_experiences:
                action_experiences[exp.action] = []
            action_experiences[exp.action].append(exp)

        # Analyze each action
        for action, exps in action_experiences.items():
            if len(exps) < 3:
                continue

            # Calculate average reward
            avg_reward = sum(e.reward for e in exps) / len(exps)
            
            # Check if pattern is significant
            if avg_reward >= self.pattern_threshold:
                # Create positive pattern
                pattern = LearnedPattern(
                    id=f"pattern_{action}_{len(self.patterns)}",
                    pattern_type="positive_action",
                    description=f"Action '{action}' consistently produces positive outcomes (avg reward: {avg_reward:.2f})",
                    evidence=[f"Experience {e.id[:8]}: reward={e.reward:.2f}" for e in exps[-3:]],
                    confidence=min(avg_reward, 1.0),
                    applicability={"action": action, "contexts": list(set(e.context.get("type", "unknown") for e in exps))},
                )
                self.patterns[pattern.id] = pattern
                
                # Trigger callbacks
                for callback in self._pattern_callbacks:
                    try:
                        callback(pattern)
                    except Exception:
                        pass

            elif avg_reward <= -self.pattern_threshold:
                # Create negative pattern (warning)
                pattern = LearnedPattern(
                    id=f"pattern_{action}_{len(self.patterns)}",
                    pattern_type="negative_action",
                    description=f"Action '{action}' consistently produces negative outcomes (avg reward: {avg_reward:.2f})",
                    evidence=[f"Experience {e.id[:8]}: reward={e.reward:.2f}" for e in exps[-3:]],
                    confidence=min(abs(avg_reward), 1.0),
                    applicability={"action": action, "contexts": list(set(e.context.get("type", "unknown") for e in exps))},
                )
                self.patterns[pattern.id] = pattern

    def get_patterns(
        self,
        pattern_type: Optional[str] = None,
        min_confidence: float = 0.0,
    ) -> List[LearnedPattern]:
        """Get learned patterns."""
        patterns = list(self.patterns.values())
        
        if pattern_type:
            patterns = [p for p in patterns if p.pattern_type == pattern_type]
        
        if min_confidence > 0:
            patterns = [p for p in patterns if p.confidence >= min_confidence]
        
        return sorted(patterns, key=lambda p: p.confidence, reverse=True)

    def validate_pattern(self, pattern_id: str) -> bool:
        """Validate a pattern against recent experiences."""
        pattern = self.patterns.get(pattern_id)
        if not pattern:
            return False

        # Find relevant experiences
        applicability = pattern.applicability.get("action")
        if not applicability:
            return False

        recent = [
            e for e in self.experiences
            if e.action == applicability
        ][-10:]

        if not recent:
            return False

        # Check if pattern still holds
        avg_reward = sum(e.reward for e in recent) / len(recent)
        
        if pattern.pattern_type == "positive_action":
            valid = avg_reward >= self.pattern_threshold * 0.8
        else:
            valid = avg_reward <= -self.pattern_threshold * 0.8

        if valid:
            pattern.validated_count += 1

        return valid

    # Optimization Generation

    def generate_optimization(
        self,
        target: str,
        description: str,
        expected_improvement: float,
        implementation: str,
    ) -> Optimization:
        """
        Generate an optimization proposal.

        Args:
            target: What to optimize
            description: Description of the optimization
            expected_improvement: Expected improvement percentage
            implementation: How to implement

        Returns:
            The generated optimization
        """
        optimization = Optimization(
            id=f"opt_{len(self.optimizations)}_{target}",
            name=f"Optimize {target}",
            description=description,
            target=target,
            expected_improvement=expected_improvement,
            implementation=implementation,
        )

        self.optimizations[optimization.id] = optimization

        # Trigger callbacks
        for callback in self._optimization_callbacks:
            try:
                callback(optimization)
            except Exception:
                pass

        return optimization

    def get_optimizations(
        self,
        status: Optional[str] = None,
    ) -> List[Optimization]:
        """Get optimizations, optionally filtered by status."""
        optimizations = list(self.optimizations.values())
        
        if status:
            optimizations = [o for o in optimizations if o.status == status]
        
        return sorted(
            optimizations,
            key=lambda o: o.expected_improvement,
            reverse=True,
        )

    def approve_optimization(self, optimization_id: str) -> bool:
        """Approve an optimization."""
        optimization = self.optimizations.get(optimization_id)
        if not optimization:
            return False

        optimization.status = "approved"
        return True

    def implement_optimization(
        self,
        optimization_id: str,
        results: Optional[Dict[str, Any]] = None,
    ) -> bool:
        """Mark an optimization as implemented."""
        optimization = self.optimizations.get(optimization_id)
        if not optimization:
            return False

        optimization.status = "implemented"
        optimization.tested_at = datetime.now()
        optimization.results = results or {}

        # Record experience from the optimization
        self.record_experience(
            experience_type=ExperienceType.OPTIMIZATION,
            context={"target": optimization.target},
            action=f"implement_{optimization_id}",
            outcome="completed",
            reward=optimization.expected_improvement if results else 0.0,
            metadata=results,
        )

        return True

    # Strategy Learning

    def get_best_action(
        self,
        context: Dict[str, Any],
        available_actions: List[str],
    ) -> Optional[str]:
        """
        Get the best action for a given context based on learning.

        Args:
            context: Current context
            available_actions: List of available actions

        Returns:
            Best action or None
        """
        if not available_actions:
            return None

        # Score each action based on past experiences
        action_scores: Dict[str, float] = {}
        
        for action in available_actions:
            experiences = [
                e for e in self.experiences
                if e.action == action
            ][-20:]  # Recent experiences

            if not experiences:
                # No history - explore
                action_scores[action] = 0.0
            else:
                # Calculate score based on rewards and recency
                total_score = 0.0
                for i, exp in enumerate(reversed(experiences)):
                    recency = 1.0 / (i + 1)  # More recent = higher weight
                    total_score += exp.reward * recency
                
                action_scores[action] = total_score / len(experiences)

        # Return best action
        best_action = max(action_scores.items(), key=lambda x: x[1])
        return best_action[0] if best_action[1] >= -0.5 else None

    def get_recommended_strategy(
        self,
        context: Dict[str, Any],
    ) -> LearningStrategy:
        """
        Recommend a learning strategy based on context.

        Args:
            context: Current context

        Returns:
            Recommended strategy
        """
        # Analyze experience count
        if self.experience_count < 10:
            return LearningStrategy.EXPLORATION
        
        # Analyze success rate
        recent = list(self.experiences)[-50:]
        if not recent:
            return LearningStrategy.EXPLORATION

        success_rate = sum(1 for e in recent if e.reward > 0) / len(recent)
        
        if success_rate > 0.8:
            # Exploit known good strategies
            return LearningStrategy.REINFORCEMENT
        elif success_rate > 0.5:
            # Balanced approach
            return LearningStrategy.META_LEARNING
        else:
            # Need more exploration
            return LearningStrategy.EXPLORATION

    # Statistics and Analytics

    def get_statistics(self) -> Dict[str, Any]:
        """Get learning engine statistics."""
        experiences = list(self.experiences)
        
        if not experiences:
            return {
                "total_experiences": 0,
                "average_reward": 0.0,
            }

        # Calculate statistics by type
        by_type = {}
        for et in ExperienceType:
            type_exps = [e for e in experiences if e.experience_type == et]
            if type_exps:
                by_type[et.value] = {
                    "count": len(type_exps),
                    "avg_reward": sum(e.reward for e in type_exps) / len(type_exps),
                }

        return {
            "total_experiences": len(experiences),
            "average_reward": self.total_rewards / len(experiences),
            "by_type": by_type,
            "patterns_learned": len(self.patterns),
            "optimizations_proposed": len(self.optimizations),
            "optimizations_implemented": sum(
                1 for o in self.optimizations.values()
                if o.status == "implemented"
            ),
        }

    def get_action_analysis(self, action: str) -> Dict[str, Any]:
        """Get detailed analysis of an action."""
        experiences = [
            e for e in self.experiences
            if e.action == action
        ]

        if not experiences:
            return {"action": action, "experiences": 0}

        rewards = [e.reward for e in experiences]
        
        return {
            "action": action,
            "experiences": len(experiences),
            "average_reward": sum(rewards) / len(rewards),
            "min_reward": min(rewards),
            "max_reward": max(rewards),
            "success_rate": sum(1 for r in rewards if r > 0) / len(rewards),
        }

    def export_data(self) -> str:
        """Export learning data as JSON."""
        data = {
            "statistics": self.get_statistics(),
            "patterns": {
                pid: {
                    "type": p.pattern_type,
                    "description": p.description,
                    "confidence": p.confidence,
                    "validated": p.validated_count,
                }
                for pid, p in self.patterns.items()
            },
            "optimizations": {
                oid: {
                    "target": o.target,
                    "description": o.description,
                    "expected_improvement": o.expected_improvement,
                    "status": o.status,
                }
                for oid, o in self.optimizations.items()
            },
        }
        return json.dumps(data, indent=2)

    def import_data(self, json_data: str) -> bool:
        """Import learning data from JSON."""
        try:
            data = json.loads(json_data)
            
            # Import patterns
            for pid, pdata in data.get("patterns", {}).items():
                self.patterns[pid] = LearnedPattern(
                    id=pid,
                    pattern_type=pdata.get("type", ""),
                    description=pdata.get("description", ""),
                    evidence=[],
                    confidence=pdata.get("confidence", 0.0),
                    applicability={},
                )
            
            return True
        except Exception:
            return False
