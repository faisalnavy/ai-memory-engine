from dataclasses import dataclass, field
from typing import Any


@dataclass
class FunctionInfo:
    name: str
    file_path: str
    qualified_name: str = ""
    args: list[dict] = field(default_factory=list)
    return_type: str = ""
    callers: list[str] = field(default_factory=list)
    callees: list[str] = field(default_factory=list)
    decorators: list[str] = field(default_factory=list)
    is_async: bool = False
    is_public: bool = True
    docstring: str = ""
    summary: str = ""
    line_start: int = 0
    line_end: int = 0


@dataclass
class FileInfo:
    file_path: str
    purpose: str = ""
    public_apis: list[str] = field(default_factory=list)
    imports: list[str] = field(default_factory=list)
    exports: list[str] = field(default_factory=list)
    dependencies: list[str] = field(default_factory=list)
    risk_level: str = "low"
    file_hash: str = ""
    line_count: int = 0
    functions: list[FunctionInfo] = field(default_factory=list)


@dataclass
class ProjectDNA:
    project_path: str
    name: str = ""
    language: str = ""
    languages: list[str] = field(default_factory=list)
    framework: str = ""
    database: str = ""
    architecture: str = ""
    entry_points: list[str] = field(default_factory=list)
    key_services: list[str] = field(default_factory=list)
    coding_standards: dict = field(default_factory=dict)


@dataclass
class ContextPackage:
    query: str
    project_dna: dict = field(default_factory=dict)
    relevant_files: list[dict] = field(default_factory=list)
    relevant_functions: list[dict] = field(default_factory=list)
    recent_decisions: list[dict] = field(default_factory=list)
    compressed_memory: list[str] = field(default_factory=list)
    token_estimate: int = 0
    original_token_estimate: int = 0

    def as_markdown(self) -> str:
        parts = []

        if self.project_dna:
            dna = self.project_dna
            parts.append(f"## Project: {dna.get('name', 'Unknown')}")
            parts.append(f"- Language: {dna.get('language')} | Framework: {dna.get('framework')}")
            parts.append(f"- Architecture: {dna.get('architecture')}")
            parts.append("")

        if self.relevant_files:
            parts.append("## Relevant Files")
            for f in self.relevant_files:
                parts.append(f"### {f['file_path']}")
                parts.append(f"**Purpose:** {f.get('purpose', '')}")
                if f.get("public_apis"):
                    parts.append(f"**Exports:** {f['public_apis']}")
                parts.append("")

        if self.relevant_functions:
            parts.append("## Relevant Functions")
            for fn in self.relevant_functions:
                sig = f"`{fn['name']}({fn.get('args', '')})`"
                if fn.get("return_type"):
                    sig += f" → {fn['return_type']}"
                parts.append(f"- {sig}  \n  {fn.get('summary') or fn.get('docstring', '')[:120]}")
            parts.append("")

        if self.compressed_memory:
            parts.append("## Project Intelligence")
            for block in self.compressed_memory:
                parts.append(block)
            parts.append("")

        if self.recent_decisions:
            parts.append("## Recent Decisions")
            for d in self.recent_decisions:
                parts.append(f"- **{d['title']}**: {d['decision']}")
            parts.append("")

        return "\n".join(parts)
