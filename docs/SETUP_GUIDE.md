# 🚀 Project Synapse - Complete Setup Guide

This guide ensures successful installation and setup of Project Synapse on any system from scratch.

## 📋 Prerequisites

### System Requirements
- **Python**: 3.8 or higher (3.9+ recommended)
- **Operating System**: Windows, macOS, or Linux
- **Memory**: Minimum 2GB RAM available
- **Network**: Internet connection for API calls

### API Requirements
- **Google Gemini API Key**: Required for LLM functionality
  - Get your free API key from: https://makersuite.google.com/app/apikey
  - Free tier includes 50 requests per day

## 🛠️ Installation Steps

### 1. Clone the Repository
```bash
git clone <your-repository-url>
cd Project-Synapse
```

### 2. Create Virtual Environment (Recommended)
```bash
# Using venv (built-in)
python -m venv .venv

# Activate virtual environment
# On Windows:
.venv\Scripts\activate
# On macOS/Linux:
source .venv/bin/activate
```

### 3. Install Dependencies
```bash
# Install all required packages
pip install -r requirements.txt

# Alternative: Install in development mode
pip install -e .
```

### 4. Environment Configuration
```bash
# Copy the environment template
cp .env.template .env

# Edit .env file with your API key
# Replace 'your_gemini_api_key_here' with your actual Gemini API key
```

**Example .env file:**
```bash
GEMINI_API_KEY=AIzaSyBcDeFgHiJkLmNoPqRsTuVwXyZ1234567890
DEBUG=false
MAX_AGENT_STEPS=20
MAX_REFLECTIONS=5
LLM_TIMEOUT=30
```

### 5. Verify Installation
```bash
# Test basic functionality
python main.py --debug-tools

# Test a simple scenario
python main.py --scenario traffic

# Run all component tests
python synapse/agent/agent.py --debug --verbose
```

## 🧪 Testing the Setup

### Quick Validation Tests
```bash
# 1. Check all scenarios are available
python main.py --list-scenarios

# 2. Test a lightweight scenario
python main.py "Check traffic status on route 101"

# 3. Verify tool integration
python main.py --debug-tools

# 4. Run comprehensive agent debug
python -m synapse.agent --debug
```

### Expected Outputs
- ✅ **Scenario list**: Should show 13 scenarios (1.0, 2.0, 2.2-2.9, traffic, merchant, weather)
- ✅ **Tool debug**: Should show "6/6 tests passed"  
- ✅ **Agent debug**: Should show "All tests passed! Agent is working correctly."

## 🚨 Common Issues and Solutions

### 1. Import Errors
**Issue**: `ModuleNotFoundError: No module named 'synapse'`

**Solutions**:
```bash
# Ensure you're in the project root directory
pwd  # Should end with /Project-Synapse

# Install in development mode
pip install -e .

# Or add to Python path temporarily
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
```

### 2. API Key Issues
**Issue**: `RuntimeError: GEMINI_API_KEY not set in environment`

**Solutions**:
```bash
# Check if .env file exists
ls -la .env

# Verify API key is set (should show key without quotes)
grep GEMINI_API_KEY .env

# Test API key manually
python -c "import os; from dotenv import load_dotenv; load_dotenv(); print(f'API Key loaded: {bool(os.getenv(\"GEMINI_API_KEY\"))}')"
```

### 3. Missing Dependencies
**Issue**: Various import errors for langchain, langgraph, etc.

**Solutions**:
```bash
# Update pip first
pip install --upgrade pip

# Reinstall requirements
pip install -r requirements.txt --force-reinstall

# Check for version conflicts
pip list | grep lang
```

### 4. Permission Issues
**Issue**: Permission denied when running scripts

**Solutions**:
```bash
# Make main.py executable
chmod +x main.py

# Or run with python explicitly
python main.py --help
```

### 5. Rate Limiting
**Issue**: `ResourceExhausted: 429 You exceeded your current quota`

**Solutions**:
- Wait a few minutes between tests (free tier has daily limits)
- Consider upgrading to paid Gemini API tier for production use
- Use shorter test scenarios to conserve quota

## 🔧 Development Setup

### Additional Development Dependencies
```bash
# Install development tools
pip install pytest pytest-cov black flake8 mypy

# Or use extras from setup.py
pip install -e ".[dev]"
```

### Running Tests
```bash
# Run unit tests
python -m pytest tests/unit/ -v

# Run integration tests  
python -m pytest tests/integration/ -v

# Run specific scenario tests
python -m pytest tests/scenarios/ -v

# Run with coverage
python -m pytest --cov=synapse tests/
```

### Code Quality Tools
```bash
# Format code
black synapse/ tests/

# Lint code
flake8 synapse/

# Type checking
mypy synapse/
```

## 📁 Critical Files and Structure

### Required Files
```
Project-Synapse/
├── .env                          # Your API keys (DO NOT COMMIT)
├── .env.template                 # Template for environment setup
├── requirements.txt              # Python dependencies
├── setup.py                     # Package installation config
├── main.py                      # Main CLI entry point
├── synapse/
│   ├── __init__.py              # Package initialization
│   ├── agent/
│   │   ├── __init__.py          # Agent module init
│   │   └── agent.py             # Core agent implementation
│   ├── tools/
│   │   ├── __init__.py          # Tools module init
│   │   └── tools.py             # Logistics tool implementations
│   ├── prompts/
│   │   └── system_prompt.txt    # LLM system instructions
│   └── cli.py                   # Command-line interface
└── tests/                       # Test suite
    └── scenarios/               # Scenario-specific tests
```

### Files That Can Be Missing (Will Auto-Generate)
- `*.pyc` files
- `__pycache__/` directories  
- `.pytest_cache/`
- `build/` and `dist/` directories

## 🚀 Production Deployment

### Environment Variables for Production
```bash
# Production .env example
GEMINI_API_KEY=your_production_api_key
DEBUG=false
MAX_AGENT_STEPS=25
MAX_REFLECTIONS=5
LLM_TIMEOUT=60
```

### Docker Setup (Optional)
```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
RUN pip install -e .

ENV PYTHONPATH=/app
CMD ["python", "main.py", "--help"]
```

## 📞 Getting Help

### Debug Commands
```bash
# Full system diagnostic
python synapse/agent/agent.py --debug --verbose

# Component-by-component testing
python synapse/agent/agent.py --debug-components
python synapse/agent/agent.py --debug-llm  
python synapse/agent/agent.py --debug-simple
```

### Common Debug Information to Collect
1. **Python version**: `python --version`
2. **Package versions**: `pip list | grep -E "(langchain|langgraph|google)"`
3. **Environment check**: `python -c "import os; print(os.getenv('GEMINI_API_KEY', 'NOT SET')[:10])"`
4. **Import test**: `python -c "from synapse import run_agent; print('Success')"`

### Success Indicators
- ✅ All imports work without errors
- ✅ `main.py --list-scenarios` shows 13 scenarios
- ✅ `main.py --debug-tools` shows "6/6 tests passed"
- ✅ Simple agent run completes with a final plan
- ✅ No missing file errors in logs

---

## 🎯 Ready to Use!

Once all validation tests pass, your Project Synapse installation is complete and ready for:
- **Scenario testing**: `python main.py --scenario 2.4`
- **Custom problems**: `python main.py "Your logistics problem here"`
- **Development**: Add new scenarios, tools, or modify agent behavior

**🏆 Your autonomous logistics coordination system is now operational!**