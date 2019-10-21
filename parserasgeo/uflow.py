from .features.boundary import Boundary


class UnsteadyFlow(object):
    """
    Imports RAS unsteady flow data in filename, i.e. project_name.u??
    """

    def __init__(self, filename):
        self.filename = filename
        self.uflow_list = []

        with open(filename, "rt") as infile:
            while True:
                line = infile.readline()
                if not line:
                    break
                if Boundary.test(line):
                    boundary = Boundary()
                    boundary.import_geo(line, infile)
                    self.uflow_list.append(boundary)
                else:  # Unknown line, add as text
                    self.uflow_list.append(line)

    def export(self, outfilename):
        """
        Writes unsteady flow data to outfilename.
        """
        with open(outfilename, "wt", newline="\r\n") as outfile:
            for line in self.uflow_list:
                outfile.write(str(line))
