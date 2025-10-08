# -*- mode: python ; coding: utf-8 -*-
import os
from PyInstaller.utils.hooks import collect_data_files

# Check if files exist before adding them
datas = []
if os.path.exists('asset'):
    datas.append(('asset', 'asset'))

# Add images folder
if os.path.exists('images'):
    datas.append(('images', 'images'))

# Collect BioPython data files
bio_datas = collect_data_files('Bio')
datas.extend(bio_datas)

a = Analysis(
    ['main.py'],
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
        'Bio.Align',
        'Bio.Align.substitution_matrices',
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
    icon='images/icon.ico' if os.path.exists('images/icon.ico') else None,
)
