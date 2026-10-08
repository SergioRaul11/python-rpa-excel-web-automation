# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['inscribir_estudiantes.py'],
    pathex=[],
    binaries=[],
    datas=[],
    hiddenimports=['selenium.webdriver.chrome.options', 'selenium.webdriver.chrome.service', 'selenium.webdriver.chrome.webdriver', 'selenium.webdriver.common.by', 'selenium.webdriver.common.keys', 'selenium.webdriver.support.expected_conditions', 'selenium.webdriver.support.ui', 'selenium.webdriver.common.selenium_manager'],
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
    [],
    exclude_binaries=True,
    name='inscribir_estudiantes',
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
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='inscribir_estudiantes',
)
