from setuptools import setup, find_packages

setup(
    name="valgrind_report",
    version="0.0.1",
    description="Generate HTML report to display errors reported by valgrind in the source code.",
    author="Bertrand Coconnier",
    license="GNU General Public License v3.0",
    packages=find_packages(),
    package_dir={"valgrind_report": "valgrind_report"},
    package_data={"valgrind_report": ["data/*.css"]},
    include_package_data=True,
    install_requires=["defusedxml", "jinja2"],
)
