import ast
import hashlib
import re
from pathlib import Path
from models.memory_types import FileInfo, FunctionInfo


def compute_hash(path: str) -> str:
    h = hashlib.sha256()
    h.update(Path(path).read_bytes())
    return h.hexdigest()


def _infer_risk(file_path: str, imports: list[str]) -> str:
    path_lower = file_path.lower()
    high_keywords = ["auth", "payment", "secret", "password", "token", "crypto",
                     "security", "admin", "billing", "database", "migration"]
    if any(k in path_lower for k in high_keywords):
        return "high"
    medium_keywords = ["api", "route", "model", "schema", "service", "middleware"]
    if any(k in path_lower for k in medium_keywords):
        return "medium"
    return "low"


class PythonParser:
    """Parse Python files using the stdlib ast module."""

    def parse(self, file_path: str) -> FileInfo:
        path = Path(file_path)
        source = path.read_text(encoding="utf-8", errors="ignore")
        lines = source.splitlines()

        try:
            tree = ast.parse(source, filename=file_path)
        except SyntaxError:
            return FileInfo(
                file_path=file_path,
                purpose="(parse error)",
                file_hash=compute_hash(file_path),
                line_count=len(lines),
            )

        imports = self._extract_imports(tree)
        functions = self._extract_functions(tree, file_path)
        exports = self._extract_exports(tree, source)
        public_apis = [f.name for f in functions if f.is_public] + exports

        return FileInfo(
            file_path=file_path,
            purpose=self._infer_purpose(tree, file_path),
            public_apis=list(set(public_apis)),
            imports=imports,
            exports=exports,
            dependencies=[],  # resolved later by graph builder
            risk_level=_infer_risk(file_path, imports),
            file_hash=compute_hash(file_path),
            line_count=len(lines),
            functions=functions,
        )

    def _extract_imports(self, tree: ast.AST) -> list[str]:
        imports = []
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    imports.append(alias.name)
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    imports.append(node.module)
        return list(set(imports))

    def _extract_functions(self, tree: ast.AST, file_path: str) -> list[FunctionInfo]:
        functions = []
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                fn = self._parse_function(node, file_path)
                functions.append(fn)
        return functions

    def _parse_function(self, node: ast.FunctionDef | ast.AsyncFunctionDef,
                        file_path: str) -> FunctionInfo:
        args = []
        for arg in node.args.args:
            arg_info = {"name": arg.arg}
            if arg.annotation:
                try:
                    arg_info["type"] = ast.unparse(arg.annotation)
                except Exception:
                    pass
            args.append(arg_info)

        return_type = ""
        if node.returns:
            try:
                return_type = ast.unparse(node.returns)
            except Exception:
                pass

        docstring = ast.get_docstring(node) or ""
        decorators = []
        for d in node.decorator_list:
            try:
                decorators.append(ast.unparse(d))
            except Exception:
                pass

        # callees: function calls within this function body
        callees = []
        for child in ast.walk(node):
            if isinstance(child, ast.Call):
                try:
                    callees.append(ast.unparse(child.func))
                except Exception:
                    pass

        return FunctionInfo(
            name=node.name,
            file_path=file_path,
            qualified_name=node.name,
            args=args,
            return_type=return_type,
            callees=list(set(callees)),
            decorators=decorators,
            is_async=isinstance(node, ast.AsyncFunctionDef),
            is_public=not node.name.startswith("_"),
            docstring=docstring[:500],
            summary=docstring.split("\n")[0][:200] if docstring else "",
            line_start=node.lineno,
            line_end=getattr(node, "end_lineno", node.lineno),
        )

    def _extract_exports(self, tree: ast.AST, source: str) -> list[str]:
        for node in ast.walk(tree):
            if isinstance(node, ast.Assign):
                for target in node.targets:
                    if isinstance(target, ast.Name) and target.id == "__all__":
                        try:
                            return ast.literal_eval(node.value)
                        except Exception:
                            pass
        return []

    def _infer_purpose(self, tree: ast.AST, file_path: str) -> str:
        # Use module docstring if present
        docstring = ast.get_docstring(tree)
        if docstring:
            return docstring.split("\n")[0][:200]

        # Infer from file path
        name = Path(file_path).stem
        name_clean = name.replace("_", " ").replace("-", " ")

        path_lower = file_path.lower()
        if "test" in path_lower:
            return f"Tests for {name_clean}"
        if "model" in path_lower:
            return f"Data model: {name_clean}"
        if "route" in path_lower or "view" in path_lower:
            return f"Route/view handler: {name_clean}"
        if "util" in path_lower or "helper" in path_lower:
            return f"Utility functions: {name_clean}"
        if "config" in path_lower:
            return f"Configuration: {name_clean}"
        if "schema" in path_lower:
            return f"Schema definition: {name_clean}"
        return f"Module: {name_clean}"


class GenericParser:
    """Fallback parser for JS/TS/other files using regex."""

    IMPORT_PATTERNS = [
        r'import\s+.*?\s+from\s+[\'"]([^\'"]+)[\'"]',
        r'require\s*\(\s*[\'"]([^\'"]+)[\'"]\s*\)',
        r'import\s*\(\s*[\'"]([^\'"]+)[\'"]\s*\)',
    ]
    EXPORT_PATTERNS = [
        r'export\s+(?:default\s+)?(?:function|class|const|let|var)\s+(\w+)',
        r'module\.exports\s*=\s*\{([^}]+)\}',
    ]
    FUNCTION_PATTERNS = [
        r'(?:async\s+)?function\s+(\w+)\s*\(',
        r'(?:const|let|var)\s+(\w+)\s*=\s*(?:async\s+)?\(',
        r'(?:const|let|var)\s+(\w+)\s*=\s*(?:async\s+)?function',
    ]

    def parse(self, file_path: str) -> FileInfo:
        path = Path(file_path)
        source = path.read_text(encoding="utf-8", errors="ignore")
        lines = source.splitlines()

        imports = []
        for pattern in self.IMPORT_PATTERNS:
            imports.extend(re.findall(pattern, source))

        exports = []
        for pattern in self.EXPORT_PATTERNS:
            exports.extend(re.findall(pattern, source))
        exports = [e.strip() for e in exports if e.strip()]

        functions = []
        for pattern in self.FUNCTION_PATTERNS:
            for match in re.finditer(pattern, source):
                line_no = source[:match.start()].count("\n") + 1
                fn_name = match.group(1)
                fn = FunctionInfo(
                    name=fn_name,
                    file_path=file_path,
                    qualified_name=fn_name,
                    is_public=not fn_name.startswith("_"),
                    line_start=line_no,
                )
                functions.append(fn)

        # Deduplicate by name
        seen = set()
        unique_functions = []
        for fn in functions:
            if fn.name not in seen:
                seen.add(fn.name)
                unique_functions.append(fn)

        return FileInfo(
            file_path=file_path,
            purpose=self._infer_purpose(file_path, source),
            public_apis=list(set(exports)),
            imports=list(set(imports)),
            exports=list(set(exports)),
            risk_level=_infer_risk(file_path, imports),
            file_hash=compute_hash(file_path),
            line_count=len(lines),
            functions=unique_functions,
        )

    def _infer_purpose(self, file_path: str, source: str) -> str:
        # Look for JSDoc comment at top
        match = re.search(r'/\*\*\s*(.*?)\s*\*/', source[:500], re.DOTALL)
        if match:
            return match.group(1).replace("*", "").strip()[:200]
        name = Path(file_path).stem.replace("_", " ").replace("-", " ")
        return f"Module: {name}"


def get_parser(file_path: str):
    suffix = Path(file_path).suffix.lower()
    if suffix == ".py":
        return PythonParser()
    return GenericParser()


def parse_file(file_path: str) -> FileInfo | None:
    try:
        parser = get_parser(file_path)
        return parser.parse(file_path)
    except Exception:
        return None


SUPPORTED_EXTENSIONS = {".py", ".js", ".ts", ".jsx", ".tsx", ".go", ".rs", ".java", ".cs"}
SKIP_DIRS = {".git", "__pycache__", "node_modules", ".venv", "venv", "dist",
             "build", ".memory", ".next", "coverage", ".pytest_cache"}


def should_index(file_path: str) -> bool:
    path = Path(file_path)
    if path.suffix.lower() not in SUPPORTED_EXTENSIONS:
        return False
    for part in path.parts:
        if part in SKIP_DIRS:
            return False
    return True
