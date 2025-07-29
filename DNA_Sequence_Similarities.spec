# -*- mode: python ; coding: utf-8 -*-
import os

# Check if files exist before adding them
datas = []
if os.path.exists('style.qss'):
    datas.append(('style.qss', '.'))
if os.path.exists('images'):
    datas.append(('images', 'images'))

a = Analysis(
    ['DSS.py'],
    pathex=[],
    binaries=[],
    datas=datas,
    hiddenimports=[
        'matplotlib', 
        'matplotlib.backends.backend_tkagg', 
        'matplotlib.backends.backend_pdf',
        'Bio',
        'Bio.Phylo',
        'Bio.SeqIO', 
        'Bio.Seq',
        'Bio.Phylo.TreeConstruction',
        'sklearn.metrics.pairwise',
        'numpy',
        'qt_material',
        'PyQt6.QtCore',
        'PyQt6.QtGui',
        'PyQt6.QtWidgets'
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=['PyQt5', 'tkinter', 'matplotlib.tests'],
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
    name='DNA_Sequence_Similarities',
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
    icon='icon.ico' if os.path.exists('icon.ico') else None,
)
