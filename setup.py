import os
from setuptools import setup, find_packages


with open(os.path.join(os.path.dirname(__file__), "README.md"), "rb") as readme:
    README = str(readme.read())

os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

install_requires = []
with open("requirements.txt") as reqs:
    for line in reqs.read().split("\n"):
        if line and not line.startswith(("#", "--", "git+ssh")):
            install_requires.append(line)

setup(
    name="django_pewtils",
    version='0.1.4.dev0',
    description="miscellaneous utilities",
    long_description=README,  # 'http://labs.pewresearch.tech/docs/libs/django_pewtils',
    url="https://github.com/pewresearch/django_pewtils",
    author="Pew Research Center",
    author_email="admin@pewresearch.tech",
    install_requires=install_requires,
    packages=find_packages(exclude=["contrib", "docs", "tests"]),
    include_package_data=True,
    classifiers=[
        # https://pypi.python.org/pypi?%3Aaction=list_classifiers
        #        'Development Status :: 1 - Planning',
        #        'Development Status :: 2 - Pre-Alpha',
        #        'Development Status :: 3 - Alpha',
        #        'Development Status :: 4 - Beta',
        "Development Status :: 5 - Production/Stable",
        #        'Development Status :: 6 - Mature',
        #        'Development Status :: 7 - Inactive'
        "Intended Audience :: Science/Research",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Utilities",
    ],
)
