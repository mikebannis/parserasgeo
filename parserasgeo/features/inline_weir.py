from .description import Description
from .feature import Feature
from .station import Station


class Header(Feature):
    def __init__(self):
        self.station = None
        self.node_type = None

    @staticmethod
    def test(line):
        return line.startswith("Type RM Length L Ch R = 5 ")

    def import_geo(self, line, geo_file):
        fields = line[23:].split(",", maxsplit=2)
        assert len(fields) == 3
        self.node_type = int(fields[0])
        self.station = Station(fields[1])
        # TODO: Not sure what the rest is
        self._remainder = fields[2]
        return next(geo_file)

    def __str__(self):
        s = "Type RM Length L Ch R = "
        s += str(self.node_type) + " ,"
        s += str(self.station) + ","
        s += self._remainder  # Note: contains \n
        return s


class InlineWeir(Feature):
    def __init__(self, river, reach):
        self.river = river
        self.reach = reach
        self.header = Header()
        self.description = Description()
        self._parts = [self.header, self.description]
        self.geo_list = []

    def import_geo(self, line, geo_file):
        while line != "\n":
            for part in self._parts:
                if part.test(line):
                    line = part.import_geo(line, geo_file)
                    self._parts.remove(part)
                    self.geo_list.append(part)
                    break
            else:
                self.geo_list.append(line)
                line = next(geo_file)
        return line

    def __str__(self):
        s = "".join(map(str, self.geo_list))
        return s + "\n"

    @staticmethod
    def test(line):
        return Header.test(line)
