# parserasgeo
Import/export HEC-RAS geometry files

parserasgeo (prg) is a python library for editing, importing, and exporting HEC-RAS geometry files. prg is a work in progress, however most cross section functionality exists. Lines that prg does not understand are stored as text and will be rewritten when the geometry is exported. Therefore it should work with any RAS geo file.

One of the goals for this library is that exported geometries will match original geometries to the character. This allows easy testing of new functionality by comparing the original geo file to one exported from prg (assuming no changes were made). 

## Known issues
* HEC-RAS allows cross section ids with trailing zeros, e.g. 225.0, 123.40. prg currently treats all XS ids as floats or ints, thereby discarding trailing zeros. While this should be easy to fix, it may break compatibility with other software I use, and will be updated at some point in the future.
