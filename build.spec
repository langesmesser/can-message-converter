# -*- mode: python ; coding: utf-8 -*-

a = Analysis(
    ['src/main.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('src/ui/theme.qss', 'src/ui'),
        ('src/ui/theme_light.qss', 'src/ui'),
    ],
    hiddenimports=[
        'can',
        'can.io.blf',
        'can.io.asc',
        'asammdf',
        'pandas',
        'numpy',
        'openpyxl',
        'src.ui.themes',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        # 大型 ML/CV 框架
        'torch', 'torchvision', 'torchaudio', 'transformers',
        'onnxruntime', 'safetensors', 'tokenizers',
        # 科学计算（仅 asammdf GUI 用到）
        'scipy', 'scipy.fft', 'scipy.fftpack', 'scipy.spatial',
        'scipy.stats', 'scipy.linalg', 'scipy.sparse',
        'scipy.optimize', 'scipy.signal', 'scipy.interpolate',
        'scipy.io', 'scipy.ndimage', 'scipy.special',
        # 绘图
        'matplotlib', 'PIL', 'Pillow', 'cv2', 'opencv',
        'pycairo', 'freetype-py', 'rlpycairo',
        # Web 框架
        'flask', 'werkzeug', 'jinja2', 'tornado',
        'aiohttp', 'aiofiles', 'websockets',
        # 数据库
        'sqlalchemy', 'alembic', 'greenlet',
        # Jupyter / IPython
        'IPython', 'jupyter', 'notebook', 'jupyter_client',
        'jupyter_core', 'jupyterlab_pygments',
        'nbclient', 'nbconvert', 'nbformat', 'ipykernel',
        # 测试
        'pytest', 'coverage', 'hypothesis',
        # 打包 / 构建
        'setuptools', 'pip', 'wheel',
        # GUI 无关
        'tkinter', '_tkinter',
        # asammdf GUI 子包（只用 MDF 核心）
        'asammdf.gui',
        # 文档处理
        'python-docx', 'python-pptx',
        'ebooklib', 'mammoth', 'markdownify', 'markitdown',
        'pymupdf', 'reportlab', 'svglib',
        # 其他大型/无关库
        'numba', 'numba.cuda',
        'scikit-learn', 'sklearn', 'tensorflow', 'keras', 'jax',
        'rich', 'typer', 'shellingham',
        'playwright', 'pyee',
        'edge-tts',
        'huggingface-hub', 'google-auth', 'google-genai',
        'openai', 'gradio',
        'kornia', 'kornia-rs',
        'spandrel', 'einops',
        'comfyui-embedded-docs', 'comfyui-frontend-package',
        'comfyui-workflow-templates',
        'sentencepiece', 'protobuf',
        'pyzmq', 'flatbuffers',
        'magika', 'markdown-it-py', 'mdurl',
        'uv',
        # 消除无害的 "hidden import not found" 警告
        # charset_normalizer 的可选 Cython 加速模块（不存在，纯 Python 回退即可）
        'ascii__mypyc', 'confusion__mypyc', 'escape__mypyc',
        'magic__mypyc', 'orchestrator__mypyc', 'statistical__mypyc',
        'structural__mypyc', 'utf1632__mypyc', 'utf8__mypyc',
        'validity__mypyc',
        # packaging 的 Linux 专属子模块（Windows 打包不存在）
        'packaging._elffile', 'packaging._manylinux',
        'packaging._musllinux', 'packaging._parser',
        'packaging._structures', 'packaging._tokenizer',
        'packaging.licenses', 'packaging.licenses._spdx',
        'packaging.markers', 'packaging.metadata',
        'packaging.requirements', 'packaging.specifiers',
        'packaging.tags', 'packaging.utils', 'packaging.version',
        # setuptools 旧版子模块（新版已合并，不存在）
        'setuptools._distutils',
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
    name='CAN报文格式转换工具V1.4.0',
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
