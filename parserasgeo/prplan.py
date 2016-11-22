"""
prplan.py - parse RAS plan file

Version 0.001

Parses very basic information from a RAS plan file.

"""

class ParseRASPlan(object):
    def __init__(self, plan_filename):
        self.plan_title = None   # Full plan name
        self.plan_id = None      # Short id
        self.geo_file = None     # geometry file extension: g01, g02, ..
        self.plan_file = None    # plan file extension: f01, f02, ..

        with open(plan_filename, 'rt') as plan_file:
            for line in plan_file:
                fields = line[:-1].split('=')  # Strip the newline and split by =
                
                # lookout for lines missing =
                if len(fields) == 1:
                    continue
                var = fields[0]
                value = fields[1]
                
                if var == 'Geom File':
                    self.geo_file = value
                elif var == 'Flow File':
                    self.plan_file = value
                elif var == 'Plan Title':
                    self.plan_title = value
                elif var == 'Short Identifier':
                    self.plan_id = value

    def __str__(self):
        s = 'Plan Title='+self.plan_title+'\n'
        s += 'Short Identifier='+self.plan_id+'\n'
        s += 'Geom File='+self.geo_file+'\n'
        s += 'Flow File='+self.plan_file+'\n'
        return s

def main():
    import sys

    prp = ParseRASPlan(sys.argv[1])
    print dir(prp)
    print str(prp)


if __name__ == '__main__':
    main()
