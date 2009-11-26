#!/usr/bin/env python
# -*- coding: UTF-8 -*-

""" 
==========================
IES lamp file reader class
==========================

Version : 0.25
Update : 2009-11-26

Copyright November 2009 Simonced and RickyBlender (richardterrelive@live.ca)

Thread started on Blenderartists.org at
http://blenderartists.org/forum/showthread.php?p=1508803#post1508803

Let us know on the blenderartists forum if you use this script and if you encounter any problems running it.

License :
---------
- For personnal use only
- Not for commercial use
- It would be nice to reference the authors of this script when using it
- Please do not change the Copyright statements in the script

External references:
--------------------
good format spec : http://www.ltblight.com/English.lproj/LTBLhelp/pages/iesformat.html
"""

import re
import pprint
import math

class IESreader:

	#object constructor
	#==================
	def __init__(self, filePath_):
		
		#the data structure of the file readen
		self.data = {}
		
		#other specific attributes to be added as the unit, the type and the candela factor.
		self.version = ""
		self.multiplier = 0
		self.units_type = 0
		self.photometric_type = 0
		self.vertical_angles_count = 0
		self.horizontal_angles_count = 0
		self.vertical_angles = []
		self.horizontal_angles = []
		self.candelas_values = []
		#new properties added on 2009-11-25
		self.lamps_number = 0
		self.lamp_lumens = 0
		self.lamp_watts = 0
		
		self.ready = False	#allows to make some data extractions and other....
		
		try:
			#lines to be used in the loop
			
			#we start to count once the Title line is passed
			tilt_line_passed = False
			data_line_id = 0
				
			for line in open(filePath_).readlines():
				
				#header analys part
				#------------------
				if not tilt_line_passed:
				
					#line = line.strip()	#may be needed for some lines, but not all
					regKW = re.match("\[(.*)\](.*)", line)
					regVer = re.match("IESNA:(.*([0-9]{4}))", line)
					regTilt = re.match("TILT=(.*)", line)
					
					#We found key / value datas?
					if regKW:
						key = regKW.group(1)
						data = regKW.group(2)
						if key in self.data:
							self.data[key] += ' '+data.strip()
							
						else:
							self.data[key] = data.strip()
							
					elif regVer:
						self.version = regVer.group(1).strip()
						
						#On other files formats, we pass, only 1995 specs suported at the moment
						if regVer.group(2) != "1995":
							print "Error : Other file formats than 1995 are not handled"
							return
							
					elif regTilt:
						self.tilt = regTilt.group(1).strip()
						tilt_line_passed = True
						
					else:
						#Nothing match for here?
						print "Unrecognized data"
						
				else:
					#Start to analyse technical data
					################################
					data_line_id += 1
					
					#line calculus and offsets
					if self.tilt == "NONE":
						global_data_line = 1
						vertical_angles_line = 3
						horizontal_angles_line = 4
						candelas_values_start = 5
					else:
						global_data_line = 5
						vertical_angles_line = 7
						horizontal_angles_line = 8
						candelas_values_start = 9

					#analyse of the technical informations allowing to load the candela values and angles
					#====================================================================================
					if data_line_id == global_data_line:
						#mask = {# of lamps} {lumens per lamp} {candela multiplier} {# of vertical angles}
						# {# of horizontal angles} {photometric type} {units type} {width} {length} {height}
						data = line.strip().split()
						self.lamps_number = int(data[0])
						self.lamp_lumens = float(data[1])
						self.multiplier = data[2]
						self.vertical_angles_count = int(data[3])
						self.horizontal_angles_count = int(data[4])
						self.photometric_type = data[5]	# 1 feet, 2 meters
						self.units_type = data[6]
						
					
					elif data_line_id == vertical_angles_line:
						#vertical angles list
						self.vertical_angles.extend( line.strip().split() )
						if(len(self.vertical_angles)<self.vertical_angles_count):
							data_line_id -= 1	#other datas on the next line
						
					elif data_line_id == horizontal_angles_line:
						#horizontal angles list
						self.horizontal_angles.extend( line.strip().split() )
						if(len(self.horizontal_angles)<self.horizontal_angles_count):
							data_line_id -= 1	#other datas on the next line
						
					#Analyse of the candelas values
					#=----------------------------=
					#Because lines are splited, we have to count the inserted data to know if we need to load more informations
					elif data_line_id >= candelas_values_start and \
					len(self.candelas_values) < (self.horizontal_angles_count * self.vertical_angles_count):
						#the candela values, fun but hard part ;-)
						
						for value in re.split("[^0-9.]+", line):
							if value != "":
								self.candelas_values.append( float(value) )
						
					else:
						#Ok, if we come here we should have all our datas
						#since we may not need anymore data, we can update the ready status
						self.ready = True
			
		except Exception as msg:
			print "IES Error... %s" % msg
		
		#last piece of work, finnish to convert the anlges into floats
		for i in range( len(self.horizontal_angles) ):
			self.horizontal_angles[i] = float(self.horizontal_angles[i])

		for i in range( len(self.vertical_angles) ):
			self.vertical_angles[i] = float(self.vertical_angles[i])
			

	#Return one information from the data attribute
	#==============================================
	def get(self, field_):
		#Entry check to prevent error
		if(field_ in self.data):
			return self.data[field_]
		else:
			return None
	
	#debug method to simply check the content of data and other things
	#=================================================================
	def debug(self):
		pprint.pprint(self.__dict__)
	
	#A function to extract the ortho coordinates for the candale angles and values
	#=============================================================================
	def getOrthoCoords(self):
		
		if not self.ready:
			return None
		
		#let's proceed
		data = []
		
		#horizontal index, vertical index and candela index
		ci = 0
		
		for ha in self.horizontal_angles:
			for va in self.vertical_angles:
				cv = self.candelas_values[ci]
				
				x = cv * math.sin(math.radians(va)) * math.cos(math.radians(ha))
				y = cv * math.sin(math.radians(va)) * math.sin(math.radians(ha))
				z = cv * math.cos(math.radians(va))
				vector = [x,y,z]

                                #read of the next candela value
				ci += 1
				
				data.append(vector)
		
		# all data should have been converted
		return data

	#here we give the candela value from the file and this apply the multiplier
	#======================================
	def getMultipliedCandela(self, cv_):
		result = cv_* (1/self.multiplier)
		return result

#entry point for single class test
#=================================
if __name__=="__main__":
	ies = IESreader("ies1.txt")
	print "File Analysed"
	ies.debug()

	#sample code to list the couples H angle, Vangle = Candela value
	"""
	for hi in range(ies.horizontal_angles_count):
		for vi in range(ies.vertical_angles_count):
			cv = hi * ies.vertical_angles_count + vi	#this is the trick
			print "angle (%iH, %s / %iV, %s) = %s cds" % \
			(hi, ies.horizontal_angles[hi], vi, ies.vertical_angles[vi], ies.getMultipliedCandela(ies.candelas_values[cv]) )
	"""


	#print "Multiplier : ", ies.multiplier

	#print "Vertical angles count : ", ies.vertical_angles_count
	#print ies.vertical_angles
	#print "Horizontal angles", ies.horizontal_angles_count
	#print ies.horizontal_angles


	#once we have the file in memory, we can extract vertext x,y,z coordinates ;)
	#xyz = ies.getOrthoCoords()
	#print xyz
	
	#print "LAMP : %s" % ies.get("LAMP")
	#print "version %s" % ies.version

	#print "Lamps number = %s" % ies.lamps_number
	#print "Lumens per lamp = %s" % ies.lamp_lumens
