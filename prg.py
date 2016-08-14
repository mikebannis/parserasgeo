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


def import_ras_geo(geo_filename, chatty=False):
    # add  test for file existence
    geo_list = []
    num_xs = 0
    num_river = 0
    num_bc = 0
    num_unknown = 0
    river = None
    reach = None

    with open(geo_filename, 'rt') as geo_file:
        for line in geo_file:
            if RiverReach.test(line):
                rr = RiverReach()
                rr.import_geo(line, geo_file)
                river, reach = rr.header.river_name, rr.header.reach_name
                # print river, reach
                num_river += 1
                geo_list.append(rr)
            elif CrossSection.test(line):
                xs = CrossSection(river, reach)
                xs.import_geo(line, geo_file)
                num_xs += 1
                geo_list.append(xs)
            elif Culvert.test(line):
                bc = Culvert(river, reach)
                bc.import_geo(line, geo_file)
                num_bc += 1
                geo_list.append(bc)
            elif Bridge.test(line):
                bc = Bridge(river, reach)
                bc.import_geo(line, geo_file)
                num_bc += 1
                geo_list.append(bc)
            elif LateralWeir.test(line):
                bc = LateralWeir(river, reach)
                bc.import_geo(line, geo_file)
                num_bc += 1
                geo_list.append(bc)
            else:
                # Unknown line encountered. Store it as text.
                geo_list.append(line)
                num_unknown += 1
    if chatty:      
        print str(num_river)+' rivers/reaches imported'
        print str(num_xs)+' cross sections imported'
        print str(num_bc)+' bridges/culverts imported'
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


def main():
    infile = 'geos/201601BigDryCreek.g27'
    #infile = 'geos/GHC_FHAD.g01'
    #infile = 'test/CCRC_prg_test.g01'
    infile = 'geos/SBK_PMR.g02'
    infile = 'geos/GHC_working.g43'
    outfile = 'test/test.out'

    geo_list = import_ras_geo(infile, chatty=True)
    
    if not True:
        for item in geo_list:
            if type(item) is Culvert:
                print '-'*50
                print 'bridge/culvert', item.header.station
                print str(item)

    if True:
        count = 0
        for item in geo_list:
            if type(item) is str:
                count += 1
                print str(item),
        print count, 'unknown lines'
                    

    if not True:
        iefa_count = 0
        xs_list = extract_xs(geo_list)
        for xs in xs_list:
            print '\nXS ID:', xs.header.xs_id
            print xs.mannings_n.horizontal, xs.mannings_n.values
            print xs.bank_sta.left, xs.bank_sta.right
            # print 'number sta_elv=', xs.sta_elev.num_pts
            # print xs.sta_elev.points
            # print xs.cutline.number_pts, xs.cutline.points
            # if xs.obstruct.blocked_type is not None:
            #     iefa_count +=1
            #     print '\nXS ID:', xs.header.xs_id
            #     # print xs.iefa.type, xs.iefa.iefa_list
            #     print xs.obstruct.blocked_type, xs.obstruct.num_blocked, xs.obstruct.blocked
            #     print xs.bank_sta.right, xs.bank_sta.left

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

    export_ras_geo(outfile, geo_list)
    
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
