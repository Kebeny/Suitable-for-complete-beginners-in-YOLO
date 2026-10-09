"""PyInstaller runtime hook: preload bundled MSVC runtime before PyQt5.

PyInstaller's pyi_rth_pyqt5 hook imports PyQt5.QtCore before the user script
runs. QtCore then loads PyQt5/Qt5/bin/MSVCP140.dll (an older MSVC runtime).
If that older runtime is loaded first, torch's c10.dll later fails to initialize
with WinError 1114.

This hook is named so it sorts before pyi_rth_pyqt5, loads the bundled
14.44 runtime first, and prevents the conflicting runtime initialization order.
"""
import os
import sys
import ctypes


def _pyi_rthook():
    if not sys.platform.startswith("win"):
        return

    base_dir = getattr(sys, "_MEIPASS", None)
    if not base_dir:
        base_dir = os.path.dirname(sys.executable)

    runtime_dir = os.path.join(base_dir, "runtime")
    if not os.path.isdir(runtime_dir):
        runtime_dir = base_dir

    for dll_name in ("msvcp140.dll", "vcruntime140.dll", "vcruntime140_1.dll"):
        dll_path = os.path.join(runtime_dir, dll_name)
        if os.path.isfile(dll_path):
            try:
                ctypes.WinDLL(dll_path)
            except OSError:
                pass


_pyi_rthook()
del _pyi_rthook
