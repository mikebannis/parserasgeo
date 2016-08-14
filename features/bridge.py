from tools import fl_int #  , split_by_n_str, pad_left, print_list_by_group, split_block_obs, split_by_n


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


# TODO: possibly move header into Bridge
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
            if line[24:25] == '3':
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


#class CutLine(object):
#    def __init__(self):
#        self.number_pts = None
#        self.points = []  # [(x1,y1),(x2,y2),(x3,y3),...] Values are currently stored as strings
#
#    @staticmethod
#    def test(line):
#        if line.split('=')[0] == 'XS GIS Cut Line':
#            return True
#        return False
#
#    def import_geo(self, line, geo_file):
#        vals = line.split('=')
#        assert vals[0] == 'XS GIS Cut Line' and len(vals) == 2
#        self.number_pts = int(vals[1])
#        line = next(geo_file)
#        while line[:1] == ' ' or line[:1].isdigit():
#            vals = split_by_n_str(line, 16)
#            for i in range(0, len(vals), 2):
#                self.points.append((vals[i], vals[i + 1]))
#            line = next(geo_file)
#        assert self.points != []
#        return line
#
#    def __str__(self):
#        s = 'XS GIS Cut Line=' + str(self.number_pts) + '\n'
#        pts = [self.points[i:i + 2] for i in range(0, len(self.points), 2)]
#        for pt in pts:
#            if len(pt) == 2:
#                s += pt[0][0] + pt[0][1] + pt[1][0] + pt[1][1] + '\n'
#            else:
#                s += pt[0][0] + pt[0][1] + '\n'
#        return s
#
#
#class LastEdit(object):
#    pass
#
#
#class StationElevation(object):
#    def __init__(self):
#        self.num_pts = None
#        self.points = []  # [(sta0, elev0), (sta1, elev1), ... ] Values stored as float/int
#
#    @staticmethod
#    def test(line):
#        if line[:9] == '#Sta/Elev':
#            return True
#        return False
#
#    def import_geo(self, line, geo_file):
#        """
#        Import XS station/elevation points.
#        :param line: current line of geo_file
#        :param geo_file: geometry file object
#        :return: line in geo_file after sta/elev data
#        """
#        self.num_pts = int(line[10:])
#        line = next(geo_file)
#        while line[:1] == ' ' or line[:1].isdigit():
#            vals = split_by_n(line, 8)
#            for i in range(0, len(vals), 2):
#                self.points.append((vals[i], vals[i + 1]))
#            line = next(geo_file)
#        assert len(self.points) == self.num_pts
#        return line
#
#    def __str__(self):
#        s = '#Sta/Elev= ' + str(self.num_pts) + ' \n'
#        # unpack tuples
#        sta_elev_list = [x for tup in self.points for x in tup]
#        # convert to padded columns of 8
#        temp_str = print_list_by_group(sta_elev_list, 8, 10)
#        s += temp_str
#        return s
#
#
#class IEFA(object):
#    # TODO: Add permanence handling
#    def __init__(self):
#        self.num_iefa = None
#        self.type = None
#        self.iefa_list = []
#        self.iefa_permanence = []
#
#    @staticmethod
#    def test(line):
#        if line[:10] == '#XS Ineff=':
#            return True
#        return False
#
#    def import_geo(self, line, geo_file):
#        values = line.split(',')
#        self.num_iefa = int(values[0][-3:])
#        self.type = int(values[1])
#        line = next(geo_file)
#        # Due to possible blank lines in geometry file, all data must be treated as a string
#        while line[:1] == ' ' or line[:1].isdigit():
#            values = split_block_obs(line, 8)
#            assert len(values) % 3 == 0
#            for i in range(0, len(values), 3):
#                self.iefa_list.append((values[i], values[i + 1], values[i + 2]))
#            line = next(geo_file)
#        assert self.num_iefa == len(self.iefa_list)
#
#        return line
#
#    def __str__(self):
#        temp_iefa = [x for tup in self.iefa_list for x in tup]
#        s = '#XS Ineff= ' + str(self.num_iefa) + ' ,' + pad_left(self.type, 2) + ' \n'
#        s += print_list_by_group(temp_iefa, 8, 9)
#        return s
#
#
#class Obstruction(object):
#    def __init__(self):
#        self.num_blocked = None
#        self.blocked_type = None
#        self.blocked = []  # [(start_sta1, end_sta1, elev1), (start_sta2, end_sta2, elev2), ...]
#
#    @staticmethod
#    def test(line):
#        if line[:16] == '#Block Obstruct=':
#            return True
#        return False
#
#    def import_geo(self, line, geo_file):
#        values = line.split(',')
#        self.num_blocked = int(values[0][-3:])
#        self.blocked_type = int(values[1])
#
#        line = next(geo_file)
#        # Due to possible missing elevation all values must be treated as strings
#        while line[:1] == ' ' or line[:1].isdigit():
#            values = split_block_obs(line, 8)
#            assert len(values) % 3 == 0
#            for i in range(0, len(values), 3):
#                self.blocked.append((values[i], values[i + 1], values[i + 2]))
#            line = next(geo_file)
#        assert self.num_blocked == len(self.blocked)
#        return line
#
#    def __str__(self):
#        # unpack tuples
#        blocked_list = [x for tup in self.blocked for x in tup]
#        s = '#Block Obstruct= ' + str(self.num_blocked) + ' ,' + pad_left(self.blocked_type, 2) + ' \n'
#        s += print_list_by_group(blocked_list, 8, 9)
#        return s
#
#
#class Mannings_n(object):
#    def __init__(self):
#        self.values = []  # [(n1, sta1, 0), (n2, sta2, 0), ...]
#        self.horizontal = None  # 0 or -1
#
#    @staticmethod
#    def test(line):
#        if line[:6] == '#Mann=':
#            return True
#        return False
#
#    def import_geo(self, line, geo_file):
#        # Parse manning's n header line
#        fields = line[6:].split(',')
#        assert len(fields) == 3
#        values = [fl_int(x) for x in fields]
#        test_length = values[0]
#        self.horizontal = values[1]
#
#        # Parse stations and n-values
#        line = next(geo_file)
#
#        # Make sure we're still reading n-values
#        while line[:1] == ' ' or line[:1].isdigit():
#            values = split_by_n(line, 8)
#            assert len(values) % 3 == 0
#            for i in range(0, len(values), 3):
#                self.values.append((values[i], values[i + 1], values[i + 2]))
#            line = next(geo_file)
#        assert test_length == len(self.values)
#        return line
#
#    def __str__(self):
#        s = '#Mann= ' + str(len(self.values)) + ' ,{:>2} , 0 \n'.format(self.horizontal)
#        # n-values - unpack tuples
#        n_list = [x for tup in self.values for x in tup]
#        # convert to padded columns of 8
#        temp_str = print_list_by_group(n_list, 8, 9)
#        s += temp_str
#        return s
#
#
#class BankStation(object):
#    def __init__(self):
#        self.left = None
#        self.right = None
#
#    @staticmethod
#    def test(line):
#        if line[:9] == 'Bank Sta=':
#            return True
#        return False
#
#    def import_geo(self, line, geo_file):
#        line = line[9:]
#        values = line.split(',')
#        assert len(values) == 2
#        self.left = fl_int(values[0])
#        self.right = fl_int(values[1])
#        return next(geo_file)
#
#    def __str__(self):
#        return 'Bank Sta=' + str(self.left) + ',' + str(self.right) + '\n'
#
#
#class ExpansionContraction(object):
#    def __init__(self):
#        self.exp_coeff = None
#        self.contract_coeff = None
#
#    @staticmethod
#    def test(line):
#        if line.split('=')[0] == 'XS GIS Cut Line':
#            return True
#        return False
#
#    def import_geo(self, line, geo_file):
#        return line
#
#    def __str__(self):
#        pass
#
#
class Bridge(object):
    def __init__(self, river, reach):
        self.river = river
        self.reach = reach

        # Load all cross sections parts
#        self.cutline = CutLine()
        self.header = Header()
#        self.sta_elev = StationElevation()
#        self.iefa = IEFA()
#        self.mannings_n = Mannings_n()
#        self.obstruct = Obstruction()
#        self.bank_sta = BankStation()
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
