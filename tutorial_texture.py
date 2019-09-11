import viz
import vizact
viz.go()

viz.clearcolor(viz.SLATE)

#Create a quad to display texture
quad = viz.addTexQuad(pos=[0,1.8,3])

#Create texture with repeating wrap mode
tex = viz.addTexture('images/tile_grass.jpg', wrap=viz.REPEAT)
tex.pos = 0

#Apply texture to quad
quad.texture(tex)

ANIMATE_SPEED = 0.1

def animateTexture():
    #Increment texture position
    tex.pos += ANIMATE_SPEED * viz.elapsed()

    #Create transform for texture
    mat = viz.Transform()
    mat.setTrans(tex.pos,0,0)

    #Apply transform to texture
    quad.texmat(mat)

vizact.ontimer(0,animateTexture)