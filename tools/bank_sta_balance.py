import parserasgeo as prg

def main():
    infile = r"Z:\UDFCD PLANNING\FHAD Review\Niver Round 3\Orig\20161012 FHAD Submittal\HEC-RAS\NiverCreek_FHAD_Sept.g01"
    infile = r"Z:\UDFCD PLANNING\Grange Hall Creek\02 HYDRAULICS\HEC-RAS\GHC_FHAD.g01"
    #infile = r"Z:\UDFCD PLANNING\FHAD Review\Sloans Lake Round 1\Orig\20161013 - Sloan'sLake_FHAD_HEC-RAS-20161007\HEC-RAS\SloansFHAD2017.g01"
    infile = r"Z:\UDFCD PLANNING\FHAD Review\Niver Round 3\Orig\20161012 FHAD Submittal\HEC-RAS\NiverCreek_FHAD_Sept.g03"
    #infile = r"Z:\UDFCD PLANNING\FHAD Review\SPR - 6th to 58th\Orig\20160907 Merrick_SPR 6th-58th_08-26-2016\SPR 6th-58th_Existing_HECRAS\SPR_Downstream.g04"

    tolerance = 1

    geo = prg.ParseRASGeo(infile)
    cross_sections = geo.extract_xs()

    for xs in cross_sections:
        left_elv = xs.sta_elev.elevation(xs.bank_sta.left)
        right_elv = xs.sta_elev.elevation(xs.bank_sta.right)
        diff = left_elv - right_elv
        if abs(diff) >= tolerance:
            print xs.river+','+xs.reach+','+str(xs.header.xs_id)+','+str(diff)

if __name__ == '__main__':
    main()
