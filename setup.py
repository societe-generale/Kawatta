"""A setuptools based setup module.
See:
https://packaging.python.org/en/latest/distributing.html
https://github.com/pypa/sampleproject
"""

# To use a consistent encoding
from codecs import open
from os import path

# Always prefer setuptools over distutils
from setuptools import setup, find_packages

here = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with open(path.join(here, "README.md"), encoding="utf-8") as f:
    long_description = f.read()

with open(path.join(here, "kawatta/VERSION"), encoding="utf-8") as f:
    version = f.read()

setup(
    name="Kawatta",
    description="Allows you to get a human-readable log of the changes between two Python structs",
    author="SG",
    author_email="",
    license="MIT",
    url="https://sgithub.fr.world.socgen/ktollec111518/Kawatta",
    version=version,
    keywords="dict comparison",
    # include_package_data=True,
    # package_data={},
    packages=find_packages(),
    long_description=long_description,
    install_requires=[],
    extras_require={
        "tests": [
            "coverage",
            "pytest",
            "pytest-mock",
            "pytest-cov",
            "pytest-coverage",
            "pytest-random-order",
            "tox",
            "flake8",
        ]
    },
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Build Tools",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
    ],
)
