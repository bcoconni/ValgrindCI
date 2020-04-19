import argparse
import os.path
import shutil
import xml.etree.ElementTree as et


class issue:
    def __init__(self, filename, line, what):
        self.filename = filename
        self.line = line
        self.what = what


def report():
    parser = argparse.ArgumentParser()
    parser.add_argument("input", help="Valgrind XML file name")
    parser.add_argument("--source", default=".", help="specifies the source directory")
    parser.add_argument(
        "--summary", default=False, action="store_true", help="Print a summary"
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
    shutil.copy("valgrind.css", "html")

    for srcfile in sorted(srcfiles):
        name = os.path.splitext(os.path.basename(srcfile))
        html_filename = os.path.join("html", name[0] + "_" + name[1][1:] + ".html")
        with open(html_filename, "w") as dest:
            dest.write(
                "<html>\n<head>\n<link href='valgrind.css' rel='stylesheet' type='text/css'></head>\n<body>"
            )
            dest.write("<h1>{}</h1>".format(os.path.relpath(srcfile, srcpath)))
            with open(srcfile, "r") as src:
                line = src.readline()
                l = 1
                while line:
                    klass = "normal"
                    for iss in srcfiles[srcfile]:
                        if l == iss.line:
                            klass = "error"
                            break
                    dest.write(f"<p class='{klass}'>{l} {line}</p>")
                    line = src.readline()
                    l += 1
            dest.write("</body>\n<html>")
        if args.summary:
            print(f"{srcfile}")
            print("{} errors".format(len(srcfiles[srcfile])))
            for iss in sorted(srcfiles[srcfile], key=lambda error: error.line):
                print(f"\tline {iss.line}: {iss.what}")
