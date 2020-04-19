import argparse
import os.path
import xml.etree.ElementTree as et


def report():
    parser = argparse.ArgumentParser()
    parser.add_argument("input", help="Valgrind XML file name")
    parser.add_argument("--source", default=".", help="specifies the source directory")
    args = parser.parse_args()

    tree = et.parse(args.input)
    root = tree.getroot()

    srcpath = os.path.abspath(args.source)
    print(srcpath)

    i = 0
    srcfiles = set()
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
                    srcfiles.add(f"{folder.text}/{srcfile.text}")
                    break
        else:
            continue
        if i <= 10:
            print(
                "{}\n\tin {}/{}:{}".format(
                    error.find("what").text, folder.text, srcfile.text, line.text
                )
            )
        i += 1

    print(srcfiles)
    print(len(srcfiles))
