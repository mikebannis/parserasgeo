from .tools import  split_by_n_str
# Global debug, this is set when initializing RiverReach
DEBUG = False

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


class RiverReach(object):
    def __init__(self, debug=False):
        # Set global debug
        global DEBUG
        DEBUG=debug

        # Load all river/reach parts
        self.header = Header()
        self.geo = Geo()
        self.text = Text()

        self.parts = [self.header, self.geo, self.text]

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


class Header(object):
    def __init__(self):
        self.river_name = None
        self.reach_name = None

    @staticmethod
    def test(line):
        if line[:12] == 'River Reach=':
            return True
        return False

    def import_geo(self, line, geo_file):
        fields = line[12:].split(',')
        assert len(fields) == 2
        self.river_name = fields[0]
        self.reach_name = fields[1][:-1]
        if DEBUG:
            print('*'*50)
            print('Imported river/reach:', self.river_name, '/', self.reach_name)
        return next(geo_file)

    def __str__(self):
        s = 'River Reach=' + self.river_name + ',' + self.reach_name + '\n'
        return s


class Geo(object):
    def __init__(self):
        self.num_points = None  # int
        self.points = []  # [(x1, y1), (x2, y2), ... ] all values are strings so that the exported file is identical

    @staticmethod
    def test(line):
        if line[:9] == 'Reach XY=':
            return True
        return False

    def import_geo(self, line, geo_file):
        self.num_points = int(line[9:].strip())
        line = next(geo_file)
        while line[:1] == ' ' or line[:1].isdigit():
            vals = split_by_n_str(line, 16)
            for i in range(0, len(vals), 2):
                self.points.append((vals[i], vals[i + 1]))
            line = next(geo_file)
        # print self.num_points, len(self.points)
        assert self.num_points == len(self.points)
        return line

    def __str__(self):
        s = 'Reach XY= ' + str(self.num_points) + ' \n'
        pts = [self.points[i:i + 2] for i in range(0, len(self.points), 2)]
        for pt in pts:
            if len(pt) == 2:
                s += pt[0][0] + pt[0][1] + pt[1][0] + pt[1][1] + '\n'
            else:
                s += pt[0][0] + pt[0][1] + '\n'
        return s


class Text(object):
    def __init__(self):
        self.position = None  # (x, y) as a string
        self.reverse = None  # int, 0 (normal) or -1 (reversed)

    @staticmethod
    def test(line):
        if line[:13] == 'Rch Text X Y=':
            return True
        return False

    def import_geo(self, line, geo_file):
        fields = line[13:].split(',')
        assert len(fields) == 2
        x = fields[0]
        y = fields[1][:-1]
        self.position = (x, y)
        line = next(geo_file)
        assert line[:19] == 'Reverse River Text='
        self.reverse = int(line[19:])
        return next(geo_file)

    def __str__(self):
        s = 'Rch Text X Y=' + self.position[0] + ',' + self.position[1] + '\n'
        s += 'Reverse River Text='
        if self.reverse == 0:
            s += ' 0 \n'
        else:
            s += '-1 \n'
        return s
