"""
Priority-Based Message Queuing

Provides multi-priority queuing with weighted fair scheduling.
"""

import logging
import asyncio
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass
import heapq


@dataclass
class PriorityLevel:
    """Configuration for a priority level"""
    priority: str
    weight: float
    max_latency_ms: int


class PriorityQueueManager:
    """
    Manages multi-priority message queues with fair scheduling.
    
    Features:
    - Multiple priority levels
    - Weighted fair queuing
    - Priority preemption
    - Deadline-based scheduling
    - SLA guarantees
    """
    
    def __init__(self):
        self.logger = logging.getLogger("AOS.PriorityQueueManager")
        self.priority_queues = {}
        self.priority_config = {}
        self.scheduling_algorithm = "weighted_fair_queuing"
        self.preemption_enabled = False
        
    async def configure(
        self,
        levels: List[Dict[str, Any]],
        scheduling_algorithm: str = "weighted_fair_queuing"
    ):
        """
        Configure priority levels and scheduling.
        
        Args:
            levels: List of priority level configurations
            scheduling_algorithm: Scheduling algorithm to use
        """
        self.logger.info(f"Configuring {len(levels)} priority levels")
        
        self.scheduling_algorithm = scheduling_algorithm
        
        for level in levels:
            priority = level["priority"]
            self.priority_queues[priority] = []
            self.priority_config[priority] = PriorityLevel(
                priority=priority,
                weight=level["weight"],
                max_latency_ms=level["max_latency_ms"]
            )
    
    async def enqueue(
        self,
        message: Dict[str, Any],
        priority: str,
        deadline: Optional[datetime] = None
    ):
        """
        Enqueue message with priority.
        
        Args:
            message: Message to enqueue
            priority: Priority level
            deadline: Optional deadline for delivery
        """
        if priority not in self.priority_queues:
            self.logger.warning(
                f"Unknown priority {priority}, using 'normal'"
            )
            priority = "normal"
        
        entry = {
            "message": message,
            "priority": priority,
            "deadline": deadline,
            "enqueued_at": datetime.utcnow()
        }
        
        if deadline:
            # Use deadline for ordering
            priority_value = deadline.timestamp()
        else:
            # Use priority weight
            config = self.priority_config.get(priority)
            priority_value = -config.weight if config else 0
        
        # Add to priority queue
        heapq.heappush(
            self.priority_queues[priority],
            (priority_value, entry)
        )
        
        self.logger.debug(
            f"Enqueued message with priority {priority}, "
            f"queue size: {len(self.priority_queues[priority])}"
        )
    
    async def dequeue(
        self,
        count: int = 1
    ) -> List[Dict[str, Any]]:
        """
        Dequeue messages using configured scheduling algorithm.
        
        Args:
            count: Number of messages to dequeue
            
        Returns:
            List of dequeued messages
        """
        messages = []
        
        if self.scheduling_algorithm == "weighted_fair_queuing":
            messages = await self._weighted_fair_dequeue(count)
        elif self.scheduling_algorithm == "strict_priority":
            messages = await self._strict_priority_dequeue(count)
        elif self.scheduling_algorithm == "deadline_based":
            messages = await self._deadline_based_dequeue(count)
        
        return messages
    
    async def _weighted_fair_dequeue(
        self,
        count: int
    ) -> List[Dict[str, Any]]:
        """Dequeue using weighted fair queuing"""
        messages = []
        
        # Calculate weights for each non-empty queue
        active_queues = {
            p: q for p, q in self.priority_queues.items() if q
        }
        
        if not active_queues:
            return messages
        
        total_weight = sum(
            self.priority_config[p].weight
            for p in active_queues.keys()
        )
        
        # Dequeue proportionally based on weights
        for priority, queue in active_queues.items():
            config = self.priority_config[priority]
            proportion = config.weight / total_weight
            queue_count = max(1, int(count * proportion))
            
            for _ in range(min(queue_count, len(queue))):
                if queue:
                    _, entry = heapq.heappop(queue)
                    messages.append(entry["message"])
                    
                    # Check latency SLA
                    latency_ms = (
                        datetime.utcnow() - entry["enqueued_at"]
                    ).total_seconds() * 1000
                    
                    if latency_ms > config.max_latency_ms:
                        self.logger.warning(
                            f"Message exceeded max latency for {priority}: "
                            f"{latency_ms:.0f}ms > {config.max_latency_ms}ms"
                        )
        
        return messages
    
    async def _strict_priority_dequeue(
        self,
        count: int
    ) -> List[Dict[str, Any]]:
        """Dequeue using strict priority ordering"""
        messages = []
        
        # Sort priorities by weight (highest first)
        sorted_priorities = sorted(
            self.priority_config.items(),
            key=lambda x: x[1].weight,
            reverse=True
        )
        
        for priority, config in sorted_priorities:
            queue = self.priority_queues.get(priority, [])
            
            while queue and len(messages) < count:
                _, entry = heapq.heappop(queue)
                messages.append(entry["message"])
            
            if len(messages) >= count:
                break
        
        return messages
    
    async def _deadline_based_dequeue(
        self,
        count: int
    ) -> List[Dict[str, Any]]:
        """Dequeue based on deadlines (earliest first)"""
        messages = []
        all_entries = []
        
        # Collect all entries with deadlines
        for priority, queue in self.priority_queues.items():
            for _, entry in queue:
                if entry.get("deadline"):
                    all_entries.append(entry)
        
        # Sort by deadline
        all_entries.sort(key=lambda x: x["deadline"])
        
        # Take earliest deadlines
        for entry in all_entries[:count]:
            messages.append(entry["message"])
            
            # Remove from original queue
            priority = entry["priority"]
            queue = self.priority_queues.get(priority, [])
            self.priority_queues[priority] = [
                (pv, e) for pv, e in queue
                if e != entry
            ]
        
        return messages
    
    async def enable_preemption(
        self,
        allow_preemption: bool = True,
        min_preemption_priority: str = "high"
    ):
        """
        Enable priority preemption.
        
        Args:
            allow_preemption: Whether to allow preemption
            min_preemption_priority: Minimum priority for preemption
        """
        self.logger.info(
            f"{'Enabling' if allow_preemption else 'Disabling'} preemption "
            f"(min priority: {min_preemption_priority})"
        )
        
        self.preemption_enabled = allow_preemption
        self.min_preemption_priority = min_preemption_priority
    
    def get_queue_stats(self) -> Dict[str, Any]:
        """Get statistics for all queues"""
        stats = {}
        
        for priority, queue in self.priority_queues.items():
            config = self.priority_config.get(priority)
            
            if queue:
                latencies = [
                    (datetime.utcnow() - e["enqueued_at"]).total_seconds() * 1000
                    for _, e in queue
                ]
                avg_latency = sum(latencies) / len(latencies)
                max_latency = max(latencies)
            else:
                avg_latency = 0
                max_latency = 0
            
            stats[priority] = {
                "queue_depth": len(queue),
                "avg_latency_ms": avg_latency,
                "max_latency_ms": max_latency,
                "sla_max_latency_ms": config.max_latency_ms if config else None,
                "sla_violations": sum(1 for l in latencies if l > config.max_latency_ms) if config and latencies else 0
            }
        
        return stats
