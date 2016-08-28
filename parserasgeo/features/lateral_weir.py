from tools import fl_int #  , split_by_n_str, pad_left, print_list_by_group, split_block_obs, split_by_n
from description import Description

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

        self.station = None
        self.node_type = None
        self.value1 = None
        self.value2 = None
        self.value3 = None

    @staticmethod
    def test(line):
        if line[:23] == 'Type RM Length L Ch R =':
            if line[24:25] == '6':
                return True
        return False

    def import_geo(self, line, geo_file):
        fields = line[23:].split(',')
        # print line, fields
        assert len(fields) == 5
        # vals = [fl_int(x) for x in fields]
        # Node type and cross section id
        self.node_type = fl_int(fields[0])
        self.station = fl_int(fields[1])
        # TODO: Not sure what these are yet
        self.value1 = fields[2]
        self.value2 = fields[3]
        self.value3 = fields[4]
        return next(geo_file)

    def __str__(self):
        s = 'Type RM Length L Ch R = '
        s += str(self.node_type) + ' ,'
        s += '{:<8}'.format(str(self.station)) + ','
        s += str(self.value1) + ',' + str(self.value2) + ',' + str(self.value3)  # + '\n' TODO: Add this back it later once the remainder of the 
                                                                                                    # header if figured out
        return s

class LateralWeir(object):
    def __init__(self, river, reach):
        self.river = river
        self.reach = reach

        # Load all cross sections parts
#        self.cutline = CutLine()
        self.header = Header()
        self.description = Description()
#        self.sta_elev = StationElevation()
#        self.iefa = IEFA()
#        self.mannings_n = Mannings_n()
#        self.obstruct = Obstruction()
#        self.bank_sta = BankStation()
        self.parts = [self.header, self.description]

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
