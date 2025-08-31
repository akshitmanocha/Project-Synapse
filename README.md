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

