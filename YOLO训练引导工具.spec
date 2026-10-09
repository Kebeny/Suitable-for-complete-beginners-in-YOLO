# -*- mode: python ; coding: utf-8 -*-
import os


a = Analysis(
    ['src\\main.py'],
    pathex=[],
    binaries=[(os.path.join(SPECPATH, 'runtime', 'msvcp140.dll'), 'runtime'), (os.path.join(SPECPATH, 'runtime', 'vcruntime140.dll'), 'runtime'), (os.path.join(SPECPATH, 'runtime', 'vcruntime140_1.dll'), 'runtime')],
    datas=[('models', 'models'), ('fonts', 'fonts')],
    hiddenimports=['PyQt5', 'cv2', 'torch', 'torch._C', 'torch.cuda', 'torch.utils._pytree', 'yaml', 'pynvml', 'ultralytics', 'ultralytics.nn', 'ultralytics.utils', 'matplotlib', 'multiprocessing'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[os.path.join(SPECPATH, 'runtime_hooks', 'pyi_rth_000_preload_msvc.py')],
    excludes=['IPython', 'jupyter'],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='YOLO训练引导工具',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=['app.ico'],
)
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='YOLO训练引导工具',
)
