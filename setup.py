import os.path

from setuptools import find_packages, setup

from ValgrindCI import __version__

with open(os.path.join(os.path.dirname(__file__), "README.md"), "r") as f:
    long_description = f.read()

setup(
    name="ValgrindCI",
    version=__version__,
    description="Tools to integrate valgrind into your Continuous Integration workflow.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    keywords="valgrind valgrind-log-parsing html-report",
    author="Bertrand Coconnier",
    url="https://github.com/bcoconni/ValgrindCI",
    license="GNU General Public License v3.0",
    packages=find_packages(),
    scripts=["valgrind-ci"],
    package_dir={"ValgrindCI": "ValgrindCI"},
    package_data={"ValgrindCI": ["data/*.css", "data/*.html", "data/*.js"]},
    include_package_data=True,
    install_requires=["defusedxml", "jinja2"],
    classifiers=[
        "Development Status :: 4 - Beta",
        "Environment :: Console",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)",
        "Operating System :: POSIX :: Linux",
        "Programming Language :: Python :: 3",
        "Topic :: Software Development :: Testing",
    ],
)
