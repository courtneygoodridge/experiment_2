import viz
import vizmat

viz.go()
#create two textures 

# background color
viz.clearcolor(viz.SKYBLUE)
	
fName = 'textures\\strong_edge_redoutline.bmp'
gtexture = viz.addTexture(fName)
gtexture.wrap(viz.WRAP_T, viz.REPEAT)
gtexture.wrap(viz.WRAP_S, viz.REPEAT)

gplane1 = viz.addTexQuad() ##
tilesize = 5 

planesize = tilesize/5.0
gplane1.setScale(tilesize, tilesize*2, tilesize)
gplane1.setEuler((0, 90, 0),viz.REL_LOCAL)

texture_z_size = tilesize*2

matrix = vizmat.Transform()
matrix.setScale( planesize, planesize*2, planesize )
gplane1.texmat( matrix )
gplane1.texture(gtexture)
gplane1.visible(1)
	
#create second texture
fName2 = 'textures\\strong_edge_blueoutline.bmp'
gtexture2 = viz.addTexture(fName2)
gtexture2.wrap(viz.WRAP_T, viz.REPEAT)
gtexture2.wrap(viz.WRAP_S, viz.REPEAT)

gplane2 = gplane1.copy() #create duplicate.
	
gplane2.setScale(tilesize, tilesize*2, tilesize)
gplane2.setEuler((0, 90, 0),viz.REL_LOCAL)
#groundplane.setPosition((0,0,1000),viz.REL_LOCAL) #move forward 1km so don't need to render as much.
gplane2.texmat( matrix )
gplane2.texture(gtexture2)
gplane2.visible(1)
gplane2.setPosition(0,0,texture_z_size)
gplane2.zoffset(-1)

viz.MainView.setPosition(0,50,0)
viz.MainView.setEuler(0,90,0)


def onTimer(num): 
#Use the time ids to identify the timer. 
	move_speed = 5
	
	if viz.MainWindow.isCulled(gplane1):
		print "gplane1 culled"

		gplane1.setPosition(0,0, texture_z_size*2,viz.REL_GLOBAL) #bring to driver pos


	if viz.MainWindow.isCulled(gplane2):
		print "gplane2 culled"
		
		gplane2.setPosition(0,0, texture_z_size*2,viz.REL_GLOBAL) #bring to driver pos

	if viz.key.isDown(viz.KEY_UP):
		viz.MainView.move([0,0,move_speed*viz.elapsed()],viz.BODY_ORI)
	elif viz.key.isDown(viz.KEY_DOWN):
		viz.MainView.move([0,0,move_speed*viz.elapsed()],viz.BODY_ORI)

#Register the timer callback. 
viz.callback(viz.TIMER_EVENT,onTimer) 
#Start both timers.  
#The first will be repeated.  
viz.starttimer( 0, 1/60.0, viz.PERPETUAL )

