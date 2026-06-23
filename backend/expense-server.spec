# -*- mode: python ; coding: utf-8 -*-
from PyInstaller.utils.hooks import collect_submodules
from PyInstaller.utils.hooks import collect_data_files

hiddenimports = [
    "dotenv",

    "waitress",
    "waitress.runner",

    "config.settings",
    "config.wsgi",
    "config.urls",

    "accounts",
    "accounts.authentication",

    "expenses",
    "tenants",
]

hiddenimports += collect_submodules("rest_framework")
hiddenimports += collect_submodules("rest_framework_simplejwt")

a = Analysis(
    ['.pyarmor_dist/server.py'],
    pathex=['.pyarmor_dist'],
    binaries=[],
    datas = collect_data_files('pyarmor_runtime_000000'),
    hiddenimports=hiddenimports,
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
    name='expense-server',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)