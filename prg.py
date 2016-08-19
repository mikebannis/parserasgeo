"""
rasgeotool - tools for importing, modifying, and exporting HEC-RAS geometry files (myproject.g01 etc)

This has NOT been extensively tested.

Mike Bannister 2/24/2016

Version 0.01
"""

from features import CrossSection, RiverReach, Culvert, Bridge, LateralWeir

# TODO - create geolist object


class CrossSectionNotFound(Exception):
    pass

class ParseRASGeo(object):
    def __init__(self, geo_filename, chatty=False):
        # add  test for file existence
        self.geo_list = []
        num_xs = 0
        num_river = 0
        num_bridge = 0
        num_culvert = 0
        num_lat_weir = 0
        num_unknown = 0
        river = None
        reach = None

        with open(geo_filename, 'rt') as geo_file:
            for line in geo_file:
                if RiverReach.test(line):
                    rr = RiverReach()
                    rr.import_geo(line, geo_file)
                    river, reach = rr.header.river_name, rr.header.reach_name
                    num_river += 1
                    self.geo_list.append(rr)
                elif CrossSection.test(line):
                    xs = CrossSection(river, reach)
                    xs.import_geo(line, geo_file)
                    num_xs += 1
                    self.geo_list.append(xs)
                elif Culvert.test(line):
                    culvert = Culvert(river, reach)
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
                else:
                    # Unknown line encountered. Store it as text.
                    self.geo_list.append(line)
                    num_unknown += 1
        if chatty:      
            print str(num_river)+' rivers/reaches imported'
            print str(num_xs)+' cross sections imported'
            print str(num_bridge)+' bridge imported'
            print str(num_culvert)+' culverts imported'
            print str(num_lat_weir)+' lateral structures imported'
            print str(num_unknown) + ' unknown lines imported'

    def write(self, out_geo_filename):
        with open(out_geo_filename, 'wt') as outfile:
            for line in self.geo_list:
                outfile.write(str(line))

    def return_xs_by_id(self, xs_id):
        for item in self.geo_list:
            if isinstance(item, CrossSection):
                if item.xs_id == xs_id:
                    return item
        raise CrossSectionNotFound

    def return_xs(self, xs_id, river, reach):
        for item in self.geo_list:
            if isinstance(item, CrossSection):
                if item.xs_id == xs_id and item.river == river and item.reach == reach:
                    return item
        raise CrossSectionNotFound

    def extract_xs(self):
        """
        :param geo_list: list of RAS geometry from import_ras_geo()
        :return: returns list of all cross sections in geo_list
        """
        new_geo_list = []
        for item in self.geo_list:
            if isinstance(item, CrossSection):
                new_geo_list.append(item)
        return new_geo_list

    def number_xs(self):
        """
        Returns the number of cross sections in geo_list
        :param geo_list: list from import_ras_geo
        :return: number (int) of XS in geolist
        """
        xs_list = extract_xs(self.geo_list)
        return len(xs_list)

    def is_xs_duplicate(self, xs_id):
        """
        Checks for duplicate cross sections in geo_list
        rasises CrossSectionNotFound if xs_id is not found
        :param geo_list: from import_ras_geo
        :return: True if duplicate
        """
        xs_list = extract_xs(self.geo_list)
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


def main():
    infile = 'geos/201601BigDryCreek.g27'
    #infile = 'geos/GHC_FHAD.g01'
    #infile = 'test/CCRC_prg_test.g01'
    infile = 'geos/SBK_PMR.g02'
    infile = 'geos/GHC_working.g43'
    outfile = 'test/test.out'

    geo = ParseRASGeo(infile, chatty=True)
    
    if not True:
        for item in geo.geo_list:
            if type(item) is Culvert:
                print '-'*50
                print 'bridge/culvert', item.header.station
                print str(item)
    
    if not True:
        for item in geo.geo_list:
            if hasattr(item, 'description'):
                if item.description is not []:
                    print type(item)
                    print item.description

    if True:
        count = 0
        for item in geo.geo_list:
            if type(item) is str:
                count += 1
                # print str(item),
        print count, 'unknown lines'
                    

    if not True:
        iefa_count = 0
        xs_list = geo.extract_xs()
        for xs in xs_list:
            print '\nXS ID:', xs.header.xs_id
            #print xs.description.text
            #print xs.mannings_n.horizontal, xs.mannings_n.values
            #print xs.bank_sta.left, xs.bank_sta.right
            # print 'number sta_elv=', xs.sta_elev.num_pts
            # print xs.sta_elev.points
            # print xs.cutline.number_pts, xs.cutline.points
            # if xs.obstruct.blocked_type is not None:
            #     iefa_count +=1
            #     print '\nXS ID:', xs.header.xs_id
            if xs.iefa.type is not None:
                print xs.iefa.type, xs.iefa.iefa_list
                print xs.iefa.iefa_permanence
                #print xs.obstruct.blocked_type, xs.obstruct.num_blocked, xs.obstruct.blocked
                #print xs.bank_sta.right, xs.bank_sta.left

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

    geo.write(outfile)
    
    if True: 
        import filecmp
        import subprocess
        if filecmp.cmp(infile, outfile, shallow=False):
            print 'Input and output files are identical'
        else:
            print 'WARNING: files are different!!!'
            subprocess.Popen(["diff", infile, outfile])

if __name__ == '__main__':
    main()
