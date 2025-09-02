#!/usr/bin/env python3
"""
Performance Demonstration Script for Synapse Agent

This script showcases the performance tracking capabilities of the Synapse agent
by running multiple scenarios and generating comparative metrics.
"""

import sys
import os
import json
import time
from datetime import datetime
from typing import Dict, List, Any

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from synapse import run_agent
from synapse.core.performance_tracker import PerformanceTracker


def run_performance_benchmark():
    """Run performance benchmarks across multiple scenarios."""
    
    print("🚀 SYNAPSE AGENT - PERFORMANCE BENCHMARK")
    print("=" * 60)
    print()
    
    # Test scenarios with varying complexity
    scenarios = [
        {
            "id": "simple",
            "type": "traffic",
            "problem": "Driver stuck in traffic, 20 minute delay expected"
        },
        {
            "id": "medium",
            "type": "2.4",
            "problem": "Driver at location but recipient not available for valuable package"
        },
        {
            "id": "complex",
            "type": "2.9",
            "problem": "Driver accepted booking 15 minutes ago but hasn't moved, not responding to messages"
        },
        {
            "id": "reflection",
            "type": "2.3",
            "problem": "Dispute at customer location, package damaged, customer refuses delivery"
        }
    ]
    
    results = []
    tracker = PerformanceTracker()
    
    for scenario in scenarios:
        print(f"📊 Running Scenario: {scenario['id'].upper()}")
        print(f"   Type: {scenario['type']}")
        print(f"   Problem: {scenario['problem'][:50]}...")
        print()
        
        start_time = time.time()
        
        # Run agent with performance tracking
        result = run_agent(
            scenario['problem'],
            scenario_type=scenario['type'],
            enable_performance_tracking=True
        )
        
        end_time = time.time()
        duration = end_time - start_time
        
        # Get metrics from the last query
        if tracker.query_history:
            query_metrics = tracker.query_history[-1]
            
            scenario_result = {
                "scenario_id": scenario['id'],
                "scenario_type": scenario['type'],
                "duration": duration,
                "steps": query_metrics.total_steps,
                "tools_used": len(query_metrics.tool_executions),
                "reflections": query_metrics.reflection_steps,
                "complexity_score": query_metrics.get_complexity_score(),
                "first_try_success": query_metrics.first_try_success,
                "estimated_cost": query_metrics.estimated_cost,
                "tokens_used": query_metrics.total_input_tokens + query_metrics.total_output_tokens,
                "time_saved": query_metrics.time_saved_by_parallelization,
                "success": result.get("done", False)
            }
            
            results.append(scenario_result)
            
            # Print summary
            print(f"   ✅ Completed in {duration:.2f}s")
            print(f"   📈 Complexity: {query_metrics.get_complexity_score()}/10")
            print(f"   💰 Cost: ${query_metrics.estimated_cost:.4f}")
            print(f"   ⚡ Time Saved: {query_metrics.time_saved_by_parallelization:.2f}s")
            print()
        
        # Small delay between scenarios
        time.sleep(1)
    
    # Print comparative analysis
    print("\n" + "=" * 60)
    print("📊 COMPARATIVE PERFORMANCE ANALYSIS")
    print("=" * 60)
    print()
    
    # Create comparison table
    print("| Scenario | Duration | Steps | Tools | Reflections | Cost    | Complexity |")
    print("|----------|----------|-------|-------|-------------|---------|------------|")
    
    for r in results:
        print(f"| {r['scenario_id']:<8} | {r['duration']:>7.2f}s | {r['steps']:>5} | {r['tools_used']:>5} | "
              f"{r['reflections']:>11} | ${r['estimated_cost']:>6.4f} | {r['complexity_score']:>10}/10 |")
    
    print()
    
    # Calculate aggregates
    avg_duration = sum(r['duration'] for r in results) / len(results)
    avg_cost = sum(r['estimated_cost'] for r in results) / len(results)
    total_tokens = sum(r['tokens_used'] for r in results)
    reflection_rate = sum(1 for r in results if r['reflections'] > 0) / len(results) * 100
    
    print("📈 AGGREGATE METRICS:")
    print(f"  • Average Duration: {avg_duration:.2f}s")
    print(f"  • Average Cost: ${avg_cost:.4f}")
    print(f"  • Total Tokens Used: {total_tokens:,}")
    print(f"  • Reflection Rate: {reflection_rate:.0f}%")
    print(f"  • Success Rate: {sum(1 for r in results if r['success']) / len(results) * 100:.0f}%")
    
    # Export detailed results
    export_data = {
        "timestamp": datetime.now().isoformat(),
        "scenarios": results,
        "aggregate_stats": tracker.get_aggregate_stats(),
        "tool_performance": tracker.get_tool_performance()
    }
    
    filename = f"benchmark_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(filename, 'w') as f:
        json.dump(export_data, f, indent=2, default=str)
    
    print(f"\n📁 Detailed results exported to: {filename}")
    print("\n✅ Performance benchmark completed!")


if __name__ == "__main__":
    try:
        run_performance_benchmark()
    except KeyboardInterrupt:
        print("\n\n⏸️ Benchmark interrupted by user.")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error during benchmark: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)