from ..source import URLSource
from ..package import Package
from ..util import target_arch


class LibreSSL(Package):
    version = '2.6.3'
    source = URLSource(f'https://ftp.openbsd.org/pub/OpenBSD/LibreSSL/libressl-{version}.tar.gz')

    def prepare(self):
        self.run_with_env([
            './configure',
            '--prefix=/usr',
            '--sysconfdir=/etc',
            '--host=' + target_arch().ANDROID_TARGET,
            '--disable-shared',
        ])

    def build(self):
        self.run(['make'])
        self.run(['make', 'install', f'DESTDIR={self.destdir()}'])
