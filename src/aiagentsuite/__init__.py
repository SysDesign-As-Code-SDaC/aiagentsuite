"""
AI Agent Suite - A comprehensive framework for AI-assisted development

Dynamic Capabilities (2026):
- Pattern Recognition & Predictive Analytics
- Adaptive Decision Making & Feedback Loops
- Real-time Context Processing & Configuration
- Event-driven Architecture & Monitoring
- Self-modifying Protocols & Learning Engine
"""

__version__ = "0.2.0"
__author__ = "AI Agent Suite Team"
__email__ = "team@aiagentsuite.com"

from .core import AIAgentSuite
from .framework import FrameworkManager
from .protocols import ProtocolExecutor
from .memory_bank import MemoryBank

# Dynamic capabilities (2026)
from .intelligence import (
    PatternRecognition,
    PredictiveAnalytics,
    AdaptiveDecisionEngine,
    FeedbackLoopSystem,
)

from .realtime import (
    StreamingContextProcessor,
    LiveConfigurationManager,
    EventBus,
    RealtimeMonitor,
)

from .dynamic import (
    AdaptiveProtocolEngine,
    LearningEngine,
)

__all__ = [
    # Core
    "AIAgentSuite",
    "FrameworkManager",
    "ProtocolExecutor",
    "MemoryBank",
    # Intelligence Layer
    "PatternRecognition",
    "PredictiveAnalytics",
    "AdaptiveDecisionEngine",
    "FeedbackLoopSystem",
    # Realtime Layer
    "StreamingContextProcessor",
    "LiveConfigurationManager",
    "EventBus",
    "RealtimeMonitor",
    # Dynamic Layer
    "AdaptiveProtocolEngine",
    "LearningEngine",
]
