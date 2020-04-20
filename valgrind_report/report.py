import argparse
import os.path
import shutil

import defusedxml.ElementTree as et
from jinja2 import Environment, PackageLoader, select_autoescape


class issue:
    def __init__(self, filename, line, what):
        self.filename = filename
        self.line = line
        self.what = what


def report():
    parser = argparse.ArgumentParser()
    parser.add_argument("input", help="Valgrind XML file name")
    parser.add_argument("--source", default=".", help="Specifies the source directory")
    parser.add_argument(
        "--summary", default=False, action="store_true", help="Prints a summary"
    )
    args = parser.parse_args()

    root = et.parse(args.input).getroot()

    srcpath = os.path.abspath(args.source)

    srcfiles = {}
    for error in root.findall("error"):
        for frame in error.findall("stack/frame"):
            folder = frame.find("dir")
            srcfile = frame.find("file")
            line = frame.find("line")
            if folder is not None:
                if (
                    os.path.commonpath([srcpath, folder.text]) == srcpath
                    and srcfile is not None
                    and line is not None
                ):
                    filename = f"{folder.text}/{srcfile.text}"
                    new_issue = issue(filename, int(line.text), error.find("what").text)
                    if filename in srcfiles:
                        for iss in srcfiles[filename]:
                            if (
                                iss.line == new_issue.line
                                and iss.what == new_issue.what
                            ):
                                break
                        else:
                            srcfiles[filename].append(new_issue)
                    else:
                        srcfiles[filename] = [new_issue]
                    break
        else:
            continue

    if not os.path.exists("html"):
        os.makedirs("html")
    shutil.copy(os.path.join(os.path.dirname(__file__), "data", "valgrind.css"), "html")

    env = Environment(
        loader=PackageLoader("valgrind_report", "data"),
        autoescape=select_autoescape(["html", "xml"]),
    )
    source_template = env.get_template("source_file.html")
    index_template = env.get_template("summary.html")

    summary = []

    for srcfile in sorted(srcfiles):
        filename = os.path.relpath(srcfile, srcpath)
        name = os.path.splitext(os.path.basename(srcfile))
        html_filename = name[0] + "_" + name[1][1:] + ".html"
        summary.append(
            {
                "filename": filename,
                "errors": len(srcfiles[srcfile]),
                "link": html_filename,
            }
        )
        codelines = []

        with open(srcfile, "r") as src:
            for l, line in enumerate(src.readlines()):
                klass = "normal"
                for iss in srcfiles[srcfile]:
                    if l + 1 == iss.line:
                        klass = "error"
                        break
                codelines.append({"line": line[:-1], "klass": klass})

        with open(os.path.join("html", html_filename), "w") as dest:
            dest.write(
                source_template.render(
                    num_errors=len(srcfiles[srcfile]),
                    source_file_name=filename,
                    codelines=codelines,
                )
            )

        if args.summary:
            print(f"{srcfile}")
            print("{} errors".format(len(srcfiles[srcfile])))
            for iss in sorted(srcfiles[srcfile], key=lambda error: error.line):
                print(f"\tline {iss.line}: {iss.what}")

    with open(os.path.join("html", "index.html"), "w") as f:
        f.write(index_template.render(source_list=summary))
