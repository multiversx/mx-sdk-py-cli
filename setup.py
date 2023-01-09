import setuptools

with open("README.md", "r") as fh:
    long_description = "https://github.com/multiversx/mx-sdk-erdpy"

VERSION = "4.0.0"

try:
    with open('./erdpy/_version.py', 'wt') as versionfile:
        versionfile.write(f'__version__ = "{VERSION}"\n')
except FileNotFoundError:
    pass

# See https://packaging.python.org/tutorials/packaging-projects/
setuptools.setup(
    name="erdpy",
    version=VERSION,
    description="MultiversX Smart Contracts Tools",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/multiversx/mx-sdk-erdpy",
    author="MultiversX",
    license="GPL",
    packages=setuptools.find_packages(
        include=["erdpy*"], exclude=["examples*"]),
    include_package_data=True,
    setup_requires=["wheel"],
    install_requires=[
        "toml>=0.10.2",
        "bottle",
        "requests",
        "pynacl",
        "pycryptodomex",
        "cryptography==36.0.2",
        "prettytable",
        "ledgercomm[hid]",
        "semver",
        "requests-cache",
        "mx-sdk-build-contract-rs==4.0.0"
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
    entry_points={
        "console_scripts": [
            "erdpy=erdpy.cli:main",
        ],
    },
    python_requires=">=3.8"
)
