from .feature import Feature
from .station import Station
from .tools import pad_left, print_list_by_group, split_by_n


class Boundary(Feature):
    """
    Boundary condition.
    """

    def __init__(self):
        # Load all boundary parts
        self.header = Header()
        self.interval = Interval()
        self.hydrograph = Hydrograph()
        self.dss = DSS()
        self.fixed_start = FixedStart()
        self.critical = Critical()
        self.parts = [
            self.header,
            self.interval,
            self.hydrograph,
            self.dss,
            self.fixed_start,
            self.critical,
        ]
        self.uflow_list = []  # holds all parts and unknown lines (as strings)

    @staticmethod
    def test(line):
        return Header.test(line)

    def import_geo(self, line, infile):
        while True:
            part = next((p for p in self.parts if p.test(line)), None)
            if part is not None:
                line = part.import_geo(line, infile)
                self.parts.remove(part)
                self.uflow_list.append(part)
            else:
                break
        return line

    def __str__(self):
        return "".join((str(l) for l in self.uflow_list))


class Header(Feature):
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


class Interval(Feature):
    def __init__(self):
        self.interval = None

    @staticmethod
    def test(line):
        return line.startswith("Interval=")

    def import_geo(self, line, infile):
        self.interval = line.split("=")[1].strip()
        return infile.readline()

    def __str__(self):
        return "Interval={}\n".format(self.interval)


class Hydrograph(Feature):
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
        return line

    def __str__(self):
        s = "Hydrograph=" + print_list_by_group(self.values, 8, 10)
        return s


class DSS(Feature):
    def __init__(self):
        self.path = None
        self.use_dss = None

    @staticmethod
    def test(line):
        return line.startswith("DSS Path")

    def import_geo(self, line, infile):
        self.path = line.split("=")[1].strip()
        line = infile.readline()
        if line.startswith("Use DSS="):
            self.use_dss = line.split("=")[1].strip().lower() == "true"
            line = infile.readline()
        return line

    def __str__(self):
        return "DSS Path={}\nUse DSS={}\n".format(self.path, self.use_dss)


class FixedStart(Feature):
    def __init__(self):
        self.use_fixed_start = None
        self.datetime = None

    @staticmethod
    def test(line):
        return line.startswith("Use Fixed Start Time")

    def import_geo(self, line, infile):
        self.use_fixed_start = line.split("=")[1].strip().lower() == "true"
        line = infile.readline()
        if line.startswith("Fixed Start Date/Time="):
            self.datetime = line.split("=")[1].strip()
            line = infile.readline()
        return line

    def __str__(self):
        return "Use Fixed Start Time={}\nFixed Start Date/Time={}\n".format(
            self.use_fixed_start, self.datetime
        )


class Critical(Feature):
    def __init__(self):
        self.is_critical = None
        self.flow = None

    @staticmethod
    def test(line):
        return line.startswith("Is Critical Boundary")

    def import_geo(self, line, infile):
        self.is_critical = line.split("=")[1].strip().lower() == "true"
        line = infile.readline()
        if line.startswith("Critical Boundary Flow"):
            self.flow = line.split("=")[1].strip()
            line = infile.readline()
        return line

    def __str__(self):
        return "Is Critical Boundary={}\nCritical Boundary Flow={}\n".format(
            self.is_critical, self.flow
        )
