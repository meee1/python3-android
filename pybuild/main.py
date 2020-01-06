import logging

from .env import packages
from .package import import_package


logger = logging.getLogger(__name__)


def build_package(pkgname: str) -> None:
    pkg = import_package(pkgname)

    logger.info(f'Building {pkgname} {pkg.get_version()}')

    if pkg.need_download():
        for src in pkg.sources:
            src.download()

        # All signatures should be downloaded first so that sources can be verified
        for src in pkg.sources:
            src.verify(pkg.validpgpkeys)
            src.extract()

        for patch in getattr(pkg, 'patches', []):
            patch.apply(pkg.source, pkg)

    pkg.build()


def main():
    logging.basicConfig(level=logging.DEBUG)

    for pkgname in packages:
        build_package(pkgname)
