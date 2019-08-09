
import os,random
from psychopy import visual,core,event

#The path to the images - currently set to the current working directory (where you're running the script from)
directory = os.getcwd()

#Setup for Screen and
# Create the window object.  Set it to full screen mode.  You'll need to set up a monitor called "Default" with the physical dimensions of your monitor in the monitor center (the icon with 2 monitors)
window = visual.Window(fullscr=False,monitor='Default',units='cm')
#Create the image object. Tell it to use our window object.
CenterImage = visual.ImageStim(window)
LeftImage = visual.ImageStim(window)
LeftImage.setPos((-8,0))
RightImage = visual.ImageStim(window)
RightImage.setPos((8,0))
#Create a clock object.
clock = core.Clock()

#Here is a function to do a forced choice
#Send it a left image and a right image
#Displays the images
#Returns the array of keypresses
#Note the general structure of drawing stuff to the screen here.  You draw other types of things to the screen in the same basic way.
def ForcedChoiceTrial(left, right,TrialDuration):
    #Assign images to the correct objects.
    LeftImage.setImage(left)
    RightImage.setImage(right)
    # Draw the jpegs to the window's back buffer
    LeftImage.draw(window)
    RightImage.draw(window)
    #Flush the key buffer and mouse movements
    event.clearEvents()
    #Put the image on the screen
    window.flip()
    #Reset our clock to zero  - I think this call should take less time than window.flip, so resetting after the flip should be slightly more accurate.
    clock.reset()
    #Wait two seconds.  Tie up the CPU the entire time (this is more accurate than letting other processes go)
    core.wait(TrialDuration,TrialDuration)
    #Get a list of all keys that were pressed during our wait.  Tell it to give also give us the amount of time since our clock was reset when the key was pressed (reaction time).
    keypresses = event.getKeys(None,clock)
    return keypresses


#The main program

#Start by pulling the images into a list
images = []
for file in os.listdir(directory):
    #Here  I'm converting the filenames to lower case and checking if they have a .jpg or .png extension
    if file.lower().endswith(".jpg")  or file.lower().endswith(".png") :
        #If the file is a jpg or png, add it to our list of images
        images.append(file)

#Randomize our image list
random.shuffle(images)

imageIndex = 0
#Go through a number of trials equal to the number of images divided by two (we're using two images per trial)
for i in range(0,len(images)/2):
    #Here we're running a forced choice trial with 2 images
    keys = ForcedChoiceTrial(images[imageIndex],images[imageIndex +1], 3)
    #Move to the next pair of images.
    imageIndex +=2
    #Print out all of the keypresses and reaction times
    for key in keys:
        #Here, the %s means that I'm sending it a varible that is a string.  The %.3f means that I'm sending a number with a decimal value and I want it to print out 3 decimal places
        #Each elemente of keys (referenced as 'key' within this loop) is a 2 item list.  The 0th element is the name of the key that was pressed.  The 1st element is the time in seconds.  I'm converting it to MS by multiplying by 1000
        print "Key: %s  RT: %.3f" %(key[0],key[1]*1000)
