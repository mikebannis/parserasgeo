from tools import fl_int, split_by_n_str, pad_left, print_list_by_group, split_block_obs, split_by_n


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


# TODO: possibly move header into CrossSection
class Header(object):
    def __init__(self):

        self.xs_id = None
        self.node_type = None
        self.lob_length = None
        self.channel_length = None
        self.rob_length = None

    @staticmethod
    def test(line):
        if line[0:23] == 'Type RM Length L Ch R =':
            if line[24:25] == '1':
                return True
        return False

    def import_geo(self, line, geo_file):
        fields = line[23:].split(',')
        assert len(fields) == 5
        vals = [fl_int(x) for x in fields]
        # Node type and cross section id
        self.node_type = vals[0]
        self.xs_id = vals[1]
        # Reach lengths
        self.lob_length = vals[2]
        self.channel_length = vals[3]
        self.rob_length = vals[4]
        return next(geo_file)

    def __str__(self):
        s = 'Type RM Length L Ch R = '
        s += str(self.node_type) + ' ,'
        s += '{:<8}'.format(str(self.xs_id)) + ','
        s += str(self.lob_length) + ',' + str(self.channel_length) + ',' + str(self.rob_length) + '\n'
        return s


class CutLine(object):
    def __init__(self):
        self.number_pts = None
        self.points = []

    @staticmethod
    def test(line):
        if line.split('=')[0] == 'XS GIS Cut Line':
            return True
        return False

    def import_geo(self, line, geo_file):
        vals = line.split('=')
        assert vals[0] == 'XS GIS Cut Line' and len(vals) == 2
        self.number_pts = int(vals[1])
        line = next(geo_file)
        while line[:1] == ' ' or line[:1].isdigit():
            vals = split_by_n_str(line, 16)
            for i in range(0, len(vals), 2):
                self.points.append((vals[i], vals[i + 1]))
            line = next(geo_file)
        assert self.points != []
        return line

    def __str__(self):
        s = 'XS GIS Cut Line=' + str(self.number_pts) + '\n'
        pts = [self.points[i:i + 2] for i in range(0, len(self.points), 2)]
        for pt in pts:
            if len(pt) == 2:
                s += pt[0][0] + pt[0][1] + pt[1][0] + pt[1][1] + '\n'
            else:
                s += pt[0][0] + pt[0][1] + '\n'
        return s


class LastEdit(object):
    pass


class StationElevation(object):
    def __init__(self):
        self.num_pts = None
        self.points = []

    @staticmethod
    def test(line):
        if line[:9] == '#Sta/Elev':
            return True
        return False

    def import_geo(self, line, geo_file):
        """
        Import XS station/elevation points.
        :param line: current line of geo_file
        :param geo_file: geometry file object
        :return: line in geo_file after sta/elev data
        """
        self.num_pts = int(line[10:])
        line = next(geo_file)
        while line[:1] == ' ' or line[:1].isdigit():
            vals = split_by_n(line, 8)
            for i in range(0, len(vals), 2):
                self.points.append((vals[i], vals[i + 1]))
            line = next(geo_file)
        assert len(self.points) == self.num_pts
        return line

    def __str__(self):
        s = '#Sta/Elev= ' + str(self.num_pts) + ' \n'
        # unpack tuples
        sta_elev_list = [x for tup in self.points for x in tup]
        # convert to padded columns of 8
        temp_str = print_list_by_group(sta_elev_list, 8, 10)
        s += temp_str
        return s


class IEFA(object):
    # TODO: Add permanence handling
    def __init__(self):
        self.num_iefa = None
        self.type = None
        self.iefa_list = []
        self.iefa_permanence = []

    @staticmethod
    def test(line):
        if line[:10] == '#XS Ineff=':
            return True
        return False

    def import_geo(self, line, geo_file):
        values = line.split(',')
        self.num_iefa = int(values[0][-3:])
        self.type = int(values[1])
        line = next(geo_file)
        # Due to possible blank lines in geometry file, all data must be treated as a string
        while line[:1] == ' ' or line[:1].isdigit():
            values = split_block_obs(line, 8)
            assert len(values) % 3 == 0
            for i in range(0, len(values), 3):
                self.iefa_list.append((values[i], values[i + 1], values[i + 2]))
            line = next(geo_file)
        assert self.num_iefa == len(self.iefa_list)

        return line

    def __str__(self):
        temp_iefa = [x for tup in self.iefa_list for x in tup]
        s = '#XS Ineff= ' + str(self.num_iefa) + ' ,' + pad_left(self.type, 2) + ' \n'
        s += print_list_by_group(temp_iefa, 8, 9)
        return s


class Obstruction(object):
    def __init__(self):
        self.num_blocked = None
        self.blocked_type = None
        self.blocked = []  # [(start_sta1, end_sta1, elev1), (start_sta2, end_sta2, elev2), ...]

    @staticmethod
    def test(line):
        if line[:16] == '#Block Obstruct=':
            return True
        return False

    def import_geo(self, line, geo_file):
        values = line.split(',')
        self.num_blocked = int(values[0][-3:])
        self.blocked_type = int(values[1])

        line = next(geo_file)
        # Due to possible missing elevation all values must be treated as strings
        while line[:1] == ' ' or line[:1].isdigit():
            values = split_block_obs(line, 8)
            assert len(values) % 3 == 0
            for i in range(0, len(values), 3):
                self.blocked.append((values[i], values[i + 1], values[i + 2]))
            line = next(geo_file)
        assert self.num_blocked == len(self.blocked)
        return line

    def __str__(self):
        # unpack tuples
        blocked_list = [x for tup in self.blocked for x in tup]
        s = '#Block Obstruct= ' + str(self.num_blocked) + ' ,' + pad_left(self.blocked_type, 2) + ' \n'
        s += print_list_by_group(blocked_list, 8, 9)
        return s


class BankStation(object):
    def __init__(self):
        self.left = None
        self.right = None

    @staticmethod
    def test(line):
        if line[:9] == 'Bank Sta=':
            return True
        return False

    def import_geo(self, line, geo_file):
        line = line[9:]
        values = line.split(',')
        assert len(values) == 2
        self.left = fl_int(values[0])
        self.right = fl_int(values[1])
        return next(geo_file)

    def __str__(self):
        return 'Bank Sta=' + str(self.left) + ',' + str(self.right) + '\n'


class ExpansionContraction(object):
    def __init__(self):
        self.exp_coeff = None
        self.contract_coeff = None

    @staticmethod
    def test(line):
        if line.split('=')[0] == 'XS GIS Cut Line':
            return True
        return False

    def import_geo(self, line, geo_file):
        return line

    def __str__(self):
        pass


class CrossSection(object):
    def __init__(self, river, reach):
        self.river = river
        self.reach = reach

        # Load all cross sections parts
        self.cutline = CutLine()
        self.header = Header()
        self.sta_elev = StationElevation()
        self.iefa = IEFA()
        self.obstruct = Obstruction()
        self.bank_sta = BankStation()
        self.parts = [self.header, self.cutline, self.iefa, self.obstruct, self.bank_sta, self.sta_elev]

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

    def test(self, line):
        return self.header.test(line)
