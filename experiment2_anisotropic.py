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

The experiment branch manipulates flow via anisotropic filtering using the anisotropy() function. This creates a sharper image depending on the ratio that is used.
Sharper images equates increased flow information.
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

def GenerateConditionLists(FACTOR_headingpool, FACTOR_flow, TrialsPerCondition):
	"""Based on two factor lists and TrialsPerCondition, create a factorial design and return trialarray and condition lists"""

	NCndts = len(FACTOR_headingpool) * len(FACTOR_flow)	

	#automatically generate factor lists so you can adjust levels using the FACTOR variables
	ConditionList_heading = np.repeat(FACTOR_headingpool, len(FACTOR_flow))
	ConditionList_flow = np.tile(FACTOR_flow, len(FACTOR_headingpool))

	print (ConditionList_heading)
	print (ConditionList_flow)

	TotalN = NCndts * TrialsPerCondition

	TRIALSEQ = range(0,NCndts)*TrialsPerCondition
	np.random.shuffle(TRIALSEQ)

	direc = [1,-1]*(TotalN/2) #makes half left and half right.
	np.random.shuffle(direc) 

	TRIALSEQ_signed = np.array(direc)*np.array(TRIALSEQ)

	return (TRIALSEQ_signed, ConditionList_heading, ConditionList_flow)

# ground texture setting
def setStage(TILING = True):
	
	"""Creates grass textured groundplane"""

	global gtexture
	
	# background color
	viz.clearcolor(viz.SKYBLUE)
	
	#CODE UP TILE-WORK WITH GROUNDPLANE.	
	##should set this up so it builds new tiles if you are reaching the boundary.
	#fName = 'textures\\strong_edge_redoutline.bmp'
	fName = 'textures\\strong_edge.bmp'
	gtexture = viz.addTexture(fName)
	gtexture.wrap(viz.WRAP_T, viz.REPEAT)
	gtexture.wrap(viz.WRAP_S, viz.REPEAT)
	# #add groundplane (wrap mode)
###UNCOMMENT FOR TILING
# Tiling saves memory by using two groundplane tiles instead of a massive groundplane. Since the drivers are essentially driving linearly forward, they cover a lot of distance across the z axis.
	gplane1 = viz.addTexQuad() ##
	tilesize = 3000
	texture_z_size = tilesize * 2
	#planesize = tilesize/5
	planesize = tilesize/5.0
	gplane1.setScale(tilesize, tilesize*2, tilesize)
	gplane1.setEuler((0, 90, 0),viz.REL_LOCAL)
	#groundplane.setPosition((0,0,1000),viz.REL_LOCAL) #move forward 1km so don't need to render as much (was originally commented out)
	matrix = vizmat.Transform()
	matrix.setScale( planesize, planesize*2, planesize )
	gplane1.texmat( matrix )
	#gplane1.texture(gtexture)
	gplane1.texture(gtexture)
	gplane1.visible(1)
#
	if TILING:
		# fName2 = 'textures\\strong_edge_blueoutline.bmp'
		#fName2 = 'textures\\strong_edge_blueoutline.bmp'
		fName2 = 'textures\\strong_edge.bmp'
		gtexture2 = viz.addTexture(fName2)
		gtexture2.wrap(viz.WRAP_T, viz.REPEAT)
		gtexture2.wrap(viz.WRAP_S, viz.REPEAT)
		gplane2 = gplane1.copy() #create duplicate.
		gplane2.setScale(tilesize, tilesize*2, tilesize)
		gplane2.setEuler((0, 90, 0),viz.REL_LOCAL)
		#groundplane.setPosition((0,0,1000),viz.REL_LOCAL) #move forward 1km so don't need to render as much.
		gplane2.texmat( matrix )
		#gplane1.texture(gtexture)
		gplane2.texture(gtexture2)
		gplane2.visible(1)
		gplane2.setPosition(0,0,tilesize*2)
		gplane2.zoffset(-1)
	else:
		gplane2 = []
	
	return(gplane1, gplane2, texture_z_size)
	

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
		self.FACTOR_flow = [1, 2, 4] #3 flow conditions. Sharpness doubles with each increase in factor level
		print(self.FACTOR_headingpool)
		self.TrialsPerCondition = 10 # was oriringally 10 for pilot	
		[trialsequence_signed, cl_heading, cl_flow]  = GenerateConditionLists(self.FACTOR_headingpool, self.FACTOR_flow, self.TrialsPerCondition)

		self.TRIALSEQ_signed = trialsequence_signed #list of trialtypes in a randomised order. -ve = leftwards, +ve = rightwards.
		self.ConditionList_heading = cl_heading
		self.ConditionList_flow = cl_flow


		self.Camera_Offset = np.linspace(-2, 2, 9)

		##### ADD GRASS TEXTURE #####
		[gplane1, gplane2, gplane_z_size] = setStage(TILING)
		self.gplane1 = gplane1
		self.gplane2 = gplane2
		self.gplane_z_size = gplane_z_size

		##### MAKE STRAIGHT OBJECT #####
		self.Straight = StraightMaker(x = 0, start_z = 0, end_z = 200)	
		self.Straight.visible(0)

		self.callback(viz.TIMER_EVENT,self.updatePositionLabel)
		self.starttimer(0,0,viz.FOREVER) #self.update position label is called every frame.
		
		self.driver = None
		self.SAVEDATA = False

		####### DATA SAVING ######
		datacolumns = ['ppid', 'heading', 'cameraoffset', 'flow', 'trialn','timestamp','trialtype_signed','World_x','World_z','WorldYaw','SWV','SWA','YawRate_seconds','TurnAngle_frames','Distance_frames','dt', 'StraightVisible', 'setpoint']
		self.Output = pd.DataFrame(columns=datacolumns) #make new empty EndofTrial data

		### parameters that are set at the start of each trial ####
		self.Trial_heading = 0	
		self.trial_flow = 1	
		self.Trial_N = 0 #nth trial
		self.Trial_trialtype_signed = 0
		self.Trial_Camera_Offset = 0 			
		self.Trial_setpoint = 0 #initial steering wheel angle 
		#self.Trial_Timer = 0 #keeps track of trial length. 
		#self.Trial_BendObject = None		
		
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
		
		global gtexture

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
			trial_flow = self.ConditionList_flow[trialtype] #set flow for trial

			print(str([trial_heading, trial_flow]))

			txtDir = ""
			
			######choose correct road object.######

			# changes message on screen			
			# msg = msg = "Heading: " + str(trial_heading) # COMMENT OUT FOR EXPERIMENT


			
			#update class trial parameters#
			self.Trial_N = i
			self.Trial_heading = trial_heading
			self.trial_flow = trial_flow	
			self.Trial_trialtype_signed = trialtype_signed
		
			yield viztask.waitTime(1) #wait for one second before change of camera heading

			#1) Offset camera
			#FOR EQUAL AND OPPOSITE USE THE LINE BELOW:
			self.Trial_Camera_Offset = trial_heading 

			#put a mask on so that the jump/flow change isn't so visible
			self.blackscreen.visible(viz.ON)
			yield viztask.waitFrame(6) #wait for six frames (.1 s)
			offset = viz.Matrix.euler( self.Trial_Camera_Offset, 0, 0 )
			viz.MainWindow.setViewOffset( offset )  # counter rotates camera
            gtexture.anisotropy(trial_flow) # sets new flow condition
			self.blackscreen.visible(viz.OFF) #turn the mask
			
			#2) give participant time with new flow field
			yield viztask.waitTime(1) #wait for one second after change of camera heading
			
			# msg = msg + '\n' + 'Offset: ' + str(self.Trial_Camera_Offset) #Save your variables - COMMENT OUT FOR EXPERIMENT
			# txtCondt.message(msg)	# COMMENT OUT FOR EXPERIMENT

			#3) Move straight to desired position			
			# Translate straight to driver position.
			driverpos = viz.MainView.getPosition()
			print driverpos
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
			output = [self.PP_id, self.Trial_heading, self.Trial_Camera_Offset, self.trial_flow, self.Trial_N, self.Current_Time, self.Trial_trialtype_signed, 
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
	
		if self.TILING:
		
			#check if groundplane is culled, and update it if it is. 
			if viz.MainWindow.isCulled(self.gplane1):
				#if it's not visible, move ahead 50m from the driver.
				
				print 'shift gplane1'

				#since the road is on average straight ahead you can just move the plane along the z axis

				#change gplane to the driver's position
				self.gplane1.setPosition(pos,viz.ABS_GLOBAL) 

				
				#change euler to match camera
				self.gplane1.setEuler([self.Current_yaw,90,0],viz.ABS_GLOBAL)
				
				#move forward one texture length.
				self.gplane1.setPosition(0,self.gplane_z_size, 0,viz.ABS_LOCAL) 

				
			if viz.MainWindow.isCulled(self.gplane2):
				#if it's not visible, move ahead 50m from the driver.
				
				print 'shift gplane2'
				
								#change gplane to the driver's position
				self.gplane2.setPosition(pos,viz.ABS_GLOBAL) 

				
				#change euler to match camera
				self.gplane2.setEuler([self.Current_yaw,90,0],viz.ABS_GLOBAL)
				
				#move forward one texture length.
				self.gplane2.setPosition(0,self.gplane_z_size, 0,viz.ABS_LOCAL) 

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

	myExp = myExperiment(EYETRACKING, PRACTICE, TILING, EXP_ID, ppid = ParticipantNumber) #initialises a myExperiment class

	viz.callback(viz.EXIT_EVENT,CloseConnections, myExp.EYETRACKING)

	viztask.schedule(myExp.runtrials())