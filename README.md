<<<<<<< Updated upstream
# Project-Synapse

Quick start
- Create a virtual environment and install deps from `requirements.txt`.
- Add a `.env` file with your API keys.

Environment variables
- GROQ_API_KEY: Required to initialize the Groq LLM via LangChain's ChatGroq.

LLM
- This project initializes a Groq LLM client in `src/agent.py`:
	- llm = ChatGroq(model_name="openai/gpt-oss-120b")
	- If the package or key is missing, the code safely leaves `llm` as None.

=======
# Synapse Agent

Autonomous logistics coordination agent with adaptive problem-solving capabilities.

## Installation

```bash
pip install -e .
```

## Usage

```bash
# Direct problem
python main.py "Driver stuck in traffic for 45 minutes"

# Predefined scenario
python main.py --scenario 2.4

# List scenarios
python main.py --list
```

## Scenarios

- **1.0**: Restaurant overloaded
- **2.0**: Package damaged, dispute
- **2.2**: Item out of stock
- **2.3**: Driver at door dispute
- **2.4**: Recipient unavailable
- **traffic**: Traffic delay
- **merchant**: Equipment broken
- **weather**: Severe weather

## Options

- `-v, --verbose`: Detailed output
- `-q, --quiet`: Minimal output
- `-s, --scenario`: Use predefined scenario
- `-l, --list`: List all scenarios

## License

MIT
>>>>>>> Stashed changes
