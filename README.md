# Polarization Simulator

The repository serves a very preliminary tool to analyze the data taken with Thorlabs PAX1000 Polarimeter using the [PAX1000-Polarimeter-Tool](https://github.com/Wallace-Chen/PAX1000-Polarimeter-Tool).

The code could:
* convert from the experiment coordinate to the sample's spherical coordinates
* plot distribution of the stokes parameters (power, s1, s2, s3) on the detector side given an input light with specific polarization shining on the sample.

# Requirements

install pre-requitesite Python modules:
```
# Geometry3D module
pip install Geometry3D

# pandas module
pip install pandas
```

# Usage

1. Have raw data taken, for example, like [here](https://drive.google.com/drive/folders/16wcE0LyY5Uue4JcfnSwVQ6B4E5ZVo0Ns).

2. Use `src/dataFormatter.py` to analyze the raw data, do the coordinate conversion and merge the data. For example:
```
from dataFormatter import *

myformatter = dataFormatter()
# './RCW' is your data folder, 
# inpol indicate the polarization of input light expressed in the format of S1_S2_S3
#   0_0_1 means the right-handed polarization
# "polarizationData_{}.csv".format(inpol) is the output file name
inpol = "0_0_1"
myformatter.combineOriginalCSVs("./RCW", inpol, "polarizationData_{}_debug.csv".format(inpol))

# you can use the following to merge multiple output files when you have data for different input polarizations
fs = ["polarizationData_RCW.csv", "polarizationData_LCW.csv"]
myformatter.mergeCSVs(fs, 'polarizationData_all.csv')
```
You will need to put `src/dataFormatter.py`, and `src/Geometry3DWrapper.py` into your local folder where you will call the module.
The final output CSV file can be found `./data/polarizationData_all.csv`

3. With the converted data file ready, `src/PolarizationSimulator.py` can be used to show the plots.

Copy `src/PolarizationSimulator.py` to your local folder, and do:
```
from PolarizationSimulator import *

# make sure you give the correct path to your data file
mysim = SampleSimulator('../data/polarizationData_all.csv')
# simulate for a right-handed polarization light, shoot to the sample with (10, 0) angle
mysim.simulate('0_0_1', 10, 0)
```

Refer to files under `./sample` for the sample code.

# Note

This is a very preliminary tool, only support circularly polarized lights currently. The distribution plots are not showing the full range for phi and eta, due to the experiment limitations. Extending to linearly polarized lights requires a bit more considerations.

Use with caution, nothing gauranteed.

