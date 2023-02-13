from pathlib import Path

import setuptools

VERSION = "6.0.0b1"

try:
    with open('./multiversx_sdk_cli/_version.py', 'wt') as versionfile:
        versionfile.write(f'__version__ = "{VERSION}"\n')
except FileNotFoundError:
    pass

# See https://packaging.python.org/tutorials/packaging-projects/
setuptools.setup(
    name="multiversx-sdk-cli",
    version=VERSION,
    description="MultiversX Smart Contracts Tools",
    long_description=Path("README.md").read_text(),
    long_description_content_type="text/markdown",
    url="https://github.com/multiversx/mx-sdk-py-cli",
    author="MultiversX",
    license="MIT",
    packages=setuptools.find_packages(
        include=["multiversx_sdk_cli*"]),
    include_package_data=True,
    setup_requires=["wheel"],
    install_requires=[
        "toml>=0.10.2",
        "bottle",
        "requests",
        "cryptography==36.0.2",
        "prettytable",
        "ledgercomm[hid]",
        "semver",
        "requests-cache",
        "multiversx-sdk-network-providers==0.6.*",
        "multiversx-sdk-wallet==0.4.*",
        "multiversx-sdk-core==0.3.*",
    ],
    zip_safe=False,
    keywords=["MultiversX"],
    classifiers=[
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "License :: OSI Approved :: GNU General Public License (GPL)",
        "Operating System :: POSIX :: Linux",
        "Intended Audience :: Developers",
        "Development Status :: 3 - Alpha"
    ],
    python_requires=">=3.8"
)
