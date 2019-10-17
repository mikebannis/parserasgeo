from abc import ABC, abstractmethod


class Feature(ABC):
    """Features implement this class"""

    @staticmethod
    @abstractmethod
    def test(line):
        """Evaluate if the feature matches the line

        :returns: boolean, True if match
        """

    @abstractmethod
    def import_geo(self, line, geo_file):
        """Parse lines and set instance with attributes

        Note that this method is responsible for advancing the geo_file handle
        cursor as it consumes lines, e.g `next(geo_file)`         
        :returns: The next line to be read
        """

    @abstractmethod
    def __str__(self):
        """Serialize the feature as should be written to the HEC-RAS file

        :returns: string representation of Feature instance
        """
