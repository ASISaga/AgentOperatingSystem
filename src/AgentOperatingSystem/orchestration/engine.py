"""
AOS Decision Engine

Provides intelligent decision-making capabilities for the Agent Operating System.
Integrates with ML models, decision trees, and scoring algorithms.
"""

import logging
import json
import os
from typing import Dict, Any, List, Optional
from datetime import datetime
from ..config.decision import DecisionConfig


class DecisionEngine:
    """
    Centralized decision engine for AOS.
    
    Provides intelligent decision-making capabilities using:
    - Principle-based scoring
    - ML-based predictions
    - Rule-based decision trees
    - Multi-criteria analysis
    """
    
    def __init__(self, config: DecisionConfig):
        self.config = config
        self.logger = logging.getLogger("AOS.DecisionEngine")
        
        # Decision components
        self.principles = {}
        self.decision_tree = {}
        self.adapters = {}
        self.decision_history = []
        
        # Load configuration
        self._load_config()
    
    def _load_config(self):
        """Load decision configuration files"""
        try:
            # Load principles
            if os.path.exists(self.config.principles_path):
                with open(self.config.principles_path, 'r') as f:
                    self.principles = json.load(f)
            
            # Load decision tree
            if os.path.exists(self.config.decision_tree_path):
                with open(self.config.decision_tree_path, 'r') as f:
                    self.decision_tree = json.load(f)
            
            # Load adapters
            if os.path.exists(self.config.adapters_path):
                with open(self.config.adapters_path, 'r') as f:
                    self.adapters = json.load(f)
            
            self.logger.info("Decision engine configuration loaded successfully")
            
        except Exception as e:
            self.logger.warning(f"Could not load decision config: {e}")
            # Use default empty configurations
            self.principles = {"principles": []}
            self.decision_tree = {"root": {"type": "default", "action": "approve"}}
            self.adapters = {"adapters": []}
    
    async def decide(self, decision_context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Make a decision based on the given context.
        
        Args:
            decision_context: Context information for the decision
            
        Returns:
            Decision result with score, action, and reasoning
        """
        try:
            decision_id = f"decision_{datetime.utcnow().timestamp()}"
            
            # Extract decision components
            evidence = decision_context.get("evidence", {})
            criteria = decision_context.get("criteria", [])
            options = decision_context.get("options", [])
            agent_id = decision_context.get("agent_id", "unknown")
            
            # Score the decision using multiple methods
            scores = []
            
            # Principle-based scoring
            if self.principles.get("principles"):
                principle_score = self._score_by_principles(evidence, criteria)
                scores.append(principle_score)
            
            # Decision tree traversal
            tree_score = self._traverse_decision_tree(evidence)
            scores.append(tree_score)
            
            # ML-based scoring (if enabled)
            if self.config.enable_ml_scoring:
                ml_score = await self._score_by_ml(evidence, criteria)
                scores.append(ml_score)
            
            # Blend scores
            final_score = self._blend_scores(scores, self.config.default_scoring_method)
            
            # Determine action
            action = self._determine_action(final_score, options)
            
            # Generate reasoning
            reasoning = self._generate_reasoning(decision_context, scores, final_score)
            
            # Create result
            result = {
                "decision_id": decision_id,
                "agent_id": agent_id,
                "timestamp": datetime.utcnow().isoformat(),
                "action": action,
                "score": final_score,
                "confidence": self._calculate_confidence(scores),
                "reasoning": reasoning,
                "context": decision_context
            }
            
            # Store in history
            self.decision_history.append(result)
            if len(self.decision_history) > 1000:  # Limit history size
                self.decision_history = self.decision_history[-1000:]
            
            self.logger.info(f"Decision made: {decision_id} -> {action} (score: {final_score})")
            return result
            
        except Exception as e:
            self.logger.error(f"Error making decision: {e}")
            return {
                "decision_id": f"error_{datetime.utcnow().timestamp()}",
                "action": "error",
                "score": {"error": 1.0},
                "error": str(e)
            }
    
    def _score_by_principles(self, evidence: Dict[str, Any], criteria: List[str]) -> Dict[str, float]:
        """Score decision based on configured principles"""
        scores = {}
        principles = self.principles.get("principles", [])
        
        for principle in principles:
            principle_name = principle.get("name", "unknown")
            weight = principle.get("weight", 1.0)
            
            # Simple scoring based on evidence matching principle criteria
            score = 0.0
            for criterion in principle.get("criteria", []):
                if criterion in evidence:
                    score += evidence[criterion] * weight
            
            scores[principle_name] = max(0.0, min(1.0, score))
        
        return scores
    
    def _traverse_decision_tree(self, evidence: Dict[str, Any]) -> Dict[str, float]:
        """Traverse decision tree to get score"""
        current_node = self.decision_tree.get("root", {})
        path = []
        
        while current_node.get("type") != "leaf":
            condition = current_node.get("condition")
            if not condition:
                break
            
            # Simple condition evaluation
            field = condition.get("field", "")
            operator = condition.get("operator", "==")
            value = condition.get("value")
            
            evidence_value = evidence.get(field)
            
            if operator == "==" and evidence_value == value:
                path.append("true")
                current_node = current_node.get("true", {})
            elif operator == ">" and isinstance(evidence_value, (int, float)) and evidence_value > value:
                path.append("true")
                current_node = current_node.get("true", {})
            else:
                path.append("false")
                current_node = current_node.get("false", {})
        
        # Get leaf node score
        action = current_node.get("action", "unknown")
        confidence = current_node.get("confidence", 0.5)
        
        return {action: confidence}
    
    async def _score_by_ml(self, evidence: Dict[str, Any], criteria: List[str]) -> Dict[str, float]:
        """Score decision using ML models (placeholder for now)"""
        # This would integrate with actual ML models
        # For now, return a simple heuristic score
        
        total_evidence = sum(v for v in evidence.values() if isinstance(v, (int, float)))
        normalized_score = max(0.0, min(1.0, total_evidence / 10.0))
        
        return {"ml_prediction": normalized_score}
    
    def _blend_scores(self, scores: List[Dict[str, float]], method: str) -> Dict[str, float]:
        """Blend multiple score dictionaries using specified method"""
        if not scores:
            return {"default": 0.5}
        
        # Get all unique keys
        all_keys = set()
        for score_dict in scores:
            all_keys.update(score_dict.keys())
        
        blended = {}
        
        for key in all_keys:
            values = [score_dict.get(key, 0.0) for score_dict in scores]
            
            if method == "weighted":
                # Simple weighted average (equal weights for now)
                blended[key] = sum(values) / len(values)
            elif method == "max":
                blended[key] = max(values)
            elif method == "min":
                blended[key] = min(values)
            else:  # default to mean
                blended[key] = sum(values) / len(values)
        
        return blended
    
    def _determine_action(self, scores: Dict[str, float], options: List[str]) -> str:
        """Determine the best action based on scores"""
        if not scores:
            return "no_action"
        
        # Find the highest scoring option
        max_score = max(scores.values())
        best_actions = [action for action, score in scores.items() if score == max_score]
        
        # If specific options are provided, prefer those
        if options:
            for option in options:
                if option in best_actions:
                    return option
        
        # Return the first best action
        return best_actions[0] if best_actions else "no_action"
    
    def _generate_reasoning(self, context: Dict[str, Any], scores: List[Dict[str, float]], 
                           final_score: Dict[str, float]) -> str:
        """Generate human-readable reasoning for the decision"""
        evidence = context.get("evidence", {})
        
        reasoning_parts = []
        reasoning_parts.append(f"Based on evidence: {evidence}")
        reasoning_parts.append(f"Scoring methods used: {len(scores)}")
        reasoning_parts.append(f"Final scores: {final_score}")
        
        best_action = max(final_score.items(), key=lambda x: x[1])
        reasoning_parts.append(f"Recommended action: {best_action[0]} (confidence: {best_action[1]:.2f})")
        
        return " | ".join(reasoning_parts)
    
    def _calculate_confidence(self, scores: List[Dict[str, float]]) -> float:
        """Calculate overall confidence in the decision"""
        if not scores:
            return 0.0
        
        # Simple confidence calculation based on score consistency
        all_values = []
        for score_dict in scores:
            all_values.extend(score_dict.values())
        
        if not all_values:
            return 0.0
        
        # Higher confidence when scores are more consistent
        mean_score = sum(all_values) / len(all_values)
        variance = sum((x - mean_score) ** 2 for x in all_values) / len(all_values)
        
        # Convert variance to confidence (lower variance = higher confidence)
        confidence = max(0.0, min(1.0, 1.0 - variance))
        
        return confidence
    
    def get_decision_history(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Get recent decision history"""
        return self.decision_history[-limit:]
    
    def get_status(self) -> Dict[str, Any]:
        """Get decision engine status"""
        return {
            "principles_loaded": bool(self.principles.get("principles")),
            "decision_tree_loaded": bool(self.decision_tree.get("root")),
            "adapters_loaded": bool(self.adapters.get("adapters")),
            "total_decisions": len(self.decision_history),
            "ml_scoring_enabled": self.config.enable_ml_scoring
        }