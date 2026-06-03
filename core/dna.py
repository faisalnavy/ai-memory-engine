"""Project DNA Generator — detects language, framework, architecture."""
import json
import os
from pathlib import Path
from models.memory_types import ProjectDNA
from storage import db


FRAMEWORK_SIGNATURES = {
    # Python
    "fastapi": ("fastapi", "FastAPI"),
    "django": ("django", "Django"),
    "flask": ("flask", "Flask"),
    "sqlalchemy": ("sqlalchemy", "SQLAlchemy ORM"),
    "pytest": ("pytest", "Pytest"),
    # JavaScript/TypeScript
    "react": ("react", "React"),
    "nextjs": ("next", "Next.js"),
    "express": ("express", "Express"),
    "nestjs": ("@nestjs", "NestJS"),
    "vue": ("vue", "Vue.js"),
    "angular": ("@angular", "Angular"),
    # Rust
    "actix": ("actix-web", "Actix-web"),
    "tokio": ("tokio", "Tokio async"),
}

DB_SIGNATURES = {
    "postgresql": ["psycopg2", "asyncpg", "postgres", "pg"],
    "mysql": ["pymysql", "mysql-connector", "mysql2"],
    "sqlite": ["sqlite3", "sqlite"],
    "mongodb": ["pymongo", "mongoose", "mongodb"],
    "redis": ["redis", "ioredis"],
}


def detect_project_dna(project_path: str) -> ProjectDNA:
    root = Path(project_path)
    dna = ProjectDNA(project_path=project_path, name=root.name)

    # Detect languages
    ext_counts: dict[str, int] = {}
    for f in root.rglob("*"):
        if f.is_file() and not any(p in str(f) for p in
                                   [".git", "node_modules", "__pycache__", ".venv", "venv"]):
            ext_counts[f.suffix.lower()] = ext_counts.get(f.suffix.lower(), 0) + 1

    lang_map = {".py": "Python", ".js": "JavaScript", ".ts": "TypeScript",
                ".go": "Go", ".rs": "Rust", ".java": "Java", ".cs": "C#",
                ".rb": "Ruby", ".php": "PHP"}
    found_langs = [(lang_map[ext], count) for ext, count in ext_counts.items()
                   if ext in lang_map]
    found_langs.sort(key=lambda x: x[1], reverse=True)

    dna.languages = [lang for lang, _ in found_langs]
    dna.language = dna.languages[0] if dna.languages else "Unknown"

    # Detect frameworks from dependency files
    dep_content = _read_dependency_files(root)
    for key, (sig, name) in FRAMEWORK_SIGNATURES.items():
        if sig.lower() in dep_content.lower():
            dna.framework = name
            break

    # Detect database
    for db_name, signals in DB_SIGNATURES.items():
        if any(s in dep_content.lower() for s in signals):
            dna.database = db_name
            break

    # Detect architecture
    dna.architecture = _detect_architecture(root)

    # Detect entry points
    dna.entry_points = _detect_entry_points(root)

    # Detect key services
    dna.key_services = _detect_services(root)

    # Basic coding standards
    dna.coding_standards = _detect_coding_standards(root)

    return dna


def _read_dependency_files(root: Path) -> str:
    dep_files = [
        "requirements.txt", "pyproject.toml", "setup.py", "Pipfile",
        "package.json", "go.mod", "Cargo.toml", "pom.xml", "build.gradle",
        "Gemfile",
    ]
    content = ""
    for name in dep_files:
        path = root / name
        if path.exists():
            try:
                content += path.read_text(encoding="utf-8", errors="ignore") + "\n"
            except Exception:
                pass
    return content


def _detect_architecture(root: Path) -> str:
    # Check for microservices signals
    has_docker_compose = (root / "docker-compose.yml").exists() or \
                         (root / "docker-compose.yaml").exists()
    services_dir = (root / "services").exists() or (root / "apps").exists()
    if has_docker_compose and services_dir:
        return "microservices"

    # Check for serverless
    if (root / "serverless.yml").exists() or (root / "serverless.yaml").exists():
        return "serverless"
    if (root / "netlify.toml").exists() or (root / "vercel.json").exists():
        return "serverless/edge"

    return "monolith"


def _detect_entry_points(root: Path) -> list[str]:
    candidates = ["main.py", "app.py", "server.py", "manage.py", "run.py",
                  "index.js", "index.ts", "server.js", "server.ts", "main.go",
                  "main.rs", "src/main.rs", "src/index.ts", "src/index.js"]
    found = []
    for candidate in candidates:
        if (root / candidate).exists():
            found.append(candidate)
    return found[:5]


def _detect_services(root: Path) -> list[str]:
    services = []
    service_dirs = ["services", "apps", "modules", "packages", "src"]
    for sdir in service_dirs:
        p = root / sdir
        if p.is_dir():
            for child in p.iterdir():
                if child.is_dir() and not child.name.startswith("."):
                    services.append(child.name)
    return services[:10]


def _detect_coding_standards(root: Path) -> dict:
    standards = {}
    if (root / ".eslintrc.js").exists() or (root / ".eslintrc.json").exists():
        standards["linter"] = "eslint"
    if (root / "pyproject.toml").exists():
        content = (root / "pyproject.toml").read_text(errors="ignore")
        if "ruff" in content:
            standards["linter"] = "ruff"
        elif "black" in content:
            standards["formatter"] = "black"
    if (root / ".prettierrc").exists():
        standards["formatter"] = "prettier"
    return standards


def generate_and_save(project_path: str) -> ProjectDNA:
    dna = detect_project_dna(project_path)
    db.upsert_project_dna(project_path, {
        "name": dna.name,
        "language": dna.language,
        "languages": dna.languages,
        "framework": dna.framework,
        "database": dna.database,
        "architecture": dna.architecture,
        "entry_points": dna.entry_points,
        "key_services": dna.key_services,
        "coding_standards": dna.coding_standards,
    })

    # Also save to .memory/project_dna.json
    import json
    memory_dir = Path(project_path) / ".memory"
    memory_dir.mkdir(parents=True, exist_ok=True)
    dna_path = memory_dir / "project_dna.json"
    dna_path.write_text(json.dumps(dna.__dict__, indent=2))

    return dna
