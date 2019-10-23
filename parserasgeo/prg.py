#! /usr/bin/python
"""
rasgeotool - tools for importing, modifying, and exporting HEC-RAS geometry files (myproject.g01 etc)

This has NOT been extensively tested.

Mike Bannister 2/24/2016
mike.bannister@respec.com

"""
import os.path
import warnings

from .features import (
    Bridge, CrossSection, Culvert, Junction, InlineWeir, LateralWeir, RiverReach
)


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
        num_inline_weir = 0
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
                elif InlineWeir.test(line):
                    lat_weir = InlineWeir(river, reach)
                    lat_weir.import_geo(line, geo_file)
                    num_inline_weir += 1
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
            print(str(num_inline_weir)+' lateral structures imported')
            print(str(num_unknown) + ' unknown lines imported')

    def write(self, out_geo_filename):
        with open(out_geo_filename, 'wt', newline='\r\n') as outfile:
            for line in self.geo_list:
                outfile.write(str(line))

    def get_cross_sections(
            self,
            station_value=None,
            station_id=None,
            river=None,
            reach=None,
            interpolated=None,
        ):
        """Get a list of matching CrossSection
        :param station_value: Optional float representing the location of the station or 2-tuple representing a range
        :param station_id: Optional string representing the CrossSection station as text
        :param river: Optional string of the name of river
        :param reach: Optional string of the name of reach
        :param interpolated: Optional bool to select based on if the CrossSection was interpolated
        :return: List of matching CrossSection instances
        """
        # Linear Search is the most efficient strategy at the moment
        cross_sections = (item for item in self.geo_list if isinstance(item, CrossSection))
        if station_id is not None:
            cross_sections = (
                xs for xs in cross_sections if xs.header.station.id == station_id
            )
        if station_value is not None:
            if isinstance(station_value, tuple):
                assert len(station_value) == 2
                if station_value[0] is not None:
                    cross_sections = (
                        xs for xs in cross_sections
                        if xs.header.station.value >= station_value[0]
                    )
                if station_value[1] is not None:
                    cross_sections = (
                        xs for xs in cross_sections
                        if xs.header.station.value <= station_value[1]
                    )
            else:
                cross_sections = (
                    xs for xs in cross_sections
                    if xs.header.station.value == station_value
                )
        if river is not None:
            cross_sections = (xs for xs in cross_sections if xs.river == river)
        if reach is not None:
            cross_sections = (xs for xs in cross_sections if xs.reach == reach)
        if interpolated is not None:
            cross_sections = (
                xs for xs in cross_sections
                if xs.header.station.is_interpolated == bool(interpolated)
            )

        return list(cross_sections)

    def return_xs_by_id(self, xs_id, rnd=False, digits=0):
        """
        Returns XS with ID xs_id. Rounds XS ids to digits decimal places if (rnd==True)
        :param xs_id: id of cross section, assumed to be in ..... format
        :param rnd: rounds xs_id to 'digits' if True
        :param digits: number of digits to round xs_id to
        :return: CrossSection object
        """
        warnings.warn(
            "return_xs_by_id is deprecated, use get_cross_sections instead",
            FutureWarning,
        )
        for item in self.geo_list:
            if isinstance(item, CrossSection):
                if rnd:
                    if round(item.header.station.value, digits) == round(xs_id, digits):
                        return item
                else:
                    if item.header.station.value == xs_id:
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
        warnings.warn(
            "return_xs is deprecated, use get_cross_sections instead",
            FutureWarning,
        )
        return self._return_node(CrossSection, xs_id, river, reach, strip, rnd, digits)
        
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
        warnings.warn(
            "return_culvert is deprecated, use get_culverts instead",
            FutureWarning,
        )
        return self._return_node(Culvert, culvert_id, river, reach, strip, rnd, digits)

    def get_culverts(self, station=None, river=None, reach=None):
        """Returns list of all culverts in geometry
        :param station: Optional number specifying the culvert station
        :param river: Optional string of the name of river
        :param reach: Optional string of the name of reach
        :return: List of matching Culvert instances
        """
        culverts = (item for item in self.geo_list if isinstance(item, Culvert))
        if station is not None:
            culverts = (c for c in culverts if c.header.station == station)
        if river is not None:
            culverts = (c for c in culverts if c.river == river)
        if reach is not None:
            culverts = (c for c in culverts if c.reach == reach)

        return list(culverts)

    def extract_all_xs(self):
        """
        Returns list of all cross sections in geometry
        """
        warnings.warn(
            "extract_all_xs is deprecated, use get_cross_sections instead",
            FutureWarning,
        )
        return self.get_cross_sections()

    def extract_all_culverts(self):
        """
        Returns list of all culverts in geometry
        """
        warnings.warn(
            "extract_all_culverts is deprecated, use get_culverts instead",
            FutureWarning,
        )
        return self.get_culverts()

    def get_junctions(self):
        """
        Returns list of all Junction in geometry
        """
        return [item for item in self.geo_list if isinstance(item, Junction)]


    def get_bridges(self):
        """
        Returns list of all Bridge in geometry
        """
        return [item for item in self.geo_list if isinstance(item, Bridge)]

    def get_lateral_weirs(self):
        """
        Returns list of all LateralWeir in geometry
        """
        return [item for item in self.geo_list if isinstance(item, LateralWeir)]

    def get_inline_weirs(self, river=None, reach=None):
        """
        Returns list of all InlineWeir instances in geometry
        :param river: Optional string of the name of river
        :param reach: Optional string of the name of reach
        """
        inline_weirs = (item for item in self.geo_list if isinstance(item, InlineWeir))
        if river is not None:
            inline_weirs = (iw for iw in inline_weirs if iw.river == river)
        if reach is not None:
            inline_weirs = (iw for iw in inline_weirs if iw.reach == reach)

        return list(inline_weirs)

    def get_reaches(self, river=None, reach=None):
        """
        Returns list of all RiverReach in geometry
        :param river: Optional string of the name of river
        :param reach: Optional string of the name of reach
        """
        reaches = (item for item in self.geo_list if isinstance(item, RiverReach))
        if river is not None:
            reaches = (r for r in reaches if r.header.river_name == river)
        if reach is not None:
            reaches = (r for r in reaches if r.header.reach_name == reach)

        return list(reaches)

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
        
        if node_type.__name__ is 'CrossSection':
            node_name = 'XS'
            NodeNotFound = CrossSectionNotFound
        if node_type.__name__ is 'Culvert':
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
                if node_type.__name__ is 'CrossSection':
                    test_node_id = item.header.station.value
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
