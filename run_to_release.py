import sys
import os
import shutil
import platform
from cx_Freeze import setup, Executable

VERSION = '1.4'

print('Python Version', sys.version)

if __name__ == '__main__':
    os_family = {'Windows': 'win', 'Darwin': 'mac', 'Linux': 'linux'}[platform.system()]
    #platform.system(): tên hệ điều hành đang được sử dụng để chạy chương trình
    sys.argv[:] = [sys.argv[0], 'build']

    buildOptions = dict(
        packages=[],
        excludes=[],
        include_files=[('assets', 'assets')])

    target = Executable(
        'main.py',
        base={'win': 'Win32GUI', 'mac': None, 'linux': None}[os_family],
        targetName='game',
        icon='assets/icon.' + {'win': 'ico', 'mac': 'icns', 'linux': 'ico'}[os_family],
        copyright='Mikhail Shubin',
    )

    setup(
        name='tetris',
        version=VERSION,
        description='Tetris for Two',
        options={'build_exe': buildOptions},
        executables=[target]
        )

    # zip files
    zip_dir = f'build/tetris_for_two_{os_family}_v{VERSION}'
    print(zip_dir)
    for path in 'linux-x86_64 win-amd64 macosx-10.9-x86_64'.split():
        build_dir = 'build/exe.' + path + '-3.9'
        if os.path.exists(build_dir):
            break
    else:
        raise Exception('path not found')
    print(build_dir)

    shutil.make_archive(zip_dir, 'zip', build_dir)

