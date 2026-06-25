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

    # Commandes de base de Django requises pour les migrations
    "django.core.management.commands.migrate",

    # django tenants
    "django_tenants.management",
    "django_tenants.management.commands",
    "django_tenants.management.commands.migrate_schemas",
]

# Collecte automatique de TOUS les sous-modules (y compris les commandes de management)
hiddenimports += collect_submodules("django_tenants")
hiddenimports += collect_submodules("rest_framework")
hiddenimports += collect_submodules("rest_framework_simplejwt")

datas = (
    collect_data_files('pyarmor_runtime_000000')
    + collect_data_files('django')
    + collect_data_files('django_tenants')
    +  collect_data_files('accounts')
    +  collect_data_files('expenses')
    +  collect_data_files('tenants')
)
a = Analysis(
    ['.pyarmor_dist/server.py'],
    pathex=['.pyarmor_dist'],
    binaries=[],
    # Collecte des fichiers de runtime PyArmor et des templates/statiques Django nécessaires
    datas = collect_data_files('pyarmor_runtime_000000')
            + collect_data_files('django')
            + collect_data_files('django_tenants'),
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
    console=True, # Laisser True le temps de vérifier que l'erreur Django a disparu
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
