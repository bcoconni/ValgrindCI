# Classes to parse XML output files from Valgrind.
#
# Copyright (c) 2020 Bertrand Coconnier
#
# This program is free software; you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free Software
# Foundation; either version 3 of the License, or (at your option) any later
# version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more
# details.
#
# You should have received a copy of the GNU General Public License along with
# this program; if not, see <http://www.gnu.org/licenses/>
#

import os.path
import defusedxml.ElementTree as et


class Error:
    def __init__(self, tag):
        self.stack = []
        self.what = tag.find("what").text
        self.kind = tag.find("kind").text
        self.unique = int(tag.find("unique").text, 16)
        for frame in tag.findall("stack/frame"):
            self.stack.append(Frame(frame))

    def __str__(self):
        s = f"{self.what} (0x{self.unique:x})"
        for i, frame in enumerate(self.stack):
            s += "\n#{} => {}".format(i, frame)
        return s

    def find_first_source_reference(self):
        for i, frame in enumerate(self.stack):
            if frame.get_path(None) is not None:
                return i
        return None


class Frame:
    def __init__(self, tag):
        self.obj = tag.find("obj").text
        func = tag.find("fn")
        if func is not None:
            self.func = tag.find("fn").text
        else:
            self.func = None
        folder = tag.find("dir")
        if folder is not None:
            self.folder = folder.text
            source_file = tag.find("file")
            line = tag.find("line")
            assert source_file is not None
            assert line is not None
            self.filename = source_file.text
            self.line = int(line.text)
        else:
            self.folder = None
            self.filename = None
            self.line = None

    def __str__(self):
        if self.folder is not None:
            return "{}:{}".format(self.get_path(None), self.line)
        return self.func

    def get_path(self, base_folder):
        if self.folder is not None:
            filename = os.path.join(self.folder, self.filename)
            if base_folder is not None:
                filename = os.path.relpath(filename, base_folder)
            return filename
        return None


class ValgrindData:
    def __init__(self):
        self.errors = []
        self.base_folder = None

    def parse(self, xml_file):
        root = et.parse(xml_file).getroot()
        for error_tag in root.findall("error"):
            self.errors.append(Error(error_tag))

    def set_base_folder(self, folder):
        self.base_folder = folder

    def get_num_errors(self):
        return len(self.errors)

    def filter_error_kind(self, kind):
        data = ValgrindData()
        data.base_folder = self.base_folder
        for error in self.errors:
            if error.kind == kind:
                data.errors.append(error)
        return data

    def filter_source_file(self, filename):
        data = ValgrindData()
        data.base_folder = self.base_folder
        for error in self.errors:
            f = error.find_first_source_reference()
            if error.stack[f].get_path(self.base_folder) == filename:
                data.errors.append(error)
        return data

    def filter_line(self, line):
        data = ValgrindData()
        data.base_folder = self.base_folder
        for error in self.errors:
            f = error.find_first_source_reference()
            if error.stack[f].line == line:
                data.errors.append(error)
        return data

    def list_error_kinds(self):
        error_kinds = []
        for error in self.errors:
            if error.kind not in error_kinds:
                error_kinds.append(error.kind)
        return error_kinds

    def list_source_files(self):
        source_files = []
        for error in self.errors:
            f = error.find_first_source_reference()
            filename = error.stack[f].get_path(self.base_folder)
            if filename not in source_files:
                source_files.append(filename)
        return source_files

    def list_lines(self):
        lines = []
        for error in self.errors:
            f = error.find_first_source_reference()
            line = error.stack[f].line
            if line not in lines:
                lines.append(line)
        return lines
