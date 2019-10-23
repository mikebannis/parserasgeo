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

    def get_boundaries(
        self, river=None, reach=None, station_value=None, hydrograph_type=None
    ):
        """Get Boundary instances from unsteady flow
        :param river: Optional string of the name of river
        :param reach: Optional string of the name of reach
        :param station_value: Optional float representing the location of the station or 2-tuple representing a range
        :param hydrograph_type: Optional string matching the boundary hydrograph type
        :return: List of matching Boundary instances
        """
        boundaries = (item for item in self.uflow_list if isinstance(item, Boundary))
        if river is not None:
            boundaries = (bnd for bnd in boundaries if bnd.header.river_name == river)
        if reach is not None:
            boundaries = (bnd for bnd in boundaries if bnd.header.reach_name == reach)
        if station_value is not None:
            if isinstance(station_value, tuple):
                assert len(station_value) == 2
                if station_value[0] is not None:
                    boundaries = (
                        bnd
                        for bnd in boundaries
                        if bnd.header.station.value is not None
                        and bnd.header.station.value >= station_value[0]
                    )
                if station_value[1] is not None:
                    boundaries = (
                        bnd
                        for bnd in boundaries
                        if bnd.header.station.value is not None
                        and bnd.header.station.value <= station_value[1]
                    )
            else:
                boundaries = (
                    bnd
                    for bnd in boundaries
                    if bnd.header.station.value == station_value
                )
        if hydrograph_type is not None:
            boundaries = (
                bnd for bnd in boundaries if bnd.hydrograph.type == hydrograph_type
            )

        return list(boundaries)
