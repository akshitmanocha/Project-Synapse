# Executive Mode Performance Example

## Running a Scenario with Executive Mode

```bash
$ python main.py --scenario 2.9 --executive
```

## Sample Output

```
🚀 ============================================================ 🚀
    SYNAPSE AGENT - Autonomous Logistics Coordination
    Advanced Problem-Solving with Reflection & Adaptation
🚀 ============================================================ 🚀

🎯 Using scenario '2.9': Driver has accepted a booking but is not moving or responding

[Live Dashboard Updates During Execution - Shows Real-Time Metrics]

======================================================================
📊 EXECUTIVE PERFORMANCE SUMMARY
======================================================================

📈 Query Metrics:
  • Total Duration: 3.42 seconds
  • Steps Executed: 5
  • Tools Used: 4
  • Reflections: 1

⚡ Efficiency Analysis:
  • Parallel Executions: 2
  • Time Saved: 1.8s
  • Complexity Score: 6/10
  • First-Try Success: No (Reflection Used)

💰 Cost Analysis:
  • Total Tokens: 2,847
  • Estimated Cost: $0.0012
  • LLM Calls: 5
  • Avg Response Time: 0.68s

🔧 Tool Execution Breakdown:
  ✅ get_driver_status: 0.42s
  ✅ notify_customer: 0.38s
  ✅ find_replacement_driver: 1.20s
  ✅ cancel_booking: 0.55s

📁 Detailed metrics exported to: metrics_a3b4c5d6.json

🎯 FINAL RESOLUTION:
Unresponsive driver replaced. Customer notified, new driver assigned with
updated ETA. Original booking cancelled and flagged for review.

✅ Agent successfully resolved the unresponsive driver situation!
```

## What Each Metric Means

### 📈 Query Metrics
- **Total Duration**: End-to-end execution time
- **Steps Executed**: Number of reasoning + action steps
- **Tools Used**: Distinct tools called during resolution
- **Reflections**: Times the agent self-corrected

### ⚡ Efficiency Analysis
- **Parallel Executions**: Groups of tools run simultaneously
- **Time Saved**: Seconds saved by parallel execution vs sequential
- **Complexity Score**: 1-10 rating of problem difficulty
- **First-Try Success**: Whether reflection was needed

### 💰 Cost Analysis
- **Total Tokens**: Input + output tokens to LLM
- **Estimated Cost**: Actual API cost in USD
- **LLM Calls**: Number of calls to Gemini
- **Avg Response Time**: Average LLM response latency

### 🔧 Tool Execution Breakdown
Shows each tool's execution status and duration, helping identify:
- Which tools are slowest (bottlenecks)
- Which tools fail most often
- Opportunities for parallelization

## Benefits for Demonstrations

1. **Professional Presentation**: Executive-friendly metrics at a glance
2. **Cost Transparency**: Shows actual operational costs
3. **Performance Proof**: Demonstrates sub-4-second resolution times
4. **Intelligence Showcase**: Reflection metrics show adaptive AI
5. **Optimization Insights**: Identifies areas for improvement

## Comparing Modes

### Standard Mode
```bash
$ python main.py --scenario 2.9
```
Shows: Chain of thought, actions taken, final resolution

### Verbose Mode
```bash
$ python main.py --scenario 2.9 --verbose
```
Shows: All tool parameters, detailed observations, debugging info

### Executive Mode
```bash
$ python main.py --scenario 2.9 --executive
```
Shows: Performance metrics, cost analysis, efficiency stats, tool timeline

### Quiet Mode
```bash
$ python main.py --scenario 2.9 --quiet
```
Shows: Only the final resolution plan

## JSON Metrics Export

The executive mode automatically exports detailed metrics to a JSON file:

```json
{
  "timestamp": "2025-09-02T20:15:30",
  "aggregate_stats": {
    "total_queries": 1,
    "success_rate": 100.0,
    "avg_resolution_time": 3.42,
    "avg_steps_to_resolution": 5,
    "reflection_trigger_rate": 20.0,
    "most_used_tools": [
      ["notify_customer", 2],
      ["get_driver_status", 1],
      ["find_replacement_driver", 1],
      ["cancel_booking", 1]
    ],
    "total_cost": 0.0012,
    "avg_complexity": 6
  },
  "tool_performance": {
    "get_driver_status": {
      "usage_count": 1,
      "success_rate": 100.0,
      "avg_duration": 0.42
    },
    "notify_customer": {
      "usage_count": 2,
      "success_rate": 100.0,
      "avg_duration": 0.38
    },
    "find_replacement_driver": {
      "usage_count": 1,
      "success_rate": 0.0,
      "avg_duration": 1.20
    },
    "cancel_booking": {
      "usage_count": 1,
      "success_rate": 100.0,
      "avg_duration": 0.55
    }
  },
  "query_history": [
    {
      "query_id": "a3b4c5d6",
      "scenario_type": "2.9",
      "total_duration": 3.42,
      "total_steps": 5,
      "tool_executions": [...],
      "reflection_events": [...],
      "complexity_score": 6,
      "resolution_achieved": true
    }
  ]
}
```

## Use Cases

1. **Executive Presentations**: Show ROI and efficiency metrics
2. **Performance Benchmarking**: Compare different scenarios
3. **Cost Optimization**: Track and reduce API costs
4. **System Monitoring**: Real-time performance tracking
5. **Quality Assurance**: Ensure consistent resolution times
6. **Competitive Analysis**: Demonstrate superior performance