from .tools import fl_int, split_by_n_str, pad_left, print_list_by_group, split_block_obs, split_by_n
from .description import Description
from math import sqrt, cos, radians

# Global debug, this is set when initializing CrossSection
DEBUG = False

class ChannelNError(Exception):
    """
    An error to raise if the user attempts to change channel n values without first defining the channel
    """
    pass

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

class Levee(object):
    """
    Levees. This is poorly implemented and only grabs the line past the "=" as a string
    """
    def __init__(self):
        self.value = None

    @staticmethod
    def test(line):
        if line.split('=')[0] == 'Levee':
            return True
        return False

    def import_geo(self, line, geo_file):
        self.value = line.split('=')[1]
        return next(geo_file)

    def __str__(self):
        return 'Levee=' + self.value  # + '\n' - not needed since it's just a dumb string (with the \n)

class RatingCurve(object):
    """
    Rating Curves. This is poorly implemented and only grabs the values on the first line and not the
    curve itself.
    """
    def __init__(self):
        self.value1 = None
        self.value2 = None

    @staticmethod
    def test(line):
        if line.split('=')[0] == 'XS Rating Curve':
            return True
        return False

    def import_geo(self, line, geo_file):
        temp = line.split('=')[1].split(',')
        self.value1 = int(temp[0])
        self.value2 = int(temp[1])
        return next(geo_file)

    def __str__(self):
        return 'XS Rating Curve= ' + str(self.value1) + ' ,' + str(self.value2) + '\n'


class Skew(object):
    """
    Cross section skew angle
    """
    def __init__(self):
        self.angle = None

    @staticmethod
    def test(line):
        if line.split('=')[0] == 'Skew Angle':
            return True
        return False

    def import_geo(self, line, geo_file):
        self.angle = float(line.split('=')[1])
        return next(geo_file)

    def __str__(self):
        return 'Skew Angle= '+str(fl_int(self.angle))+' \n'


# TODO: possibly move header into CrossSection
class Header(object):
    def __init__(self):
        # TODO: change xs_id to station
        self.xs_id = None
        self.node_type = None
        self.lob_length = None
        self.channel_length = None
        self.rob_length = None

    @staticmethod
    def test(line):
        if line[:23] == 'Type RM Length L Ch R =':
            if line[24:25] == '1':
                return True
        return False

    def import_geo(self, line, geo_file):
        fields = line[23:].split(',')
        assert len(fields) == 5
        vals = [self._header_fl_int(x) for x in fields]
        # Node type and cross section id
        self.node_type = vals[0]
        # TODO - RAS allows Xs ids to be in the format '225.20', fl_int() strips trailing zeros
        # This should be fixed at some point, but may break compatibility with other things
        # like the FHAD tools, and probably things within prg
        self.xs_id = vals[1]
        # Reach lengths
        self.lob_length = vals[2]
        self.channel_length = vals[3]
        self.rob_length = vals[4]

        if DEBUG:
            print('-'*30)
            print('Importing XS:', self.xs_id)

        return next(geo_file)

    ### TODO: Handle null reach lengths appropriately
    @staticmethod
    def _header_fl_int(x):
        """ 
        Reach lengths may be blank at the downstream end. This looks out for 
        that scenario and returns 0. This will break the ability to reproduce 
        some geometry file to the character and should be updated at some point!
        """
        if x == '' or x == '\n':
            return 0
        else:
            return fl_int(x)
        
    def __str__(self):
        s = 'Type RM Length L Ch R = '
        s += str(self.node_type) + ' ,'
        s += '{:<8}'.format(str(self.xs_id)) + ','
        s += str(self.lob_length) + ',' + str(self.channel_length) + ',' + str(self.rob_length) + '\n'
        return s


class CutLine(object):
    def __init__(self):
        self.number_pts = None
        self.points = []  # [(x1,y1),(x2,y2),(x3,y3),...] Values are currently stored as strings

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
        while line[:1] == ' ' or line[:1].isdigit() or line[:1] == '-' or line[:1] == '.':
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
        self.points = []  # [(sta0, elev0), (sta1, elev1), ... ] Values stored as float/int

    @staticmethod
    def test(line):
        if line[:9] == '#Sta/Elev':
            return True
        return False

    def elevation(self, sta):
        """
        Returns elevation of point at station 'station'
        Raises AttributeError if station is not foudn
        :param sta: float, station of interest
        :return: double, elevation
        """
        # TODO - implement more efficient search
        for pt in self.points:
            if pt[0] == sta:
                return pt[1]
        raise AttributeError('No station matching ' + str(sta) + ' in current XS.')


    def import_geo(self, line, geo_file):
        """
        Import XS station/elevation points.
        :param line: current line of geo_file
        :param geo_file: geometry file object
        :return: line in geo_file after sta/elev data
        """
        self.num_pts = int(line[10:])
        line = next(geo_file)
        while line[:1] == ' ' or line[:1].isdigit() or line[:1] == '-' or line[:1] == '.':
            vals = split_by_n(line, 8)
            for i in range(0, len(vals), 2):
                self.points.append((vals[i], vals[i + 1]))
            line = next(geo_file)
        if DEBUG:
            print('len(self.points)=', len(self.points), 'self.num_pts=', self.num_pts)
            # print self.points
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
        while line[:1] == ' ' or line[:1].isdigit() or line[:1] == '-' or line[:1] == '.':
            values = split_block_obs(line, 8)
            assert len(values) % 3 == 0
            for i in range(0, len(values), 3):
                self.iefa_list.append((values[i], values[i + 1], values[i + 2]))
            line = next(geo_file)
        assert self.num_iefa == len(self.iefa_list)

        # Process IEFA permanence
        if line != 'Permanent Ineff=\n':
            raise ValueError('Permanent Ineff= does not follow IEFA in geometry file. Aborting.')
        line = next(geo_file)
        while line[:1] == ' ':
            values = line.split()
            for value in values:
                if value == 'T':
                    self.iefa_permanence.append(True)
                elif value == 'F':
                    self.iefa_permanence.append(False)
                else:
                    raise ValueError(value + ' found in IEFA permanence filed. Should be T or F. Aborting')
            line = next(geo_file)
        assert len(self.iefa_list) == len(self.iefa_permanence)

        return line

    def __str__(self):
        temp_iefa = [x for tup in self.iefa_list for x in tup]
        s = '#XS Ineff= ' + str(self.num_iefa) + ' ,' + pad_left(self.type, 2) + ' \n'
        s += print_list_by_group(temp_iefa, 8, 9)
        s += 'Permanent Ineff=\n'
        for value in self.iefa_permanence:
            if value:
                s += '       T'
            else:
                s += '       F'
        s += '\n'
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
        while line[:1] == ' ' or line[:1].isdigit() or line[:1] == '-' or line[:1] == '.':
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


class Mannings_n(object):
    def __init__(self):
        self.values = []  # [(sta1, n1, 0), (sta2, n2, 0), ...]
        self.horizontal = None  # 0 or -1

    @staticmethod
    def test(line):
        if line[:6] == '#Mann=':
            return True
        return False

    def import_geo(self, line, geo_file):
        # Parse manning's n header line
        fields = line[6:].split(',')
        assert len(fields) == 3
        values = [fl_int(x) for x in fields]
        test_length = values[0]
        self.horizontal = values[1]

        # Parse stations and n-values
        line = next(geo_file)

        # Make sure we're still reading n-values
        while line[:1] == ' ' or line[:1].isdigit() or line[:1] == '-'or line[:1] == '.':
            values = split_by_n(line, 8)
            if len(values) % 3 != 0:
                raise ValueError ('Error processing n-values: ' + line + '\n' + str(values))
            for i in range(0, len(values), 3):
                self.values.append((values[i], values[i + 1], values[i + 2]))
            line = next(geo_file)
        assert test_length == len(self.values)
        return line

    def __str__(self):
        s = '#Mann= ' + str(len(self.values)) + ' ,{:>2} , 0 \n'.format(self.horizontal)
        # n-values - unpack tuples
        n_list = [x for tup in self.values for x in tup]
        # convert to padded columns of 8
        temp_str = print_list_by_group(n_list, 8, 9)
        s += temp_str
        return s

    def check_for_duplicate_n_values(self):
        """
        Checks cross section for two n-value changes at the same station. This does happen, I'm not sure how, and
        HEC-RAS is okay with it. Raises ValueError if self.mannings_n is empty
        :return: Returns a list of station with multiple n-value changes if they exist, otherwise returns None
        """
        n_values = list(self.values)
        if n_values == []:
            raise ValueError('Cross section has no Manning\'s n values.')
        errors = []
        last_station = n_values.pop(0)[0]
        for n_value in n_values:
            if n_value[0] == last_station:
                errors.append(last_station)
            last_station = n_value[0]
        if errors != []:
            return errors
        else:
            return None

    def check_for_redundant_n_values(self):
        """
        Checks for redundant n-value changes, e.g. 0.035 then 0.035. Raises ValueError if self.mannings_n is empty
        :return: Returns a list of station with redundant n-value changes if they exist, otherwise returns None
        """
        n_values = list(self.values)
        if n_values == []:
            raise ValueError('Cross section has no Manning\'s n values.')
        errors = []
        last_n_value = n_values.pop(0)[1]
        for n_value in n_values:
            if n_value[1] == last_n_value:
                errors.append(n_value[0])
            last_n_value = n_value[1]
        if errors != []:
            return errors
        else:
            return None


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

# TODO: implement contraction/expansion
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
    def __init__(self, river, reach, debug=False):
        # Set global debug
        global DEBUG
        DEBUG = debug

        self.river = river
        self.reach = reach

        # Load all cross sections parts
        # TODO: Add "Node Name=" tag, see harvard gulch/dry gulch for example
        self.cutline = CutLine()
        self.header = Header()
        self.description = Description()
        self.sta_elev = StationElevation()
        self.iefa = IEFA()
        self.mannings_n = Mannings_n()
        self.obstruct = Obstruction()
        self.bank_sta = BankStation()
        self.skew = Skew()
        self.levee = Levee()
        self.rating_curve = RatingCurve()
        self.parts = [self.header, self.description, self.cutline, self.iefa, self.mannings_n, self.obstruct, self.bank_sta,
                      self.sta_elev, self.skew, self.levee, self.rating_curve]

        self.geo_list = []  # holds all parts and unknown lines (as strings)
        
        # used to define n-values in the channel only (i.e. between the bank stations)
        # gets defined in define_channel_n
        self.channel_n = None
        
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

    def cut_line_ratio(self):
        """
        Returns ratio of xs geometry length to cutline length.
        Raises AttributeError if either are empty
        """
        # TODO - correct for skew!
        if self.cutline.points == []:
            raise AttributeError('Cross section does not have a defined cutline')

        if self.sta_elev.points == []:
            raise AttributeError('Cross section does not have a geometry')

        length = self.sta_elev.points[-1][0] - self.sta_elev.points[0][0]
        # the line below should work, but needs to be tested
        #length = length/cos(radians(self.skew.angle))

        # Add up length of all segments of the cutline
        cl_length = 0.0
        last_pt = self.cutline.points[0]
        for pt in self.cutline.points[1:]:
            dist = sqrt((float(pt[0])-float(last_pt[0]))**2 + (float(pt[1])-float(last_pt[1]))**2)
            cl_length += dist
            last_pt = pt

        return cl_length/length
    
    def define_channel_n(self):
        """
        Checks if the Manning's n is defined at the bank stations
        If they are not defined at the bank stations, add Manning's n values at those points that correspond with the nearest-left n-value
        
        :returns: None
        """
        manning_stations = [x[0] for x in self.mannings_n.values]
        
        for bank in [self.bank_sta.left, self.bank_sta.right]:
            # if the bank station is not in the list, grab the Manning's n to the left
            if bank not in manning_stations:
                leftward_manning_all = [x[1] for x in self.mannings_n.values if x[0] < bank]
                leftward_index = len(leftward_manning_all)
                leftward_manning_nearest = leftward_manning_all[-1]
                manning_insert = (bank, leftward_manning_nearest, 0)
                self.mannings_n.values.insert(leftward_index, manning_insert)
        
        # do not pull the n-value at the right bank because that defines the n-values to the right of the bank
        self.channel_n = [x for x in self.mannings_n.values if (x[0] >= self.bank_sta.left and x[0] <self.bank_sta.right)]        
            
    def alter_channel_n(self, scalar):
        """
        Alters the channel n-values by a scaling factor
        
        :param scalar: a number by which the channel n values are scaled
        :returns: None
        :raises ChannelNError: raises error if channel_n not defined
        """
        
        if self.channel_n is not None:
            new_channel_n = []
            for n in self.channel_n:
                temp_n = n[1]*scalar
                temp_tuple = (n[0], temp_n, 0)
                new_channel_n.append(temp_tuple)
            
            for ind, old_n in enumerate(self.mannings_n.values):
                for new_n in new_channel_n:
                    if old_n[0] == new_n[0]:
                        self.mannings_n.values.pop(ind)
                        self.mannings_n.values.insert(ind, new_n)
                        break
                
            self.channel_n = new_channel_n
        else:
            raise ChannelNError('The channel is undefined. Run define_channel_n before using alter_channel_n')
            
    def alter_overbank_n(self, scalar):
        """
        Alters the overbank n-values by a scaling factor.
        
        :param scalar: a number by which the channel n values are scaled
        :raises ChannelNError: raises error if channel_n not defined
        """
        
        if self.channel_n is None:
            raise ChannelNError('The channel is undefined. Run define_channel_n before using alter_overbank_n')
        
        channel_n_stations = [x[0] for x in self.channel_n]
        for ind, old_n in enumerate(self.mannings_n.values):
            if old_n[0] in channel_n_stations:
                pass
            else:
                temp_n = old_n[1]*scalar
                temp_tuple = (old_n[0], temp_n, 0)
                self.mannings_n.values.pop(ind)
                self.mannings_n.values.insert(ind, temp_tuple)

    def __str__(self):
        s = ''
        for line in self.geo_list:
            s += str(line)
        return s + '\n'

    @staticmethod
    def test(line):
        return Header.test(line)
