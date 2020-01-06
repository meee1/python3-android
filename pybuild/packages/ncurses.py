from ..source import URLSource
from ..package import Package
from ..util import target_arch


class NCurses(Package):
    validpgpkeys = ['C52048C0C0748FEE227D47A2702353E0F7E48EDB']

    @property
    def source(self):
        return URLSource(
            f'https://invisible-mirror.net/archives/ncurses/ncurses-{self.version}.tar.gz',
            sig_suffix='.asc')

    def build(self):
        self.run_with_env([
            './configure',
            '--prefix=/usr',
            f'--host={target_arch().ANDROID_TARGET}',
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
        self.run(['make', 'install', f'DESTDIR={self.destdir()}'])
