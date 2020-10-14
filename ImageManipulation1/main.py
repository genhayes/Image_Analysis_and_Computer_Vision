# Image manipulation
# Genevieve Hayes 
#
# You'll need Python 2.7 and must install these packages:
#
#   numpy, PyOpenGL, Pillow
#
# Note that file loading and saving (with 'l' and 's') are not
# available if 'haveTK' below is False.  If you manage to install
# python-tk, you can set that to True.  Otherwise, you'll have to
# provide the filename in 'imgFilename' below.
#
# Note that images, when loaded, are converted to the YCbCr
# colourspace, and that you should manipulate only the Y component 
# of each pixel when doing intensity changes.


import sys, os, numpy, math

try: # Pillow
  from PIL import Image
except:
  print( 'Error: Pillow has not been installed.' )
  sys.exit(0)

try: # PyOpenGL
  from OpenGL.GLUT import *
  from OpenGL.GL import *
  from OpenGL.GLU import *
except:
  print( 'Error: PyOpenGL has not been installed.' )
  sys.exit(0)



haveTK = False # sys.platform != 'darwin'


# Globals

windowWidth  = 600 # window dimensions
windowHeight =  800

localHistoRadius = 5  # distance within which to apply local histogram equalization



# Current image

imgDir      = 'images'
imgFilename = 'mandrill.png'
#imgFilename = 'pup.jpg'
#imgFilename = 'veggies.jpg'

currentImage = Image.open( os.path.join( imgDir, imgFilename ) ).convert( 'YCbCr' ).transpose( Image.FLIP_TOP_BOTTOM )
tempImage    = None



# File dialog (doesn't work on Mac OSX)

if haveTK:
  import Tkinter, tkFileDialog
  root = Tkinter.Tk()
  root.withdraw()

#%%

# Apply brightness and contrast to tempImage and store in
# currentImage.  The brightness and constrast changes are always made
# on tempImage, which stores the image when the left mouse button was
# first pressed, and are stored in currentImage, so that the user can
# see the changes immediately.  As long as left mouse button is held
# down, tempImage will not change.

def applyBrightnessAndContrast( brightness, contrast ):

  width  = currentImage.size[0]
  height = currentImage.size[1]

  srcPixels = tempImage.load()
  dstPixels = currentImage.load()

  # YOUR CODE HERE:
  a = contrast
  b = brightness
  for i in range(width): #loop through each pixel horizontally 
           for j in range(height): #loop through each pixel vertically
                 newYpixel = a*srcPixels[i,j][0] + b #apply brightness and contrast values to Y component of tempImage pixel 
                 currentImage.putpixel((i,j), (newYpixel,dstPixels[i,j][1],dstPixels[i,j][2])) #set currentImage pixel to equal altered tempImage pixel

# Check pixel values before and after brightness and contrast manipulation
  print('Original currentImage Y pixel value:', srcPixels[width-1,height-1][0])
  print('Manipulated Y pixel value:', newYpixel)
  alteredPixels = currentImage.load()
  print('New currentImage Y pixel value:', alteredPixels[width-1,height-1][0])
  print( 'adjust brightness = %f, contrast = %f' % (brightness,contrast) )


# Perform local histogram equalization on the current image using the given radius.

def performHistoEqualization( radius ):
#performHistoEqualization( radius ) conducts a local histogram equalization on the current image within a neighbourhood of pixels given a radius.
#The chessboard method is used to select the neighbouring pixels.
  pixels = currentImage.load()
  width  = currentImage.size[0]
  height = currentImage.size[1]
  N = width*height #total number of pixels

  # YOUR CODE HERE
  L = 256 #number of possible intensity values
  h_local = [0] * L
  np_pixels = numpy.asarray(currentImage)
  for i in range(radius,width): #loop through each pixel horizontally 
          for j in range(radius,height): #loop through each pixel vertically
            #check for start and end boundary conditions and only include pixel inside of image within neighbourhood.
            if i<= radius:
              widthStart = 0
              widthEnd = i+radius
            if j<= radius:
              heightStart = 0
              heightEnd = j+radius
            if i>= width-radius:
              widthStart = i-radius
              widthEnd = width
            if j>= height-radius:
              heightStart = j-radius
              heightEnd = height
            if i>radius and i<width-radius:
              widthStart = i-radius
              widthEnd = i+radius
            if j>radius and j<height-radius:
              heightStart = j-radius
              heightEnd = j+radius

            Y_local = np_pixels[heightStart:heightEnd,widthStart:widthEnd,0] #height and width are swapped in 3D numpy array

            h_local, bin_edges = numpy.histogram(Y_local.flatten(), bins = range(L+1)) #make histogram of all pixel intensities in neighbourhood
            localSum = numpy.cumsum(h_local)
            localLookup = (L*localSum/((2*radius+1)*(2*radius)))+1 #build look table
            Y_ij = pixels[i,j][0] #find current pixel's intensity value
            newPixel = localLookup[Y_ij] 
            currentImage.putpixel((i,j), (newPixel,pixels[i,j][1],pixels[i,j][2])) #set currentImage pixel to contain new altered pixel
  print( 'perform local histogram equalization with radius %d' % radius )

# Scale the tempImage by the given factor and store it in
# currentImage.  Use backward projection.  This is called when the
# mouse is moved with the right button held down.

def scaleImage( factor ):
  #scaleImage( factor ) scales the image about the origin (bottom left corner). If the scaling factor > 1, some of the
  #zoomed in image will cropped to maintain the same image size. If the scaling factor < 1, some of the top and right 
  #borders of the zoomed out image will be filled in with black.
  
  width  = currentImage.size[0]
  height = currentImage.size[1]
  
  srcPixels = tempImage.load()
  dstPixels = currentImage.load()

  # YOUR CODE HERE
  f = factor
  print('the scaling factor is', f)
  #set width and height
  newWidth = int(numpy.round(f*width))
  newHeight = int(numpy.round(f*height))
  print('width and height', width, height)
  print('scaled width and height', newWidth, newHeight)

  if f>=1: #scaling currentImage up
    for i_unscaled in range(width): #loop through each pixel of the scaled image horizontally 
           for j_unscaled in range(height): #loop through each pixel of the scaled image vertically
                i = int(numpy.floor(i_unscaled/f))
                j = int(numpy.floor(j_unscaled/f))
                newPixel = srcPixels[i,j]
                #new pixel value in currentImage
                currentImage.putpixel((i_unscaled,j_unscaled), newPixel)
  
  if f<1: #scaling currentImage down
    for i_unscaled in range(width): #loop through each pixel of the scaled image horizontally 
           for j_unscaled in range(height): #loop through each pixel of the scaled image vertically
                i = int(numpy.floor(i_unscaled/f)) #width index at inverse the scaling factor
                j = int(numpy.floor(j_unscaled/f)) #height index at inverse the scaling factor
                if i_unscaled<newWidth and j_unscaled<newHeight:
                  #set scaled currentImage pixel to closest unscaled tempImage pixel
                  newPixel = srcPixels[i,j] #sample original image at index equivalent to inverse the scaling factor
                  currentImage.putpixel((i_unscaled,j_unscaled), newPixel)
                else:
                  #set pixels outside of new image boundaries to neural colour
                  currentImage.putpixel((i_unscaled,j_unscaled), srcPixels[0,0]) #set currentImage pixel to contain new altered pixel
            
  #print('final i and j:',i,j)
  #print('final unscaled i and j:',i_unscaled,j_unscaled)

# Set up the display and draw the current image

def display():

  # Clear window

  glClearColor ( 1, 1, 1, 0 )
  glClear( GL_COLOR_BUFFER_BIT )

  # rebuild the image

  img = currentImage.convert( 'RGB' )

  width  = img.size[0]
  height = img.size[1]

  # Find where to position lower-left corner of image

  baseX = (windowWidth-width)/2
  baseY = (windowHeight-height)/2

  glWindowPos2i( baseX, baseY )

  # Get pixels and draw

  imageData = numpy.array( list( img.getdata() ), numpy.uint8 )

  glDrawPixels( width, height, GL_RGB, GL_UNSIGNED_BYTE, imageData )

  glutSwapBuffers()


  
# Handle keyboard input

def keyboard( key, x, y ):

  global localHistoRadius

  if key == '\033': # ESC = exit
    sys.exit(0)

  elif key == 'l':
    if haveTK:
      path = tkFileDialog.askopenfilename( initialdir = imgDir )
      if path:
        loadImage( path )

  elif key == 's':
    if haveTK:
      outputPath = tkFileDialog.asksaveasfilename( initialdir = '.' )
      if outputPath:
        saveImage( outputPath )

  elif key == 'h':
    performHistoEqualization( localHistoRadius )

  elif key in ['+','=']:
    localHistoRadius = localHistoRadius + 1
    print( 'radius =', localHistoRadius )

  elif key in ['-','_']:
    localHistoRadius = localHistoRadius - 1
    if localHistoRadius < 1:
      localHistoRadius = 1
    print( 'radius =', localHistoRadius )

  else:
    print( 'key =', key )    # DO NOT REMOVE THIS LINE.  It will be used during automated marking.

  glutPostRedisplay()



# Load and save images.
#
# Modify these to load to the current image and to save the current image.
#
# DO NOT CHANGE THE NAMES OR ARGUMENT LISTS OF THESE FUNCTIONS, as
# they will be used in automated marking.


def loadImage( path ):

  global currentImage

  currentImage = Image.open( path ).convert( 'YCbCr' ).transpose( Image.FLIP_TOP_BOTTOM )


def saveImage( path ):

  global currentImage

  currentImage.transpose( Image.FLIP_TOP_BOTTOM ).convert('RGB').save( path )
  


# Handle window reshape


def reshape( newWidth, newHeight ):

  global windowWidth, windowHeight

  windowWidth  = newWidth
  windowHeight = newHeight

  glutPostRedisplay()



# Mouse state on initial click

button = None
initX = 0
initY = 0



# Handle mouse click/release

def mouse( btn, state, x, y ):

  global button, initX, initY, tempImage

  if state == GLUT_DOWN:
    tempImage = currentImage.copy()
    button = btn
    initX = x
    initY = y
  elif state == GLUT_UP:
    tempImage = None
    button = None

  glutPostRedisplay()

  

# Handle mouse motion

def motion( x, y ):

  if button == GLUT_LEFT_BUTTON:

    diffX = x - initX
    diffY = y - initY

    applyBrightnessAndContrast( 255 * diffX/float(windowWidth), 1 + diffY/float(windowHeight) )

  elif button == GLUT_RIGHT_BUTTON:

    initPosX = initX - float(windowWidth)/2.0
    initPosY = initY - float(windowHeight)/2.0
    initDist = math.sqrt( initPosX*initPosX + initPosY*initPosY )
    if initDist == 0:
      initDist = 1

    newPosX = x - float(windowWidth)/2.0
    newPosY = y - float(windowHeight)/2.0
    newDist = math.sqrt( newPosX*newPosX + newPosY*newPosY )

    scaleImage( newDist / initDist )

  glutPostRedisplay()
  


# Run OpenGL

glutInit()
glutInitDisplayMode( GLUT_DOUBLE | GLUT_RGB )
glutInitWindowSize( windowWidth, windowHeight )
glutInitWindowPosition( 50, 50 )

glutCreateWindow( 'imaging' )

glutDisplayFunc( display )
glutKeyboardFunc( keyboard )
glutReshapeFunc( reshape )
glutMouseFunc( mouse )
glutMotionFunc( motion )

glutMainLoop()
