# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['/Users/kylebrodeur/workspace/universal-agent-context/src/uacs/mcp_server_entry.py'],
    pathex=['/Users/kylebrodeur/workspace/universal-agent-context/src'],
    binaries=[],
    datas=[],
    hiddenimports=['tiktoken_ext.openai_public', 'tiktoken_ext'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='uacs-mcp-server',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
