import parserasgeo as prg

def main():
    infile = r"Z:\UDFCD PLANNING\FHAD Review\Niver Round 3\Orig\20161012 FHAD Submittal\HEC-RAS\NiverCreek_FHAD_Sept.g01"
    #infile = r"Z:\UDFCD PLANNING\Grange Hall Creek\02 HYDRAULICS\HEC-RAS\GHC_FHAD.g01"
    infile = r"Z:\UDFCD PLANNING\FHAD Review\Sloans Lake Round 1\Orig\20161013 - Sloan'sLake_FHAD_HEC-RAS-20161007\HEC-RAS\SloansFHAD2017.g01"
    infile = r"Z:\UDFCD PLANNING\FHAD Review\Clear Creek Round 1\Orig\20161013 Review Submittal\ClearCreek_ModelReviewSubmittal\Hydraulics\ClearCreek_FHAD2016.g07"
    infile = r"Z:\UDFCD PLANNING\Second Creek\12 FHAD\01_RAS\HEC-RAS\Submittal 2 - working\SCFHAD.g02"

    geo = prg.ParseRASGeo(infile)
    cross_sections = geo.extract_xs()

    print 'There are skews at the flowing cross sections - river, reach, xs_id, skew_angle'

    skew = False
    for xs in cross_sections:
        if xs.skew.angle is not None:
            print xs.river+','+xs.reach+','+str(xs.header.xs_id)+','+str(xs.skew.angle)
            skew = True

    if not skew:
        print 'No cross sections are skewed'

if __name__ == '__main__':
    main()
