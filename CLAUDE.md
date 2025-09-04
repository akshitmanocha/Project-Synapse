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

# Debug available tools
python main.py --debug-tools

# Check API quota before running
python check_api_quota.py

```

### Testing
```bash
# Quick validation (no API calls required)
python validate_installation.py

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

### Performance Scripts
```bash
# Performance benchmark across scenarios
python demo_performance.py

# Agent component debugging
python synapse/agent/agent.py --debug --verbose
```

### Environment Variables
Required in `.env` file (copy from `.env.template`):
- `GEMINI_API_KEY` - Required for Google Gemini LLM operations
- `DEBUG=false` - Enable debug logging  
- `MAX_AGENT_STEPS=20` - Max reasoning steps before termination
- `MAX_REFLECTIONS=5` - Max reflection cycles per problem
- `LLM_TIMEOUT=30` - LLM timeout in seconds

## Architecture Overview

### Core Agent System (LangGraph StateGraph)

The agent uses **LangGraph StateGraph** with three main nodes:

1. **Reasoning Node** (`synapse/agent/agent.py:reasoning_node`)
   - Analyzes logistics problems using Google Gemini LLM
   - Selects optimal tool actions from structured system prompts
   - Parses LLM responses to extract tool calls and reasoning

2. **Tool Execution Node** (`synapse/agent/agent.py:tool_exec_node`) 
   - Executes specialized logistics tools from the registry
   - Captures results and integrates with performance tracking
   - Handles tool failures with comprehensive error information

3. **Reflection Node** (`synapse/agent/agent.py:reflection_node`)
   - Detects failures and suboptimal outcomes automatically
   - Implements intelligent escalation chains for robust recovery
   - Prevents infinite loops while suggesting alternative approaches

### State Management
**AgentState** flows between nodes with key fields:
- `input`: User's problem description
- `steps`: Chronological audit log of all reasoning/actions/observations
- `plan`: Final resolution plan when agent completes
- `action`/`observation`: Current execution context
- `needs_adaptation`: Triggers reflection system when tools fail
- `reflection_reason`/`suggested_alternative`: Adaptive recovery state

### Tool Ecosystem (`synapse/tools/tools.py`)

**40+ specialized logistics tools** across categories:
- **Traffic & Routing**: Real-time traffic analysis, dynamic re-routing
- **Merchant Operations**: Status checks, contact, nearby alternatives
- **Customer Communication**: Multi-channel notifications, recipient contact
- **Evidence & Disputes**: Evidence collection, AI-powered fault analysis
- **Delivery Management**: Safe drop-off, locker search, redelivery scheduling
- **Refund Processing**: Instant/partial refunds, substitute recommendations
- **Human Intervention**: Live support escalation, management oversight, emergency protocols

Each tool returns structured responses with status indicators, rich contextual data, and realistic failure modes for agent training.

### Performance & Executive Systems (`synapse/core/`)

**PerformanceTracker**: Singleton metrics collection system tracking LLM calls, tool executions, reflection events, complexity scores, and cost estimates with JSON export capability.

**ExecutiveDisplay**: Real-time Rich terminal dashboard providing live agent execution metrics, tool timeline visualization, and performance analysis during runs.

## Key Implementation Details

### Agent Workflow Control
- **Conditional routing** between nodes based on agent state
- **Recursive execution** until problem resolution (max steps configurable via MAX_AGENT_STEPS)
- **Graceful termination** via `done` flag or step limits

### Error Recovery Strategy
Built-in escalation chains for robust problem resolution:
- **Contact failure**: Safe drop-off → Locker → Redelivery → Sender contact
- **Dispute resolution**: Evidence analysis → Partial refund → Full refund
- **Traffic delays**: Re-routing → Customer notification → Time adjustment

### LLM Integration
- **Google Gemini 1.5 Flash** via `langchain_google_genai`
- **System prompts** located in `synapse/prompts/system_prompt.txt`
- **JSON parsing** for structured tool call extraction
- **Timeout handling** and retry logic (configurable via LLM_TIMEOUT)

### CLI Interface (`main.py`)
Four display modes for different use cases:
- **Standard**: Chain of thought + final resolution
- **Verbose** (`--verbose`): Detailed tool parameters and observations  
- **Quiet** (`--quiet`): Final resolution only
- **Executive** (`--executive`): Real-time performance metrics dashboard

### Module Organization
```
synapse/
├── agent/          # Core LangGraph agent (agent.py)
├── tools/          # 40+ specialized logistics tools (tools.py)
├── core/           # Performance tracking and executive display
├── prompts/        # LLM system prompts (system_prompt.txt)
└── utils/          # Utility functions
```

## Predefined Scenarios
23 test scenarios accessible via `--scenario` flag:
- **Basic scenarios** (1.0, traffic, merchant, weather): Simple logistics issues
- **Progressive complexity** (2.0-2.9): Multi-step resolution chains
- **Authorization scenarios** (approval.1-5): Financial/management approval workflows  
- **Human escalation** (human.1-5): Critical situations requiring human intervention

Access scenarios via `python main.py --scenario <ID>` or `get_predefined_scenarios()` in code.

## Development Notes

### Adding New Tools
1. Add tool function to `synapse/tools/tools.py`
2. Create adapter function in `synapse/agent/agent.py` (see existing `adapt_*` functions)
3. Register in `_tool_registry()` return dictionary
4. Test with `python synapse/agent/agent.py --debug-components` to verify registration

### Modifying Reflection Logic
- Failure detection patterns in `synapse/agent/agent.py:reflection_node()` 
- Escalation chains defined in reflection system (lines 822-870)
- Agent state fields: `needs_adaptation`, `reflection_reason`, `suggested_alternative`
- **Important**: Ensure all referenced tools exist in registry to prevent recursion errors

### Environment Configuration
All limits are configurable via environment variables in `.env` file:
- `MAX_AGENT_STEPS=15` - Maximum reasoning steps before termination
- `MAX_REFLECTIONS=3` - Maximum reflection cycles per problem  
- `LLM_TIMEOUT=30` - LLM request timeout in seconds
- `GEMINI_API_KEY` - Required for Google Gemini LLM operations

### Troubleshooting Common Issues
**Recursion Limit Errors**:
- Check `MAX_AGENT_STEPS` and `MAX_REFLECTIONS` in `.env`
- Ensure routing functions don't modify state
- Verify all tools referenced in reflection system exist

**Missing Tool Errors**:
- Tool exists in `tools.py` but not in `_tool_registry()`? Add adapter function
- Check tool registry with: `python synapse/agent/agent.py --debug-components`

**API Rate Limits**:
- Agent handles gracefully with timeouts
- Adjust `LLM_TIMEOUT` for slower connections
- Monitor with executive mode: `python main.py --scenario X --executive`

### Performance Optimization  
- **State immutability**: AgentState.steps is append-only audit log
- **Executive mode** provides detailed metrics for analysis and cost tracking
- **Configurable limits** prevent runaway executions
- **Graceful degradation** with comprehensive error handling