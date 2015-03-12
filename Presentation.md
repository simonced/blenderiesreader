# Introduction #

This started as a script help on blenderartists.org here :
http://blenderartists.org/forum/showthread.php?t=171630

The authors of this project are :
  * Rickyblender
  * Simonced

Let us know on the blenderartists forum if you use this script and if you encounter any problems running it.

# License #

Please read the [License](License.md) page.

# Description #

The goal of this project it to have a blender script to show the IES curves of light fixture as 2D polar diagram or as a 3D vector diagram independently of external programs like _ies viewer_ which allows to view the beam shape for a light fixture in 2D or 3D with an intensity value in candelas.

Here is a snapshot of the 3D mesh generated from an IES file:

![http://img514.imageshack.us/img514/1632/blenderiestest03.jpg](http://img514.imageshack.us/img514/1632/blenderiestest03.jpg)

**2010-09-13 : Blender 2.5 API update**
The script have been updated to work in Blender 2.5 API.

Still modifiers have to be done but the data from the IES python class can be loaded now.

Screenie (sorry for huge pic):
![http://img829.imageshack.us/img829/2323/portage25.jpg](http://img829.imageshack.us/img829/2323/portage25.jpg)


**Note:**
For the time being there is no relationship between these values and what you see in blender's render.

The parts of this project are :
  * a blend file that creates and display the object.
  * a python library created to convert the IES data into vertices coordinates for blender.

# Our references #
The main ies specifications we read about are located here :

http://www.ltblight.com/English.lproj/LTBLhelp/pages/iesformat.html

# How does it work? #

The blend file (polar6.blend) is the entry point. You can use the script included inside (see the screen editor) to launch an import of an IES file.

_(The IES file can be in any directory, but are located in the same directory as the blend file for convenience.)_

This blend file uses the external library we created (iesreader1995.py) to get the data and generate the diagram. The goal of the library is to convert the polar coordinates contained in the IES file into corrdinates understandable by blender.

# Todo #

  * A simple documentation on how to use it.
  * A simple documentation about the python class. ([Started here](LibraryDocumentation.md))
  * Updating the script to use a GUI. (RickyBlender is on it)
  * Changing the mesh object into a spline object to allow more control of the display.