import viz # vizard library
import numpy as np # numpy library - such as matrix calculation
import random # python library
import vizdriver_BenLui as vizdriver # vizard library
import viztask # vizard library
import math as mt # python library
import vizshape

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
viz.clip(1,150) #Further clip means higher band of dots. 

##Create array of trials.
global radiiPool,occlPool
#radiiPool = [50, 150, 250, 900, 1100, 1300, 2500, 3000, 3500, -1] #This was the selection used for Pilot.
radiiPool = [300, 600, 900, 1200, 1500, 1800, 2100, 2400, 2700, 3000, 3300, 3600,-1] #13 radii conditions. 300m steps.
occlPool = [0, .5, 1] #3 occlusion conditions

N = len(radiiPool) * len(occlPool) ###Number of conditions.
TRIALS = 10 #is this enough? Let's see.
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
	
#	###should set this hope so it builds new tiles if you are reaching the boundary.
#	fName = 'textures\strong_edge.bmp'
#	
#	# add groundplane (wrap mode)
#	groundtexture = viz.addTexture(fName)
#	groundtexture.wrap(viz.WRAP_T, viz.REPEAT)
#	groundtexture.wrap(viz.WRAP_S, viz.REPEAT)
#	
#	groundplane = viz.addTexQuad() ##ground for right bends (tight)
#	tilesize = 5000#300 #F***ING MASSIVE
#	planesize = tilesize/5
#	groundplane.setScale(tilesize, tilesize, tilesize)
#	groundplane.setEuler((0, 90, 0),viz.REL_LOCAL)
#	#groundplane.setPosition((0,0,1000),viz.REL_LOCAL) #move forward 1km so don't need to render as much.
#	matrix = vizmat.Transform()
#	matrix.setScale( planesize, planesize, planesize )
#	groundplane.texmat( matrix )
#	groundplane.texture(groundtexture)
#	groundplane.visible(1)	
	
	gsize = [1000,1000] #groundplane size, metres
	groundplane = vizshape.addPlane(size=(gsize[0],gsize[1]),axis=vizshape.AXIS_Y,cullFace=True) ##make groundplane
	groundplane.texture(viz.add('black.bmp')) #make groundplane black

	#Build dot plane to cover black groundplane
	ndots = 200000 #arbitrarily picked. perhaps we could match dot density to K & W, 2013? 
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
	grey = [.8,.8,.8]
	for r in radlist:
		x1 = np.zeros(rdsize)
		z1 = np.zeros(rdsize)
		x2 = np.zeros(rdsize)
		z2 = np.zeros(rdsize)	
			
		i = 0
		viz.startlayer(viz.LINE_STRIP) 
		#viz.linewidth(5)
		viz.linewidth(3)
		viz.vertexColor(grey)
		viz.vertex(0, .1, 0) #START AT ORIGIN
		
		if r > 0:	#r=-1 means it is a straight.
			while i < rdsize:			
				x1[i] = (r*np.cos(right_array[i])) + r
				z1[i] = (r*np.sin(right_array[i]))
				#print (z1[i])
				viz.vertexColor(grey)
				viz.vertex(x1[i], .1, z1[i] )		
				
				i += 1
		else:
			viz.vertex(0,.1,100.0) #100m straight
			
		rightbend = viz.endlayer()
		rightbend.visible(0)
		rightbend.dynamic()
			
		# left bend of a given radii
		viz.startlayer(viz.LINE_STRIP)
		#viz.linewidth(5)
		viz.linewidth(3)
		viz.vertexColor(grey)
		viz.vertex(0, .1, 0) #START AT ORIGIN
		i = 0
		if r > 0:	#r=-1 means it is a straight.
			while i < rdsize:			
				x1[i] = (r*np.cos(left_array[i])) - r
				z1[i] = (r*np.sin(left_array[i]))
				viz.vertexColor(grey)
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
	
	#yield viztask.waitTime(5.0) #allow me to get into the seat.
	
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

		
		# Define a function that saves data
		def SaveData(pos_x, pos_z, ori, steer):
			global out
			
			#what data do we want? RoadVisibility Flag. SWA. Time, TrialType. x,z of that trial These can be reset in processing by subtracting the initial position and reorienting.
			if out != '-1':
				# Create the output string
				currTime = viz.tick()										
				out = out + str(float((currTime))) + '\t' + str(trialtype_signed) + '\t' + str(pos_x) + '\t' + str(pos_z)+ '\t' + str(ori)+  '\t' + str(steer) + '\t' + str(radius) + '\t' + str(occlusion) + '\t' + str(int(trialbend.getVisible())) + '\n'							
		
		radiipick = 1
		occlpick = 1
		L = len(radiiPool)
		L2 = L*2
		print trialtype, L, L2
		if trialtype > L and trialtype <= L2:
			print 'here'
			radiipick = trialtype-L #reset trialtype and occl index
			occlpick = 2				
		elif trialtype > L2:
			print 'here too'
			radiipick = trialtype - L2
			occlpick = 3
			
		print radiipick
			#pick correct object
		if trialtype_signed > 0: #right bend
			trialbend = rightbends[radiipick-1]
			txtDir = "R"
		else:
			trialbend = leftbends[radiipick-1]
			txtDir = "L"
				
		
		radius= radiiPool[radiipick-1]
		occlusion = occlPool[occlpick-1]
		if radius > 0: 
			msg = "Radius: " + str(radius) + txtDir + '_' + str(occlusion)
		else:
			msg = "Radius: Straight" + txtDir + '_' + str(occlusion)
		txtCondt.message(msg)				
		
		#translate bend to driver position.
		driverpos = viz.MainView.getPosition()
		print driverpos
		trialbend.setPosition(driverpos[0],0, driverpos[2])
				
		#now need to set orientation
		driverEuler = viz.MainView.getEuler()
		trialbend.setEuler(driverEuler, viz.ABS_GLOBAL)		
		
		#will need to save initial vertex for line origin, and Euler. Is there a nifty way to save the relative position to the road?
		driver.setSWA_invisible()		
		
		yield viztask.waitTime(occlusion) #wait an occlusion period
		
		trialbend.visible(1)
		
		yield viztask.waitTime(2.5-occlusion) #after the occlusion add the road again. 2.5s to avoid ceiling effects.
		
		trialbend.visible(0)
		#driver.setSWA_visible()
		
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
		
		driver.setSWA_visible()
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

