# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['blog_converter_gui.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('convert_blog.py', '.'),
        ('tagFinder.py', '.'),
        ('README.md', '.'),
        ('Tags.txt', '.'),
        ('icon.png', '.'),
        ('header.png', '.'),
    ],
    hiddenimports=[
        'googleapiclient',
        'googleapiclient.discovery',
        'googleapiclient.http',
        'google_auth_oauthlib',
        'google_auth_oauthlib.flow',
        'google.auth.transport.requests',
        'bs4',
        'PIL',
        'PIL._tkinter_finder',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='DPPBlogConvert',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # No console window
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='icon.ico',
)
