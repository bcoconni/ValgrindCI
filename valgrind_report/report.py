import argparse
import os.path
import shutil

from jinja2 import Environment, PackageLoader, select_autoescape

from .parse import ValgrindData


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

    data = ValgrindData()
    data.load(args.input)
    # data.set_base_folder(args.source)

    if not os.path.exists("html"):
        os.makedirs("html")
    shutil.copy(os.path.join(os.path.dirname(__file__), "data", "valgrind.css"), "html")
    shutil.copy(os.path.join(os.path.dirname(__file__), "data", "valgrind.js"), "html")

    env = Environment(
        loader=PackageLoader("valgrind_report", "data"),
        autoescape=select_autoescape(["html", "xml"]),
        trim_blocks=True,
        lstrip_blocks=True,
    )
    source_template = env.get_template("source_file.html")
    index_template = env.get_template("index.html")

    summary = []
    total_num_errors = 0
    srcpath = os.path.abspath(args.source)

    for srcfile in sorted(data.list_source_files()):
        if os.path.commonpath([srcpath, srcfile]) != srcpath:
            continue
        data_srcfile = data.filter_source_file(srcfile)
        error_lines = data_srcfile.list_lines()
        num_errors = len(error_lines)
        filename = os.path.relpath(srcfile, srcpath)
        name = os.path.splitext(os.path.basename(srcfile))
        html_filename = name[0] + "_" + name[1][1:] + ".html"
        summary.append(
            {"filename": filename, "errors": num_errors, "link": html_filename,}
        )
        total_num_errors += num_errors
        codelines = []

        with open(srcfile, "r") as src:
            for l, line in enumerate(src.readlines()):
                klass = "normal"
                issue = {"stack": []}
                if l + 1 in error_lines:
                    klass = "error"
                    current_error = data_srcfile.filter_line(l + 1).errors[0]
                    what = current_error.what
                    issue["what"] = what
                    first = current_error.find_first_source_reference()
                    for frame in current_error.stack[first + 1 :]:
                        stack = {}
                        fullname = frame.get_path(None)
                        stack["code"] = []
                        stack["function"] = frame.func
                        if fullname is None:
                            stack["fileref"] = frame.func
                        else:
                            error_line = frame.line
                            stack["line"] = error_line - 4
                            stack["error_line"] = 4
                            stack["fileref"] = "{}:{}".format(
                                frame.get_path(srcpath), error_line
                            )
                            if os.path.commonpath([srcpath, fullname]) == srcpath:
                                with open(fullname, "r") as f:
                                    for l, code_line in enumerate(f.readlines()):
                                        if l >= error_line - 4 and l <= error_line + 2:
                                            stack["code"].append(code_line)
                        issue["stack"].append(stack)
                codelines.append({"line": line[:-1], "klass": klass, "issue": issue})

        with open(os.path.join("html", html_filename), "w") as dest:
            dest.write(
                source_template.render(
                    num_errors=num_errors,
                    source_file_name=filename,
                    codelines=codelines,
                )
            )

        if args.summary:
            print(f"{filename}")
            print("{} errors".format(num_errors))
            for line in sorted(error_lines):
                error = data_srcfile.filter_line(line).errors[0]
                print(f"\tline {line}: {error.what}")

    with open(os.path.join("html", "index.html"), "w") as f:
        f.write(index_template.render(source_list=summary, num_errors=total_num_errors))
