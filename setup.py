from setuptools import setup, find_packages

setup(
    name="ai-memory-engine",
    version="0.1.0",
    description="Universal AI Coding Memory Engine — reduce AI token usage by 90-98%",
    packages=find_packages(),
    install_requires=[
        "typer>=0.12.0",
        "rich>=13.0.0",
        "networkx>=3.0",
        "watchdog>=4.0.0",
    ],
    entry_points={
        "console_scripts": [
            "memory=cli.main:app",
        ],
    },
    python_requires=">=3.11",
)
