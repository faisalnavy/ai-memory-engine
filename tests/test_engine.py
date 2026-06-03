"""Integration tests for the memory engine."""
import sys
import tempfile
import os
from pathlib import Path

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from storage import db
from core import dna, file_summarizer, function_summarizer, graph_builder, retriever


def create_sample_project(root: Path) -> None:
    """Create a minimal sample Python project for testing."""
    (root / "app.py").write_text('''"""Main Flask application."""
from flask import Flask
from routes.users import users_bp
from models.user import User

app = Flask(__name__)
app.register_blueprint(users_bp)

def create_app():
    """Create and configure the Flask app."""
    return app
''')

    (root / "models").mkdir()
    (root / "models" / "__init__.py").write_text("")
    (root / "models" / "user.py").write_text('''"""User data model."""
import sqlite3

class User:
    """Represents a user in the system."""

    def __init__(self, id: int, name: str, email: str):
        self.id = id
        self.name = name
        self.email = email

    def to_dict(self) -> dict:
        """Convert user to dictionary."""
        return {"id": self.id, "name": self.name, "email": self.email}

    @classmethod
    def from_dict(cls, data: dict) -> "User":
        """Create user from dictionary."""
        return cls(data["id"], data["name"], data["email"])
''')

    (root / "routes").mkdir()
    (root / "routes" / "__init__.py").write_text("")
    (root / "routes" / "users.py").write_text('''"""User route handlers."""
from flask import Blueprint, jsonify
from models.user import User

users_bp = Blueprint("users", __name__, url_prefix="/users")

def get_all_users() -> list:
    """Return all users from the database."""
    return []

def get_user_by_id(user_id: int):
    """Return a single user by ID."""
    return None

async def create_user(data: dict) -> User:
    """Create a new user asynchronously."""
    return User(1, data["name"], data["email"])
''')

    (root / "requirements.txt").write_text("flask>=3.0\nsqlite3\n")


def test_full_pipeline():
    with tempfile.TemporaryDirectory() as tmpdir:
        create_sample_project(Path(tmpdir))

        # Init
        db.init_db(tmpdir)

        # DNA
        project_dna = dna.generate_and_save(tmpdir)
        assert project_dna.language == "Python"
        assert "flask" in project_dna.framework.lower() or project_dna.framework != ""

        # Index files
        results = file_summarizer.summarize_directory(tmpdir)
        assert len(results) >= 2, f"Expected >=2 results, got {len(results)}"

        # Index functions
        fn_count = function_summarizer.summarize_all_functions(tmpdir, results)
        assert fn_count >= 3, f"Expected >=3 functions, got {fn_count}"

        # Build graph
        graph_builder.build_graph(tmpdir)
        stats = db.get_stats(tmpdir)
        assert stats["file_memory"] >= 2
        assert stats["function_memory"] >= 3

        # Retrieve
        pkg = retriever.retrieve(tmpdir, "user model database")
        assert pkg.token_estimate > 0
        assert pkg.original_token_estimate >= pkg.token_estimate
        markdown = pkg.as_markdown()
        assert len(markdown) > 10

        print(f"\nOK Files indexed: {stats['file_memory']}")
        print(f"OK Functions stored: {stats['function_memory']}")
        print(f"OK Graph edges: {stats['knowledge_graph']}")
        print(f"OK Context tokens: {pkg.token_estimate}")
        print(f"OK Original tokens: {pkg.original_token_estimate}")
        savings = round((1 - pkg.token_estimate / max(pkg.original_token_estimate, 1)) * 100, 1)
        print(f"OK Token savings: {savings}%")


def test_incremental_update():
    with tempfile.TemporaryDirectory() as tmpdir:
        create_sample_project(Path(tmpdir))
        db.init_db(tmpdir)
        file_summarizer.summarize_directory(tmpdir)

        from core import updater
        changed = updater.get_changed_files(tmpdir)
        # After initial index all hashes stored — no changes expected
        assert len(changed) == 0, f"Expected 0 changes after index, got {len(changed)}"

        # Modify a file
        (Path(tmpdir) / "app.py").write_text('"""Modified app."""\ndef new_function(): pass\n')
        changed = updater.get_changed_files(tmpdir)
        assert len(changed) == 1, f"Expected 1 changed file, got {len(changed)}"
        print(f"\nOK Incremental update detected {len(changed)} change(s)")


def test_fts_search():
    with tempfile.TemporaryDirectory() as tmpdir:
        create_sample_project(Path(tmpdir))
        db.init_db(tmpdir)
        file_summarizer.summarize_directory(tmpdir)

        results = db.search_files_fts(tmpdir, "user", limit=5)
        assert len(results) >= 1, "FTS search should find user-related files"
        print(f"\nOK FTS search found {len(results)} file(s) for 'user'")


if __name__ == "__main__":
    print("Running memory engine tests...\n")
    test_full_pipeline()
    test_incremental_update()
    test_fts_search()
    print("\nAll tests passed!")
