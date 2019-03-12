from .tools import fl_int #  , split_by_n_str, pad_left, print_list_by_group, split_block_obs, split_by_n
from .description import Description

class Feature(object):
    """
    This is a template for other features.
    """
    def __init__(self):
        pass

    @staticmethod
    def test(line):
        if line.split('=')[0] == 'XS GIS Cut Line':
            return True
        return False

    def import_geo(self, line, geo_file):
        return line

    def __str__(self):
        pass


# TODO: possibly move header into LateralWeir
class Header(object):
    def __init__(self):
        self.name = None

    @staticmethod
    def test(line):
        if line[:11] == 'Junct Name=':
            return True
        return False

    def import_geo(self, line, geo_file):
        fields = line.split('=')
        # print line, fields
        assert len(fields) == 2
        self.name = fields[1][:-1]
        return next(geo_file)

    def __str__(self):
        s = 'Junct Name=' + self.name + '\n'
        return s

class Junction(object):
    def __init__(self):

        # Load all cross sections parts
        self.header = Header()
        self.parts = [self.header]

        self.geo_list = []  # holds all parts and unknown lines (as strings)

    def import_geo(self, line, geo_file):
        while line != '\n':
            for part in self.parts:
                if part.test(line):
                    # print str(type(part))+' found!'
                    line = part.import_geo(line, geo_file)
                    self.parts.remove(part)
                    self.geo_list.append(part)
                    break
            else:  # Unknown line, add as text
                self.geo_list.append(line)
                line = next(geo_file)
        return line

    def __str__(self):
        s = ''
        for line in self.geo_list:
            s += str(line)
        return s + '\n'

    @staticmethod
    def test(line):
        return Header.test(line)
