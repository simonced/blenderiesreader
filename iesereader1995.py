#!/usr/bin/env python
# -*- coding: UTF-8 -*-

""" 
==========================
IES lamp file reader class
==========================

Version : 0.32
Update : 2009-12-11

Copyright November 2009 Simonced and RickyBlender (richardterrelive@live.ca)

See licence and other informations at
http://code.google.com/p/blenderiesreader/wiki/License

Project page :
http://code.google.com/p/blenderiesreader

Dev note :
----------
The EU std files are analysed.
The candelas values parsing is NOT finished yet.
The 26 first header lines are parsed.

Because a second std is taken in consideration here, this lb will be renamed, as the class name.

"""

import re
import pprint
import math

class IESreader:

	#object constructor
	#==================
	def __init__(self, filePath_):
		
		#the data structure of the file readen (HEADER PART)
		self.data = {}
		self.dataEU = {}	#Same for EU specific use

		# other specific attributes to be added as the unit, the type and the candela factor.
		self.version = ""
		self.multiplier = 1.0
		self.unit_type = ""
		self.photometric_type = ""
		self.vertical_angles_count = 0
		self.horizontal_angles_count = 0
		self.vertical_angles = []
		self.horizontal_angles = []
		self.candelas_values = []	# Groups of all H angles of each V angle (IES std)
		self.candelas_valuesEU = []	# Groups of all V angles of each H angle (EU std)
		self.tilt = ''
		# new properties added on 2009-11-25
		self.lamps_number = 0
		self.lamp_lumens = 0
		self.lamp_watts = 0
		# new properties added on 2009-12-02
		self.width = 0.0
		self.length = 0.0
		self.height = 0.0
		self.ballast_factor = 0.0
		
		self.ready = False	# allows to make some data extractions and other....

		#To convert from the ies data into a human readable form
		unit_types = ('dummy', 'feet', 'meters')
		photometric_types = ('dummy', 'C', 'B', 'A')

		try:
			#lines to be used in the loop
			
			#we start to count once the Title line is passed
			tilt_line_passed = False
			data_line_id = 0
			read_line = 0	#allow to follow the reading process from anywhere

			for line in open(filePath_).readlines():
				read_line += 1	#line in reading process

				if self.version == 'EU':
					# Shunt for EU data analysis
					# --------------------------
					self._analyseEU(line, read_line)

				elif not tilt_line_passed:
					# IES header analys part
					#-----------------------
					
					#line = line.strip()	#may be needed for some lines, but not all
					regVer = re.match("IESNA:(.*([0-9]{4}))", line)
					regKW = re.match("\[(.*)\](.*)", line)
					regTilt = re.match("TILT=(.*)", line)
					
					#We found key / value datas?
					if regVer:
						self.version = regVer.group(1).strip()

						#On other files formats, we pass, only 1995 specs suported at the moment
						if regVer.group(2) != "1995":
							print "Error : Other file formats than 1995 are not handled"
							return
							
					elif regKW:
						key = regKW.group(1)
						data = regKW.group(2)
						if key in self.data:
							self.data[key] += ' '+data.strip()
						else:
							self.data[key] = data.strip()
							
					elif regTilt:
						self.tilt = regTilt.group(1).strip()
						tilt_line_passed = True
						
					else:
						#difficult case, format non recognized?

						if self.version == '' and read_line == 1:
							#first update to do
							self.version = 'EU'
							self._analyseEU(line, read_line)
							#Allow to insert the first data of the EU file in the dataEU attribute

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
						global_second_line = 2
						vertical_angles_line = 3
						horizontal_angles_line = 4
						candelas_values_start = 5
					else:
						global_data_line = 5
						global_second_line = 6
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
						self.photometric_type = photometric_types[int(data[5])]
						self.unit_type = unit_types[int(data[6])] 	# 1 feet, 2 meters
						self.width = float(data[7])
						self.length = float(data[8])
						self.height = float(data[9])

					if data_line_id == global_second_line:
						# MAsk : {ballast factor} {future use} {input watts}
						data = line.strip().split()
						self.ballast_factor = float(data[0])
						self.lamp_watts = float(data[2])
					
					elif data_line_id == vertical_angles_line:
						#vertical angles list
						self.vertical_angles.extend( map( float, line.strip().split() ) )
						if(len(self.vertical_angles)<self.vertical_angles_count):
							data_line_id -= 1	#other datas on the next line
						
					elif data_line_id == horizontal_angles_line:
						#horizontal angles list
						self.horizontal_angles.extend( map(float, line.strip().split() ) )
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


	#Return one information from the data attribute
	#==============================================
	def get(self, field_):
		#Let's first check if the field_ could be a property.
		#The goal of it is to make this lib easily compatible with other formats thant 1995
		if field_ in self.__dict__ :
			return self.__dict__[field_]

		#Entry check in the header data analysed to prevent error
		if self.version=='LM-63-1995' and field_ in self.data:
			return self.data[field_]

		elif self.version=='EU' and field_ in self.dataEU:
			return self.dataEU[field_]
		
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
			#first check, file ready?
			return None

		elif self.version == "LM-63-1995":
			#Ok, IES 95 standrd file
			return self._getOrthoCoordsFromIES95()

		elif self.version == 'EU':
			#Same thing woth the EU data, because they are stored in a different way
			return self._getOrthoCoordsFromEU()
		

	#The analysing function for the EU file std
	#==========================================
	def _analyseEU(self, data_, read_line_):
		#Some initialisations
		last_header_line = 30	#about
		va_start_line = 43
		ha_start_line = va_start_line + self.vertical_angles_count
		cv_start_line = ha_start_line + self.horizontal_angles_count
		cv_end_line = cv_start_line + (self.vertical_angles_count * self.horizontal_angles_count)

		#cleaning of the data
		data = data_.strip()

		#Simple parsing at the moment (HEADER DATA)
		if read_line_ == 1:
			self.dataEU['company'] = data
		elif read_line_ == 2:
			self.dataEU['ityp'] = int(data)	# Type indicator
		elif read_line_ == 3:
			self.dataEU['isym'] = int(data)	# Symmetry
		elif read_line_ == 4:
			self.vertical_angles_count = int(data)
			self.dataEU['mc'] = int(data)
		elif read_line_ == 5:
			self.dataEU['dc'] = float(data)	# distance => float
		elif read_line_ == 6:
			self.horizontal_angles_count = int(data)
			self.dataEU['ng'] = int(data)	# number of luminous intensities in each C plane
		elif read_line_ == 7:
			self.dataEU['dg'] = float(data)	# Distance between C planes
		elif read_line_ == 8:
			self.dataEU['repnum'] = data	# Report number
		elif read_line_ == 9:
			self.dataEU['lumname'] = data	# Luminaire name
		elif read_line_ == 10:
			self.dataEU['lumnumb'] = data	# luminaire number
		elif read_line_ == 11:
			self.dataEU['filename'] = data	# File name
		elif read_line_ == 12:
			self.dataEU['dateuser'] = data	# Date / User
		elif read_line_ == 13:
			self.dataEU['l1'] = float(data)	# Length / Diameter
		elif read_line_ == 14:
			self.dataEU['w1'] = float(data)	# Width
		elif read_line_ == 15:
			self.dataEU['h1'] = float(data)	# Height
		elif read_line_ == 16:
			self.dataEU['ldlum'] = float(data)	# length / diameter of luminous area
		elif read_line_ == 17:
			self.dataEU['b1'] = float(data)	# width of luminous area
		elif read_line_ == 18:
			self.dataEU['hlumc0'] = float(data)	# height of luminous area C plane 0
		elif read_line_ == 19:
			self.dataEU['hlumc90'] = float(data)	# height of luminous area C plane 90
		elif read_line_ == 20:
			self.dataEU['hlumc180'] = float(data)	# height of luminous area C plane 180
		elif read_line_ == 21:
			self.dataEU['hlumc270'] = float(data)	# height of luminous area C plane 270
		elif read_line_ == 22:
			self.dataEU['dff'] = float(data)	# Downward flux fraction %
		elif read_line_ == 23:
			self.dataEU['lorl'] = float(data)	# Light output ratio luminaire %
		elif read_line_ == 24:
			self.dataEU['convfactor'] = float(data)	# Conversion factor for luminous intensity
		elif read_line_ == 25:
			self.dataEU['tiltlum'] = float(data)	# Tilt of luminaire during measurement
		elif read_line_ == 26:
			self.dataEU['nstd'] = int(data)	# Number of std sets of lamps
		#next few lines are difficult to understand... let's pass for the moment.

		elif read_line_ >= va_start_line and read_line_< ha_start_line:
			self.vertical_angles.append( float(data) )

		elif read_line_ >= ha_start_line and read_line_< cv_start_line:
			self.horizontal_angles.append( float(data) )

		elif read_line_ >= cv_start_line and read_line_ < cv_end_line:
			self.candelas_valuesEU.append( float(data) )

		else:
			print "Unparsed EU data at line ", read_line_

		#print "reading EU : ", read_line_, cv_end_line
		
		#finished parsing?
		if read_line_ > last_header_line and read_line_ > cv_end_line:
			self.ready = True
		

	#The function to create the ortho data from the 1995 IES standard
	#================================================================
	def _getOrthoCoordsFromIES95(self):
		#let's proceed
		data = []

		#candela index
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


	#The function to create the ortho data from the EU standard
	#==========================================================
	def _getOrthoCoordsFromEU(self):
		#let's proceed
		data = []

		#candela index
		ci = 0

		for va in self.vertical_angles:
			for ha in self.horizontal_angles:
				cv = self.candelas_valuesEU[ci]

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
	# @param cv_ Float
	# @return Float
	#======================================
	def getMultipliedCandela(self, cv_):
		result = cv_* (1/self.multiplier)
		return result

	#TODO
	#Create a function to parse the angles and candelas values the same way
	#independently from the format
	

#entry point for single class test
#=================================
if __name__=="__main__":
	#IES std = ies1.txt
	#EUR std : ERCO_34162000_1xQT-DE12_1000W.ies
	ies = IESreader("ERCO_34162000_1xQT-DE12_1000W.ies")
	print "File Analysed"
	#ies.debug()

	#sample code to list the couples H angle, Vangle = Candela value
	"""
	for hi in range(ies.horizontal_angles_count):
		for vi in range(ies.vertical_angles_count):
			cv = hi * ies.vertical_angles_count + vi	#this is the trick
			print "angle (%iH, %s / %iV, %s) = %s cds" % \
			(hi, ies.horizontal_angles[hi], vi, ies.vertical_angles[vi], ies.getMultipliedCandela(ies.candelas_values[cv]) )
	"""

	#new attribute acccess method
	print "Version : ", ies.get("version")

	if ies.get("version")=='EU':
		# -= EU specific value tests =-
		print "Company = ", ies.get('company')
		print "DFF = ", ies.get('dff')

	else:
		# -= IES specific tests =-
		print "LAMP : %s" % ies.get("LAMP")

		print "Lamps number = %s" % ies.get('lamps_number')
		print "Lumens per lamp = %s" % ies.get('lamp_lumens')

	"""
	#Check of the angles only
	print "Vertical angles count : ", ies.vertical_angles_count
	print ies.vertical_angles
	print "Horizontal angles", ies.horizontal_angles_count
	print ies.horizontal_angles
	"""

	"""
	#The candela values?
	if ies.version=='EU':
		pprint.pprint( ies.candelas_valuesEU )
	else:
		pprint.pprint( ies.candelas_values )
	"""

	print "Ready? ", ies.ready

	#once we have the file in memory, we can extract vertext x,y,z coordinates ;)
	print "Ortho Data :"
	print ies.getOrthoCoords()
