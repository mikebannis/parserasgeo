import prg

def main():
    geo_file = 'geos\\SBK_PMR_MJB_Working.g02'
    print 'hasdfa'
    geo_list = prg.import_ras_geo(geo_file)
    print 'asdf'
    xs_list = prg.extract_xs(geo_list)

    with open('xs_reach.csv', 'wt') as outfile:
        for xs in xs_list:
            outfile.write(str(xs.xs_id)+' '+str(xs.channel_length)+'\n')

if __name__ == '__main__':
    main()
