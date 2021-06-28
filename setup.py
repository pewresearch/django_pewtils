from distutils.core import setup
from setuptools import find_packages


with open("README.md") as README:
    readme = str(README.read())

install_requires = []
with open("requirements.txt") as reqs:
    for line in reqs.read().split("\n"):
        if not line.startswith("#"):
            install_requires.append(line)

setup(
    name="django_pewtiils",
    version="1.0.0",
    description="Miscellaneous Django utilities from Pew Research Center",
    long_description=readme,
    url="https://github.com/pewresearch/django_pewtils",
    author="Pew Research Center",
    author_email="info@pewresearch.org",
    install_requires=install_requires,
    packages=find_packages(exclude=["contrib", "docs", "tests"]),
    include_package_data=True,
    keywords="django, pew pew pew",
    license="GPLv2+",
    classifiers=[
        # https://pypi.python.org/pypi?%3Aaction=list_classifiers
        "Development Status :: 5 - Production/Stable",
        "Environment :: Console",
        "Intended Audience :: Information Technology",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: GNU General Public License v2 or later (GPLv2+)",
        "Natural Language :: English",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Utilities",
    ],
)
