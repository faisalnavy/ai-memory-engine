"""Context Builder — assembles the final context string sent to AI models."""
from models.memory_types import ContextPackage


def build_context_string(pkg: ContextPackage) -> str:
    """Return the full formatted context package as a Markdown string."""
    return pkg.as_markdown()


def build_system_prompt_prefix(pkg: ContextPackage) -> str:
    """Return a system prompt prefix that injects memory context."""
    context = pkg.as_markdown()
    return f"""You are working on a codebase. Here is the relevant project memory:

{context}

Use this memory to answer accurately. Do not repeat information already shown above.
---
"""


def savings_report(pkg: ContextPackage) -> dict:
    if pkg.original_token_estimate <= 0:
        return {"savings_pct": 0, "original": 0, "optimized": pkg.token_estimate}
    savings = 1 - (pkg.token_estimate / pkg.original_token_estimate)
    return {
        "original": pkg.original_token_estimate,
        "optimized": pkg.token_estimate,
        "savings_pct": round(savings * 100, 1),
    }
