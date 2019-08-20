"""
prprj.py - parse RAS project file

Version 0.001

Parses very basic information from a RAS project file.

"""

class ParseRASProject(object):
    def __init__(self, project_filename):
        self.project_title = None   # Full project name
        self.plan_files = []    # list of plan file extension: p01, p02, ..
        self.geom_files = []    # list of geom file extension: g01, g02, ..
        self.unsteady_files = []     # list of unsteady file extension: u01, u02, ...

        with open(project_filename, 'rt') as project_file:
            for line in project_file:
                fields = line[:-1].split('=')# Strip the newline

                # lookout for lines missing =
                if len(fields) == 1:
                    continue
                var = fields[0]
                value = fields[1]

                if var == 'Proj Title':
                    self.project_title = value
                elif var == 'Plan File':
                    self.plan_files.append(value)
                elif var == 'Geom File':
                    self.geom_files.append(value)
                elif var == 'Unsteady File':
                    self.unsteady_files.append(value)

    def __str__(self):
        s = 'Proj Title='+self.project_title+'\n'
        for plan in self.plan_files:
            s += 'Plan File='+plan+'\n'
        for geom in self.geom_files:
            s += 'Geom file='+geom+'\n'
        for unsteady in self.unsteady_files:
            s += 'Unsteady File='+unsteady+'\n'
        return s

def main():
    import sys

    prp = ParseRASProject(sys.argv[1])
    print(dir(prp))
    print(str(prp))


if __name__ == '__main__':
    main()
