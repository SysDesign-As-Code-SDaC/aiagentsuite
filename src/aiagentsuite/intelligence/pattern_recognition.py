"""
Pattern Recognition Module

Advanced pattern detection using ML algorithms for identifying
recurring patterns in code, workflows, and system behavior.
"""

from typing import Any, Callable, Optional
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import json
import hashlib


class PatternType(Enum):
    """Types of patterns that can be detected."""
    CODE_STRUCTURE = "code_structure"
    WORKFLOW = "workflow"
    ERROR = "error"
    PERFORMANCE = "performance"
    SECURITY = "security"
    USER_BEHAVIOR = "user_behavior"
    TEMPORAL = "temporal"


@dataclass
class Pattern:
    """Represents a detected pattern."""
    id: str
    type: PatternType
    confidence: float
    features: dict[str, Any]
    occurrences: int = 1
    first_seen: datetime = field(default_factory=datetime.now)
    last_seen: datetime = field(default_factory=datetime.now)
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        if not self.id:
            self.id = self._generate_id()

    def _generate_id(self) -> str:
        """Generate unique ID from pattern features."""
        content = f"{self.type.value}:{json.dumps(self.features, sort_keys=True)}"
        return hashlib.sha256(content.encode()).hexdigest()[:16]

    def update(self, features: dict[str, Any]) -> None:
        """Update pattern with new occurrence."""
        self.occurrences += 1
        self.last_seen = datetime.now()
        # Merge new features
        for key, value in features.items():
            if key in self.features:
                if isinstance(self.features[key], list):
                    if value not in self.features[key]:
                        self.features[key].append(value)
                elif self.features[key] != value:
                    self.features[key] = [self.features[key], value]
            else:
                self.features[key] = value


@dataclass
class PatternMatch:
    """Result of pattern matching."""
    pattern: Pattern
    similarity: float
    context: dict[str, Any]
    timestamp: datetime = field(default_factory=datetime.now)


class PatternRecognition:
    """
    ML-based pattern recognition system for detecting and learning patterns.

    Provides:
    - Pattern detection in code and workflows
    - Similarity matching against known patterns
    - Pattern clustering and categorization
    - Temporal pattern analysis
    """

    def __init__(
        self,
        min_confidence: float = 0.7,
        max_patterns: int = 1000,
        similarity_threshold: float = 0.8,
    ):
        """
        Initialize pattern recognition system.

        Args:
            min_confidence: Minimum confidence threshold for pattern detection
            max_patterns: Maximum number of patterns to store
            similarity_threshold: Threshold for pattern matching
        """
        self.min_confidence = min_confidence
        self.max_patterns = max_patterns
        self.similarity_threshold = similarity_threshold
        self.patterns: dict[str, Pattern] = {}
        self.pattern_index: dict[PatternType, list[str]] = {
            pt: [] for pt in PatternType
        }
        self._similarity_fn: Optional[Callable] = None

    def set_similarity_function(
        self, fn: Callable[[dict, dict], float]
    ) -> None:
        """Set custom similarity calculation function."""
        self._similarity_fn = fn

    def detect_pattern(
        self,
        data: dict[str, Any],
        pattern_type: PatternType,
    ) -> Optional[Pattern]:
        """
        Detect if data matches an existing pattern or create new one.

        Args:
            data: Data to analyze for patterns
            pattern_type: Type of pattern to look for

        Returns:
            Pattern if detected, None otherwise
        """
        # Check for similar existing patterns
        match = self.find_similar(data, pattern_type)
        if match and match.similarity >= self.similarity_threshold:
            match.pattern.update(data)
            self.patterns[match.pattern.id] = match.pattern
            return match.pattern

        # Check if new pattern meets confidence threshold
        confidence = self._calculate_confidence(data, pattern_type)
        if confidence >= self.min_confidence:
            pattern = Pattern(
                id="",
                type=pattern_type,
                confidence=confidence,
                features=data,
            )
            self._add_pattern(pattern)
            return pattern

        return None

    def find_similar(
        self,
        data: dict[str, Any],
        pattern_type: Optional[PatternType] = None,
        limit: int = 5,
    ) -> Optional[PatternMatch]:
        """
        Find patterns similar to the given data.

        Args:
            data: Data to match against
            pattern_type: Optional filter by pattern type
            limit: Maximum number of matches to return

        Returns:
            Best matching pattern or None
        """
        candidates = []
        types_to_check = (
            [pattern_type] if pattern_type else list(PatternType)
        )

        for pt in types_to_check:
            for pattern_id in self.pattern_index.get(pt, []):
                pattern = self.patterns.get(pattern_id)
                if not pattern:
                    continue

                similarity = self._calculate_similarity(
                    data, pattern.features
                )
                if similarity >= self.min_confidence:
                    candidates.append(
                        PatternMatch(
                            pattern=pattern,
                            similarity=similarity,
                            context=data,
                        )
                    )

        if not candidates:
            return None

        candidates.sort(key=lambda x: x.similarity, reverse=True)
        return candidates[0] if candidates else None

    def get_patterns_by_type(
        self,
        pattern_type: PatternType,
        min_occurrences: int = 1,
    ) -> list[Pattern]:
        """Get all patterns of a specific type."""
        result = []
        for pattern_id in self.pattern_index.get(pattern_type, []):
            pattern = self.patterns.get(pattern_id)
            if pattern and pattern.occurrences >= min_occurrences:
                result.append(pattern)
        return sorted(result, key=lambda p: p.occurrences, reverse=True)

    def get_frequent_patterns(
        self,
        min_occurrences: int = 5,
    ) -> list[Pattern]:
        """Get patterns that occur frequently."""
        return [
            p for p in self.patterns.values()
            if p.occurrences >= min_occurrences
        ]

    def analyze_sequence(
        self,
        sequence: list[dict[str, Any]],
        pattern_type: PatternType,
    ) -> list[Pattern]:
        """
        Analyze a sequence of data for temporal patterns.

        Args:
            sequence: Ordered list of data points
            pattern_type: Type of patterns to find

        Returns:
            List of detected sequential patterns
        """
        detected = []
        for i, data in enumerate(sequence):
            pattern = self.detect_pattern(data, pattern_type)
            if pattern:
                detected.append(pattern)

        # Find sequential dependencies
        sequential_patterns = self._find_sequential_patterns(
            detected, sequence
        )
        return sequential_patterns

    def _find_sequential_patterns(
        self,
        patterns: list[Pattern],
        sequence: list[dict[str, Any]],
    ) -> list[Pattern]:
        """Find patterns that occur in sequence."""
        # Group consecutive similar patterns
        if not patterns:
            return []

        groups: list[list[Pattern]] = []
        current_group = [patterns[0]]

        for i in range(1, len(patterns)):
            if patterns[i].id == patterns[i-1].id:
                current_group.append(patterns[i])
            else:
                if len(current_group) > 1:
                    groups.append(current_group)
                current_group = [patterns[i]]

        if len(current_group) > 1:
            groups.append(current_group)

        # Create sequential patterns
        result = []
        for group in groups:
            if len(group) >= 2:
                seq_pattern = Pattern(
                    id=f"seq_{group[0].id}_{len(group)}",
                    type=group[0].type,
                    confidence=sum(p.confidence for p in group) / len(group),
                    features={"sequence_length": len(group), "pattern_ids": [p.id for p in group]},
                    occurrences=1,
                    metadata={"is_sequential": True},
                )
                result.append(seq_pattern)

        return result

    def _calculate_similarity(
        self,
        data1: dict[str, Any],
        data2: dict[str, Any],
    ) -> float:
        """Calculate similarity between two data dictionaries."""
        if self._similarity_fn:
            return self._similarity_fn(data1, data2)

        # Default: Jaccard similarity on keys
        if not data1 or not data2:
            return 0.0

        keys1 = set(data1.keys())
        keys2 = set(data2.keys())

        if not keys1 or not keys2:
            return 0.0

        intersection = len(keys1 & keys2)
        union = len(keys1 | keys2)

        return intersection / union if union > 0 else 0.0

    def _calculate_confidence(
        self,
        data: dict[str, Any],
        pattern_type: PatternType,
    ) -> float:
        """Calculate confidence score for potential new pattern."""
        # Simple confidence based on feature completeness
        if not data:
            return 0.0

        # More features = higher confidence
        feature_score = min(len(data) / 10.0, 1.0)

        # Check for known pattern types in data
        type_indicators = {
            PatternType.CODE_STRUCTURE: ["file", "class", "function", "import"],
            PatternType.WORKFLOW: ["step", "task", "action", "transition"],
            PatternType.ERROR: ["error", "exception", "traceback"],
            PatternType.PERFORMANCE: ["time", "memory", "cpu", "duration"],
            PatternType.SECURITY: ["auth", "permission", "access", "token"],
            PatternType.USER_BEHAVIOR: ["user", "action", "session"],
            PatternType.TEMPORAL: ["timestamp", "time", "date"],
        }

        indicators = type_indicators.get(pattern_type, [])
        matched = sum(1 for k in data.keys() for i in indicators if i in k.lower())
        type_score = min(matched / 3.0, 1.0)

        return (feature_score * 0.7) + (type_score * 0.3)

    def _add_pattern(self, pattern: Pattern) -> None:
        """Add a new pattern to the system."""
        # Evict oldest pattern if at capacity
        if len(self.patterns) >= self.max_patterns:
            self._evict_pattern()

        self.patterns[pattern.id] = pattern
        self.pattern_index[pattern.type].append(pattern.id)

    def _evict_pattern(self) -> None:
        """Remove least frequent pattern to make room."""
        if not self.patterns:
            return

        # Find least valuable pattern (lowest occurrences * confidence)
        least_valuable = min(
            self.patterns.values(),
            key=lambda p: p.occurrences * p.confidence
        )
        self.remove_pattern(least_valuable.id)

    def remove_pattern(self, pattern_id: str) -> bool:
        """Remove a pattern from the system."""
        pattern = self.patterns.get(pattern_id)
        if not pattern:
            return False

        del self.patterns[pattern_id]
        if pattern_id in self.pattern_index[pattern.type]:
            self.pattern_index[pattern.type].remove(pattern_id)

        return True

    def get_statistics(self) -> dict[str, Any]:
        """Get pattern recognition statistics."""
        return {
            "total_patterns": len(self.patterns),
            "patterns_by_type": {
                pt.value: len(ids) for pt, ids in self.pattern_index.items()
            },
            "total_occurrences": sum(p.occurrences for p in self.patterns.values()),
            "average_confidence": (
                sum(p.confidence for p in self.patterns.values()) / len(self.patterns)
                if self.patterns else 0.0
            ),
        }

    def export_patterns(self) -> str:
        """Export all patterns as JSON."""
        data = {
            pid: {
                "type": p.type.value,
                "confidence": p.confidence,
                "features": p.features,
                "occurrences": p.occurrences,
                "first_seen": p.first_seen.isoformat(),
                "last_seen": p.last_seen.isoformat(),
                "metadata": p.metadata,
            }
            for pid, p in self.patterns.items()
        }
        return json.dumps(data, indent=2)

    def import_patterns(self, json_data: str) -> int:
        """Import patterns from JSON."""
        data = json.loads(json_data)
        imported = 0

        for pid, pdata in data.items():
            pattern = Pattern(
                id=pid,
                type=PatternType(pdata["type"]),
                confidence=pdata["confidence"],
                features=pdata["features"],
                occurrences=pdata.get("occurrences", 1),
                first_seen=datetime.fromisoformat(pdata["first_seen"]),
                last_seen=datetime.fromisoformat(pdata["last_seen"]),
                metadata=pdata.get("metadata", {}),
            )
            self._add_pattern(pattern)
            imported += 1

        return imported
