# -*- mode: python ; coding: utf-8 -*-

a = Analysis(
    ['src/main.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('src/ui/theme.qss', 'src/ui'),
    ],
    hiddenimports=[
        'can',
        'can.io.blf',
        'can.io.asc',
        'asammdf',
        'pandas',
        'numpy',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'torch', 'torchvision', 'torchaudio', 'transformers',
        'onnxruntime', 'scipy', 'lxml', 'sqlalchemy',
        'matplotlib', 'PIL', 'Pillow', 'cv2', 'opencv',
        'sklearn', 'tensorflow', 'keras', 'jax',
        'sympy', 'numba', 'numba.cuda',
        'IPython', 'jupyter', 'notebook',
        'pytest', 'coverage', 'hypothesis',
        'setuptools', 'pip', 'wheel',
        'tkinter', '_tkinter',
    ],
    noarchive=False,
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='CAN-Converter',
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
    icon=None,
)
