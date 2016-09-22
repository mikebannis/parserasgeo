#from tools import fl_int #  , split_by_n_str, pad_left, print_list_by_group, split_block_obs, split_by_n


class Description(object):
    """
    This is a template for other features.
    """
    def __init__(self):
        self.text = []
        pass

    @staticmethod
    def test(line):
        if line == 'BEGIN DESCRIPTION:\n':
            return True
        return False

    def import_geo(self, line, geo_file):
        line = next(geo_file)
        while line != 'END DESCRIPTION:\n':
            self.text.append(line[:-1])
            line = next(geo_file)
        return next(geo_file)

    def __str__(self):
        s = 'BEGIN DESCRIPTION:\n'
        for line in self.text:
            s += line + '\n'
        s += 'END DESCRIPTION:\n'
        return s
