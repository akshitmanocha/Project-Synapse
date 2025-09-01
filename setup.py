from setuptools import setup, find_packages

setup(
    name="synapse-agent",
    version="1.0.0",
    description="Autonomous Logistics Coordination Agent",
    packages=find_packages(exclude=["tests*", "docs", "examples"]),
    python_requires=">=3.8",
    install_requires=[
        "langchain",
        "langgraph",
        "python-dotenv",
    ],
    entry_points={
        "console_scripts": [
            "synapse=main:main",
        ],
    },
)