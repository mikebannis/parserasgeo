"""
rasgeotool - tools for importing, modifying, and exporting HEC-RAS geometry files (myproject.g01 etc)

This has NOT been extensively tested.

Mike Bannister 2/24/2016

Version 0.01
"""

from features import CrossSection

# TODO - create geolist object


class CrossSectionNotFound(Exception):
    pass


class RiverReach(object):
    """
    Holds data for River Reach (name, georef'd line)
    """
    def __init__(self):
        self.river_name = None
        self.reach_name = None
        self.geo = []  # list of tuples (x, y)
        self.text_location = None  # tuple of location (x, y)
        self.reverse_text = None  # Boolean

    @staticmethod
    def test(line):
        """
        Tests "line" to see if it is the first line of a river/reach block
        :param line: string
        :return boolean - true if first line of river/reach, otherwise false
        """
        if line[:12] == 'River Reach=':
            return True
        else:
            return False

    # TODO: remove this line once RiverReach is fully implemented
    @staticmethod
    def get_river_reach(line):
        """
        returns name of river and reach from first line of river/reach block.
        :param line: string
        :return: river, reach - strings
        """
        fields = line.split('=')[1].split(',')
        river = fields[0].strip()
        reach = fields[1].strip()
        return river, reach


class OldCrossSection(object):
    """ Holds info for cross section in HEC-RAS geometry file
    """
    def __init__(self, river, reach):
        self.river = river
        self.reach = reach
        self.xs_id = None
        self.node_type = None
        self.lob_length = None
        self.channel_length = None
        self.rob_length = None

        # self.last_edit = ''
        self.horizontal_mann = True
        self.mannings_n = []  # [(n1, sta1, 0), (n2, sta2, 0), ...]

        # ------ GIS cut lines
        self.num_cutline_pts = None
        self.gis_cut_line = []  # [(x1,y1),(x2,y2),(x3,y3),...] Values are currently stored as strings

        # ------ Station/Elevation data
        self.num_sta_elev_pts = None  # int
        self.sta_elev_pts = []  # [(sta0, elev0), (sta1, elev1), ... ] Values stored as float/int

        # --- IEFA
        # self.num_iefa = None
        # self.iefa_type = None
        # self.iefa = []
        # self.iefa_permanence = []  # TODO: implement

        # --- Block obstruction stuff
        # self.num_blocked = None
        # self.blocked_type = None
        # self.blocked = []  # [(start_sta1, end_sta1, elev1), (start_sta2, end_sta2, elev2), ...]
        #
        # self.l_bank_sta = 0
        # self.r_bank_sta = 0

        ### XS Ration Curve stuff

        # self.exp_coeff = 0
        # self.contract_coeff = 0

    def import_geo(self, line, geo_file):
        # # ---------Parse first line
        # fields = line[23:].split(',')
        # assert len(fields) == 5
        # vals = [_fl_int(x) for x in fields]
        # # Node type and cross section id
        # self.node_type = vals[0]
        # self.xs_id = vals[1]
        # # Reach lengths
        # self.lob_length = vals[2]
        # self.channel_length = vals[3]
        # self.rob_length = vals[4]

        # --- Description
        # TODO - make this store the description in a variable
        self.temp_lines0 = ''
        line = next(geo_file)
        while line[:15] != 'XS GIS Cut Line':
            self.temp_lines0 += line
            line = next(geo_file)

        # ---- GIS Cut line
        # vals = line.split('=')
        # assert vals[0] == 'XS GIS Cut Line' and len(vals) == 2
        # self.num_cutline_pts = int(vals[1])
        # line = next(geo_file)
        # while line[:16] != 'Node Last Edited':
        #     vals = _split_by_n_str(line, 16)
        #     for i in range(0, len(vals), 2):
        #         self.gis_cut_line.append((vals[i], vals[i+1]))
        #     line = next(geo_file)
        # assert self.gis_cut_line != []

        # store unused lines - Node Last Edited & sta-elev points
        self.temp_lines = ''
        while line[:9] != '#Sta/Elev':
            self.temp_lines += line
            line = next(geo_file)

        # --- Store sta/elev points
        line = self._import_sta_elev(line, geo_file)

        # --- parse manning's n values
        line = self._import_manning_n(line, geo_file)

        # store more unused lines
        self.temp_lines1 = ''
        while line[:16] != '#Block Obstruct=' and line[:9] != 'Bank Sta=' and line[:10] != '#XS Ineff=':
            self.temp_lines1 += line
            line = next(geo_file)

        # --- Parse IEFA
        # if line[:10] == '#XS Ineff=':
        #     line = self._import_iefa(line, geo_file)

        # store more unused lines
        self.temp_lines1B = ''
        while line[:16] != '#Block Obstruct=' and line[:9] != 'Bank Sta=':
            self.temp_lines1B += line
            line = next(geo_file)

        # --- parse blocked obstructions
        # if line[:16] == '#Block Obstruct=':
        #     line = self._import_blocked(line, geo_file)

        # store more unused lines
        # self.temp_lines2 = ''
        # while line[:9] != 'Bank Sta=':
        #     self.temp_lines2 += line
        #     line = next(geo_file)
        #
        # # import bank stations
        # line = self._import_bank_sta(line, geo_file)

        # store more unused lines
        self.temp_lines3 = ''
        while line != '\n':
            self.temp_lines3 += line
            line = next(geo_file)
        self.temp_lines3 += '\n'

    def _import_bank_sta(self, line, geo_file):
        """ Import bank stations, only one line
        :param line: line from geo file to parse
        :param geo_file: geo_file iterator
        :return: returns the next line in geo_file
        """
        # Strip header
        # line = line[9:]
        # values = line.split(',')
        # assert len(values) == 2
        # self.l_bank_sta = _fl_int(values[0])
        # self.r_bank_sta = _fl_int(values[1])
        # return next(geo_file)

    def _import_blocked(self, line, geo_file):
        """
        Imports reads blocked obstructions info from geo_file
        :param line: next line from geo_file
        :param geo_file: File object
        :return: returns last read lien from geo_file
        """
        # values = line.split(',')
        # self.num_blocked = int(values[0][-3:])
        # self.blocked_type = int(values[1])
        #
        # line = next(geo_file)
        # # Due to possible missing elevation all values must be treated as strings
        # while line[:1] == ' ' or line[:1].isdigit():
        #     values = _split_block_obs(line, 8)
        #     assert len(values) % 3 == 0
        #     for i in range(0, len(values), 3):
        #         self.blocked.append((values[i], values[i + 1], values[i + 2]))
        #     line = next(geo_file)
        # assert self.num_blocked == len(self.blocked)
        # return line

    def _import_iefa(self, line, geo_file):
        """
        Imports reads IEFA info from geo_file
        :param line: next line from geo_file
        :param geo_file: File object
        :return: returns last read line from geo_file
        """
        # TODO: add support for permanent/non-permanent. Currently ignored
        values = line.split(',')
        self.num_iefa = int(values[0][-3:])
        self.iefa_type = int(values[1])
        # if True:
        #     print self.river, self.reach, self.xs_id
        #     print line
        line = next(geo_file)
        # Due to possible blank lines in geometry file, all data must be treated as a string
        while line[:1] == ' ' or line[:1].isdigit():
            # print line
            values = _split_block_obs(line, 8)
            assert len(values) % 3 == 0
            for i in range(0, len(values), 3):
                self.iefa.append((values[i], values[i + 1], values[i + 2]))
            line = next(geo_file)
        assert self.num_iefa == len(self.iefa)
        return line

    def _import_manning_n(self, line, geo_file):
        # Parse manning's n header line
        fields = line[6:].split(',')
        assert len(fields) == 3
        values = [_fl_int(x) for x in fields]
        test_length = values[0]
        self.horizontal_mann = values[1]

        # Parse stations and n-values
        line = next(geo_file)

        # Make sure we're still reading n-values
        while line[:1] == ' ' or line[:1].isdigit():
            values = _split_by_8(line)
            assert len(values) % 3 == 0
            for i in range(0, len(values), 3):
                self.mannings_n.append((values[i], values[i+1], values[i+2]))
            line = next(geo_file)
        assert test_length == len(self.mannings_n)
        return line

    def _import_sta_elev(self, line, geo_file):
        """
        Import XS station/elevation points.
        :param line: current line of geo_file
        :param geo_file: geometry file object
        :return: line in geo_file after sta/elev data
        """
        # #Sta/Elev= 142
        self.num_sta_elev_pts = int(line[10:])
        line = next(geo_file)
        while line[:6] != '#Mann=':
            vals = _split_by_n(line, 8)
            for i in range(0, len(vals), 2):
                self.sta_elev_pts.append((vals[i], vals[i + 1]))
            line = next(geo_file)
        assert len(self.sta_elev_pts) == self.num_sta_elev_pts
        return line

    def __str__(self):
        # Header
        # s = 'Type RM Length L Ch R = '
        # s += str(self.node_type) + ' ,'
        # s += '{:<8}'.format(str(self.xs_id)) + ','
        # s += str(self.lob_length) + ',' + str(self.channel_length) + ',' + str(self.rob_length) + '\n'

        # temp_lines0
        for line in self.temp_lines0:
            s += line

        # GIS cut line
        # s += 'XS GIS Cut Line='+str(self.num_cutline_pts)+'\n'
        # pts = [self.gis_cut_line[i:i+2] for i in range(0, len(self.gis_cut_line), 2)]
        # for pt in pts:
        #     if len(pt) == 2:
        #         s += pt[0][0] + pt[0][1] + pt[1][0] + pt[1][1] + '\n'
        #     else:
        #         s += pt[0][0] + pt[0][1] + '\n'

        # temp_lines
        for line in self.temp_lines:
            s += line

        # --- Sta/elevation points
        s += '#Sta/Elev= ' + str(self.num_sta_elev_pts) + ' \n'
        # unpack tuples
        sta_elev_list = [x for tup in self.sta_elev_pts for x in tup]
        # convert to padded columns of 8 
        temp_str = _print_list_by_group(sta_elev_list, 8, 10)
        s += temp_str

        # --- Manning's n header
        s += '#Mann= ' + str(len(self.mannings_n)) + ' ,{:>2} , 0 \n'.format(self.horizontal_mann)
        # n-values - unpack tuples
        n_list = [x for tup in self.mannings_n for x in tup]
        # convert to padded columns of 8
        temp_str = _print_list_by_group(n_list, 8, 9)
        s += temp_str

        # temp_lines1
        for line in self.temp_lines1:
            s += line

        # --- IEFA
        # if self.num_iefa is not None:
        #     # unpack tuples
        #     iefa_list = [x for tup in self.iefa for x in tup]
        #     s += '#XS Ineff= ' + str(self.num_iefa) + ' ,' + _pad_left(self.iefa_type, 2) + ' \n'
        #     s += _print_list_by_group(iefa_list, 8, 9)

        for line in self.temp_lines1B:
            s += line

        # # Blocked obstructions
        # if self.num_blocked is not None:
        #     # unpack tuples
        #     blocked_list = [x for tup in self.blocked for x in tup]
        #     s += '#Block Obstruct= ' + str(self.num_blocked) + ' ,' + _pad_left(self.blocked_type, 2) + ' \n'
        #     s += _print_list_by_group(blocked_list, 8, 9)

        # temp_lines2
        for line in self.temp_lines2:
            s += line

        # Banks stations
        # s += 'Bank Sta='+str(self.l_bank_sta)+','+str(self.r_bank_sta)+'\n'

        # temp_lines3
        for line in self.temp_lines3:
            s += line

        return s


def import_ras_geo(geo_filename):
    # add  test for file existence
    geo_list = []
    num_xs = 0
    num_unknown = 0
    river = None
    reach = None

    with open(geo_filename, 'rt') as geo_file:
        for line in geo_file:
            if RiverReach.test(line):
                river, reach = RiverReach.get_river_reach(line)
                #print river, reach
                geo_list.append(line)
                num_unknown += 1
            elif _xs_test(line):
                xs = CrossSection(river, reach)
                xs.import_geo(line, geo_file)
                num_xs += 1
                geo_list.append(xs)
            else:
                # Unknown line encountered. Store it as text.
                geo_list.append(line)
                num_unknown += 1
    #print str(num_xs)+' cross sections imported'
    #print str(num_unknown) + ' unknown lines imported'
    return geo_list


def export_ras_geo(out_geo_filename, geo_list):
    with open(out_geo_filename, 'wt') as outfile:
        for line in geo_list:
            outfile.write(str(line))


def return_xs_by_id(geo_list, xs_id):
    for item in geo_list:
        if isinstance(item, CrossSection):
            if item.xs_id == xs_id:
                return item
    raise CrossSectionNotFound


def return_xs(geo_list, xs_id, river, reach):
    for item in geo_list:
        if isinstance(item, CrossSection):
            if item.xs_id == xs_id and item.river == river and item.reach == reach:
                return item
    raise CrossSectionNotFound


def extract_xs(geo_list):
    """
    :param geo_list: list of RAS geometry from import_ras_geo()
    :return: returns list of all cross sections in geo_list
    """
    new_geo_list = []
    for item in geo_list:
        if isinstance(item, CrossSection):
            new_geo_list.append(item)
    return new_geo_list


def number_xs(geo_list):
    """
    Returns the number of cross sections in geo_list
    :param geo_list: list from import_ras_geo
    :return: number (int) of XS in geolist
    """
    xs_list = extract_xs(geo_list)
    return len(xs_list)


def is_xs_duplicate(geo_list, xs_id):
    """
    Checks for duplicate cross sections in geo_list
    rasises CrossSectionNotFound if xs_id is not found
    :param geo_list: from import_ras_geo
    :return: True if duplicate
    """
    xs_list = extract_xs(geo_list)
    count = 0
    for xs in xs_list:
        if xs.xs_id == xs_id:
            count += 1
    if count > 1:
        return True
    elif count == 1:
        return False
    else:
        raise CrossSectionNotFound


def _xs_test(test_line):
    if test_line[0:23] == 'Type RM Length L Ch R =':
        if test_line[24:25] == '1':
            return True
    return False


def _split_by_8(line):
    return _split_by_n(line, 8)


def _split_by_16(line):
    return _split_by_n(line, 16)


def _split_by_n(line, n):
    """

    :param line:
    :param n:
    :return:
    """
    values = []
    line = line[:-1]
    length = len(line)
    for i in range(0, length, n):
        if i+n < length:
            values.append(_fl_int(line[i:i+n]))
        else:
            values.append(_fl_int(line[i:]))
    return values


def _split_by_n_str(line, n):
    """
    Splits line in to a list of n length strings. This differs from _split_by_n(
    :param line:  string
    :param n: int
    :return: list of strings
    """
    values = []
    line = line[:-1]
    length = len(line)
    for i in range(0, length, n):
        if i+n < length:
            values.append(line[i:i+n])
        else:
            values.append(line[i:])
    return values


def _split_block_obs(line, n):
    """
    Also used for iefa
    :param line:
    :param n:
    :return:
    """
    values = []
    line = line[:-1]
    length = len(line)
    for i in range(0, length, n):
        if i+n < length:
            new_value = line[i:i+n].strip()
        else:
            new_value = line[i:].strip()
        if new_value == '':
            values.append(new_value)
        else:
            values.append(_fl_int(new_value))

    return values

def _fl_int(value):
    """ Converts string to either float or int depending on precense of decimal point.
    The RAS geo file does not have a decimal place if it is not needed. weird.
    :param value: string to convert
    :return: returns int or float
    """
    x = float(value)
    if x.is_integer():
        x = int(x)
    return x


def _print_list_by_group(values, width, num_columns):
    """
    Returns string of items in list values padded left to width in width, with num_columns of items per line.
    Lines are separated by newlines. No error thrown if value[i] width exceeds width.

    :param values: list of values to convert to string
    :param width: width of white space padded columns
    :param num_columns: number of columns per line
    :return: string broken into multiple lines with \n
    """
    length = len(values)
    s = ''
    for row in range(0, length, num_columns):
        # Make sure we don't overrun length of values if len(values) % num_columns != 0
        last_column = length - row
        if last_column > num_columns:
            last_column = num_columns
        # Loop through and add every item in the row
        for column in range(0, last_column):
            temp = ('{:>'+str(width)+'}').format(values[row + column])

            # Strip leading 0 from 0.12345 - with or without spaces or '-'
            if temp[:2] == '0.':
                temp = temp[1:]
            temp = temp.replace(' 0.', '  .')
            temp = temp.replace('-0.', ' -.')

            s += temp
        # End of row, add newline
        s += '\n'
    return s


def _pad_left(guts, pad_number):
    """
    pads guts (left) with spaces up to pad_number
    :param guts: anything
    :param pad_number: int
    :return: string
    """
    return ('{:>'+str(pad_number)+'}').format(guts)


def main():
    infile = 'geos/201601BigDryCreek.g27'
    #infile = 'geos/GHC_FHAD.g01'
    #infile = 'test/CCRC_prg_test.g01'
    infile = 'geos/SBK_PMR.g02'
    infile = 'geos/GHC_working.g43'
    outfile = 'test/test.out'

    geo_list = import_ras_geo(infile)

    xs_list = extract_xs(geo_list)
    if True:
        iefa_count = 0
        for xs in xs_list:
            if xs.obstruct.blocked_type is not None:
                iefa_count +=1
                print '\nXS ID:', xs.header.xs_id
                # print xs.iefa.type, xs.iefa.iefa_list
                print xs.obstruct.blocked_type, xs.obstruct.num_blocked, xs.obstruct.blocked
                print xs.bank_sta.right, xs.bank_sta.left

            #print xs.mannings_n
            # print xs.num_blocked
            # print xs.blocked_type
            # print xs.blocked
            # print xs.num_sta_elev_pts
            # print len(xs.sta_elev_pts)
            # print xs.sta_elev_pts
            # print xs.num_iefa
            # print xs.iefa_type
            # print xs.iefa
    print len(xs_list)
    # print iefa_count, 'cross sections with iefa'

    export_ras_geo(outfile, geo_list)

    import filecmp
    import subprocess
    if filecmp.cmp(infile, outfile, shallow=False):
        print 'Input and output files are identical'
    else:
        print 'WARNING: files are different!!!'
        subprocess.Popen(["diff", infile, outfile])

if __name__ == '__main__':
    main()
