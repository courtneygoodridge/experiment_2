1 
"""
Script to run threshold vs accumulator experiment. The participant experiences vection across a textured ground-plane. 
After a few seconds a straight road appears with a experimentally controlled deflection angle. The participants task is to steer so as to try and stay on the straight road.
A further few seconds elapses. The road disapears. The participant experiences a few seconds of vection without a road, then a new straight appears with a different deflection angle.
The main script to run the experiment is Ben-Lui__beta_main.py
The Class myExperiment handles execution of the experiment.
This script relies on the following modules:
For eyetracking - eyetrike_calibration_standard.py; eyetrike_accuracy_standard.py; also the drivinglab_pupil plugin.
For perspective correct rendering - myCave.py
For motion through the virtual world - vizdriver_BenLui.py

The difference in this script is that the green grass plane is removed and replaced with a dot flow field. 
"""
import sys

rootpath = 'C:\\VENLAB data\\shared_modules\\Logitech_force_feedback'
sys.path.append(rootpath)
rootpath = 'C:\\VENLAB data\\shared_modules'
sys.path.append(rootpath)
rootpath = 'C:\\VENLAB data\\shared_modules\\pupil\\capture_settings\\plugins\\drivinglab_pupil\\'
sys.path.append(rootpath)

import viz # vizard library
import numpy as np # numpy library - such as matrix calculation
import random # python library
import vizdriver_BenLui as vizdriver # vizard library
import viztask # vizard library
import math as mt # python library
import vizshape
import vizact
import vizmat
import myCave
import pandas as pd
import random

def LoadEyetrackingModules():

	"""load eyetracking modules and check connection"""

	from eyetrike_calibration_standard import Markers, run_calibration
	from eyetrike_accuracy_standard import run_accuracy
	from UDP_comms import pupil_comms

	###Connect over network to eyetrike and check the connection
	comms = pupil_comms() #Initiate a communication with eyetrike	
	#Check the connection is live
	connected = comms.check_connection()

	if not connected:
		print("Cannot connect to Eyetrike. Check network")
		raise Exception("Could not connect to Eyetrike")
	else:
		pass	
	#markers = Markers() #this now gets added during run_calibration				
	
def LoadCave():
	"""loads myCave and returns Caveview"""

	#set EH in myCave
	cave = myCave.initCave()
	#caveview = cave.getCaveView()
	return (cave)

def GenerateConditionLists(FACTOR_headingpool, FACTOR_dots, TrialsPerCondition):
	"""Based on two factor lists and TrialsPerCondition, create a factorial design and return trialarray and condition lists"""

	NCndts = len(FACTOR_headingpool) * len(FACTOR_dots)	

		#automatically generate factor lists so you can adjust levels using the FACTOR variables
	ConditionList_heading = np.repeat(FACTOR_headingpool, len(FACTOR_dots))
	ConditionList_dots = np.tile(FACTOR_dots, len(FACTOR_headingpool))

	print(ConditionList_heading)
	print(ConditionList_dots)

	TotalN = NCndts * TrialsPerCondition

	TRIALSEQ = range(0,NCndts)*TrialsPerCondition
	np.random.shuffle(TRIALSEQ)

	direc = [1,-1]*(TotalN/2) #makes half left and half right.
	np.random.shuffle(direc) 

	TRIALSEQ_signed = np.array(direc)*np.array(TRIALSEQ)

	return (TRIALSEQ_signed, ConditionList_heading, ConditionList_dots)

# background color
viz.clearcolor(viz.SKYBLUE) # comment out for black sky plane but might be best to leave sky blue in order 

# ground texture setting
def setStage():
	
	global ndots	
	
	gsize = [1000,1000] #groundplane size, metres
	groundplane = vizshape.addPlane(size=(gsize[0],gsize[1]),axis=vizshape.AXIS_Y,cullFace=True) ##make groundplane
	groundplane.texture(viz.add('black.bmp')) #make groundplane black

	#Build dot plane to cover black groundplane
	ndots = 3645 #arbitrarily picked. perhaps we could match dot density to K & W, 2013? 
	viz.startlayer(viz.POINTS)
	viz.vertexColor(viz.WHITE)	
	viz.pointSize(2)
	for i in range (0,ndots):
		x =  (random.random() - .5)  * gsize[0]
		z = (random.random() - .5) * gsize[1]
		viz.vertex([x,0,z])
	
	dots = viz.endLayer()
	dots.setPosition(0,0,0)
	dots.visible(1)
	groundplane.visible(1)


def StraightMaker(x, start_z, end_z, colour = [.8,.8,.8], primitive= viz.QUAD_STRIP, width=None):
	"""returns a straight, given some starting coords and length"""
	viz.startlayer(primitive)
	if width is None:
		if primitive == viz.QUAD_STRIP:
			width = .05
		elif primitive == viz.LINE_STRIP:
			width = 2
			viz.linewidth(width)
			width = 0
	
	viz.vertex(x-width,.1,start_z)
	viz.vertexcolor(colour)
	viz.vertex(x+width,.1,start_z)
	viz.vertexcolor(colour)
	viz.vertex(x-width,.1,end_z)
	viz.vertexcolor(colour)
	viz.vertex(x+width,.1,end_z)		

	straightedge = viz.endlayer()

	return straightedge

class myExperiment(viz.EventClass):

	def __init__(self, eyetracking, practice, tiling, exp_id, ppid = 1):

		viz.EventClass.__init__(self) #specific to vizard classes
	
		self.EYETRACKING = eyetracking
		self.PRACTICE = practice
		self.TILING = tiling
		self.EXP_ID = exp_id

		self.datafilename = str(exp_id) + '_' + str(ppid) + '.csv'

		if EYETRACKING == True:	
			LoadEyetrackingModules()

		self.PP_id = ppid
		self.VisibleRoadTime = 2.5 #length of time that road is visible. Constant throughout experiment
	
		#### PERSPECTIVE CORRECT ######
		self.cave = LoadCave()
		self.caveview = self.cave.getCaveView() #this module includes viz.go()

		##### SET CONDITION VALUES #####
		self.FACTOR_headingpool = np.linspace(-2, 2, 9) # experimental angles
		self.FACTOR_dots = [1, 10000, 1000000000] # experiment dot flow fields 
		print(self.FACTOR_headingpool)
		print(self.FACTOR_dots)
		self.TrialsPerCondition = 10 # was oriringally 10 for pilot	
		[trialsequence_signed, cl_heading, cl_dots]  = GenerateConditionLists(self.FACTOR_headingpool, self.FACTOR_dots, self.TrialsPerCondition)

		self.TRIALSEQ_signed = trialsequence_signed #list of trialtypes in a randomised order. -ve = leftwards, +ve = rightwards.
		self.ConditionList_heading = cl_heading
		self.ConditionList_dots = cl_dots

		self.Camera_Offset = np.linspace(-2, 2, 9)

		##### MAKE STRAIGHT OBJECT #####
		self.Straight = StraightMaker(x = 0, start_z = 0, end_z = 200)	
		self.Straight.visible(0)

		self.callback(viz.TIMER_EVENT,self.updatePositionLabel)
		self.starttimer(0,0,viz.FOREVER) #self.update position label is called every frame.
		
		self.driver = None
		self.SAVEDATA = False

		####### DATA SAVING ######
		datacolumns = ['ppid', 'heading', 'cameraoffset', ' dots', 'trialn','timestamp','trialtype_signed','World_x','World_z','WorldYaw','SWV','SWA','YawRate_seconds','TurnAngle_frames','Distance_frames','dt', 'StraightVisible', 'setpoint']
		self.Output = pd.DataFrame(columns=datacolumns) #make new empty EndofTrial data

		### parameters that are set at the start of each trial ####
		self.Trial_heading = 0
		self.Trial_dots = 0			
		self.Trial_N = 0 #nth trial
		self.Trial_trialtype_signed = 0
		self.Trial_Camera_Offset = 0 			
		self.Trial_setpoint = 0 #initial steering wheel angle 
		#self.Trial_Timer = 0 #keeps track of trial length. 
		
		#### parameters that are updated each timestamp ####
		self.Current_pos_x = 0
		self.Current_pos_z = 0
		self.Current_yaw = 0
		self.Current_SWV = 0
		self.Current_SWA = 0
		self.Current_Time = 0
		self.Current_RowIndex = 0		
		self.Current_YawRate_seconds = 0
		self.Current_TurnAngle_frames = 0
		self.Current_distance = 0
		self.Current_dt = 0


		self.blackscreen = viz.addTexQuad(viz.SCREEN)
		self.blackscreen.color(viz.BLACK)
		self.blackscreen.setPosition(.5,.6)
		self.blackscreen.setScale(100,100)
		self.blackscreen.visible(viz.OFF)

		self.callback(viz.EXIT_EVENT,self.SaveData) #if exited, save the data. 

	def runtrials(self):
		"""Loops through the trial sequence"""
		
		setStage()
		self.driver = vizdriver.Driver(self.caveview)	
		self.SAVEDATA = True # switch saving data on.
		
		viz.MainScene.visible(viz.ON,viz.WORLD)		
	
		#add text to denote conditons - COMMENT OUT FOR EXPERIMENT
		# txtCondt = viz.addText("Condition",parent = viz.SCREEN)
		# txtCondt.setPosition(.7,.2)
		# txtCondt.fontSize(36)		

		if self.EYETRACKING:
			comms.start_trial()
		
		for i, trialtype_signed in enumerate(self.TRIALSEQ_signed):

			### iterates each trial ###

			#import vizjoy		
			print("Trial: ", str(i))
			print("TrialType: ", str(trialtype_signed))
			
			trialtype = abs(trialtype_signed)

			trial_heading = self.ConditionList_heading[trialtype] #set heading for that trial
			trial_dots = self.ConditionList_dots[trialtype]

			print(str([trial_heading, trial_dots]))

			txtDir = ""
			
			######choose correct road object.######

			# changes message on screen			
			# msg = msg = "Heading: " + str(trial_heading) # COMMENT OUT FOR EXPERIMENT


			
			#update class trial parameters#
			self.Trial_N = i
			self.Trial_heading = trial_heading	
			self.Trial_dots = trial_dots
			self.Trial_trialtype_signed = trialtype_signed			
			
		
			yield viztask.waitTime(1) #wait for one second before change of camera heading

			#1) Offset camera
			#FOR EQUAL AND OPPOSITE USE THE LINE BELOW:
			self.Trial_Camera_Offset = trial_heading 

			#put a mask on so that the jump isn't so visible
			self.blackscreen.visible(viz.ON)
			yield viztask.waitFrame(6) #wait for six frames (.1 s)
			offset = viz.Matrix.euler( self.Trial_Camera_Offset, 0, 0)
			viz.MainWindow.setViewOffset( offset )  # counter rotates camera
			ndots = trial_dots
			self.blackscreen.visible(viz.OFF) #turn the mask
			
			#2) give participant time with new flow field
			yield viztask.waitTime(1) #wait for one second after change of camera heading
			
			# msg = msg + '\n' + 'Offset: ' + str(self.Trial_Camera_Offset) #Save your variables - COMMENT OUT FOR EXPERIMENT
			# txtCondt.message(msg)	# COMMENT OUT FOR EXPERIMENT

			#3) Move straight to desired position			
			# Translate straight to driver position.
			driverpos = viz.MainView.getPosition()
			print(driverpos) 
			self.Straight.setPosition(driverpos[0],0, driverpos[2])


			# Match straight orientation to the driver
			driverEuler = viz.MainView.getEuler() # gets current driver euler (orientation)
			print ("driverEuler", driverEuler) # prints the euler 
			self.Straight.setEuler(driverEuler, viz.ABS_GLOBAL) # then sets the straight euler as the driver euler in global coordinates.
			
			# Offset the angle
			offsetEuler = [trial_heading, 0, 0] # this creates the straight offset
			self.Straight.setEuler(offsetEuler, viz.REL_LOCAL)

			#will need to save initial vertex for line origin, and Euler. Is there a nifty way to save the relative position to the road?
			
			#4) Reset set point and make the straight visible 
			self.Trial_setpoint = self.driver.reset_setpoint()
			self.driver.setSWA_invisible() # sets SWA invisible on screen		
			self.Straight.visible(1)
			
			#5) Wait for the trial time
			yield viztask.waitTime(self.VisibleRoadTime) # add the road again. 2.5s to avoid ceiling effects.
			
			#6) Remove straight
			self.Straight.visible(0)
			

			
			def checkCentred():
				
				centred = False
				x = self.driver.getPos()
				if abs(x) < .1:
					centred = True
					return (centred)
			
			##wait a while
			#print "waiting"
			#TODO: Recentre the wheel on automation.

			#yield viztask.waitTrue(checkCentred)
			#print "waited"	
	
		#loop has finished.
		CloseConnections(self.EYETRACKING)
		#viz.quit() 

	
	def getNormalisedEuler(self):
		"""returns three dimensional euler on 0-360 scale"""
		
		euler = self.caveview.getEuler()
		
		euler[0] = vizmat.NormAngle(euler[0])
		euler[1] = vizmat.NormAngle(euler[1])
		euler[2] = vizmat.NormAngle(euler[2])

		return euler

	def RecordData(self):
		
		"""Records Data into Dataframe"""
		

		if self.SAVEDATA:
			output = [self.PP_id, self.Trial_heading, self.Trial_Camera_Offset, self.Trial_dots, self.Trial_N, self.Current_Time, self.Trial_trialtype_signed, 
			self.Current_pos_x, self.Current_pos_z, self.Current_yaw, self.Current_SWV, self.Current_SWA, self.Current_YawRate_seconds, self.Current_TurnAngle_frames, 
			self.Current_distance, self.Current_dt, self.Current_StraightVisibleFlag, self.Trial_setpoint] #output array.		

			self.Output.loc[self.Current_RowIndex,:] = output #this dataframe is actually just one line. 		
	
	def SaveData(self):

		"""Saves Current Dataframe to csv file"""

		# self.Output.to_csv('Data//Pilot.csv') #pilot
		
		self.Output.to_csv(self.datafilename)
	

	def updatePositionLabel(self, num): #num is a timer parameter
		
		"""Timer function that gets called every frame. Updates parameters for saving and moves groundplane if TILING mode is switched on"""

		#print("UpdatingPosition...")	
		#update driver view.
		if self.driver is None: #if self.driver == None, it hasn't been initialised yet. Only gets initialised at the start of runtrials()
			UpdateValues = [0, 0, 0, 0, 0]
		else:
			UpdateValues = self.driver.UpdateView() #update view and return values used for update
		
		# get head position(x, y, z)
		pos = self.caveview.getPosition()
				
		ori = self.getNormalisedEuler()		
									
		### #update Current parameters ####
		self.Current_pos_x = pos[0]
		self.Current_pos_z = pos[2]
		self.Current_SWV = UpdateValues[4]
		self.Current_SWA = self.Current_SWV * 90 #-1 is -90, 1 = 90.
		self.Current_yaw = ori[0]
		self.Current_RowIndex += 1
		self.Current_Time = viz.tick()
		self.Current_YawRate_seconds = UpdateValues[0]
		self.Current_TurnAngle_frames = UpdateValues[1]
		self.Current_distance = UpdateValues[2]
		self.Current_dt = UpdateValues[3]

		
		self.Current_StraightVisibleFlag = self.Straight.getVisible()	
	


		self.RecordData() #write a line in the dataframe.
	
def CloseConnections(EYETRACKING):
	
	"""Shuts down EYETRACKING and wheel threads then quits viz"""		
	
	print ("Closing connections")
	if EYETRACKING: 
	 	comms.stop_trial() #closes recording			
	
	#kill automation
	viz.quit()
	
if __name__ == '__main__':

	###### SET EXPERIMENT OPTIONS ######	
	EYETRACKING = True
	PRACTICE = True
	TILING = True #to reduce memory load set True to create two groundplane tiles that dynamically follow the driver's position instead of one massive groundplane.
	EXP_ID = "BenLui17"

	if PRACTICE == True: # HACK
		EYETRACKING = False 

	
	ParticipantNumber = viz.input('Enter participant number') #cmg edit 
	#ParticipantID = viz.input('Enter unique participant ID') #cmg edit

	#datafilename = str(ParticipantNumber) + '_' + str(ParticipantID) #cmg edit

	myExp = myExperiment(EYETRACKING, PRACTICE, TILING, EXP_ID, ppid = ParticipantNumber) #initialises a myExperiment class

	viz.callback(viz.EXIT_EVENT,CloseConnections, myExp.EYETRACKING)

	viztask.schedule(myExp.runtrials())