class Station(object):
    def __init__(self, station):
        self._raw_station = station
        self._id = station.strip()
        self._is_interpolated = self._id.endswith("*")
        self._value = float(self._id[:-1]) if self._is_interpolated else float(self._id)

    def __str__(self):
        return self._raw_station

    @property
    def is_interpolated(self):
        return self._is_interpolated

    @property
    def value(self):
        return self._value

    @property
    def id(self):
        return self._id
