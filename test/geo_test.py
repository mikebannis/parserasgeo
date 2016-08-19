import glob
import sys
import filecmp
import subprocess
sys.path.insert(0, '..')

import prg


def main():
    outfile = 'test.out'
    test_files = glob.glob('../geos/*.g??')
    print test_files

    for test_file in test_files:
        print '*' * 100,
        print 'Processing ', test_file
        geo = prg.ParseRASGeo(test_file)
        geo.write(outfile)

        if filecmp.cmp(test_file, outfile, shallow=False):
            print 'Geometry file', test_file, 'exported correctly.'
        else:
            print 'WARNING: file', test_file, 'did not export properly'
            subprocess.Popen(["diff", test_file, outfile])
            sys.exit('WARNING: file' + test_file + 'did not export properly')

if __name__ == '__main__':
    main()
