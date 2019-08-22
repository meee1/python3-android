from .package import enumerate_packages, import_package


def main():
    target_packages = enumerate_packages()
    for pkg in target_packages:
        for src in import_package(pkg, will_build=False).sources:
            src.download()


if __name__ == '__main__':
    main()
