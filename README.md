# Parserasgeo

PARSE hec-RAS GEOmetry - Import/Export [HEC-RAS](https://www.hec.usace.army.mil/software/hec-ras/) geometry files. 

Parserasgeo is a python library for importing, editing, and exporting HEC-RAS geometry files and can be used for automating sensitivity analyses, Monte Carlo analyses, and any other work flow that requires changing RAS geometry programmatically. Parserasgeo is a work in progress, however most cross section functionality exists. Lines that are not understand are stored as text and will be rewritten when the geometry is exported. Parserasgeo is known to work with Python 2 and should also work with Python 3.

HEC-RAS models can be run automatically using [rascontrol](https://github.com/mikebannis/rascontrol).


## Getting Started

Parserasgeo is mostly easily installed from GitHub

```
C:\> git clone https://github.com/mikebannis/parserasgeo.git

C:\> cd parserasgeo

C:\parserasgeo> pip install .
```

## Example 

Open a model, increase all Manning's n values by 50%, and save the geometry as a new file.

```python
import parserasgeo as prg

geo = prg.ParseRASGeo('my_model.g01')

for xs in geo.get_cross_sections():
	n_vals = xs.mannings_n.values 
	
	# n-values are stored as a list of 3-tuples
	new_n = [(station, n*1.5, other) for station, n, other in n_vals]
	
	xs.mannings_n.values = new_n
	
geo.write('my_model.g02')
```

## Contributing

While currently functional, this is very much a work in progress. Well written and tested pull requests are gladly accepted.

One of the goals for this library is that exported geometries will match original geometries to the character. This allows easy testing of new functionality by comparing the original geometry file to one exported from parserasgeo (assuming no changes were made).
