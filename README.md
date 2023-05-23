![CI/CD](https://github.com/bcoconni/ValgrindCI/workflows/Test%20&%20Deploy%20Python%20Package/badge.svg)
[![PyPI](https://img.shields.io/pypi/v/valgrindci)](https://pypi.org/project/ValgrindCI)
[![Downloads](https://pepy.tech/badge/valgrindci)](https://pepy.tech/project/valgrindci)

# Continuous Integration with Valgrind

ValgrindCI is a Python package that provides tools to facilitate the integration of [valgrind](https://valgrind.org/) into your Continuous Integration workflow.

Valgrind can sometimes generate an overwhelming amount of findings and it can be difficult to extract the information you need from these data. ValgrindCI most basic feature is to terminate a job if the findings from valgrind meet some criteria defined by the user, for example, as soon as valgrind reports a single error. ValgrindCI can also help you get a better insight into the errors reported by valgrind:

- Errors can be grouped or filtered (for example leak errors only).
- A summary of the errors found by valgrind can be printed in the console.
- ValgrindCI can generate an HTML report to investigate the errors directly within your code.

## Installation

### Download and install with `pip`

ValgrindCI is a tool written in Python and can be installed from `pip`. This is the prefered method to install ValgrindCI.

```bash
> pip install ValgrindCI
```

### Install from the sources

Alternatively, ValgrindCI can be built and installed from the source files.

#### Pre-requisites

ValgrindCI uses the Python packages [`defusedxml`](https://github.com/tiran/defusedxml) and [`jinja2`](https://palletsprojects.com/p/jinja/).
If you are building ValgrindCI from source, these dependencies must be installed with `pip` in the first place.

```bash
> pip install -r requirements.txt
```

#### Build and install the package

ValgrindCI uses the `setuptools` to build its package which can then be installed by `pip`

```bash
> python setup.py bdist_wheel
> pip install ValgrindCI --no-index -f dist
```

#### Build and package an executable with `pyinstaller`

You can use `pyinstaller` to create a single-file executable binary:

```bash
> pip install pyinstaller
> pyinstaller --onefile --add-data ValgrindCI:ValgrindCI valgrind-ci
> ./dist/valgrind-ci --help
```

## How to use

ValgrindCI is a command tool designed to be executed within jobs of your favorite Continuous Integration platform. It parses the XML output of valgrind to provide its services.

First, Valgrind must be run with the options `--xml=yes` and `--xml-file` in order to report its findings in an XML file.

```bash
> valgrind --tool=memcheck --xml=yes --xml-file==/path/to/output_file.xml my_executable --options-of-my-executable
```

### Get basic information

Now, ValgrindCI can be invoked to parse the XML output file and report the total number of errors found by valgrind.

```bash
> valgrind-ci /path/to/output_file.xml --number-of-errors
```

### Abort on errors

Most CI platforms detect a job failure when the system command `exit()` is called with a non zero value. This feature allows ValgrindCI to report a failure as soon as valgrind reports an error:

```bash
> valgrind-ci /path/to/output_file.xml --abort-on-errors
```

### Summary report of errors

You can request ValgrindCI to print a summary report of the errors found by valgrind.

```bash
> valgrind-ci /path/to/output_file.xml --summary
```

An example of the output is given below:

```text
src/models/FGAtmosphere.cpp:
9 errors
 line 125: UninitCondition (1 errors)
 line 129: UninitCondition (6 errors)
           UninitValue (2 errors)
src/models/FGMassBalance.cpp:
13 errors
 line 207: UninitCondition (11 errors)
 line 472: SyscallParam (1 errors)
           UninitCondition (1 errors)
```

Since a function can be called from different places, a single line of code can be reported several times as an offending line by valgrind. In the example above, the line 207 of the file `src/models/FGMassBalance.cpp` is reported 11 times, each time with a different call stack. Clearly, the added value of ValgrindCI in such a case is to group errors by source files and by line numbers. By this simple process, and for the particular case illustrated above, the number of errors has been narrowed down from 2147 to 185 !

### HTML report

ValgrindCI can generate an HTML report that displays the errors reported by Valgrind inside your code. The command below generates an HTML report in the directory `html`. The argument `--source-dir` is used to build paths relative to that directory rather than absolute paths.

```bash
> valgrind-ci /path/to/output_file.xml --source-dir=/path/to/source/code --output-dir=html
```

If you open the document `html/index.html` you can review the report with your web browser, errors with their corresponding call stack are displayed within the source code.

![View of HTML report](https://github.com/bcoconni/ValgrindCI/raw/master/media/HTMLreport.png)

### Other options

ValgrindCI command line tool has a number of arguments than can be used to adapt the tool to your specific need:

```bash
usage: valgrind-ci [-h] [--version] [--source-dir SOURCE_DIR]
                   [--output-dir OUTPUT_DIR] [--summary] [--number-of-errors]
                   [--lines-before LINES_BEFORE] [--lines-after LINES_AFTER]
                   [--abort-on-errors]
                   xml_file

positional arguments:
  xml_file              Valgrind XML file name

optional arguments:
  -h, --help            show this help message and exit
  --version             show program's version number and exit
  --source-dir SOURCE_DIR
                        specifies the source directory
  --output-dir OUTPUT_DIR
                        directory where the HTML report will be generated
  --summary             print a summary of errors
  --number-of-errors    print the total number of errors found by Valgrind
  --lines-before LINES_BEFORE
                        number of code lines to display in the HTML report
                        before the error line (default to 3)
  --lines-after LINES_AFTER
                        number of code lines to display in the HTML report
                        after the error line (default to 3)
  --abort-on-errors     call exit(1) if errors have been reported by Valgrind
```

## Advanced usage

ValgrindCI can also be used as a Python library that helps you filter and select errors programmatically.

### Errors filtering

Valgrind can generate a significant amount of errors, not all of which might be relevant to your project. In that case, ValgrindCI can filter data to report only the errors that are of interest to you.

For example, if you only need errors generated by the leaks that are definitely lost then you can filter the data with the method `filter_error_kind()` to report that kind of errors:

```python
from ValgrindCI.parse import ValgrindData

data = ValgrindData()
data.parse('/path/to/output_file.xml')
# Output the number of errors for leaks definitely lost.
print(data.filter_error_kind('Leak_DefinitelyLost').get_num_errors()) 
```

There are some other filters available to select a subset of source files or a particular line of code.

### HTML report

Once errors have been filtered to suit your need, you can generate an HTML report from the instance `data`:

```python
from ValgrindCI.render import HTMLRenderer

renderer = HTMLRenderer(data)
renderer.render('html', lines_before=3, lines_after=3)
```

### Summary report

Alternatively you can print a summary report in the console:

```python
from ValgrindCI.report import Report

report = Report(data)
print(report.summary())
```

## Releases

- `v0.3.0` : New Release
  - Fixed issue #17 (checking that a second occurrence of `<stack>` exists)
  - Added type hints for ValgrindCI so that tools like `mypy` can check your types.
- `v0.2.0` : New Release
  - Added the management of the `<auxwhat>` tags.
  - Added the ability to filter by functions in addition to filtering by files
    and lines.
  - An exception is now raised when Valgrind cannot find either the tag `<what>`
    or the tag `<xwhat>`.
  - ValgrindCI can now handle relative paths (PR #4)
  - Valgrind now rejects frames without an `<obj>` tag (PR #5)
- `v0.1.1`: Bug fixes
  - Fixed issue #1 (the tag `<xwhat>` used for leak errors was not recognized).
  - Fixed an issue where the incorrect number of errors was reported when the optional argument `--source-dir` was not specified.
- `v0.1.0`: Initial Release
