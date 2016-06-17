"""
rasgeotool - tools for importing, modifying, and exporting HEC-RAS geometry files (myproject.g01 etc)

This has NOT been extensively tested.

Mike Bannister 2/24/2016

Version 0.01
"""


class CrossSectionNotFound(Exception):
    pass


class CrossSection(object):
    """ Holds info for cross section in HEC-RAS geometry file
    """
    def __init__(self):
        self.xs_id = None
        self.node_type = None
        self.lob_length = None
        self.channel_length = None
        self.rob_length = None

        self.last_edit = ''
        self.sta_elev = []
        self.horizontal_mann = True
        self.mannings_n = []

        # ------ GIS cut lines
        self.num_cutline_pts = None
        self.gis_cut_line = []  # [(x1,y1),(x2,y2),(x3,y3),...] Values are currently stored as strings

        ##### IEFA stuff

        #### Block obstruction stuff

        self.l_bank_sta = 0
        self.r_bank_sta = 0

        ### XS Ration Curve stuff

        self.exp_coeff = 0
        self.contract_coeff = 0

    def import_geo(self, line, geo_file):
        # ---------Parse first line
        fields = line[23:].split(',')
        assert len(fields) == 5
        vals = [_fl_int(x) for x in fields]
        # Node type and cross section id
        self.node_type = vals[0]
        self.xs_id = vals[1]
        # Reach lengths
        self.lob_length = vals[2]
        self.channel_length = vals[3]
        self.rob_length = vals[4]

        # --- Description
        self.temp_lines0 = ''
        line = next(geo_file)
        while line[:15] != 'XS GIS Cut Line':
            self.temp_lines0 += line
            line = next(geo_file)

        # ---- GIS Cut line
        vals = line.split('=')
        assert vals[0] == 'XS GIS Cut Line' and len(vals) == 2
        self.num_cutline_pts = int(vals[1])
        line = next(geo_file)
        while line[:16] != 'Node Last Edited':
            vals = _split_by_n_str(line,16)
            for i in range(0, len(vals), 2):
                self.gis_cut_line.append((vals[i], vals[i+1]))
            line = next(geo_file)
        assert self.gis_cut_line is not []

        # store unused lines
        self.temp_lines = ''
        while line[:5] != '#Mann':
            self.temp_lines += line
            line = next(geo_file)

        # --- parse manning's n values
        line = self._import_manning_n(line, geo_file)

        # store more unused lines
        self.temp_lines2 = ''
        while line[:9] != 'Bank Sta=':
            self.temp_lines2 += line
            line = next(geo_file)

        # import bank stations
        line = self._import_bank_sta(line, geo_file)

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
        line = line[9:]
        values = line.split(',')
        assert len(values) == 2
        self.l_bank_sta = _fl_int(values[0])
        self.r_bank_sta = _fl_int(values[1])
        return next(geo_file)

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

    def __str__(self):
        # Header
        s = 'Type RM Length L Ch R = '
        s += str(self.node_type) + ' ,'
        s += '{:<8}'.format(str(self.xs_id)) + ','
        s += str(self.lob_length) + ',' + str(self.channel_length) + ',' + str(self.rob_length) + '\n'

        # temp_lines0
        for line in self.temp_lines0:
            s += line

        # GIS cut line
        s += 'XS GIS Cut Line='+str(self.num_cutline_pts)+'\n'
        pts = [self.gis_cut_line[i:i+2] for i in range(0, len(self.gis_cut_line), 2)]
        for pt in pts:
            if len(pt) == 2:
                s += pt[0][0] + pt[0][1] + pt[1][0] + pt[1][1] + '\n'
            else:
                s += pt[0][0] + pt[0][1] + '\n'

        # temp_lines
        for line in self.temp_lines:
            s += line

        # Manning's n header
        s += '#Mann= ' + str(len(self.mannings_n)) + ' ,{:>2} , 0 \n'.format(self.horizontal_mann)
        # n-values - unpack tuples
        n_list = [x for tup in self.mannings_n for x in tup]
        # convert to padded columns of 8 - fix RAS decimal silliness
        temp_str = _print_list_by_group(n_list, 8, 9)
        temp_str = temp_str.replace(' 0.', '  .')
        s += temp_str

        # temp_lines2
        for line in self.temp_lines2:
            s += line

        # Banks stations
        s += 'Bank Sta='+str(self.l_bank_sta)+','+str(self.r_bank_sta)+'\n'

        # temp_lines3
        for line in self.temp_lines3:
            s += line

        return s


def import_ras_geo(geo_filename):
    # add  test for file existence
    geo_list = []
    num_xs = 0
    num_unknown = 0

    with open(geo_filename, 'rt') as geo_file:
        for line in geo_file:
            if _xs_test(line):
                xs = CrossSection()
                xs.import_geo(line, geo_file)
                num_xs += 1
                geo_list.append(xs)
            else:
                # Unknown line encountered. Store it as text.
                geo_list.append(line)
                num_unknown += 1
    print str(num_xs)+' cross sections imported'
    print str(num_unknown) + ' unknown lines imported'
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
    Splits line in to a list of n length strings.
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
    Returns string of items in list values padded to width in width, with num_columns of items per line.
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
            s += ('{:>'+str(width)+'}').format(values[row + column])
        # End of row, add newline
        s += '\n'
    return s


def main():
    infile = 'GHC_working.g43'
    outfile = 'test.out'

    geo_list = import_ras_geo(infile)

    xs_list = extract_xs(geo_list)
    for xs in xs_list:
        print '\nXS ID:', xs.xs_id
        print xs.mannings_n
        print xs.num_cutline_pts
        print xs.gis_cut_line
    print len(xs_list)

    # for x in geo_list:
    #     if isinstance(x, CrossSection):
    #         print x.xs_id, x.l_bank_sta, x.r_bank_sta
    #         for i in range(0, len(x.mannings_n)-1):
    #             if x.mannings_n[i][1] == x.mannings_n[i+1][1]:
    #                 is_double = False
    #                 try:
    #                     if x.mannings_n[i+1][0] == x.mannings_n[i+2][0]:
    #                         is_double = True
    #                 except IndexError:
    #                     is_double = False
    #                 if not is_double:
    #                     print 'On XS', x.xs_id, 'Redundant n-value', x.mannings_n[i+1][1], \
    #                         'at sta ', x.mannings_n[i+1][0]
    #                 else:
    #                     print 'WEIRD - On XS', x.xs_id, 'Redundant n-value', x.mannings_n[i+1][1], \
    #                         'at sta ', x.mannings_n[i+1][0]
    export_ras_geo(outfile, geo_list)

    import filecmp
    if filecmp.cmp(infile, outfile, shallow=False):
        print 'Input and output files are identical'
    else:
        print 'WARNING: files are different!!!'

if __name__ == '__main__':
    main()
