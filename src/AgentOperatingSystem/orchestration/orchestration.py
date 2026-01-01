import os
import json
import asyncio
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from ..messaging.bus import MessageBus
from ..monitoring.audit_trail import AuditTrailManager, AuditEventType, AuditSeverity, audit_log
from .orchestrator import OrchestrationEngine
from ..storage.manager import StorageManager
from ..ml.pipeline import MLPipelineManager
from .state import State
from .role import Role
from .member import Member
from .decision import Decision

class Orchestration():
    """
    Core autonomous boardroom infrastructure
    """
    def __init__(self, aos_instance=None):
        super().__init__("autonomous_boardroom", aos_instance)
        self.state = State.INITIALIZING
        self.members: Dict[str, Member] = {}
        self.active_decisions: Dict[str, Decision] = {}
        self.decision_history: List[Decision] = []
        self.message_bus = MessageBus()
        self.audit_manager = AuditTrailManager()
        self.orchestrator = OrchestrationEngine()
        self.storage_manager = StorageManager()
        self.ml_pipeline = MLPipelineManager()
        self.config = self._load_config()
        self.lorax_enabled = False  # LoRAx integration status

    def _load_config(self) -> Dict[str, Any]:
        return {
            "max_members": 15,
            "decision_timeout": 3600,
            "quorum_threshold": 0.6,
            "auto_execution": True,
            "audit_level": "detailed",
            "enable_lorax": os.getenv("AOS_ENABLE_LORAX", "true").lower() == "true"
        }

    async def initialize(self):
        try:
            self.logger.info("Initializing Autonomous Boardroom")
            await self.message_bus.initialize()
            await self.audit_manager.initialize()
            await self.orchestrator.initialize()
            await self.storage_manager.initialize()
            await self.ml_pipeline.initialize()
            
            # Initialize LoRAx if enabled
            if self.config.get("enable_lorax", True):
                await self._initialize_lorax()
            
            await self._load_boardroom_state()
            await self._start_boardroom_operations()
            self.state = State.ACTIVE
            await audit_log(
                AuditEventType.SYSTEM_STARTUP,
                "Autonomous Boardroom initialized successfully",
                severity=AuditSeverity.INFO,
                component="boardroom",
                metadata={
                    "member_count": len(self.members),
                    "lorax_enabled": self.lorax_enabled
                }
            )
        except Exception as e:
            self.logger.error(f"Failed to initialize boardroom: {e}")
            self.state = State.SUSPENDED
            raise

    async def add_member(self, member: Member) -> bool:
        try:
            if len(self.members) >= self.config["max_members"]:
                raise ValueError("Boardroom at maximum capacity")
            if member.agent_id in self.members:
                raise ValueError(f"Member {member.agent_id} already exists")
            if not await self._validate_member(member):
                raise ValueError(f"Member validation failed for {member.agent_id}")
            self.members[member.agent_id] = member
            await self.message_bus.broadcast({
                "type": "member_joined",
                "member_id": member.agent_id,
                "role": member.role.value,
                "expertise": member.expertise_domains
            })
            await audit_log(
                AuditEventType.MEMBER_ADDED,
                f"New boardroom member added: {member.agent_id}",
                severity=AuditSeverity.INFO,
                component="boardroom",
                metadata={"member_id": member.agent_id, "role": member.role.value}
            )
            return True
        except Exception as e:
            self.logger.error(f"Failed to add member {member.agent_id}: {e}")
            return False

    async def initiate_decision(self, topic: str, decision_type: str, context: Dict[str, Any]) -> str:
        try:
            decision_id = f"decision_{datetime.now().isoformat()}_{hash(topic) % 10000}"
            decision = Decision(
                decision_id=decision_id,
                topic=topic,
                decision_type=decision_type,
                participants=[],
                outcome={},
                confidence_score=0.0,
                timestamp=datetime.now()
            )
            self.active_decisions[decision_id] = decision
            await self.orchestrator.start_decision_process(decision, context)
            await audit_log(
                AuditEventType.DECISION_INITIATED,
                f"Decision process initiated: {topic}",
                severity=AuditSeverity.INFO,
                component="boardroom",
                metadata={"decision_id": decision_id, "type": decision_type}
            )
            return decision_id
        except Exception as e:
            self.logger.error(f"Failed to initiate decision: {e}")
            raise

    async def get_boardroom_status(self) -> Dict[str, Any]:
        return {
            "state": self.state.value,
            "member_count": len(self.members),
            "active_decisions": len(self.active_decisions),
            "members": {
                member_id: {
                    "role": member.role.value,
                    "status": member.status,
                    "last_activity": member.last_activity.isoformat() if member.last_activity else None
                }
                for member_id, member in self.members.items()
            },
            "system_health": await self._get_system_health()
        }

    async def _validate_member(self, member: Member) -> bool:
        return True

    async def _load_boardroom_state(self):
        try:
            state_data = await self.storage_manager.load("boardroom_state")
            if state_data:
                pass
        except Exception as e:
            self.logger.warning(f"Could not load boardroom state: {e}")

    async def _start_boardroom_operations(self):
        asyncio.create_task(self._monitor_members())
        asyncio.create_task(self._process_decisions())

    async def _monitor_members(self):
        while self.state == State.ACTIVE:
            try:
                for member_id, member in self.members.items():
                    pass
                await asyncio.sleep(60)
            except Exception as e:
                self.logger.error(f"Error monitoring members: {e}")
                await asyncio.sleep(300)

    async def _process_decisions(self):
        while self.state == State.ACTIVE:
            try:
                for decision_id, decision in list(self.active_decisions.items()):
                    if self._is_decision_expired(decision):
                        await self._handle_expired_decision(decision)
                await asyncio.sleep(30)
            except Exception as e:
                self.logger.error(f"Error processing decisions: {e}")
                await asyncio.sleep(60)

    def _is_decision_expired(self, decision: Decision) -> bool:
        timeout = timedelta(seconds=self.config["decision_timeout"])
        return datetime.now() - decision.timestamp > timeout

    async def _handle_expired_decision(self, decision: Decision):
        if decision.decision_id in self.active_decisions:
            del self.active_decisions[decision.decision_id]
        decision.implementation_status = "expired"
        self.decision_history.append(decision)
        await audit_log(
            AuditEventType.DECISION_EXPIRED,
            f"Decision expired: {decision.topic}",
            severity=AuditSeverity.WARNING,
            component="boardroom",
            metadata={"decision_id": decision.decision_id}
        )

    async def _initialize_lorax(self):
        """Initialize LoRAx multi-adapter serving for cost-effective ML inference"""
        try:
            # Start LoRAx server
            success = await self.ml_pipeline.start_lorax_server()
            
            if success:
                self.lorax_enabled = True
                self.logger.info("LoRAx multi-adapter serving enabled")
                
                # Register adapters for all board members
                for member_id, member in self.members.items():
                    # Register LoRA adapter for this member's role
                    await self._register_member_adapter(member)
            else:
                self.logger.warning("LoRAx server failed to start, falling back to standard inference")
                self.lorax_enabled = False
                
        except Exception as e:
            self.logger.warning(f"LoRAx initialization failed: {e}, using standard inference")
            self.lorax_enabled = False
    
    async def _register_member_adapter(self, member: Member):
        """Register LoRA adapter for a board member"""
        try:
            # Adapter path based on member role
            adapter_path = f"/models/{member.role.value.lower()}_lora_adapter"
            
            self.ml_pipeline.register_lorax_adapter(
                agent_role=member.role.value,
                adapter_path=adapter_path,
                metadata={
                    "member_id": member.agent_id,
                    "expertise": member.expertise_domains
                }
            )
            
            self.logger.info(f"Registered LoRAx adapter for {member.role.value}")
            
        except Exception as e:
            self.logger.warning(f"Failed to register adapter for {member.agent_id}: {e}")

    async def _get_system_health(self) -> Dict[str, Any]:
        health = {
            "message_bus": await self.message_bus.health_check(),
            "storage": await self.storage_manager.health_check(),
            "orchestrator": await self.orchestrator.health_check(),
            "ml_pipeline": await self.ml_pipeline.health_check()
        }
        
        # Add LoRAx status if enabled
        if self.lorax_enabled:
            health["lorax"] = self.ml_pipeline.get_lorax_status()
        
        return health

async def create_autonomous_boardroom(aos_instance=None) -> Orchestration:
    boardroom = Orchestration(aos_instance)
    await boardroom.initialize()
    return boardroom
