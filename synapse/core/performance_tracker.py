"""
Performance Tracking Module for Synapse Agent

This module provides real-time performance metrics collection and visualization
for the Synapse logistics coordination agent. It tracks execution times, tool usage,
reflection patterns, and LLM token consumption.
"""

import time
import json
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field, asdict
from datetime import datetime
from collections import defaultdict
import threading
from queue import Queue


@dataclass
class ToolExecution:
    """Represents a single tool execution with timing and status."""
    tool_name: str
    start_time: float
    end_time: Optional[float] = None
    duration: Optional[float] = None
    status: str = "pending"  # pending, running, success, failed
    parameters: Dict[str, Any] = field(default_factory=dict)
    result: Optional[str] = None
    parallel_group: Optional[int] = None
    
    def complete(self, status: str, result: Optional[str] = None):
        """Mark tool execution as complete."""
        self.end_time = time.time()
        self.duration = self.end_time - self.start_time
        self.status = status
        self.result = result


@dataclass
class ReflectionEvent:
    """Tracks reflection system activation."""
    timestamp: float
    reason: str
    original_tool: str
    suggested_alternative: str
    recovery_time: Optional[float] = None


@dataclass
class QueryMetrics:
    """Complete metrics for a single query execution."""
    query_id: str
    scenario_type: str
    start_time: float
    end_time: Optional[float] = None
    total_duration: Optional[float] = None
    
    # Execution metrics
    total_steps: int = 0
    action_steps: int = 0
    reflection_steps: int = 0
    tool_executions: List[ToolExecution] = field(default_factory=list)
    reflection_events: List[ReflectionEvent] = field(default_factory=list)
    
    # Parallel execution metrics
    parallel_executions: int = 0
    time_saved_by_parallelization: float = 0.0
    
    # LLM metrics
    total_input_tokens: int = 0
    total_output_tokens: int = 0
    estimated_cost: float = 0.0
    llm_calls: int = 0
    avg_llm_response_time: float = 0.0
    
    # Success metrics
    first_try_success: bool = True
    resolution_achieved: bool = False
    final_plan: Optional[str] = None
    
    def complete(self, success: bool = True):
        """Mark query as complete."""
        self.end_time = time.time()
        self.total_duration = self.end_time - self.start_time
        self.resolution_achieved = success
        
    def calculate_parallelization_savings(self):
        """Calculate time saved through parallel tool execution."""
        # Group tools by parallel execution group
        groups = defaultdict(list)
        for tool in self.tool_executions:
            if tool.parallel_group is not None:
                groups[tool.parallel_group].append(tool)
        
        total_saved = 0.0
        for group_tools in groups.values():
            if len(group_tools) > 1:
                # Time if executed sequentially
                sequential_time = sum(t.duration or 0 for t in group_tools)
                # Time when executed in parallel (max duration)
                parallel_time = max(t.duration or 0 for t in group_tools)
                total_saved += (sequential_time - parallel_time)
        
        self.time_saved_by_parallelization = total_saved
        self.parallel_executions = len(groups)
        
    def get_complexity_score(self) -> int:
        """Calculate scenario complexity score (1-10)."""
        score = min(10, max(1, 
            self.total_steps * 0.5 + 
            self.reflection_steps * 2 + 
            (0 if self.first_try_success else 3)
        ))
        return int(score)


class PerformanceTracker:
    """
    Singleton performance tracker for the Synapse agent.
    Collects and aggregates performance metrics across all query executions.
    """
    
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
            
        self.current_query: Optional[QueryMetrics] = None
        self.query_history: List[QueryMetrics] = []
        self.active_tools: Dict[str, ToolExecution] = {}
        self.metrics_queue = Queue()
        
        # Aggregate statistics
        self.total_queries = 0
        self.successful_queries = 0
        self.total_reflection_triggers = 0
        self.tool_usage_counts = defaultdict(int)
        self.tool_success_rates = defaultdict(lambda: {"success": 0, "total": 0})
        
        # LLM cost tracking (Gemini pricing estimates)
        self.gemini_input_cost_per_1k = 0.00025  # $0.25 per 1M tokens
        self.gemini_output_cost_per_1k = 0.001   # $1.00 per 1M tokens
        
        self._initialized = True
    
    def start_query(self, query_id: str, scenario_type: str, problem: str) -> QueryMetrics:
        """Begin tracking a new query execution."""
        self.current_query = QueryMetrics(
            query_id=query_id,
            scenario_type=scenario_type,
            start_time=time.time()
        )
        self.total_queries += 1
        return self.current_query
    
    def start_tool(self, tool_name: str, parameters: Dict[str, Any]) -> str:
        """Record tool execution start."""
        if not self.current_query:
            return ""
            
        tool_id = f"{tool_name}_{int(time.time() * 1000)}"
        tool_exec = ToolExecution(
            tool_name=tool_name,
            start_time=time.time(),
            parameters=parameters,
            status="running"
        )
        
        self.active_tools[tool_id] = tool_exec
        self.current_query.tool_executions.append(tool_exec)
        self.tool_usage_counts[tool_name] += 1
        
        return tool_id
    
    def complete_tool(self, tool_id: str, success: bool, result: Optional[str] = None):
        """Record tool execution completion."""
        if tool_id in self.active_tools:
            tool = self.active_tools[tool_id]
            tool.complete("success" if success else "failed", result)
            
            # Update success rates
            stats = self.tool_success_rates[tool.tool_name]
            stats["total"] += 1
            if success:
                stats["success"] += 1
            
            del self.active_tools[tool_id]
    
    def record_reflection(self, reason: str, original_tool: str, alternative: str):
        """Record reflection system activation."""
        if not self.current_query:
            return
            
        event = ReflectionEvent(
            timestamp=time.time(),
            reason=reason,
            original_tool=original_tool,
            suggested_alternative=alternative
        )
        
        self.current_query.reflection_events.append(event)
        self.current_query.first_try_success = False
        self.current_query.reflection_steps += 1
        self.total_reflection_triggers += 1
    
    def record_llm_call(self, input_tokens: int, output_tokens: int, response_time: float):
        """Record LLM API usage metrics."""
        if not self.current_query:
            return
            
        self.current_query.total_input_tokens += input_tokens
        self.current_query.total_output_tokens += output_tokens
        self.current_query.llm_calls += 1
        
        # Update average response time
        prev_avg = self.current_query.avg_llm_response_time
        self.current_query.avg_llm_response_time = (
            (prev_avg * (self.current_query.llm_calls - 1) + response_time) 
            / self.current_query.llm_calls
        )
        
        # Calculate cost
        input_cost = (input_tokens / 1000) * self.gemini_input_cost_per_1k
        output_cost = (output_tokens / 1000) * self.gemini_output_cost_per_1k
        self.current_query.estimated_cost += (input_cost + output_cost)
    
    def complete_query(self, success: bool = True, final_plan: Optional[str] = None):
        """Mark current query as complete."""
        if not self.current_query:
            return
            
        self.current_query.complete(success)
        self.current_query.final_plan = final_plan
        self.current_query.calculate_parallelization_savings()
        
        if success:
            self.successful_queries += 1
        
        self.query_history.append(self.current_query)
        self.current_query = None
    
    def get_current_metrics(self) -> Optional[Dict[str, Any]]:
        """Get real-time metrics for current query."""
        if not self.current_query:
            return None
            
        return {
            "query_id": self.current_query.query_id,
            "elapsed_time": time.time() - self.current_query.start_time,
            "steps_completed": self.current_query.total_steps,
            "active_tools": len(self.active_tools),
            "reflection_count": self.current_query.reflection_steps,
            "estimated_cost": f"${self.current_query.estimated_cost:.4f}",
            "complexity_score": self.current_query.get_complexity_score()
        }
    
    def get_aggregate_stats(self) -> Dict[str, Any]:
        """Get aggregate performance statistics."""
        if not self.query_history:
            return {}
            
        avg_duration = sum(q.total_duration or 0 for q in self.query_history) / len(self.query_history)
        avg_steps = sum(q.total_steps for q in self.query_history) / len(self.query_history)
        
        return {
            "total_queries": self.total_queries,
            "success_rate": (self.successful_queries / self.total_queries * 100) if self.total_queries > 0 else 0,
            "avg_resolution_time": avg_duration,
            "avg_steps_to_resolution": avg_steps,
            "reflection_trigger_rate": (self.total_reflection_triggers / self.total_queries * 100) if self.total_queries > 0 else 0,
            "most_used_tools": sorted(self.tool_usage_counts.items(), key=lambda x: x[1], reverse=True)[:5],
            "total_cost": sum(q.estimated_cost for q in self.query_history),
            "avg_complexity": sum(q.get_complexity_score() for q in self.query_history) / len(self.query_history)
        }
    
    def get_tool_performance(self) -> Dict[str, Any]:
        """Get detailed tool performance metrics."""
        tool_metrics = {}
        
        for tool_name, stats in self.tool_success_rates.items():
            if stats["total"] > 0:
                tool_metrics[tool_name] = {
                    "usage_count": self.tool_usage_counts[tool_name],
                    "success_rate": (stats["success"] / stats["total"] * 100),
                    "avg_duration": self._get_avg_tool_duration(tool_name)
                }
        
        return tool_metrics
    
    def _get_avg_tool_duration(self, tool_name: str) -> float:
        """Calculate average duration for a specific tool."""
        durations = []
        for query in self.query_history:
            for tool in query.tool_executions:
                if tool.tool_name == tool_name and tool.duration:
                    durations.append(tool.duration)
        
        return sum(durations) / len(durations) if durations else 0.0
    
    def export_metrics(self, filepath: str):
        """Export all metrics to JSON file."""
        export_data = {
            "timestamp": datetime.now().isoformat(),
            "aggregate_stats": self.get_aggregate_stats(),
            "tool_performance": self.get_tool_performance(),
            "query_history": [asdict(q) for q in self.query_history[-10:]]  # Last 10 queries
        }
        
        with open(filepath, 'w') as f:
            json.dump(export_data, f, indent=2, default=str)


# Global tracker instance
tracker = PerformanceTracker()