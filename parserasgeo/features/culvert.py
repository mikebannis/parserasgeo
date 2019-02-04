from tools import fl_int, split_by_n #  , split_by_n_str, pad_left, print_list_by_group, split_block_obs, split_by_n
from description import Description
from collections import namedtuple

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


# TODO: possibly move header into Culvert
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
            if line[24:25] == '2':
                return True
        return False

    def import_geo(self, line, geo_file):
        fields = line[23:].split(',')
        if DEBUG:
                print('fields:', fields)
        assert len(fields) == 5
        # vals = [fl_int(x) for x in fields]
        # Node type and cross section id
        self.node_type = fl_int(fields[0])
        self.station = fl_int(fields[1])
        # TODO: Not sure what these are yet
        self.value1 = fields[2]
        self.value2 = fields[3]
        self.value3 = fields[4]
        if DEBUG:
            print ('Imported culvert:', str(self.station))
        return next(geo_file)
   
    def __str__(self):
        s = 'Type RM Length L Ch R = '
        s += str(self.node_type) + ' ,'
        s += '{:<8}'.format(str(self.station)) + ','
        s += str(self.value1) + ',' + str(self.value2) + ',' + str(self.value3)  # + '\n' TODO: Add this back it later once the remainder of the 
                                                                                                    # header if figured out
        return s

class CulvertGroup(object):
    """
    A group of culverts (either single or multiple)
    """
    def __init__(self):
        self.shape = None
        self.height = None  # or size diameter
        self.width = None  # or span
        self.length = None
        self.manning_top = None
        self.enter_loss_coef = None
        self.exit_loss_coef = None
        self.chart_num = None
        self.scale_num = None
        self.up_invert_elev = None
        self.down_invert_elev = None
        self.num_identical_barrels = None
        self.culvert_name = None
        self.solution_criteria = None
        self.up_xs_dist = None
        
        # upstream and downstream are stored as named tuples
        self.station_distances = list()
        
        self.barrel_names = list()
        
        self.manning_bot = None
        self.depth_manning_bot = None
        self.depth_blocked = None

    @staticmethod
    def test(line):
        if (line.split('=')[0] == 'Culvert' or 
            line.split('=')[0] == 'Multiple Barrel Culv'):
            return True
        return False

    def import_geo(self, line, geo_file):
        # a named tuple subclass for station distances
        DistanceTuple = namedtuple('DistanceTuple', ['upstream', 'downstream'])
        
        equals_ind = line.index('=')
        line = line[equals_ind+1:]
        values = line.split(',')
        
        if equals_ind == 7:
            assert len(values) == 16, 'You have the incorrect number of values on the first line. There are {}'.format(len(values))
        else:
            assert len(values) == 15, 'You have the incorrect number of values on the first line. There are {}'.format(len(values))

        self.shape = fl_int(values[0])
        self.height = fl_int(values[1])  # or diameter
        if self.shape == 1 or self.shape == 6:
            # 1 = cirular and 6 = semi-circle
            pass
        else:
            self.width = fl_int(values[2])  # or span
        self.length = fl_int(values[3])
        self.manning_top = float(values[4])
        self.entrance_loss = fl_int(values[5])
        self.exit_loss_coef = fl_int(values[6])
        self.chart_num = int(values[7])
        self.scale_num = int(values[8])
        self.up_invert_elev = fl_int(values[9])

        # single barrel culvert
        if equals_ind == 7:
            self.down_invert_elev = fl_int(values[11])
            self.num_identical_barrels = 1
            self.culvert_name = str(values[13])
            self.solution_criteria = int(values[14])
            self.up_xs_dist = fl_int(values[15])
            
            self.station_distances.append(DistanceTuple(fl_int(values[10]), fl_int(values[12])))
            
            line = next(geo_file)
            
            try:
                # Version 5.x.x
                temp_distances = split_by_n(line, 8)
                float(temp_distances[0])
                line = next(geo_file)
            except ValueError:
                # Version 4.x.x
                pass
        
        # multiple barrel culvert
        else:
            self.down_invert_elev = fl_int(values[10])
            self.num_identical_barrels = int(values[11])
            self.culvert_name = str(values[12])
            self.solution_criteria = int(values[13])
            self.up_xs_dist = fl_int(values[14])

            line = next(geo_file)
            
            # collect all barrel station distances (up stream and down stream)
            # this continues until a barrel name or the culvert's parameters
            while 'Culvert' not in line:
                barrel_ind = 0
                
                values = split_by_n(line, 8)
                up = None
                down = None
                for distance in values:
                    if (barrel_ind) % 2 == 0:
                        up = distance
                    else:
                        down = distance
                        self.station_distances.append(DistanceTuple(up, down))
                    barrel_ind += 1

                line = next(geo_file)
        
        if 'BC Culvert Barrel' in line:
            for i in range(self.num_identical_barrels):
                barrel_name = line.split(',')[1]
                self.barrel_names.append(barrel_name)
                
                line = next(geo_file)

        # stop when you get to the next culvert group or are at the end of the culvert groups
        while 'BC Design=' not in line and 'BR U' not in line and 'Culvert=' not in line and 'Multiple Barrel Culv=' not in line:
            description = line.split('=')[0]
            value = line.split('=')[1]

            if description == 'Culvert Bottom n':
                self.manning_bot = float(value)
            elif description == 'Culvert Bottom Depth':
                self.depth_manning_bot = fl_int(value)
            else:
                self.depth_blocked = fl_int(value)
            
            line = next(geo_file)
            
        return line

    def __str__(self):
        s = ''
        if self.num_identical_barrels == 1:
            s += 'Culvert='
        else:
            s += 'Multiple Barrel Culv='
            
        s += str(self.shape)
        s += ',' + str(self.height)
        
        if self.shape == 1 or self.shape == 6:
            s += ','
        else:
            s += ',' + str(self.width)
            
        s += ',' + str(self.length)
        s += ',' + str(self.manning_top)
        s += ',' + str(self.entrance_loss)
        s += ',' + str(self.exit_loss_coef)
        s += ',' + str(self.chart_num)
        s += ',' + str(self.scale_num)
        s += ',' + str(self.up_invert_elev)
        
        if self.num_identical_barrels == 1:
            s += ',' + str(self.station_distances[0][0])
            s += ',' + str(self.down_invert_elev)
            s += ',' + str(self.station_distances[0][1])
            s += ',' + self.culvert_name
        else:
            s += ',' + str(self.down_invert_elev)
            s += ',' + str(self.num_identical_barrels).rjust(2)
            s += ',' + self.culvert_name
        
        s += ',' + ' ' + str(self.solution_criteria) + ' '
        s += ',' + str(self.up_xs_dist) + '\n'
        
        # Version 5.x.x: single or multiple barrels
        # has barrel names
        if len(self.barrel_names) > 0:
            barrel_counter = 1
            mod_ind = 1
            
            for i in range(self.num_identical_barrels):
                # new line every 5 barrels
                if barrel_counter % (5 + mod_ind) == 0:
                    # the modular index increases by 1 for every line (since barrel_counter starts at 1)
                    mod_ind += 1
                    s += '\n'

                s += str(self.station_distances[i].upstream).rjust(8)
                s += str(self.station_distances[i].downstream).rjust(8)
                
                barrel_counter += 1
                
            s += '\n'
            
            # add barrel names
            for i in range(self.num_identical_barrels):
                s += 'BC Culvert Barrel={0},{1},0\n'.format(str(i+1), self.barrel_names[i])
            
        # Version 4.x.x: multiple barrels
        # does not have barrel names
        elif len(self.barrel_names) == 0 and self.num_identical_barrels > 1:
            
            barrel_counter = 1
            mod_ind = 1
            
            for i in range(self.num_identical_barrels):
                # new line every 5 barrels
                if barrel_counter % (5 + mod_ind) == 0:
                    # the modular index increases by 1 for every line (since barrel_counter starts at 1)
                    mod_ind += 1
                    s += '\n'
                
                s += str(self.station_distances[i].upstream).rjust(8)
                s += str(self.station_distances[i].downstream).rjust(8)
                
                barrel_counter += 1
                
            s += '\n'
            
        if self.manning_bot is not None:
            s += 'Culvert Bottom n={}\n'.format(str(self.manning_bot))
        
        if self.depth_manning_bot is not None:
            s += 'Culvert Bottom Depth={}\n'.format(str(self.depth_manning_bot))
            
        if self.depth_blocked is not None:
            s += 'Culvert Depth Blocked={}\n'.format(str(self.depth_blocked))
            
        return s
        
class Culvert(object):
    def __init__(self, river, reach, debug=False):
        global DEBUG
        DEBUG = debug

        self.river = river
        self.reach = reach

        self.header = Header()
        self.description = Description()
        self.culvert_groups = list()
        temp_culvert_group = CulvertGroup()

        self.parts = [self.header, self.description, temp_culvert_group]

        self.geo_list = []  # holds all parts and unknown lines (as strings)

    def import_geo(self, line, geo_file):
        while line != '\n':
            for part in self.parts:
                if part.test(line):
                    #print str(type(part))+' found!'
                    line = part.import_geo(line, geo_file)
                    self.parts.remove(part)
                    self.geo_list.append(part)
                    
                    if 'CulvertGroup' in str(type(part)):
                        self.culvert_groups.append(part)
                        self.parts.append(CulvertGroup())
                    
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

if __name__ == '__main__':
    path = 'Z:/City of Aurora/03079_Channel Sensitivity Study/scratch/culvert obstruction RAS/'
    file_name = 'culvert_snippet.g01'
    
    file_full = path+file_name
    
    river = 'test river'
    reach = 'test reach'
    
    '''
    with open(file_full, 'rt') as geo_file:
        for line in geo_file:
            if Culvert.test(line):
                culvert = Culvert(river, reach)
                culvert.import_geo(line, geo_file)

    print(str(culvert))
    
    '''
    test = CulvertGroup()
    
    with open(file_full, 'rt') as geo_file:
        for line in geo_file:
            if test.test(line):
                test.import_geo(line, geo_file)
                break
         
    #print('Chart number: {}'.format(str(test.chart_num)))
    #print('Culvert name: {}'.format(str(test.culvert_name)))
    #print('Barrel 1 down station distance: {}'.format(str(test.down_station_dist[0])))
    #print('Barrel 1 up station distance: {}'.format(str(test.up_station_dist[0])))
    #print('Depth blocked: {}'.format(str(test.depth_blocked)))
    #print('Manning bottom: {}'.format(str(test.manning_bot)))
    print(str(test))
    
