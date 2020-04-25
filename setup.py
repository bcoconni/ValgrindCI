from setuptools import find_packages, setup

from ValgrindCI import __version__

setup(
    name="ValgrindCI",
    version=__version__,
    description="Tools to integrate valgrind into your Continuous Integration.",
    author="Bertrand Coconnier",
    license="GNU General Public License v3.0",
    packages=find_packages(),
    scripts=["valgrindci"],
    package_dir={"ValgrindCI": "ValgrindCI"},
    package_data={"ValgrindCI": ["data/*.css", "data/*.html", "data/*.js"]},
    include_package_data=True,
    install_requires=["defusedxml", "jinja2"],
)
