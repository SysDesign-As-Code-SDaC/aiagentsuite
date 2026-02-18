"""
Adaptive Protocol Engine Module

Self-modifying protocol engine that adapts workflows
based on context and feedback.
"""

from typing import Any, Callable, Dict, List, Optional
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import json
import hashlib


class ProtocolStatus(Enum):
    """Protocol execution status."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    ADAPTED = "adapted"


class AdaptationTrigger(Enum):
    """Triggers for protocol adaptation."""
    CONTEXT_CHANGE = "context_change"
    FEEDBACK_RECEIVED = "feedback_received"
    PERFORMANCE_DEGRADATION = "performance_degradation"
    PATTERN_DETECTED = "pattern_detected"
    MANUAL = "manual"


@dataclass
class ProtocolStep:
    """A single step in a protocol."""
    id: str
    name: str
    description: str
    action: str  # Action to perform
    conditions: Dict[str, Any] = field(default_factory=dict)
    expected_outcome: str = ""
    estimated_duration: int = 0  # seconds
    alternatives: List[str] = field(default_factory=list)


@dataclass
class Protocol:
    """A protocol definition."""
    id: str
    name: str
    description: str
    steps: List[ProtocolStep]
    context_requirements: Dict[str, Any] = field(default_factory=dict)
    version: int = 1
    created_at: datetime = field(default_factory=datetime.now)
    adapted_from: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        if not self.id:
            content = f"{self.name}:{self.version}"
            self.id = hashlib.sha256(content.encode()).hexdigest()[:16]


@dataclass
class ProtocolExecution:
    """Execution instance of a protocol."""
    id: str
    protocol_id: str
    status: ProtocolStatus
    current_step: int = 0
    started_at: datetime = field(default_factory=datetime.now)
    completed_at: Optional[datetime] = None
    step_results: List[Dict[str, Any]] = field(default_factory=list)
    context: Dict[str, Any] = field(default_factory=dict)
    adaptations: List[Dict[str, Any]] = field(default_factory=list)


@dataclass
class ProtocolTemplate:
    """Template for generating protocols."""
    id: str
    name: str
    category: str
    step_templates: List[Dict[str, Any]]
    context_requirements: Dict[str, Any] = field(default_factory=dict)
    adaptation_rules: List[Dict[str, Any]] = field(default_factory=list)

    def generate_protocol(
        self,
        context: Dict[str, Any],
        overrides: Optional[Dict[str, Any]] = None,
    ) -> Protocol:
        """Generate a protocol from this template."""
        steps = []
        
        for i, template in enumerate(self.step_templates):
            step = ProtocolStep(
                id=f"step_{i}_{template.get('name', 'unnamed')}",
                name=template.get("name", f"Step {i+1}"),
                description=template.get("description", ""),
                action=template.get("action", ""),
                conditions=template.get("conditions", {}),
                expected_outcome=template.get("expected_outcome", ""),
                estimated_duration=template.get("estimated_duration", 60),
                alternatives=template.get("alternatives", []),
            )
            steps.append(step)

        return Protocol(
            id="",
            name=self.name,
            description=f"Generated from template: {self.name}",
            steps=steps,
            context_requirements=self.context_requirements.copy(),
        )


class AdaptiveProtocolEngine:
    """
    Adaptive protocol engine for self-modifying workflows.

    Provides:
    - Protocol generation from templates
    - Context-aware protocol adaptation
    - Performance-based optimization
    - Feedback-driven improvements
    """

    def __init__(
        self,
        adaptation_threshold: float = 0.7,
        max_versions: int = 10,
    ):
        """
        Initialize adaptive protocol engine.

        Args:
            adaptation_threshold: Threshold for triggering adaptation
            max_versions: Maximum versions to keep per protocol
        """
        self.adaptation_threshold = adaptation_threshold
        self.max_versions = max_versions

        # Protocol storage
        self.protocols: Dict[str, Protocol] = {}
        self.templates: Dict[str, ProtocolTemplate] = {}
        self.executions: List[ProtocolExecution] = []
        
        # Adaptation tracking
        self.adaptation_history: List[Dict[str, Any]] = []

        # Setup defaults
        self._setup_default_templates()

    def _setup_default_templates(self) -> None:
        """Set up default protocol templates."""
        # Feature Development Template
        self.register_template(ProtocolTemplate(
            id="template_feature_dev",
            name="Feature Development",
            category="development",
            step_templates=[
                {"name": "Analyze Requirements", "action": "analyze", "estimated_duration": 300},
                {"name": "Design Solution", "action": "design", "estimated_duration": 600},
                {"name": "Implement Code", "action": "implement", "estimated_duration": 1800},
                {"name": "Write Tests", "action": "test", "estimated_duration": 600},
                {"name": "Review Code", "action": "review", "estimated_duration": 300},
                {"name": "Deploy", "action": "deploy", "estimated_duration": 180},
            ],
            context_requirements={"project_type": "software"},
        ))

        # Security Audit Template
        self.register_template(ProtocolTemplate(
            id="template_security_audit",
            name="Security Audit",
            category="security",
            step_templates=[
                {"name": "Scope Assessment", "action": "scope", "estimated_duration": 180},
                {"name": "Threat Modeling", "action": "threat_model", "estimated_duration": 600},
                {"name": "Vulnerability Scan", "action": "scan", "estimated_duration": 900},
                {"name": "Penetration Testing", "action": "pentest", "estimated_duration": 1800},
                {"name": "Report Generation", "action": "report", "estimated_duration": 600},
            ],
            context_requirements={"security_level": "high"},
        ))

    # Template Management

    def register_template(self, template: ProtocolTemplate) -> None:
        """Register a protocol template."""
        self.templates[template.id] = template

    def get_template(self, template_id: str) -> Optional[ProtocolTemplate]:
        """Get a template by ID."""
        return self.templates.get(template_id)

    def list_templates(self, category: Optional[str] = None) -> List[ProtocolTemplate]:
        """List templates, optionally filtered by category."""
        if category:
            return [t for t in self.templates.values() if t.category == category]
        return list(self.templates.values())

    # Protocol Management

    def generate_protocol(
        self,
        template_id: str,
        context: Dict[str, Any],
    ) -> Optional[Protocol]:
        """Generate a protocol from a template."""
        template = self.templates.get(template_id)
        if not template:
            return None

        protocol = template.generate_protocol(context)
        self.protocols[protocol.id] = protocol
        return protocol

    def register_protocol(self, protocol: Protocol) -> None:
        """Register a custom protocol."""
        self.protocols[protocol.id] = protocol

    def get_protocol(self, protocol_id: str) -> Optional[Protocol]:
        """Get a protocol by ID."""
        return self.protocols.get(protocol_id)

    def list_protocols(self) -> List[Protocol]:
        """List all protocols."""
        return list(self.protocols.values())

    # Execution Management

    def start_execution(
        self,
        protocol_id: str,
        context: Optional[Dict[str, Any]] = None,
    ) -> Optional[ProtocolExecution]:
        """Start executing a protocol."""
        protocol = self.protocols.get(protocol_id)
        if not protocol:
            return None

        execution = ProtocolExecution(
            id=f"exec_{len(self.executions)}_{protocol_id}",
            protocol_id=protocol_id,
            status=ProtocolStatus.RUNNING,
            context=context or {},
        )
        
        self.executions.append(execution)
        return execution

    def complete_step(
        self,
        execution_id: str,
        step_result: Dict[str, Any],
    ) -> Optional[ProtocolExecution]:
        """Record step completion."""
        execution = self._get_execution(execution_id)
        if not execution:
            return None

        execution.step_results.append(step_result)
        execution.current_step += 1
        
        # Check if protocol is complete
        protocol = self.protocols.get(execution.protocol_id)
        if protocol and execution.current_step >= len(protocol.steps):
            execution.status = ProtocolStatus.COMPLETED
            execution.completed_at = datetime.now()

        return execution

    def _get_execution(self, execution_id: str) -> Optional[ProtocolExecution]:
        """Get execution by ID."""
        for exec in self.executions:
            if exec.id == execution_id:
                return exec
        return None

    # Adaptation

    def adapt_protocol(
        self,
        protocol_id: str,
        trigger: AdaptationTrigger,
        feedback: Optional[Dict[str, Any]] = None,
    ) -> Optional[Protocol]:
        """
        Adapt a protocol based on trigger and feedback.

        Args:
            protocol_id: Protocol to adapt
            trigger: What triggered the adaptation
            feedback: Optional feedback data

        Returns:
            Adapted protocol or None
        """
        original = self.protocols.get(protocol_id)
        if not original:
            return None

        # Create adapted version
        adapted = Protocol(
            id="",
            name=original.name,
            description=f"Adapted from {original.id} (trigger: {trigger.value})",
            steps=original.steps.copy(),
            context_requirements=original.context_requirements.copy(),
            version=original.version + 1,
            adapted_from=original.id,
        )

        # Apply adaptations based on trigger
        if trigger == AdaptationTrigger.CONTEXT_CHANGE:
            self._adapt_for_context(adapted, feedback or {})
        elif trigger == AdaptationTrigger.FEEDBACK_RECEIVED:
            self._adapt_for_feedback(adapted, feedback or {})
        elif trigger == AdaptationTrigger.PERFORMANCE_DEGRADATION:
            self._adapt_for_performance(adapted, feedback or {})
        elif trigger == AdaptationTrigger.PATTERN_DETECTED:
            self._adapt_for_pattern(adapted, feedback or {})

        # Store adaptation
        self.adaptation_history.append({
            "original_id": original.id,
            "adapted_id": adapted.id,
            "trigger": trigger.value,
            "timestamp": datetime.now().isoformat(),
        })

        # Manage version history
        self._manage_versions(original.id)

        # Store new protocol
        self.protocols[adapted.id] = adapted
        
        return adapted

    def _adapt_for_context(
        self,
        protocol: Protocol,
        context: Dict[str, Any],
    ) -> None:
        """Adapt protocol for context changes."""
        # Add or remove steps based on context
        if context.get("skip_tests"):
            protocol.steps = [s for s in protocol.steps if "test" not in s.name.lower()]
        
        if context.get("skip_review"):
            protocol.steps = [s for s in protocol.steps if "review" not in s.name.lower()]
        
        if context.get("urgent"):
            # Reduce durations for urgent work
            for step in protocol.steps:
                step.estimated_duration = max(60, step.estimated_duration // 2)

    def _adapt_for_feedback(
        self,
        protocol: Protocol,
        feedback: Dict[str, Any],
    ) -> None:
        """Adapt protocol based on feedback."""
        failed_steps = feedback.get("failed_steps", [])
        
        # Add alternatives for failed steps
        for step in protocol.steps:
            if step.id in failed_steps and step.alternatives:
                step.action = step.alternatives[0]

    def _adapt_for_performance(
        self,
        protocol: Protocol,
        feedback: Dict[str, Any],
    ) -> None:
        """Adapt protocol for performance issues."""
        slow_steps = feedback.get("slow_steps", [])
        
        # Mark slow steps for optimization
        for step in protocol.steps:
            if step.id in slow_steps:
                step.estimated_duration = int(step.estimated_duration * 0.8)

    def _adapt_for_pattern(
        self,
        protocol: Protocol,
        feedback: Dict[str, Any],
    ) -> None:
        """Adapt protocol based on detected patterns."""
        patterns = feedback.get("patterns", [])
        
        # Adjust steps based on patterns
        for pattern in patterns:
            if pattern.get("type") == "repetition":
                # Add automation for repetitive tasks
                for step in protocol.steps:
                    if pattern.get("step_name") == step.name:
                        step.action = f"auto_{step.action}"

    def _manage_versions(self, protocol_id: str) -> None:
        """Manage protocol version history."""
        versions = [
            p for p in self.protocols.values()
            if p.adapted_from == protocol_id or p.id == protocol_id
        ]
        
        # Remove old versions if over limit
        if len(versions) > self.max_versions:
            versions.sort(key=lambda p: p.version)
            for old in versions[:-self.max_versions]:
                del self.protocols[old.id]

    # Analytics

    def get_execution_stats(self, protocol_id: str) -> Dict[str, Any]:
        """Get execution statistics for a protocol."""
        executions = [e for e in self.executions if e.protocol_id == protocol_id]
        
        if not executions:
            return {"total_executions": 0}

        completed = [e for e in executions if e.status == ProtocolStatus.COMPLETED]
        failed = [e for e in executions if e.status == ProtocolStatus.FAILED]
        
        return {
            "total_executions": len(executions),
            "completed": len(completed),
            "failed": len(failed),
            "success_rate": len(completed) / len(executions) if executions else 0,
        }

    def get_adaptation_history(
        self,
        protocol_id: Optional[str] = None,
        limit: int = 10,
    ) -> List[Dict[str, Any]]:
        """Get adaptation history."""
        history = self.adaptation_history
        
        if protocol_id:
            history = [
                h for h in history
                if h["original_id"] == protocol_id
            ]
        
        return history[-limit:]

    def export_protocols(self) -> str:
        """Export all protocols as JSON."""
        data = {
            pid: {
                "name": p.name,
                "description": p.description,
                "version": p.version,
                "steps": [
                    {
                        "id": s.id,
                        "name": s.name,
                        "action": s.action,
                        "estimated_duration": s.estimated_duration,
                    }
                    for s in p.steps
                ],
                "created_at": p.created_at.isoformat(),
                "adapted_from": p.adapted_from,
            }
            for pid, p in self.protocols.items()
        }
        return json.dumps(data, indent=2)
