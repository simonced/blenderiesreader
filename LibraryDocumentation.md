# Introduction

You'll find here some tips and informations about how to use this library.

# Basic usage

From a python program:

    #First you need to include the lib in your script:
    from iesreader1995 import *
    
    #Then you can instanciate it:
    ies = iesReader(*path to your ies file here*)

From blender, it's a bit tricky:

    import Blender
    import bpy
    from Blender import *
    
    #to make python look into the same directory as the blend file
    blendPath = Blender.sys.expandpath('//')
    import sys
    sys.path.append(blendPath)
    from iesreader1995 import *
    
    #Then you can instanciate it:
    ies = iesReader(*name to your ies file here*)


# Methods

The library provides several methods to use or extract data:

## debug()

Allows to display the object content and data imported from the ies.

## get(*attribute*)

*This function can do many things:*
- If the file format is an IES: _get('version')_ returns "LM-63-1995"
  - It gets the associated ies header element. It is the lines with *`[xxx] yyy`*.
  - Supply *xxx* as parameter to the function and *yyy* is returned if the data exist.
  - All data of the IES out of the header are also accessible here. Refer to the table below for the list.
- If the file format is a EU: _get('version')_ returns "EU"
  - All data of the EU header are accessible here. Refer to the table below for the list.

## getOrthoCoords()

Converts the IES / EU candela values into a list of rectangular coordinates.  
The order of the data returned will be the SAME for all formats, even if these
data are in a different order from the file read.  
See details bellow.

## getMultipliedCandela(cv_) : float

This method returns the candela value *cv_* with the factor *multiplier* applied.
**Note:**  
Only for IES at the moment. Patch ready to take a similar value in consideration for the EU std.  
*This method is still under developpement as the source of the multiplier in the ies file is not clear yet.*

# Attributes

## For IES

| *Attribute Name* | *Usage* |
|------------------|---------|
| data | A dictionary containing the key:values of the header. Lines with `[`xxx`]` yyy data are inserted here. |
| version | The first line version is memorized here. *ONLY 1995 format is supported at the moment!* |
| tilt | The tilt content from the ies file : NONE, INCLUDE or FILE. |
| multiplier | The coefficient to be applied to the candela values.Used in the *getMultipliedCandela()* method. |
| unit\_type | feet or meters |
| photometric\_type | A,B or C |
| vertical\_angles\_count | Number of vertical angles. |
| horizontal\_angles\_count | Number of the horizontal angles. |
| vertical\_angles | List of the vertical angles. |
| horizontal\_angles | List of the horizontal angles. |
| candelas\_values | List of the candela values. *It's a flat list, has to be parsed together with the horizontal and vertical angles values to get sense. But you may not need to do it yourself.See details bellow. |
| ready | Once the file is parsed and all the candela values in memory, this attribute turns to True. |
| lamps_number | Number of lamps. |
| lamp_lumens | Lumens per lamp. |
| lamp_watts | Lamp watt input. |
| width | The width, info contained on the same line as the global informations. (types, angles...) |
| length | The length, info contained on the same line as the global informations. (types, angles...) |
| height | The height, info contained on the same line as the global informations. (types, angles...) |
| ballast_factor | The ballast factor. |

## For EU

| *Attribute Name* | *Usage* |
|------------------|---------|
| company | name of the company |
| ityp | type indicator |
| isym | symmetry |
| mc | number of C planes / accessible by *vertical\_angles\_count* too |
| dc | distance => float |
| ng | number of luminous intensities in each C plane / accessible by *horizontal\_angles\_count* too |
| dg | distance between C planes |
| repnum | report number |
| lumname | luminaire name |
| lumnumb | luminaire number |
| filename | file name |
| dateuser | date / user |
| l1 | length / Diameter |
| w1 | width |
| h1 | height |
| ldlum | length / diameter of luminous area |
| b1 | width of luminous area |
| hlumc0 | height of luminous area C plane 0 |
| hlumc90 | height of luminous area C plane 90 |
| hlumc180 | height of luminous area C plane 180 |
| hlumc270 | height of luminous area C plane 270 |
| dff | downward flux fraction % |
| lorl | light output ratio luminaire % |
| convfactor | conversion factor for luminous intensity |
| tiltlum | tilt of luminaire during measurement |
| nstd | number of std sets of lamps |

# Linearized data access

*Note:* Seems to need to be uploaded again... Need corrections anyway... TODO

![](http://img42.imageshack.us/img42/2254/linearizeddataexplannat.png)
