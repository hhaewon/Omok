# -*- mode: python ; coding: utf-8 -*-

added_files = [("./image/*", './image'),
               ("./font/*", './font'),
              ]

a = Analysis(
    ['main.py'],
    pathex=[r'D:\CodingWorkspace\PythonWorld\Omok'],
    binaries=[],
    datas=added_files,
    hiddenimports=["pygame"],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure, a.zipped_data)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='오목 AI',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    uac_admin=True,
    icon="./icon.ico"
)
