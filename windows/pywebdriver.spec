block_cipher = None

a = Analysis(['..\\pywebdriverd'],
             datas=[('config.ini', 'config'),
             ('mkcert.exe', '.'),
             ('generate_certificate.bat', '.'),
             ('nssm.exe', '.'),
             ('install.bat', '.'),
             ('uninstall.bat', '.'),
             ('capabilities.json', 'escpos'),
             ('..\\pywebdriver\\templates\\*', 'pywebdriver\\templates'),
             ('..\\pywebdriver\\static\\css\\*', 'pywebdriver\\static\\css'),
             ('..\\pywebdriver\\static\\images\\*', 'pywebdriver\\static\\images'),
             ('..\\pywebdriver\\static\\js\\*', 'pywebdriver\\static\\js'),
             ('..\\pywebdriver\\translations\\*', 'pywebdriver\\translations'),
             ('..\\pywebdriver\\translations\\fr', 'pywebdriver\\translations\\fr'),
             ('..\\venv\\Lib\\site-packages\\pif\\checkers\\dyndns', 'pif\\checkers\\dyndns'),
             ('..\\venv\\Lib\\site-packages\\pif\\checkers\\httpbin', 'pif\\checkers\\httpbin'),
             ('..\\venv\\Lib\\site-packages\\pif\\checkers\\icanhazip', 'pif\\checkers\\icanhazip'),
             ('..\\venv\\Lib\\site-packages\\pif\\checkers\\ident', 'pif\\checkers\\ident'),
             ('..\\venv\\Lib\\site-packages\\pif\\checkers\\ip42', 'pif\\checkers\\ip42'),
             ('..\\venv\\Lib\\site-packages\\pif\\checkers\\ipecho', 'pif\\checkers\\ipecho'),
             ('..\\venv\\Lib\\site-packages\\pif\\checkers\\ipify', 'pif\\checkers\\ipify'),
             ('..\\venv\\Lib\\site-packages\\pif\\checkers\\myexternalip', 'pif\\checkers\\myexternalip'),
             ('..\\venv\\Lib\\site-packages\\pif\\checkers\\tnx', 'pif\\checkers\\tnx'),
             ('..\\venv\\Lib\\site-packages\\pif\\checkers\\whatismyip', 'pif\\checkers\\whatismyip'),
             ('..\\venv\\Lib\\site-packages\\pif\\checkers\\wtfismyip', 'pif\\checkers\\wtfismyip'),
             ],
             binaries=[ ( '..\\pywebdriver\\SAT.dll', '.' ) ],
             hiddenimports=['pywebdriver.plugins.cups_driver', 'pywebdriver.plugins.display_driver',
             'pywebdriver.plugins.escpos_driver', 'pywebdriver.plugins.serial_driver',
             'pywebdriver.plugins.signature_driver', 'pywebdriver.plugins.telium_driver',
             'pywebdriver.plugins.opcua_driver', 'pywebdriver.plugins.odoo7', 'pywebdriver.plugins.odoo8',
             'pywebdriver.plugins.win32print_driver','pywebdriver.plugins.sat_driver',
             'win32timezone', 'usb', 'requests', 'pkg_resources.py2_warn',],
             hookspath=[],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher,
             noarchive=False)
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          [],
          exclude_binaries=True,
          name='pywebdriver',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          console=True )
coll = COLLECT(exe,
               a.binaries,
               a.zipfiles,
               a.datas,
               strip=False,
               upx=True,
               upx_exclude=[],
               name='pywebdriver')
