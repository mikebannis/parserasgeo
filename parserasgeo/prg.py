#! /usr/bin/python
"""
rasgeotool - tools for importing, modifying, and exporting HEC-RAS geometry files (myproject.g01 etc)

This has NOT been extensively tested.

Mike Bannister 2/24/2016
mike.bannister@respec.com

"""

from .features import CrossSection, RiverReach, Culvert, Bridge, LateralWeir, Junction
import os.path

# TODO - create geolist object


class CrossSectionNotFound(Exception):
    pass

class CulvertNotFound(Exception):
    pass

class ParseRASGeo(object):
    def __init__(self, geo_filename, chatty=False, debug=False):
        # add  test for file existence
        self.geo_list = []
        num_xs = 0
        num_river = 0
        num_bridge = 0
        num_culvert = 0
        num_lat_weir = 0
        num_junc = 0
        num_unknown = 0
        river = None
        reach = None

        if debug:
            print('Debugging is turned on')

        if geo_filename == '' or geo_filename is None:
            raise AttributeError('Filename passed to ParseRASGeo is blank.')

        if not os.path.isfile(geo_filename):
            raise AttributeError('File ' + str(geo_filename) + ' does not appear to exist.')

        # TODO - add 'debug' to all objects
        with open(geo_filename, 'rt') as geo_file:
            for line in geo_file:
                if RiverReach.test(line):
                    rr = RiverReach(debug)
                    rr.import_geo(line, geo_file)
                    river, reach = rr.header.river_name, rr.header.reach_name
                    num_river += 1
                    self.geo_list.append(rr)
                elif CrossSection.test(line):
                    xs = CrossSection(river, reach, debug)
                    xs.import_geo(line, geo_file)
                    num_xs += 1
                    self.geo_list.append(xs)
                elif Culvert.test(line):
                    culvert = Culvert(river, reach, debug)
                    culvert.import_geo(line, geo_file)
                    num_culvert += 1
                    self.geo_list.append(culvert)
                elif Bridge.test(line):
                    bridge = Bridge(river, reach)
                    bridge.import_geo(line, geo_file)
                    num_bridge += 1
                    self.geo_list.append(bridge)
                elif LateralWeir.test(line):
                    lat_weir = LateralWeir(river, reach)
                    lat_weir.import_geo(line, geo_file)
                    num_lat_weir += 1
                    self.geo_list.append(lat_weir)
                elif Junction.test(line):
                    junc = Junction()
                    junc.import_geo(line, geo_file)
                    num_junc += 1
                    self.geo_list.append(junc)
                else:
                    # Unknown line encountered. Store it as text.
                    self.geo_list.append(line)
                    num_unknown += 1
        if chatty:
            print(str(num_river)+' rivers/reaches imported')
            print(str(num_junc)+' junctions imported')
            print(str(num_xs)+' cross sections imported')
            print(str(num_bridge)+' bridge imported')
            print(str(num_culvert)+' culverts imported')
            print(str(num_lat_weir)+' lateral structures imported')
            print(str(num_unknown) + ' unknown lines imported')

    def write(self, out_geo_filename):
        with open(out_geo_filename, 'wt') as outfile:
            for line in self.geo_list:
                outfile.write(str(line))

    def return_xs_by_id(self, xs_id, rnd=False, digits=0):
        """
        Returns XS with ID xs_id. Rounds XS ids to digits decimal places if (rnd==True)
        :param xs_id: id of cross section, assumed to be in ..... format
        :param rnd: rounds xs_id to 'digits' if True
        :param digits: number of digits to round xs_id to
        :return: CrossSection object
        """
        for item in self.geo_list:
            if isinstance(item, CrossSection):
                if rnd:
                    if round(item.header.xs_id, digits) == round(xs_id, digits):
                        return item
                else:
                    if item.header.xs_id == xs_id:
                        return item
        raise CrossSectionNotFound

    def return_xs(self, xs_id, river, reach, strip=False, rnd=False, digits=0):
        """
        returns matching CrossSection if it is in self.geo_list. raises CrossSectionNotFound otherwise
        
        :param xs_id: cross section id number
        :param river: name of river
        :param reach: name of reach
        :param strip: strips whitespace off river and reach if true
        :return: CrossSection object
        "raises CrossSectionNotFound: raises error if xs is not in the geometry file
        """
        return self._return_node(self, CrossSection, xs_id, river, reach, strip, rnd, digits)
        
    def return_culvert(self, culvert_id, river, reach, strip=False, rnd=False, digits=0):
        """
        returns matching Culvert if it is in self.geo_list. raises CulvertNotFound otherwise
        
        :param culvert_id: culvert id number
        :param river: name of river
        :param reach: name of reach
        :param strip: strips whitespace off river and reach if true
        :return: Culvert object
        :raises CulvertNotFound: raises error if culvert is not in the geometry file
        """
        return self._return_node(self, Culvert, culvert_id, river, reach, strip, rnd, digits)

    def extract_xs(self):
        """
        Returns list of all cross sections in geometry
        """
        return self._extract_node(CrossSection)

    def extract_culverts(self):
        """
        Returns list of all culverts in geometry
        """
        return self._extract_node(Culvert)

    def number_xs(self):
        """
        Returns the number of cross sections in geo_list
        :param geo_list: list from import_ras_geo
        :return: number (int) of XS in geolist
        """
        xs_list = self.extract_xs()
        return len(xs_list)

    def is_xs_duplicate(self, xs_id):
        """
        Checks for duplicate cross sections in geo_list
        rasises CrossSectionNotFound if xs_id is not found
        :param geo_list: from import_ras_geo
        :return: True if duplicate
        """
        xs_list = self.extract_xs(self.geo_list)
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
    
    def _return_node(self, node_type, node_id, river, reach, strip=False, rnd=False, digits=0):
        """
        This semi-private method is written in a general format.
        It is meant to be called by more user friendly methods, such as
        return_xs or return_culvert
        
        returns matching node if it is in self.geo_list. raises <Node>NotFound otherwise where
        <Node> is a type of node
        
        :param node_type: the type of node to be returned
        :param culvert_id: culvert id number
        :param river: name of river
        :param reach: name of reach
        :param strip: strips whitespace off river and reach if true
        :return: Culvert object
        :raises NodeNotFound: raises error if the node is not found in the geometry file
        """
        wanted_river = river
        wanted_reach = reach
        wanted_node_id = node_id
        
        if isinstance(node_type, CrossSection):
            node_name = 'XS'
            NodeNotFound = CrossSectionNotFound
        if isinstance(node_type, Culvert):
            node_name = 'culvert'
            NodeNotFound = CulvertNotFound

        if strip:
            if type(river) is not str and type(river) is not unicode:
                raise AttributeError('For {} "river" is not a string, got: {} instead.'.format(node_name, river))
            if type(reach) is not str and type(reach) is not unicode:
                raise AttributeError('For {} "reach" is not a string, got: {} instead.'.format(node_name, reach))
            wanted_river = river.strip()
            wanted_reach = reach.strip()
        if rnd:
            wanted_node_id = round(node_id, digits)

        for item in self.geo_list:
            if isinstance(item, node_type):
                test_river = item.river
                test_reach = item.reach
                
                # TODO: get rid of if-else statements after changing xs_id to station in cross_section.py
                if isinstance(node_type, CrossSection):
                    test_node_id = item.header.xs_id
                else:
                    test_node_id = item.header.station

                if strip:
                    test_river = test_river.strip()
                    test_reach = test_reach.strip()
                if rnd:
                    test_node_id = round(test_node_id, digits)

                # Rounding and strip is done, see if this is the right XS
                if test_node_id == wanted_node_id and test_river == wanted_river and test_reach == wanted_reach:
                    return item
        raise NodeNotFound 
            
    def _extract_node(self, node_type):
        """
        This semi-private method is written in a general format.
        It is meant to be called by more user friendly methods, such as
        extract_xs or extract_culvert
        
        :param node_type: the type of node to be returned
        :return: a list of all nodes of type <node_type> in geometry
        """
        new_geo_list = []
        for item in self.geo_list:
            if isinstance(item, node_type):
                new_geo_list.append(item)
        return new_geo_list


def main():
    outfile = '../test/test.out'
    infile = '../geos/third/third_final.g01'
    geo = ParseRASGeo(infile, chatty=True, debug=True)

    if not True:
        for item in geo.geo_list:
            if type(item) is Culvert:
                print('-'*50)
                print('bridge/culvert', item.header.station)
                print(str(item))

    if not True:
        for item in geo.geo_list:
            if hasattr(item, 'description'):
                if item.description is not []:
                    print(type(item))
                    print(item.description)

    if not True:
        count = 0
        for item in geo.geo_list:
            if type(item) is str:
                count += 1
                print('unknown: ', str(item),)
        print(count, 'unknown lines')

    if not True:
        xs_list = geo.extract_xs()
        for xs in xs_list:
                print(str(xs.header.xs_id)+','+str(xs.rating_curve.value1))

    if not True:
        for item in geo.geo_list:
            if type(item) is Junction:
                print('Junction', item.header.name)

    geo.write(outfile)

    if True:
        print('Comparing', infile, 'and', outfile)
        import filecmp
        import subprocess
        if filecmp.cmp(infile, outfile, shallow=False):
            print('Input and output files are identical')
        else:
            print('WARNING: files are different!!!')
            subprocess.Popen(["diff", infile, outfile])

if __name__ == '__main__':
    main()
