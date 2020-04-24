from setuptools import setup, find_packages

setup(
    name="ValgrindCI",
    version="0.0.1",
    description="Tools to integrate valgrind in your Continuous Integration.",
    author="Bertrand Coconnier",
    license="GNU General Public License v3.0",
    packages=find_packages(),
    package_dir={"ValgrindCI": "ValgrindCI"},
    package_data={"ValgrindCI": ["data/*.css", "data/*.html", "data/*.js"]},
    include_package_data=True,
    install_requires=["defusedxml", "jinja2"],
)
