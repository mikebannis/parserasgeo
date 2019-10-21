# Boundary handling Copyright (C) KISTERS Nederland B.V.

from .features.station import Station
from .features.tools import (
    fl_int,
    pad_left,
    print_list_by_group,
    split_block_obs,
    split_by_n,
    split_by_n_str,
)


class UnsteadyFlow(object):
    """
    Imports RAS unsteady flow data in filename, i.e. project_name.u??
    """

    def __init__(self, filename):
        self.filename = filename
        self.uflow_list = []

        with open(filename, "rt") as infile:
            while True:
                line = infile.readline()
                if not line:
                    break
                if Boundary.test(line):
                    boundary = Boundary()
                    boundary.import_geo(line, infile)
                    self.uflow_list.append(boundary)
                else:  # Unknown line, add as text
                    self.uflow_list.append(line)

    def export(self, outfilename):
        """
        Writes unsteady flow data to outfilename.
        """
        with open(outfilename, "wt", newline="\r\n") as outfile:
            for line in self.uflow_list:
                outfile.write(str(line))


class Boundary(object):
    """
    Boundary condition.
    """

    def __init__(self):
        # Load all boundary parts
        self.header = Header()
        self.interval = Interval()
        self.hydrograph = Hydrograph()

        self.parts = [self.header, self.interval, self.hydrograph]

        self.uflow_list = []  # holds all parts and unknown lines (as strings)

    @staticmethod
    def test(line):
        return Header.test(line)

    def import_geo(self, line, infile):
        while line:
            for part in self.parts:
                if part.test(line):
                    # print str(type(part))+' found!'
                    line = part.import_geo(line, infile)
                    self.parts.remove(part)
                    self.uflow_list.append(part)
                    break
            else:  # Unknown line, add as text
                self.uflow_list.append(line)
                line = infile.readline()
        return line

    def __str__(self):
        s = ""
        for line in self.uflow_list:
            s += str(line)
        return s + "\n"


class Header(object):
    def __init__(self):
        self.river_name = None
        self.reach_name = None
        self.station = None

    @staticmethod
    def test(line):
        return line.startswith("Boundary Location=")

    def import_geo(self, line, infile):
        self._parts = line.split("=")[1].split(",")
        self.river_name = self._parts[0].strip()
        self.reach_name = self._parts[1].strip()
        self.station = Station(self._parts[2])
        return infile.readline()

    def __str__(self):
        lengths = [16, 16, 8, 6, 16, 16, 16, 16]
        values = [pad_left(part, length) for part, length in zip(self._parts, lengths)]
        s = "Boundary Location=" + ",".join(values)
        return s


class Interval(object):
    def __init__(self):
        self.interval = None

    @staticmethod
    def test(line):
        return line.startswith("Interval=")

    def import_geo(self, line, infile):
        self.interval = line.split("=")[1]
        return infile.readline()

    def __str__(self):
        s = "Interval=" + self.interval
        return s


class Hydrograph(object):
    def __init__(self):
        self.type = None
        self.values = []

    @staticmethod
    def test(line):
        return line.split("=")[0].endswith("Hydrograph")

    def import_geo(self, line, infile):
        parts = line.split(" Hydrograph=")
        self.type = parts[0]
        num_pts = int(parts[1])
        line = infile.readline()
        while (
            line[:1] == " " or line[:1].isdigit() or line[:1] == "-" or line[:1] == "."
        ):
            vals = split_by_n(line, 8)
            self.values.extend(vals)
            line = infile.readline()
        assert len(self.values) == num_pts

    def __str__(self):
        s = "Hydrograph=" + print_list_by_group(self.values, 8, 10)
        return s
