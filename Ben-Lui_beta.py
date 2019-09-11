import viz # vizard library
import numpy as np # numpy library - such as matrix calculation
import random # python library
import vizdriver_BenLui as vizdriver # vizard library
import viztask # vizard library
import math as mt # python library

##Code will be the threshold vs accumulator pop up bends experiment.

global driver, out # global variable
driver = vizdriver.Driver()

out = "-1"
# start empty world
###################  PERSPECTIVE CORRECT  ##################
###SET UP PHYSICAL DIMENSIONS OF SCREEN####
EH = 1.2 #metres from ground.
Eye_ScreenDist = 1 #distance from screen of ocular point
Proj_V = 1.115 #vertical extent of projection (m)
Proj_H = 1.965 #horizontal extent of projection (m)

# setting Field-of-View fov(vertical degree, horizontal ratio(vertical*ratio[deg]))
vfov = ((np.arctan((Proj_V/2)/Eye_ScreenDist))*2) * (180/np.pi)
h2v = Proj_H/Proj_V
viz.go()
viz.fov(vfov,h2v) #sets window aspect ratio.
viz.eyeheight(1.2)#viz.MainView.setPosition(0,EH,0) 
viz.clip(1,60) #clips world at 60m

##Create array of trials.
global radiiPool 
radiiPool = [50, 150, 250, 900, 1100, 1300, 2500, 3000, 3500, -1]

N = 10 ###Number of conditions, for this code we only have one.
TRIALS = 10
TotalN = N*TRIALS
TRIALSEQ = range(1,N+1)*TRIALS
direc = [1,-1]*(TotalN/2)
TRIALSEQ = np.sort(TRIALSEQ)
TRIALSEQ_signed = np.array(direc)*np.array(TRIALSEQ)
random.shuffle(TRIALSEQ_signed)

# background color
viz.clearcolor(viz.SKYBLUE)

# ground texture setting
def setStage():
	
	global groundplane, groundtexture	
	
	###should set this hope so it builds new tiles if you are reaching the boundary.
	fName = 'textures\strong_edge.bmp'
	
	# add groundplane (wrap mode)
	groundtexture = viz.addTexture(fName)
	groundtexture.wrap(viz.WRAP_T, viz.REPEAT)
	groundtexture.wrap(viz.WRAP_S, viz.REPEAT)
	
	groundplane = viz.addTexQuad() ##ground for right bends (tight)
	tilesize = 5000#300 #F***ING MASSIVE
	planesize = tilesize/5
	groundplane.setScale(tilesize, tilesize, tilesize)
	groundplane.setEuler((0, 90, 0),viz.REL_LOCAL)
	#groundplane.setPosition((0,0,1000),viz.REL_LOCAL) #move forward 1km so don't need to render as much.
	matrix = vizmat.Transform()
	matrix.setScale( planesize, planesize, planesize )
	groundplane.texmat( matrix )
	groundplane.texture(groundtexture)
	groundplane.visible(1)	
	
# road edge setting. Make at start of trial.
def BendMaker(radlist):
	
	#make left and right road edges for for a given radii and return them in a list.
	
	#needs to work with an array of radii

	rdsize = 1000 # Hz size for curve length
	
	#left_array= np.arange(0.0, np.pi*1000)/1000
	left_array= np.linspace(0.0, np.pi,rdsize)
	#right_array = np.arange(np.pi*1000, 0.0, -1)/1000  ##arange(start,stop,step). Array with 3142(/1000) numbers
	right_array = np.linspace(np.pi, 0.0, rdsize)  ##arange(start,stop,step). Array with 3142(/1000) numbers
		
	leftbendlist = []
	rightbendlist = []
	for r in radlist:
		x1 = np.zeros(rdsize)
		z1 = np.zeros(rdsize)
		x2 = np.zeros(rdsize)
		z2 = np.zeros(rdsize)	
			
		i = 0
		viz.startlayer(viz.LINE_STRIP) 
		viz.linewidth(5)
		viz.vertex(0, .1, 0) #START AT ORIGIN
		
		if r > 0:	#r=-1 means it is a straight.
			while i < rdsize:			
				x1[i] = (r*np.cos(right_array[i])) + r
				z1[i] = (r*np.sin(right_array[i]))
				#print (z1[i])
				viz.vertex(x1[i], .1, z1[i] )				
				i += 1
		else:
			viz.vertex(0,.1,100.0) #100m straight
			
		rightbend = viz.endlayer()
		rightbend.visible(0)
		rightbend.dynamic()
			
		# left bend of a given radii
		viz.startlayer(viz.LINE_STRIP)
		viz.linewidth(5)
		viz.vertex(0, .1, 0) #START AT ORIGIN
		i = 0
		if r > 0:	#r=-1 means it is a straight.
			while i < rdsize:			
				x1[i] = (r*np.cos(left_array[i])) - r
				z1[i] = (r*np.sin(left_array[i]))
				
				viz.vertex(x1[i], .1, z1[i] )				
				i += 1
		else:
			viz.vertex(0,.1,100.0) #100m straight
		leftbend = viz.endlayer()	
		leftbend.visible(0)
		leftbend.dynamic()
			
		leftbendlist.append(leftbend)
		rightbendlist.append(rightbend)
	
	
	return leftbendlist,rightbendlist 

def runtrials():
	
	global trialtype, trialtype_signed, groundplane, radiiPool, out
	
	yield viztask.waitTime(5.0) #allow me to get into the seat.
	
	setStage() # texture setting. #likely to have to be expanded.
	driver.reset() # initialization of driver
	[leftbends,rightbends] = BendMaker(radiiPool)
	viz.MainScene.visible(viz.ON,viz.WORLD)
	
	
	
	#add text to denote conditons.
	txtCondt = viz.addText("Condition",parent = viz.SCREEN)
	txtCondt.setPosition(.7,.2)
	txtCondt.fontSize(36)
	
	out = ""
	
	def updatePositionLabel():
		global driver, trialtype_signed, trialtype
		##WHAT DO I NEED TO SAVE?
		
		# get head position(x, y, z)
		pos = viz.get(viz.HEAD_POS)
		pos[1] = 0.0 # (x, 0, z)
		# get body orientation
		ori = viz.get(viz.BODY_ORI)
		steeringWheel = driver.getPos()
									
		#what data do we want? RoadVisibility Flag. SWA. Time, TrialType. x,z of that trial These can be reset in processing by subtracting the initial position and reorienting.
		SaveData(pos[0], pos[2], ori, steeringWheel) ##.
	
	vizact.ontimer((1.0/60.0),updatePositionLabel)
	

	for j in range(0,TotalN):
		#import vizjoy		

		trialtype=abs(TRIALSEQ_signed[j])
		trialtype_signed = TRIALSEQ_signed[j]								
			
		txtDir = ""
		#pick correct object
		if trialtype_signed > 0: #right bend
			trialbend = rightbends[trialtype-1]
			txtDir = "R"
		else:
			trialbend = leftbends[trialtype-1]
			txtDir = "L"
		
		# Define a function that saves data
		def SaveData(pos_x, pos_z, ori, steer):
			global out
			
			#what data do we want? RoadVisibility Flag. SWA. Time, TrialType. x,z of that trial These can be reset in processing by subtracting the initial position and reorienting.
			if out != '-1':
				# Create the output string
				currTime = viz.tick()			
				out = out + str(float((currTime))) + '\t' + str(trialtype_signed) + '\t' + str(pos_x) + '\t' + str(pos_z)+ '\t' + str(ori)+  '\t' + str(steer) + '\t' + str(radius) + '\t' + str(trialbend.getVisible()) + '\n'							
		
		radius= radiiPool[trialtype-1]
		if radius > 0: 
			msg = "Radius: " + str(radius) + txtDir
		else:
			msg = "Radius: Straight" + txtDir
		txtCondt.message(msg)
		trialbend.visible(1)
		
		#translate bend to driver position.
		driverpos = viz.MainView.getPosition()
		print driverpos
		trialbend.setPosition(driverpos[0],0, driverpos[2])
				
		#now need to set orientation
		driverEuler = viz.MainView.getEuler()
		trialbend.setEuler(driverEuler, viz.ABS_GLOBAL)
		
		
		
		#will need to save initial vertex for line origin, and Euler. Is there a nifty way to save the relative position to the road?
		driver.setSWA_invisible()
		yield viztask.waitTime(2) #wait for input .		
		
		trialbend.visible(0)
		driver.setSWA_visible()
		
		def checkCentred():
			
			centred = False
			while not centred:
				x = driver.getPos()
				if abs(x) < .5:
					centred = True
					break
			
#		centred = False
#		while not centred:
#			x = driver.getPos()
#			print x
		
		##wait a while
		print "waiting"
		yield viztask.waitDirector(checkCentred)
		print "waited"
		
		yield viztask.waitTime(2) #wait for input .		
		
		
		
	else:
		#print file after looped through all trials.
		fileproper=('Pilot_CDM.dat')
		# Opens nominated file in write mode
		path = viz.getOption('viz.publish.path/')
		file = open(path + fileproper, 'w')
		file.write(out)
		# Makes sure the file data is really written to the harddrive
		file.flush()                                        
		#print out
		file.close()
		
		#exit vizard
		
		viz.quit() ##otherwise keeps writting data onto last file untill ESC


viztask.schedule(runtrials())

