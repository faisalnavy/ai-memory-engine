# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller spec for the Desktop App Python API server.
Produces: desktop-app/api-dist/api.exe
"""
from pathlib import Path

ROOT     = Path(SPECPATH).parent          # memory-engine/
API_DIR  = Path(SPECPATH)                 # memory-engine/desktop-app/

a = Analysis(
    [str(API_DIR / 'api' / 'server.py')],
    pathex=[str(ROOT), str(API_DIR)],
    binaries=[],
    datas=[
        # Bundle the SQL schema
        (str(ROOT / 'storage' / 'schema.sql'), 'storage'),
    ],
    hiddenimports=[
        'storage', 'storage.db',
        'core', 'core.dna', 'core.file_summarizer', 'core.function_summarizer',
        'core.graph_builder', 'core.retriever', 'core.context_builder',
        'core.compressor', 'core.updater', 'core.session_manager',
        'core.decision_manager',
        'parsers', 'parsers.base_parser',
        'models', 'models.memory_types',
        'networkx', 'networkx.algorithms', 'networkx.classes',
        'fastapi', 'fastapi.middleware.cors',
        'uvicorn', 'uvicorn.main', 'uvicorn.config',
        'uvicorn.lifespan.on', 'uvicorn.protocols.http.auto',
        'uvicorn.protocols.websockets.auto',
        'uvicorn.loops.auto',
        'pydantic', 'pydantic.v1',
        'anyio', 'anyio._backends._asyncio',
        'starlette', 'starlette.routing',
        'h11', 'httptools', 'watchfiles', 'websockets',
    ],
    hookspath=[],
    runtime_hooks=[],
    excludes=['pytest', 'numpy', 'pandas', 'matplotlib', 'tkinter'],
    noarchive=False,
    optimize=1,
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='api',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,          # no console window
    disable_windowed_traceback=False,
)
