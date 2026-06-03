# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller spec for AI Memory Engine GUI
Produces: dist/MemoryEngine.exe  (single-file, no console window)
"""
from pathlib import Path

ROOT = Path(SPECPATH)

a = Analysis(
    [str(ROOT / 'gui' / 'app.py')],
    pathex=[str(ROOT)],
    binaries=[],
    datas=[
        # Bundle the SQL schema so it's available inside the .exe
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
        'tkinter', 'tkinter.ttk', 'tkinter.filedialog', 'tkinter.scrolledtext',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=['pytest', 'numpy', 'pandas', 'matplotlib'],
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
    name='MemoryEngine',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,       # no black console window — GUI only
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,           # add an .ico path here if you have one
    version=None,
)
