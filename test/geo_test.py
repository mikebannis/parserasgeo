#! /usr/bin/python 
import glob
import sys
import os
import filecmp
import subprocess

sys.path.insert(0, os.path.abspath('..'))
import parserasgeo as prg

def main():
    print '-' * 50
    print 'Using', prg.__path__, 'for parserasgeo'
    print '-' * 50, '\n'

    outfile = 'test.out'
    test_files = glob.glob('../geos/*.g??')
    #print len(test_files)
    #for x in test_files:
        #print type(x), x
    #    print  x

    for test_file in test_files:
        print '*' * 30,
        print 'Processing ', test_file
        geo = prg.ParseRASGeo(test_file)
	xss = geo.extract_xs()
	#xss[0].alter_channel_n()
        geo.write(outfile)

        if filecmp.cmp(test_file, outfile, shallow=False):
            print 'Geometry file', test_file, 'exported correctly.'
        else:
            print 'WARNING: file', test_file, 'did not export properly'
            subprocess.Popen(["diff", test_file, outfile])
            sys.exit('WARNING: file' + test_file + 'did not export properly')

if __name__ == '__main__':
    main()
