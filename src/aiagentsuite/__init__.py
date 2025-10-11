"""
AI Agent Suite - A comprehensive framework for AI-assisted development
"""

__version__ = "0.1.0"
__author__ = "AI Agent Suite Team"
__email__ = "team@aiagentsuite.com"

from .core import AIAgentSuite
from .framework import FrameworkManager
from .protocols import ProtocolExecutor
from .memory_bank import MemoryBank

__all__ = [
    "AIAgentSuite",
    "FrameworkManager",
    "ProtocolExecutor",
    "MemoryBank",
]