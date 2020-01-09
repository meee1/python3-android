import shlex
import logging
import os
import pathlib
import shutil
import subprocess
import sys
from typing import List

BASE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(BASE))

from util import ARCHITECTURES, env_vars, ndk, parse_args

logger = logging.getLogger(__name__)

SYSROOT = BASE / 'build'


class CPythonSourceDeps:
    def __init__(self, tag: str, organization: str = None):
        self.tag = tag
        self.organization = organization

    def run_in_source_dir(self, cmd: List[str]):
        cwd = BASE.parent / 'externals' / self.tag
        logger.debug(f'Running in {os.path.relpath(cwd)}: ' + ' '.join([shlex.quote(str(arg)) for arg in cmd]))
        subprocess.check_call(cmd, cwd=cwd)

    def download(self):
        cmd = [BASE.parent / 'PCbuild' / 'get_external.py', '--ext', 'tar.gz']
        if self.organization:
            cmd += ['-O', self.organization]
        cmd += [self.tag]
        subprocess.check_call(cmd)


class Package:
    source: CPythonSourceDeps

    def __init__(self, target_arch_name: str, android_api_level: int):
        self.name = type(self).__name__.lower()
        self.target_arch_name = target_arch_name
        self.target_arch = ARCHITECTURES[target_arch_name]
        self.android_api_level = android_api_level

    def run(self, cmd: List[str]) -> None:
        self.source.run_in_source_dir(cmd)

    def build(self):
        raise NotImplementedError


class BZip2(Package):
    source = CPythonSourceDeps('bzip2', organization='yan12125')

    def build(self):
        self.run([
            'cmake',
            f'-DCMAKE_TOOLCHAIN_FILE={ndk.cmake_toolchain}',
            f'-DANDROID_ABI={self.target_arch.CMAKE_ANDROID_ABI}',
            f'-DANDROID_PLATFORM=android-{self.android_api_level}',
            '-DENABLE_STATIC_LIB=ON',
            '-DENABLE_SHARED_LIB=OFF',
            '-DCMAKE_INSTALL_PREFIX=/usr',
            '.'
        ])

        self.run(['make'])
        self.run(['make', 'install', f'DESTDIR={SYSROOT}'])


class GDBM(Package):
    source = CPythonSourceDeps('gdbm', organization='yan12125')

    def build(self):
        self.run(['autoreconf', '--install', '--verbose', '--force'])

        self.run([
            'sh', './configure',
            '--prefix=/usr',
            '--host=' + self.target_arch.ANDROID_TARGET,
            '--enable-libgdbm-compat',
            '--disable-static',
        ])

        self.run(['make', 'V=1'])
        self.run(['make', 'install', f'DESTDIR={SYSROOT}'])


class LibFFI(Package):
    source = CPythonSourceDeps('libffi')

    def build(self):
        self.run(['autoreconf', '--install', '--verbose', '--force'])

        self.run([
            'sh', './configure',
            '--prefix=/usr',
            '--host=' + self.target_arch.ANDROID_TARGET,
            '--disable-shared',
        ])

        self.run(['make'])
        self.run(['make', 'install', f'DESTDIR={SYSROOT}'])


class LibUUID(Package):
    source = CPythonSourceDeps('util-linux', organization='yan12125')

    def build(self):
        self.run([
            'sh', './configure',
            '--prefix=/usr',
            '--libdir=/usr/lib',
            '--bindir=/usr/bin',
            '--sbindir=/usr/bin',
            '--host=' + self.target_arch.ANDROID_TARGET,
            '--disable-all-programs',
            '--enable-libuuid',
        ])

        self.run(['make'])
        self.run(['make', 'install', f'DESTDIR={SYSROOT}'])


class NCurses(Package):
    source = CPythonSourceDeps('ncurses', organization='yan12125')

    def build(self):
        self.run([
            'sh', './configure',
            '--prefix=/usr',
            '--host=' + self.target_arch.ANDROID_TARGET,
            '--without-ada',
            '--enable-widec',
            '--without-shared',
            '--with-normal',
            '--without-debug',
            '--without-cxx-binding',
            '--enable-warnings',
            '--disable-stripping',
        ])

        self.run(['make'])
        self.run(['make', 'install', f'DESTDIR={SYSROOT}'])


class OpenSSL(Package):
    source = CPythonSourceDeps('openssl-1.1.1')

    def build(self):
        # OpenSSL handles NDK internal paths by itself
        path = os.pathsep.join((
            # OpenSSL requires NDK's clang in $PATH to enable usage of clang
            str(ndk.unified_toolchain),
            # and it requires unprefixed binutils, too
            str(ndk.unified_toolchain.parent / self.target_arch.ANDROID_TARGET / 'bin'),
            os.environ['PATH'],
        ))

        logger.debug(f'$PATH for OpenSSL: {path}')

        os.environ.update({
            'PATH': path,
            'HASHBANGPERL': '/system/bin/env perl',
        })
        os.environ['CPPFLAGS'] += f' -D__ANDROID_API__={self.android_api_level}'

        openssl_target = 'android-' + self.target_arch_name

        self.run(['perl', './Configure', '--prefix=/usr', '--openssldir=/etc/ssl', openssl_target, 'no-shared', 'no-tests'])

        self.run(['make'])
        self.run(['make', 'install_sw', 'install_ssldirs', f'DESTDIR={SYSROOT}'])


class Readline(Package):
    source = CPythonSourceDeps('readline', organization='yan12125')

    def build(self):
        # See the wcwidth() test in aclocal.m4. Tested on Android 6.0 and it's broken
        # XXX: wcwidth() is implemented in [1], which may be in Android P
        # Need a conditional configuration then?
        # [1] https://android.googlesource.com/platform/bionic/+/c41b560f5f624cbf40febd0a3ec0b2a3f74b8e42
        self.run([
            'sh', './configure',
            'bash_cv_wcwidth_broken=yes',
            '--prefix=/usr',
            '--host=' + self.target_arch.ANDROID_TARGET,
            '--disable-shared',
        ])

        self.run(['make'])
        self.run(['make', 'install', f'DESTDIR={SYSROOT}'])


class SQLite(Package):
    source = CPythonSourceDeps('sqlite', organization='yan12125')

    def build(self):
        self.run([
            'sh', './configure',
            '--prefix=/usr',
            '--host=' + self.target_arch.ANDROID_TARGET,
            '--disable-shared',
        ])

        self.run(['make'])
        self.run(['make', 'install', f'DESTDIR={SYSROOT}'])


class Tools(Package):
    '''
    This is not an actual package. It just copies some handy files into target/
    '''

    def build(self):
        for f in ('c_rehash.py', 'env.sh', 'import_all.py', 'ssl_test.py'):
            (SYSROOT / 'tools').mkdir(exist_ok=True)
            shutil.copy2(BASE / 'tools' / f, SYSROOT / 'tools' / f)


class XZ(Package):
    source = CPythonSourceDeps('xz')

    def build(self):
        self.run(['autoreconf', '--install', '--verbose', '--force'])

        self.run([
            'sh', './configure',
            '--prefix=/usr',
            '--host=' + self.target_arch.ANDROID_TARGET,
            '--disable-shared',
        ])

        self.run(['make'])
        self.run(['make', 'install', f'DESTDIR={SYSROOT}'])


class ZLib(Package):
    source = CPythonSourceDeps('zlib')

    def build(self):
        os.environ.update({
            'CHOST': self.target_arch.ANDROID_TARGET + '-',
            'CFLAGS': os.environ['CPPFLAGS'] + os.environ['CFLAGS'],
        })

        self.run([
            'sh', './configure',
            '--prefix=/usr',
            '--static',
        ])

        self.run(['make', 'libz.a'])
        self.run(['make', 'install', f'DESTDIR={SYSROOT}'])


def build_package(pkg: Package) -> None:
    logger.info(f'Building {pkg.name}')

    SYSROOT.mkdir(exist_ok=True, parents=True)

    pkg.source.download()

    try:
        saved_env = os.environ.copy()
        pkg.build()
    finally:
        os.environ.clear()
        os.environ.update(saved_env)


def main():
    logging.basicConfig(level=logging.DEBUG)

    args = parse_args()

    os.environ.update(env_vars(args.target_arch_name, args.android_api_level))

    package_classes = (
        # ncurses is a dependency of readline
        NCurses,
        BZip2, GDBM, LibFFI, LibUUID, OpenSSL, Readline, SQLite, Tools, XZ, ZLib,
    )

    for pkg_cls in package_classes:
        build_package(pkg_cls(args.target_arch_name, args.android_api_level))


if __name__ == '__main__':
    main()
