print 'importing arcpy...',
import arcpy
print 'done'
import os
import sys
import prg

N_VALUE_FIELD = 'Mannings_n'
FIELD_LENGTH = 50


class CrossSectionLengthError(Exception):
    pass


class ManningPoint(object):
    def __init__(self, x, y, station, n_value=-1):
        self.X = x
        self.Y = y
        self.station = station
        self.n_value = n_value

    def __str__(self):
        return str(self.X)+', '+str(self.Y)+', sta='+str(self.station)+', n_value='+str(self.n_value)

    def __repr__(self):
        return self.__str__()


def message(x):
    print x


def warn(x):
    print x


def error(x):
    print x


def next_filename():
    with open('out\\number.txt')as num_file:
        x = num_file.readline()
        number = int(x)
    with open('out\\number.txt', 'wt') as num_file:
        num_file.write(str(number+1))
    return 'out\\out'+str(number)+'.shp'


def _array_to_list(arc_array):
    # Converts arcpy array to a list of arcpy points
    points = []
    for i in range(arc_array.count):
        points.append(arc_array.getObject(i))
    return points


def _setup_output_shapefile(filename, xs_id_field, river_field, reach_field, spatial_reference):
    try:
        message('Creating output shapefile: ' + filename)
        arcpy.CreateFeatureclass_management(os.path.dirname(filename), os.path.basename(filename),
                                            'POLYLINE', '', '', '', spatial_reference)
        message('Adding fields...')
        arcpy.AddField_management(filename, xs_id_field, 'FLOAT', '')
        arcpy.AddField_management(filename, river_field, 'TEXT', field_length=FIELD_LENGTH)
        arcpy.AddField_management(filename, reach_field, 'TEXT', field_length=FIELD_LENGTH)
        arcpy.AddField_management(filename, N_VALUE_FIELD, 'FLOAT', '')
    except Exception as e:
        error(str(e))
        error('Unable to create ' + filename +
              '. Is the shape file open in another program or is the workspace being edited?')
        sys.exit()
    else:
        arcpy.AddMessage('Done.')


def _create_n_value_lines(line_geo, n_values):
    # First n-value should be station 0
    assert n_values[0][0] == 0

    # verify n-values aren't longer than cross section
    if n_values[-1][0] > line_geo.length:
        raise CrossSectionLengthError

    # Extract station 0 n-value - this is done to avoid possible rounding errors with positionAlongLine
    xs_points = _array_to_list(line_geo.getPart(0))
    first_n_value = n_values.pop(0)
    first_point = xs_points[0]
    combo_points = [ManningPoint(first_point.X, first_point.Y, 0, first_n_value[1])]

    # Extract rest of the n-values
    for station, n_value, _ in n_values:
        new_point = line_geo.positionAlongLine(station).firstPoint
        new_point = ManningPoint(new_point.X, new_point.Y, station, n_value)
        combo_points.append(new_point)

    # Add stationing and n-value flag to xs_points
    new_xs_points = []
    first_lap = True
    station = 0
    for xs_point in xs_points:
        if first_lap:
            last_point = xs_point
            first_lap = False
        else:
            station += _dist(xs_point, last_point)
        new_point = ManningPoint(xs_point.X, xs_point.Y, station)
        last_point = xs_point
        new_xs_points.append(new_point)
    # Ditch first point, already created above from n-values
    new_xs_points.pop(0)
    combo_points = combo_points + new_xs_points
    combo_points.sort(key=lambda x: x.station)

    return _combo_points_to_polylines(combo_points)


def _combo_points_to_polylines(points):
    assert points[0].n_value != -1

    # Split points into n-value segments
    current_n_value = points[0].n_value
    current_index = 0
    segments = []
    for i in range(1, len(points)):
        if points[i].n_value != -1:
            new_segment = (points[current_index:i+1], current_n_value)
            segments.append(new_segment)
            current_index = i
            current_n_value = points[i].n_value
    new_segment = (points[current_index:i+1], current_n_value)
    segments.append(new_segment)

    # convert segments to arcpy polylines
    n_lines = []
    for points, n_value in segments:
        arc_array = arcpy.Array()
        arc_point = arcpy.Point()
        for point in points:
            arc_point.X = point.X
            arc_point.Y = point.Y
            arc_array.add(arc_point)
        n_lines.append((arcpy.Polyline(arc_array), n_value))
    return n_lines


def _dist(point1, point2):
    return ((point1.X - point2.X)**2 + (point1.Y - point2.Y)**2)**0.5


def main():
    geofile = 'GHC_working.g43'
    xs_shape_file = 'ghc_xs.shp'
    xs_id_field = 'ProfileM'
    reach_field = 'ReachCode'
    river_field = 'RiverCode'
    outfile = next_filename()

    # Setup output shapefile
    spatial_reference = arcpy.Describe(xs_shape_file).spatialReference
    _setup_output_shapefile(outfile, xs_id_field, river_field, reach_field, spatial_reference)

    geo_list = prg.import_ras_geo(geofile)

    with arcpy.da.SearchCursor(xs_shape_file, ['SHAPE@', xs_id_field, river_field, reach_field]) as xs_cursor:
        with arcpy.da.InsertCursor(outfile, ['SHAPE@', xs_id_field, river_field, reach_field,
                                             N_VALUE_FIELD]) as out_cursor:
            for xs in xs_cursor:
                geo = xs[0]
                xs_id = xs[1]
                river = xs[2]
                reach = xs[3]

                try:
                    geo_xs = prg.return_xs_by_id(geo_list, xs_id)
                except prg.CrossSectionNotFound:
                    warn('Warning: Cross section ' + str(xs_id) + ' is in cross section shape file but is not in ' + \
                         'the HEC-RAS geometry file. Continuing')
                    continue

                if geo.isMultipart:
                    warn('Warning: Cross section ' + xs_id + ' is multipart. Using part 0.')
                
                #### Add check for duplicate n-values
                n_values = geo_xs.mannings_n

                print '\n', xs_id
                print n_values

                try:
                    n_lines = _create_n_value_lines(geo, n_values)
                except CrossSectionLengthError:
                    warn('Error: N-value stating for cross section ' + str(xs_id) + ' in RAS geometry exceeds GIS' + \
                         ' feature length. Ignored.')
                    continue

                for n_line in n_lines:
                    out_cursor.insertRow([n_line[0], xs_id, river, reach, n_line[1]])


if __name__ == '__main__':
    main()
