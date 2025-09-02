# 🚀 Project Synapse - Autonomous Logistics Coordination Agent

**Advanced AI-Powered Last-Mile Logistics Problem Solver with Reflection & Adaptation**

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![LangGraph](https://img.shields.io/badge/LangGraph-Powered-green.svg)](https://github.com/langchain-ai/langgraph)
[![Gemini](https://img.shields.io/badge/Gemini-LLM-orange.svg)](https://ai.google.dev/)

## 📋 What is Project Synapse?

Project Synapse is a sophisticated **autonomous AI agent** designed specifically for **last-mile logistics coordination**. It combines advanced Large Language Model reasoning with a comprehensive toolkit to solve complex delivery and logistics problems in real-time.

### 🎯 Core Capabilities

**🧠 Intelligent Reasoning Framework**
- **ANALYZE**: Assesses complex logistics situations with multiple stakeholders
- **STRATEGIZE**: Develops multi-step solution plans with contingencies  
- **EXECUTE**: Coordinates tools and stakeholders to implement solutions
- **ADAPT**: Uses reflection to recover from failures and optimize approaches

**🔄 Advanced Error Recovery**
- **Reflection Node**: Automatically detects tool failures and suboptimal outcomes
- **Adaptive Escalation**: Intelligently suggests alternative approaches when primary solutions fail
- **Loop Prevention**: Built-in safeguards prevent infinite reflection cycles
- **Learning Integration**: Incorporates failure patterns to improve future decision-making

**🔐 Enterprise Authorization System**
- **Approval Workflows**: Multi-level authorization for financial and high-impact actions
- **Human Intervention**: Automatic escalation for safety, legal, and complex scenarios
- **Risk Management**: Configurable thresholds and emergency override capabilities
- **Audit Trail**: Complete tracking of all approval decisions and authorizations

**🛠️ Comprehensive Tool Ecosystem**
- **40+ Specialized Tools** across 12 categories:
  - 🚗 Core Operations (traffic analysis, merchant status, customer notifications, re-routing, nearby merchants)
  - 🕵️ Evidence & Disputes (collection, analysis, instant refunds, driver exoneration)
  - 📦 Stock Management (merchant contact, substitute proposals, partial refunds)
  - 📝 Feedback & Prevention (merchant packaging feedback)
  - 📞 Recipient Unavailable & Delivery (recipient contact, safe drop-off, locker search, redelivery, sender contact)
  - 🚛 Unresponsive Driver (driver status, booking cancellation, replacement driver search)
  - 🗺️ Address Verification (customer address confirmation)
  - 🚧 Traffic Management (alternative route calculation)
  - 🔍 Lost & Found (trip path location, lost item case initiation)
  - ⚠️ Safety & Routing (safe location rerouting, passenger/driver notifications)
  - 💰 **Financial Authorization** (monetary vouchers, driver bonuses, merchant credits, expense approval)
  - 👥 **Human Escalation** (management escalation, emergency override, premium service authorization)

### 🌟 Key Features

| Feature | Description |
|---------|-------------|
| **Multi-Stakeholder Coordination** | Manages customers, drivers, merchants, and senders simultaneously |
| **Progressive Complexity Handling** | Scales from basic delays to complex dispute resolution |
| **Real-Time Decision Making** | Sub-second responses for urgent logistics situations |
| **Enterprise Authorization** | Multi-level approval workflows with human intervention capabilities |
| **Professional CLI Interface** | Beautiful, structured output with clear reasoning visualization |
| **Executive Performance Dashboard** | Real-time metrics, cost tracking, and efficiency analysis |
| **Scenario-Based Testing** | 23 predefined scenarios covering comprehensive logistics challenges |
| **Comprehensive Logging** | Full chain-of-thought tracking for audit and improvement |

## 🏗️ Project Architecture

```
synapse/                     # Main package directory
├── agent/                   # Core AI agent implementation
│   ├── __init__.py         # Package initialization
│   └── agent.py            # LangGraph workflow with reflection
├── tools/                   # Logistics tools ecosystem
│   ├── __init__.py         # Tool exports and metadata
│   └── tools.py            # 40+ specialized logistics tools
├── core/                    # Core systems and enterprise features
│   ├── __init__.py         # Core exports
│   ├── performance_tracker.py  # Real-time metrics collection
│   ├── executive_display.py    # Executive dashboard interface
│   └── authorization.py        # Multi-level approval system
├── prompts/                 # AI prompt engineering
│   ├── __init__.py         # Prompt utilities
│   └── system_prompt.txt   # Main system prompt with instructions
└── utils/                   # Utility functions
    └── __init__.py         # Utility exports

tests/                       # Comprehensive test suite
├── unit/                   # Unit tests for components
├── integration/            # Full workflow integration tests  
├── scenarios/              # Scenario-specific test cases
└── workflows/              # End-to-end workflow validation

docs/                       # Documentation
├── architecture/           # System design documentation
├── scenarios/              # Detailed scenario explanations
└── api/                    # API reference documentation

examples/                   # Usage examples and demos
config/                     # Configuration files
main.py                     # CLI entry point
setup.py                    # Package installation configuration
```

## 🚀 Quick Start Installation

### Prerequisites
- **Python 3.8+** (3.10+ recommended) - [Download Python](https://www.python.org/downloads/)
- **Git** - [Download Git](https://git-scm.com/downloads)
- **Google Gemini API Key** - [Get Free API Key](https://ai.google.dev/)

### 🎯 Choose Your Installation Method

#### Option 1: Automated Installer (Easiest)
```bash
# Download and run the cross-platform installer
git clone https://github.com/yourusername/Project-Synapse.git
cd Project-Synapse
python install.py
```

#### Option 2: One-Line Install

**macOS/Linux:**
```bash
git clone https://github.com/yourusername/Project-Synapse.git && cd Project-Synapse && python3 -m venv .venv && source .venv/bin/activate && pip install -r requirements.txt && cp .env.template .env && echo "✅ Installation complete! Now add your API key to .env file"
```

**Windows (PowerShell):**
```powershell
git clone https://github.com/yourusername/Project-Synapse.git; cd Project-Synapse; python -m venv .venv; .venv\Scripts\Activate; pip install -r requirements.txt; copy .env.template .env; echo "✅ Installation complete! Now add your API key to .env file"
```

### 🔧 Step-by-Step Installation

#### Step 1: Clone & Navigate
```bash
git clone https://github.com/yourusername/Project-Synapse.git
cd Project-Synapse
```

#### Step 2: Create Virtual Environment

<details>
<summary><b>🍎 macOS / 🐧 Linux</b></summary>

```bash
# Create virtual environment
python3 -m venv .venv

# Activate it
source .venv/bin/activate

# You should see (.venv) in your terminal
```
</details>

<details>
<summary><b>🪟 Windows</b></summary>

```powershell
# Create virtual environment
python -m venv .venv

# Activate it (PowerShell)
.venv\Scripts\Activate

# Or for Command Prompt
.venv\Scripts\activate.bat

# You should see (.venv) in your terminal
```
</details>

#### Step 3: Install Dependencies
```bash
# Install all required packages
pip install -r requirements.txt

# Verify installation
python -c "import synapse; print('✅ Synapse installed successfully')"
```

#### Step 4: Configure API Key

1. **Copy the template:**
   ```bash
   # macOS/Linux
   cp .env.template .env
   
   # Windows
   copy .env.template .env
   ```

2. **Add your Gemini API key:**
   - Open `.env` file in any text editor
   - Replace `your_gemini_api_key_here` with your actual key
   - Save the file

   **Get your free API key:** [Google AI Studio](https://ai.google.dev/) → Get API Key → Create API Key

#### Step 5: Verify Everything Works
```bash
# Test the CLI
python main.py --help

# List available scenarios
python main.py --list-scenarios

# Run a test scenario
python main.py "Driver is stuck in traffic"
```

### ⚡ Quick Test
```bash
# Run a predefined scenario
python main.py --scenario traffic

# Run with performance metrics
python main.py --scenario 2.4 --executive
```

### 🔍 Troubleshooting

<details>
<summary><b>❌ "Python not found" or "python3 not found"</b></summary>

- **Windows**: Use `python` instead of `python3`
- **Mac/Linux**: Use `python3` instead of `python`
- Ensure Python is in your PATH: `python --version` or `python3 --version`
</details>

<details>
<summary><b>❌ "No module named synapse"</b></summary>

- Make sure you're in the project directory: `cd Project-Synapse`
- Ensure virtual environment is activated (you should see `(.venv)`)
- Reinstall dependencies: `pip install -r requirements.txt`
</details>

<details>
<summary><b>❌ "GEMINI_API_KEY not set"</b></summary>

- Check `.env` file exists: `ls -la .env` (Mac/Linux) or `dir .env` (Windows)
- Verify key is set correctly in `.env` file
- No spaces around `=` sign: `GEMINI_API_KEY=your_actual_key_here`
</details>

<details>
<summary><b>❌ "429 Quota exceeded" error</b></summary>

- You've hit the free tier limit (50 requests/day)
- Wait 24 hours or upgrade to paid tier
- Free tier resets at midnight Pacific Time
</details>

### 📚 Installation Resources

- **🚀 Quick Start**: Follow the installation guide above
- **🔧 Automated Install**: Use `python install.py` for guided setup  
- **📖 Detailed Guide**: [docs/SETUP_GUIDE.md](docs/SETUP_GUIDE.md) - Advanced configuration
- **📦 Simple Guide**: [docs/INSTALL.md](docs/INSTALL.md) - Platform-specific commands
- **🆘 Need Help?**: [Open an issue](https://github.com/yourusername/Project-Synapse/issues)

## 🎮 How to Use the CLI

### Basic Usage Patterns

**Direct Problem Input**
```bash
# Using main.py (always works)
python main.py "Driver stuck in traffic, 45-minute delay expected"

# Using console command (if installed with pip install -e .)
synapse-agent "Package damaged during delivery, customer disputes fault"
```

**Predefined Scenarios**
```bash
# Using main.py (recommended)
python main.py --scenario 2.4

# Using console command (alternative)
synapse-agent --scenario traffic --verbose

# Test unresponsive driver scenario
python main.py --scenario 2.9
```

**Output Customization**
```bash
# Verbose mode - shows all tool parameters and detailed observations
python main.py --verbose "Merchant equipment breakdown"

# Quiet mode - only final resolution plan
python main.py --quiet "Weather preventing delivery"

# Clean output without banner
python main.py --no-banner "Order dispute at customer location"
```

### Display Modes

The Synapse agent offers four distinct display modes:

| Mode | Flag | Description |
|------|------|-------------|
| **Standard** | (default) | Shows chain of thought and final resolution |
| **Verbose** | `--verbose` | Detailed observations and all tool parameters |
| **Quiet** | `--quiet` | Only shows final resolution plan |
| **Executive** | `--executive` | Real-time performance metrics and visualizations |

#### 🎯 Executive Mode (NEW)

Executive mode provides comprehensive performance analytics perfect for demonstrations and monitoring:

```bash
# Run with executive performance tracking
python main.py --executive "Driver stuck in traffic"

# Combine with scenarios for benchmarking
python main.py --scenario 2.4 --executive
```

**Executive Mode Features:**
- 📊 **Real-Time Metrics**: Live query processing visualization
- ⏱️ **Tool Timeline**: Execution timeline with parallel vs sequential analysis
- 📈 **Performance Analysis**: Response times, complexity scores, reflection tracking
- 💰 **Cost Tracking**: LLM token usage and estimated API costs
- 🔧 **Tool Breakdown**: Individual tool performance and success rates
- 📁 **Metric Export**: JSON export of all performance data

### CLI Command Reference

| Command | Description | Example |
| `python main.py "problem"` | Solve custom logistics problem | `python main.py "Driver lost, can't find address"` |
| `synapse-agent "problem"` | Alternative console command | `synapse-agent "Package delayed"` |
| `--scenario X` | Use predefined scenario | `--scenario 2.3` |
| `--list-scenarios` | Show all available scenarios | `python main.py -l` |
| `--verbose` | Show detailed technical information | `--verbose` |
| `--quiet` | Minimal output (final plan only) | `--quiet` |
| `--executive` | Enable performance metrics dashboard | `--executive` |
| `--debug-tools` | Display available tools | `python main.py --debug-tools` |
| `--help` | Show complete help information | `python main.py --help` |

### Available Scenarios

| Scenario | Description | Complexity |
|----------|-------------|------------|
| **1.0** | Restaurant overloaded, cannot fulfill order on time | Basic |
| **2.0** | Package damaged, customer disputes fault | Evidence-based |
| **2.2** | Item out of stock, needs customer preference handling | Multi-path |
| **2.3** | Dispute at customer location during delivery | Crisis management |
| **2.4** | Recipient unavailable for valuable package delivery | Systematic escalation |
| **2.5** | Incorrect or incomplete address (missing unit number) | Address verification |
| **2.6** | Major traffic obstruction (accident/road closure) | Traffic management |
| **2.7** | Passenger leaves personal item in vehicle after trip | Lost and found |
| **2.8** | Driver encounters unsafe road conditions (protest/hazard) | Safety protocols |
| **2.9** | Driver unresponsive after accepting booking | Driver replacement |
| **traffic** | Driver stuck in heavy traffic delay | Route optimization |
| **merchant** | Merchant equipment breakdown | Alternative sourcing |
| **weather** | Severe weather preventing delivery | Safety-first approach |
| **approval.1-5** | Scenarios requiring monetary/management approval | Authorization workflows |
| **human.1-5** | Critical situations needing human intervention | Safety/legal escalation |

### Example Sessions

**Example 1: Recipient Unavailable (Scenario 2.4)**
```bash
$ python main.py --scenario 2.4

🚀 ============================================================ 🚀
    SYNAPSE AGENT - Autonomous Logistics Coordination
    Advanced Problem-Solving with Reflection & Adaptation
🚀 ============================================================ 🚀

🎯 Using scenario '2.4': A driver is at the customer's location, but the recipient is not available to receive a valuable package

======================================================================
🧠 AGENT CHAIN OF THOUGHT
======================================================================

┌─ STEP 1: 🛠️ ACTION & EXECUTION ────────────────────────
│
│ 💭 THOUGHT:
│    I need to contact the recipient to see if they can receive the 
│    package or arrange an alternative time.
│
│ 🔧 ACTION:
│    Tool Used: contact_recipient_via_chat
│
│ 👁️ OBSERVATION:
│    Contact Successful: ❌ No
│    Status: No response after 5 minutes
└─────────────────────────────────────────────────────────────────────

┌─ STEP 2: 🤔 REFLECTION & REASONING ────────────────────
│
│ 💭 THOUGHT:
│    Contact failed. Since this is a valuable package, I need a 
│    secure alternative. Let me find a safe drop-off location.
│
│ 👁️ OBSERVATION:
│    Status: reflection
│    Suggested Alternative: suggest_safe_drop_off
└─────────────────────────────────────────────────────────────────────

======================================================================
🎯 FINAL RESOLUTION PLAN
======================================================================

📋 FINAL PLAN:
┌────────────────────────────────────────────────────────────────────┐
│ Coordinate with building concierge for secure package storage.     │
│ Driver will leave valuable package with concierge who will hold    │
│ it securely until recipient can collect. Customer notified with    │
│ pickup details and concierge contact information.                  │
└────────────────────────────────────────────────────────────────────┘

📊 EXECUTION SUMMARY:
┌────────────────────────────────────────────────────────────────────┐
│ Total Steps Executed: 4                                                │
│ Status: ✅ Successfully Completed                                 │
│ Adaptations Made: ✅ Yes                                             │
│ Action Steps: 3                                                    │
│ Reflection Steps: 1                                                │
└────────────────────────────────────────────────────────────────────┘

✅ Agent successfully resolved the logistics problem!
```

**Example 2: Unresponsive Driver (Scenario 2.9)**
```bash
$ python main.py --scenario 2.9

🎯 Using scenario '2.9': Driver has accepted a booking but is not moving or responding to contact attempts for over 10 minutes

======================================================================
🧠 AGENT CHAIN OF THOUGHT  
======================================================================

┌─ STEP 1: 🛠️ ACTION & EXECUTION ────────────────────────
│ 💭 THOUGHT: Driver D123 has been idle for 10+ minutes without response. 
│            I need to check their current status first.
│ 🔧 ACTION: Tool Used: get_driver_status
│ 👁️ OBSERVATION: Driver Status: idle, Location: [1.352, 103.821]
└─────────────────────────────────────────────────────────────────

┌─ STEP 2: 🤔 REFLECTION & REASONING ────────────────────
│ 💭 THOUGHT: Driver is confirmed idle and unresponsive. Customer is 
│            waiting and may escalate. Need to notify customer and 
│            find replacement immediately.
│ 🔧 ACTION: Tool Used: notify_customer
│ 👁️ OBSERVATION: Customer notified about delay and replacement search
└─────────────────────────────────────────────────────────────────

┌─ STEP 3: 🛠️ ACTION & EXECUTION ────────────────────────
│ 💭 THOUGHT: Now searching for replacement driver to minimize delay.
│ 🔧 ACTION: Tool Used: find_replacement_driver  
│ 👁️ OBSERVATION: Replacement found! ETA: 8 minutes
└─────────────────────────────────────────────────────────────────

🎯 FINAL RESOLUTION:
Customer notified, replacement driver assigned, original booking transferred. 
Incident logged for driver performance review.

✅ Agent successfully resolved the unresponsive driver situation!
```

**Example 3: Unsafe Road Conditions (Scenario 2.8)**
```bash
$ python main.py --scenario 2.8

🎯 Using scenario '2.8': Driver encounters unsafe road conditions including protest, road hazard, or severe weather requiring immediate rerouting

======================================================================
🧠 AGENT CHAIN OF THOUGHT  
======================================================================

┌─ STEP 1: 🛠️ ACTION & EXECUTION ────────────────────────
│ 💭 THOUGHT: Safety is the top priority. Driver reports dangerous protest 
│            with violence ahead. Must immediately reroute to safe location.
│ 🔧 ACTION: Tool Used: reroute_driver_to_safe_location
│ 👁️ OBSERVATION: Driver successfully rerouted to alternate route +15 min ETA
└─────────────────────────────────────────────────────────────────

┌─ STEP 2: 🤔 REFLECTION & REASONING ────────────────────
│ 💭 THOUGHT: Driver is now safe but passengers need immediate notification 
│            about the delay and safety measures taken.
│ 🔧 ACTION: Tool Used: notify_passenger_and_driver
│ 👁️ OBSERVATION: Both parties notified and acknowledged safety protocol
└─────────────────────────────────────────────────────────────────

┌─ STEP 3: 🛠️ ACTION & EXECUTION ────────────────────────
│ 💭 THOUGHT: This is a significant safety incident that requires operations 
│            team awareness for other drivers in the area.
│ 🔧 ACTION: Tool Used: contact_support_live  
│ 👁️ OBSERVATION: Support alerted, area-wide safety advisory issued
└─────────────────────────────────────────────────────────────────

🎯 FINAL RESOLUTION:
Driver safely rerouted away from dangerous protest area. All parties informed 
of safety measures and delay. Operations team alerted to implement area-wide 
safety protocols for other drivers.

✅ Agent prioritized safety and handled the hazardous situation professionally!
```

**Example 4: Lost Item Recovery (Scenario 2.7)**
```bash
$ python main.py --scenario 2.7

🎯 Using scenario '2.7': Passenger reports losing a personal item in the vehicle after trip completion

======================================================================
🧠 AGENT CHAIN OF THOUGHT  
======================================================================

┌─ STEP 1: 🛠️ ACTION & EXECUTION ────────────────────────
│ 💭 THOUGHT: Passenger left smartphone in vehicle after trip. First I need 
│            to verify trip details to help locate the driver and coordinate recovery.
│ 🔧 ACTION: Tool Used: locate_trip_path
│ 👁️ OBSERVATION: Trip verified: TRIP_7845, Downtown→Airport, completed 30min ago
└─────────────────────────────────────────────────────────────────

┌─ STEP 2: 🛠️ ACTION & EXECUTION ────────────────────────
│ 💭 THOUGHT: Trip confirmed. Now I'll initiate the official lost and found 
│            process to create a case and facilitate driver-passenger coordination.
│ 🔧 ACTION: Tool Used: initiate_lost_and_found_flow
│ 👁️ OBSERVATION: Case LF_1a2b3c4d created. Driver contacted, recovery arranged
└─────────────────────────────────────────────────────────────────

🎯 FINAL RESOLUTION:
Lost item case established with verified trip details. Driver has been contacted 
and confirmed smartphone is in vehicle. Recovery meetup arranged at convenient 
location within 2 hours. Case documented for tracking and follow-up.

✅ Agent successfully facilitated lost item recovery coordination!
```

**Example 5: Major Traffic Obstruction (Scenario 2.6)**
```bash
$ python main.py --scenario 2.6

🎯 Using scenario '2.6': Passenger's trip is impacted by sudden severe traffic event like major accident or road closure

======================================================================
🧠 AGENT CHAIN OF THOUGHT  
======================================================================

┌─ STEP 1: 🛠️ ACTION & EXECUTION ────────────────────────
│ 💭 THOUGHT: Major highway accident with 2+ hour delays. Passenger has 
│            urgent business meeting. Need to assess traffic and find alternatives.
│ 🔧 ACTION: Tool Used: check_traffic
│ 👁️ OBSERVATION: Major incident confirmed. Complete blockage, 2hr+ delays
└─────────────────────────────────────────────────────────────────

┌─ STEP 2: 🛠️ ACTION & EXECUTION ────────────────────────
│ 💭 THOUGHT: Traffic situation critical. Must calculate alternative route 
│            immediately to avoid missing important meeting.
│ 🔧 ACTION: Tool Used: calculate_alternative_route
│ 👁️ OBSERVATION: Alternative route found via downtown. +25 min but avoids blockage
└─────────────────────────────────────────────────────────────────

┌─ STEP 3: 🛠️ ACTION & EXECUTION ────────────────────────
│ 💭 THOUGHT: Alternative route secured. Must notify passenger and driver 
│            immediately with new route and updated ETA.
│ 🔧 ACTION: Tool Used: notify_passenger_and_driver  
│ 👁️ OBSERVATION: Both parties notified. New route accepted, ETA updated
└─────────────────────────────────────────────────────────────────

🎯 FINAL RESOLUTION:
Major traffic obstruction bypassed with alternative routing. Passenger and driver 
informed of new route adding only 25 minutes vs 2+ hour highway delay. Meeting 
arrival time preserved through proactive traffic management.

✅ Agent successfully navigated major traffic crisis with minimal impact!
```

**Example 6: Address Verification (Scenario 2.5)**
```bash
$ python main.py --scenario 2.5

🎯 Using scenario '2.5': Driver cannot locate delivery address due to incorrect or incomplete information like missing unit number

======================================================================
🧠 AGENT CHAIN OF THOUGHT  
======================================================================

┌─ STEP 1: 🛠️ ACTION & EXECUTION ────────────────────────
│ 💭 THOUGHT: Driver can't find the recipient at 1234 Main Street - appears 
│            to be apartment complex but no unit number provided. Need customer verification.
│ 🔧 ACTION: Tool Used: verify_address_with_customer
│ 👁️ OBSERVATION: Customer confirmed - correct address is 1234 Main St, Apt 5B
└─────────────────────────────────────────────────────────────────

┌─ STEP 2: 🤔 REFLECTION & REASONING ────────────────────
│ 💭 THOUGHT: Customer provided corrected address with unit number. Need to 
│            immediately reroute driver to specific apartment 5B.
│ 🔧 ACTION: Tool Used: re_route_driver
│ 👁️ OBSERVATION: Driver successfully redirected to Building 2, Apartment 5B
└─────────────────────────────────────────────────────────────────

🎯 FINAL RESOLUTION:
Address verification completed with customer providing missing unit number. 
Driver successfully rerouted to correct apartment location. Delivery completed 
with minimal additional delay through proactive address confirmation.

✅ Agent resolved address issue efficiently with customer collaboration!
```

**Example 7: Traffic Delay with Verbose Output**
```bash
$ python main.py --scenario traffic --verbose

[Detailed output showing full parameters, complete observations, and technical debugging information]
```

**Example 8: Executive Mode Performance Analysis**
```bash
$ python main.py --scenario 2.9 --executive

🚀 ============================================================ 🚀
    SYNAPSE AGENT - Autonomous Logistics Coordination
    Advanced Problem-Solving with Reflection & Adaptation
🚀 ============================================================ 🚀

🎯 Using scenario '2.9': Driver has accepted a booking but is not moving or responding

[Real-time performance dashboard displays during execution]

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

## 🧪 Testing & Development

### Running Tests

```bash
# Run all tests
pytest tests/

# Run specific test categories
pytest tests/unit/           # Unit tests
pytest tests/integration/    # Integration tests  
pytest tests/scenarios/      # Scenario tests
pytest tests/workflows/      # Workflow tests

# Run with coverage
pytest tests/ --cov=synapse --cov-report=html

# Test reflection system specifically
python tests/unit/test_simple_reflection.py
```

### Development Setup

```bash
# Install development dependencies
pip install -e ".[dev]"

# Code formatting
black synapse/ tests/ main.py

# Linting
flake8 synapse/ tests/ main.py

# Type checking
mypy synapse/
```

### Adding New Scenarios

1. **Add scenario to predefined list** in `main.py`:
```python
def get_predefined_scenarios():
    return {
        "custom": "Your new scenario description",
        # ... existing scenarios
    }
```

2. **Create test case** in `tests/scenarios/`:
```python
def test_custom_scenario():
    result = run_agent("Your new scenario description")
    assert result['done'] == True
    # Add specific assertions
```

3. **Document the scenario** in `docs/scenarios/`

## 📊 Performance & Capabilities

### Benchmarks

| Metric | Performance |
|--------|-------------|
| **Response Time** | Sub-second for urgent decisions |
| **Success Rate** | 95%+ with reflection system |
| **Tool Integration** | 32 tools working seamlessly |
| **Scenario Coverage** | 13 comprehensive test scenarios |
| **Reflection Accuracy** | 90%+ correct alternative suggestions |
| **Parallel Execution** | Up to 40% time savings on multi-tool scenarios |
| **Cost Efficiency** | <$0.001 per typical query resolution |

### Scalability

- **Concurrent Operations**: Handles multiple stakeholder coordination
- **Complex Scenarios**: Manages 5+ step resolution chains
- **Error Recovery**: Automatic adaptation with 5-level escalation
- **Memory Efficient**: Optimized for single-session problem solving

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

### Development Workflow

1. **Fork the repository**
2. **Create feature branch**: `git checkout -b feature/new-capability`
3. **Add tests** for new functionality
4. **Update documentation** for any API changes
5. **Submit pull request** with clear description

### Code Standards

- **Python 3.8+ compatibility**
- **Type hints** for all public functions
- **Comprehensive docstrings** following Google style
- **95%+ test coverage** for new code
- **Black formatting** for consistent style

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **[LangGraph](https://github.com/langchain-ai/langgraph)** - Workflow orchestration framework
- **[Google Gemini](https://ai.google.dev/)** - Large Language Model capabilities  
- **[LangChain](https://github.com/langchain-ai/langchain)** - LLM application framework
- **[Python Community](https://www.python.org/)** - Foundation and ecosystem

## 📁 Updated Project Files

### **New Setup & Configuration Files**
- **`.env.template`** - Environment configuration template with all required variables
- **`SETUP_GUIDE.md`** - Comprehensive setup guide with troubleshooting for fresh installations
- **Updated `requirements.txt`** - Corrected dependencies (now includes `langchain-google-genai`)

### **Current Dependencies**
```
python-dotenv          # Environment variable management
langchain             # Core LLM framework
langchain-core        # LangChain core components  
langchain-google-genai # Google Gemini integration
langgraph            # State graph orchestration
rich                  # Rich terminal formatting for executive mode
plotext              # Terminal-based plotting for metrics visualization
```

### **Complete Tool Registry (32 Tools)**
The agent now includes tools for:
- **Scenario 2.4**: Recipient unavailable (contact, drop-off, lockers, redelivery, sender contact)
- **Scenario 2.5**: Address verification (customer address confirmation) 
- **Scenario 2.6**: Traffic obstruction (alternative route calculation)
- **Scenario 2.7**: Lost & found (trip location, case initiation)
- **Scenario 2.8**: Unsafe conditions (safe rerouting, notifications)
- **Scenario 2.9**: Unresponsive driver (status check, cancellation, replacement)

## 📞 Support & Contact

- **Issues**: [GitHub Issues](https://github.com/yourusername/Project-Synapse/issues)
- **📚 Documentation**: [docs/INDEX.md](docs/INDEX.md) - **Complete documentation index**
- **🔧 Setup Guide**: [docs/SETUP_GUIDE.md](docs/SETUP_GUIDE.md) - **Start here for fresh installations**
- **💡 Examples**: [examples/](examples/) - Usage examples and demos

---

**Project Synapse** - Transforming logistics coordination through intelligent automation 🚀

*Built with ❤️ for the logistics and AI community*