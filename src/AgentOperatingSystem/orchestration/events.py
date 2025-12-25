"""
Event-Driven Orchestration

Provides complex event processing and reactive workflow triggering.
"""

import logging
import asyncio
from typing import Dict, Any, List, Optional, Callable
from datetime import datetime, timedelta
from dataclasses import dataclass


@dataclass
class EventPattern:
    """Defines a complex event pattern for triggering workflows"""
    name: str
    conditions: List[Dict[str, Any]]
    temporal_relationship: str  # "all_within", "sequence", "any"
    window_minutes: int
    

class EventDrivenOrchestrator:
    """
    Orchestrates workflows based on complex event patterns.
    
    Features:
    - Complex event processing (CEP)
    - Pattern-based workflow triggering
    - Event stream integration
    - Real-time reactive workflows
    """
    
    def __init__(self):
        self.logger = logging.getLogger("AOS.EventDrivenOrchestrator")
        self.patterns = {}
        self.event_buffer = []
        self.reactive_mode = False
        self.workflow_triggers = {}
        
    async def register_pattern(
        self,
        pattern: EventPattern,
        workflow_trigger: str,
        context_enrichment: Optional[List[str]] = None
    ):
        """
        Register an event pattern that triggers a workflow.
        
        Args:
            pattern: Event pattern to detect
            workflow_trigger: Workflow to trigger when pattern matches
            context_enrichment: Additional context to include
        """
        self.logger.info(f"Registering event pattern: {pattern.name}")
        
        self.patterns[pattern.name] = {
            "pattern": pattern,
            "workflow_trigger": workflow_trigger,
            "context_enrichment": context_enrichment or []
        }
        
        self.workflow_triggers[pattern.name] = workflow_trigger
    
    async def enable_reactive_mode(
        self,
        debounce_ms: int = 500,
        correlation_keys: Optional[List[str]] = None
    ):
        """
        Enable reactive mode for automatic workflow triggering.
        
        Args:
            debounce_ms: Milliseconds to wait before triggering
            correlation_keys: Keys to correlate related events
        """
        self.logger.info("Enabling reactive orchestration mode")
        self.reactive_mode = True
        self.debounce_ms = debounce_ms
        self.correlation_keys = correlation_keys or []
        
        # Start event processor
        asyncio.create_task(self._process_events())
    
    async def process_event(self, event: Dict[str, Any]):
        """
        Process an incoming event and check for pattern matches.
        
        Args:
            event: Event data
        """
        # Add timestamp if not present
        if "timestamp" not in event:
            event["timestamp"] = datetime.utcnow()
        
        self.event_buffer.append(event)
        
        # Limit buffer size
        max_buffer_size = 10000
        if len(self.event_buffer) > max_buffer_size:
            self.event_buffer = self.event_buffer[-max_buffer_size:]
        
        # Check for pattern matches
        await self._check_patterns(event)
    
    async def _process_events(self):
        """Background task to process buffered events"""
        while self.reactive_mode:
            try:
                # Clean up old events
                cutoff_time = datetime.utcnow() - timedelta(hours=1)
                self.event_buffer = [
                    e for e in self.event_buffer
                    if e.get("timestamp", datetime.utcnow()) > cutoff_time
                ]
                
                await asyncio.sleep(10)  # Check every 10 seconds
                
            except Exception as e:
                self.logger.error(f"Error processing events: {e}")
                await asyncio.sleep(5)
    
    async def _check_patterns(self, new_event: Dict[str, Any]):
        """Check if new event matches any registered patterns"""
        for pattern_name, pattern_data in self.patterns.items():
            pattern = pattern_data["pattern"]
            
            if await self._matches_pattern(new_event, pattern):
                self.logger.info(f"Event pattern '{pattern_name}' matched!")
                
                # Trigger workflow
                workflow_id = pattern_data["workflow_trigger"]
                await self._trigger_workflow(
                    workflow_id,
                    pattern_name,
                    new_event,
                    pattern_data.get("context_enrichment", [])
                )
    
    async def _matches_pattern(
        self,
        event: Dict[str, Any],
        pattern: EventPattern
    ) -> bool:
        """Check if event matches a pattern"""
        # Get relevant events within time window
        window_start = datetime.utcnow() - timedelta(minutes=pattern.window_minutes)
        recent_events = [
            e for e in self.event_buffer
            if e.get("timestamp", datetime.utcnow()) > window_start
        ]
        
        if pattern.temporal_relationship == "all_within":
            # All conditions must be met within window
            return all(
                any(self._event_matches_condition(e, cond) for e in recent_events)
                for cond in pattern.conditions
            )
        
        elif pattern.temporal_relationship == "sequence":
            # Events must occur in sequence
            matched_conditions = []
            for event in sorted(recent_events, key=lambda x: x.get("timestamp", datetime.utcnow())):
                for cond in pattern.conditions:
                    if cond not in matched_conditions and self._event_matches_condition(event, cond):
                        matched_conditions.append(cond)
            return len(matched_conditions) == len(pattern.conditions)
        
        elif pattern.temporal_relationship == "any":
            # Any condition met
            return any(
                self._event_matches_condition(event, cond)
                for cond in pattern.conditions
            )
        
        return False
    
    def _event_matches_condition(
        self,
        event: Dict[str, Any],
        condition: Dict[str, Any]
    ) -> bool:
        """Check if event matches a single condition"""
        event_type = condition.get("event")
        
        # Check event type match
        if event.get("event_type") != event_type and event.get("type") != event_type:
            return False
        
        # Check additional conditions
        for key, value in condition.items():
            if key == "event":
                continue
            
            if key not in event:
                return False
            
            # Handle different comparison types
            if isinstance(value, dict):
                # Threshold comparison
                if "threshold" in value:
                    if event[key] < value["threshold"]:
                        return False
                if "increase" in value:
                    # Would need historical comparison
                    pass
            else:
                # Exact match
                if event[key] != value:
                    return False
        
        return True
    
    async def _trigger_workflow(
        self,
        workflow_id: str,
        pattern_name: str,
        triggering_event: Dict[str, Any],
        context_enrichment: List[str]
    ):
        """Trigger a workflow based on pattern match"""
        self.logger.info(f"Triggering workflow '{workflow_id}' from pattern '{pattern_name}'")
        
        # In real implementation, would call orchestration engine
        # For now, just log
        context = {
            "pattern": pattern_name,
            "triggering_event": triggering_event,
            "enrichment": context_enrichment,
            "triggered_at": datetime.utcnow().isoformat()
        }
        
        self.logger.debug(f"Workflow context: {context}")
    
    async def setup_stream_processing(self, stream_config: Dict[str, Any]):
        """
        Setup real-time stream processing.
        
        Args:
            stream_config: Stream sources and processing configuration
        """
        self.logger.info("Setting up stream processing")
        
        sources = stream_config.get("sources", [])
        windowing = stream_config.get("windowing", {})
        trigger_workflows = stream_config.get("trigger_workflows", {})
        
        # Store configuration
        self.stream_config = {
            "sources": sources,
            "windowing": windowing,
            "trigger_workflows": trigger_workflows
        }
        
        self.logger.info(f"Configured {len(sources)} stream sources")
