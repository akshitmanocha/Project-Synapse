# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Development Commands

### Setup and Installation
```bash
# Quick installation
python install.py

# Manual setup
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.template .env  # Then add your GEMINI_API_KEY
```

### Running the Agent
```bash
# Basic usage
python main.py "problem description"

# Predefined scenarios  
python main.py --scenario 2.4

# Executive mode with performance metrics
python main.py --scenario traffic --executive

# List all scenarios
python main.py --list-scenarios

# Debug tools
python main.py --debug-tools
```

### Testing
```bash
# Run all tests
pytest tests/

# Run specific test categories
pytest tests/unit/           # Unit tests
pytest tests/integration/    # Integration tests
pytest tests/scenarios/      # Scenario tests
pytest tests/workflows/      # Workflow tests

# Run single test file
pytest tests/unit/test_simple_reflection.py

# Test with coverage
pytest tests/ --cov=synapse --cov-report=html
```

### Performance and Demo Scripts
```bash
# Performance benchmark across scenarios
python demo_performance.py

# Agent component debugging
python synapse/agent/agent.py --debug --verbose
```

### Environment Variables
Set in `.env` file (copy from `.env.template`):
- `GEMINI_API_KEY` - Required for LLM operations
- `DEBUG=true` - Enable debug logging  
- `MAX_AGENT_STEPS=20` - Max reasoning steps
- `MAX_REFLECTIONS=5` - Max reflection cycles
- `LLM_TIMEOUT=30` - LLM timeout in seconds

## Architecture Overview

### Core Agent System (ANALYZE → STRATEGIZE → EXECUTE → ADAPT)

The agent is built on **LangGraph StateGraph** with three main nodes:

1. **Reasoning Node** (`synapse/agent/agent.py:reasoning_node`)
   - Analyzes logistics problems and selects optimal tool actions
   - Uses Google Gemini LLM with structured system prompts
   - Parses LLM responses to extract tool calls and reasoning

2. **Tool Execution Node** (`synapse/agent/agent.py:tool_exec_node`) 
   - Executes selected logistics tools from the tool registry
   - Captures results and handles tool failures
   - Integrates with performance tracking system

3. **Reflection Node** (`synapse/agent/agent.py:reflection_node`)
   - Detects tool failures and suboptimal outcomes
   - Implements intelligent escalation chains
   - Suggests alternative approaches and prevents infinite loops

### State Management
**AgentState** (TypedDict) flows between nodes containing:
- `input`: User's problem description
- `steps`: Chronological audit log of reasoning/actions/observations
- `plan`: Final resolution when complete
- `action`/`observation`: Current execution context
- `needs_adaptation`/`reflection_reason`/`suggested_alternative`: Reflection system state

### Tool Ecosystem (`synapse/tools/tools.py`)

**32+ specialized logistics tools** organized by category:
- Traffic & routing (check_traffic, re_route_driver)
- Merchant operations (get_merchant_status, contact_merchant) 
- Customer communication (notify_customer, contact_recipient_via_chat)
- Evidence & disputes (collect_evidence, analyze_evidence)
- Delivery management (suggest_safe_drop_off, find_nearby_locker)
- Refund processing (issue_instant_refund, propose_substitute)

Tools return structured responses with:
- Status indicators (success/failure)
- Rich contextual data for agent reasoning
- Realistic failure modes for robust training

### Performance Tracking System (`synapse/core/`)

**PerformanceTracker** (`performance_tracker.py`):
- Singleton pattern for metrics collection
- Tracks LLM calls, tool executions, reflection events
- Calculates complexity scores, parallelization savings, cost estimates
- Exports detailed JSON metrics for analysis

**ExecutiveDisplay** (`executive_display.py`):
- Real-time dashboard using Rich terminal UI
- Live metrics during agent execution
- Tool timeline with parallel execution visualization
- Performance summaries and cost analysis

## Key Implementation Details

### Agent Workflow Control
- **Conditional routing** between nodes based on agent state
- **Recursive execution** until problem resolution (max 25 steps)
- **Graceful termination** via `done` flag or step limits

### Error Recovery Strategy
Escalation chains for common scenarios:
- Contact failure → Safe drop-off → Locker → Redelivery → Sender contact
- Evidence analysis → Partial refund → Full refund
- Traffic delays → Re-routing → Customer notification

### LLM Integration
- **Gemini 1.5 Flash** model via `langchain_google_genai`
- **Structured prompts** in `synapse/prompts/system_prompt.txt`
- **JSON parsing** of LLM responses for tool calls
- **Timeout handling** and retry logic for robustness

### CLI Interface (`main.py`)
Four display modes:
- **Standard**: Chain of thought + final resolution
- **Verbose**: Detailed tool parameters and observations
- **Quiet**: Final resolution only
- **Executive**: Real-time performance metrics dashboard

### Module Organization
```
synapse/
├── agent/          # Core LangGraph agent implementation
├── tools/          # 32+ specialized logistics tools
├── core/           # Performance tracking and executive display
├── prompts/        # LLM system prompts
└── utils/          # Utility functions
```

## Predefined Scenarios
13 test scenarios ranging from simple (traffic delays) to complex (multi-stakeholder disputes):
- **1.0**: Restaurant overloaded
- **2.0-2.9**: Progressive complexity scenarios  
- **traffic/merchant/weather**: Common situation handlers

Access via `--scenario` flag or `get_predefined_scenarios()` function.

## Performance Considerations
- **Sub-second** response times for urgent decisions
- **Parallel tool execution** where possible (tracked via ExecutiveDisplay)
- **Token optimization** in LLM calls (estimated costs in performance metrics)
- **Memory efficient** single-session problem solving
- **Graceful degradation** with comprehensive error handling

## Development Tips
- **State immutability**: AgentState steps are append-only audit log
- **Tool registry**: Add new tools via `_tool_registry()` function with parameter adapters
- **Reflection patterns**: Add new failure detection in `reflection_node()`
- **Executive mode**: Ideal for demos and performance analysis
- **Comprehensive logging**: Full chain-of-thought available in verbose modes