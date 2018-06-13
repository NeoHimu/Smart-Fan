# import the necessary packages
from picamera.array import PiRGBArray
from picamera import PiCamera
import time
import cv2
import sys
import RPi.GPIO as GPIO


# Switches off if face is not detected continuously for 10 sec
# Use BCM GPIO references
# instead of physical pin numbers
GPIO.setmode(GPIO.BCM) 

pin_relay = 18
GPIO.setup(pin_relay,GPIO.OUT)
# Define GPIO signals to use
# Physical pins 11,15,16,18
# GPIO17,GPIO22,GPIO23,GPIO24
StepPins = [17,22,23,24]

# Set all pins as output
for pin in StepPins:
  #print "Setup pins"
  GPIO.setup(pin,GPIO.OUT)
  GPIO.output(pin, False)

# Define advanced sequence
# as shown in manufacturers datasheet

Seq = [[1,0,0,1],
       [1,0,0,0],
       [1,1,0,0],
       [0,1,0,0],
       [0,1,1,0],
       [0,0,1,0],
       [0,0,1,1],
       [0,0,0,1]]
#Seq = [[0,0,0,1], [0,0,1,1],[0,0,1,0],[0,1,1,0],[0,1,0,0],[1,1,0,0],[1,0,0,0],[1,0,0,1]]       

StepCount = len(Seq)
StepDir = 1 # Set to 1 or 2 for clockwise
            # Set to -1 or -2 for anti-clockwise

# Read wait time from command line
if len(sys.argv)>1:
  WaitTime = int(sys.argv[1])/float(1000)
else:
  WaitTime = 10/float(1000)

# Initialise variables
StepCounter = 0

#time.sleep(15000)

# initialize the camera and grab a reference to the raw camera capture
camera = PiCamera()
camera.resolution = (320, 240)
camera.framerate = 32
rawCapture = PiRGBArray(camera, size=(320, 240))
# time to remove HDMI cable
time.sleep(10) 
# allow the camera to warmup
time.sleep(0.1)
prev_x = -1
gear_one = 0 # if set, fan is in speed one
gear_two = 0 # if set, fan is in speed two
prev_gear = 0
consecutive_face_size_larger = 0
consecutive_face_size_smaller = 0

number_of_steps_left = 0
number_of_steps_right = 0

leftmost_in_middle_of_the_frame = 0
rightmost_in_middle_of_the_frame = 0

switch_off = 0 # if it is greater than some threshold, it switches off the fan
# capture frames from the camera
(x,y,w,h) = (0.0,0.0,0.0,0.0)
for frame in camera.capture_continuous(rawCapture, format="bgr", use_video_port=True):
    # grab the raw NumPy array representing the image, then initialize the timestamp
    # and occupied/unoccupied text
    image = frame.array
    face_cascade = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')

    #Convert to grayscale
    gray = cv2.cvtColor(image,cv2.COLOR_BGR2GRAY)

    #Look for faces in the image using the loaded cascade file
    faces = face_cascade.detectMultiScale(gray, 1.1, 5)
            
    
    #print "Found "+str(len(faces))+" face(s)"
    temp_count=3
    #Draw a rectangle around every found face
    for (x,y,w,h) in faces:
        cv2.rectangle(image,(x,y),(x+w,y+h),(255,255,0),2)
    
    smallest_wh = 0
    for (x,y,w,h) in faces:
        cv2.rectangle(image,(x,y),(x+w,y+h),(255,255,0),2)
        if smallest_wh < w*h:
            smallest_wh = w*h
        
        
    if prev_gear == gear_two and switch_off > 40:
        GPIO.output(pin_relay,False) #3rd gear
        time.sleep(0.1)
        GPIO.output(pin_relay, True)
        time.sleep(0.1)
        GPIO.output(pin_relay,False) #4th gear
        time.sleep(0.1)
        GPIO.output(pin_relay, True)
        time.sleep(0.1)
        GPIO.output(pin_relay,False) #0th gear
        time.sleep(0.1)
        GPIO.output(pin_relay, True)
        
        gear_one = 0 # if set, fan is in speed one
        gear_two = 0 # if set, fan is in speed two
        prev_gear = -1
        
    elif prev_gear == gear_one and switch_off > 40:
        GPIO.output(pin_relay,False) #2nd gear
        time.sleep(0.1)
        GPIO.output(pin_relay, True)
        time.sleep(0.1)
        GPIO.output(pin_relay,False) #3rd gear
        time.sleep(0.1)
        GPIO.output(pin_relay, True)
        time.sleep(0.1)
        GPIO.output(pin_relay,False) #4th gear
        time.sleep(0.1)
        GPIO.output(pin_relay, True)
        time.sleep(0.1)
        GPIO.output(pin_relay,False) #0th gear
        time.sleep(0.1)
        GPIO.output(pin_relay, True)
        
        gear_one = 0 # if set, fan is in speed one
        gear_two = 0 # if set, fan is in speed two
        prev_gear = -1
        
    else:
        # Control the speed of the fan
        if smallest_wh >= 70.0*70.0:
            consecutive_face_size_larger += 1
            consecutive_face_size_smaller = 0
            if gear_one==0 and consecutive_face_size_larger>=5:#Initially : 1st gear
                GPIO.output(pin_relay,False)
                time.sleep(0.1)
                GPIO.output(pin_relay, True)
                gear_one = 1
                gear_two = 2
                prev_gear = gear_one
            elif prev_gear == gear_two and consecutive_face_size_larger>=5:#If fan is in 2nd gear then it should change to 1st gear now
                prev_gear = gear_one
                GPIO.output(pin_relay,False) #3rd gear
                time.sleep(0.1)
                GPIO.output(pin_relay, True)
                time.sleep(0.1)
                GPIO.output(pin_relay,False) #4th gear
                time.sleep(0.1)
                GPIO.output(pin_relay, True)
                time.sleep(0.1)
                GPIO.output(pin_relay,False) #0th gear
                time.sleep(0.1)
                GPIO.output(pin_relay, True)
                time.sleep(0.1)
                GPIO.output(pin_relay,False) #1st gear
                time.sleep(0.1)
                GPIO.output(pin_relay, True)
        elif smallest_wh <= 70.0*70.0 and smallest_wh>1:
            consecutive_face_size_larger = 0
            consecutive_face_size_smaller += 1
            if gear_two==0 and consecutive_face_size_smaller >= 5:#Initially : 2nd gear
                GPIO.output(pin_relay,False) #1st gear
                time.sleep(0.1)
                GPIO.output(pin_relay, True)
                time.sleep(0.1)
                GPIO.output(pin_relay,False) #2nd gear
                time.sleep(0.1)
                GPIO.output(pin_relay, True)
                gear_one = 1
                gear_two = 2
                prev_gear = gear_two
            elif prev_gear == gear_one and consecutive_face_size_smaller >= 5:#If fan is in 1st gear then it should change to 2nd gear now
                prev_gear = gear_two
                GPIO.output(pin_relay,False) #2nd gear
                time.sleep(0.1)
                GPIO.output(pin_relay, True)
               
   
    print(len(faces))    
    if len(faces)==1: #Single face
        (x,y,w,h) = faces[0]
        (x_left,w_left) = (int(x),int(w))
        leftmost_in_middle_of_the_frame = 0
    elif len(faces)>1:
        (x,y,w,h) = faces[0]
        (x_left,w_left) = (int(x),int(w))
        (x,y,w,h) = faces[len(faces)-1]
        (x_right,w_right) = (int(x),int(w))
        if (x_left+w_left/2) >= 150 and (x_left+w_left/2) <= 170 and (x_right+w_right/2) >= 150 and (x_right+w_right/2) <= 170:#both faces are in the center of the frame
            temp_count = 0
        if leftmost_in_middle_of_the_frame==0: #leftmost face is not in the middle
            (x,y,w,h) = faces[0]
            (x_left,w_left) = (int(x),int(w))
            number_of_steps_left += 1
            number_of_steps_right = 0
        elif rightmost_in_middle_of_the_frame == 0: #rightmost face is not in the middle
            (x,y,w,h) = faces[len(faces)-1]
            (x_right,w_right) = (int(x),int(w))
            number_of_steps_right += 1
            number_of_steps_left = 0
        
        
    # intialization of prev_x to the intial x position of the face i.e. when the fan is switched on
    if prev_x == -1:
        prev_x = x + w/2
        
    # face is in the left side of the frame
    if (x+w/2) < 150:
        if prev_x + 10 <= (x+w/2): # Face moves from left to right when it is in the left region
            StepDir = -1
            prev_x = x+w/2
        elif prev_x > 150: # SHARP CHANGE : Face has just come from the center-right region to left region, we need to change the previous value of x coordinate
            prev_x = x+w/2
            StepDir = 1
        else:
            StepDir = 1
            
               
    elif (x+w/2) > 170: # Face moves from right to left when it is in the right region
        if prev_x >= (x+w/2) + 10:
            StepDir = 1
            prev_x = x+w/2
        elif prev_x < 170: # SHARP CHANGE : Face has just come from the center-left region to left region, we need to change the previous value of x coordinate
            prev_x = x+w/2
            StepDir = -1
        else:
            StepDir = -1
                
    else: # face is in the center of the frame
        temp_count = 0 #No movement
        if (x_left,w_left) == (int(x),int(w)): #leftmost face in the center
            leftmost_in_middle_of_the_frame = 1
            rightmost_in_middle_of_the_frame = 0
        elif (x_right,w_right) == (int(x),int(w)): #rightmost face in the center
            leftmost_in_middle_of_the_frame = 0
            rightmost_in_middle_of_the_frame = 1
            
        if len(faces)>1: #only when number of faces are more than one
            if StepDir == -1: #if fan was moving in the left direction preiviously, then it should move to right desired number of steps
                temp_count = number_of_steps_left*temp_count
                StepDir = 1 #towards the right direction
            else: #if fan was moving in the right direction preiviously, then it should move to left desired number of steps
                temp_count = number_of_steps_right*temp_count
                StepDir = -1 #towards the left direction
            
    
    if len(faces) == 0: # No face found
        temp_count=0  #No movement
        switch_off += 1 # switch_off maintains number of times, no face has been seen continuously
    else:
        switch_off = 0
    
    while temp_count>0:
        for pin in range(0, 4):
            xpin = StepPins[pin]
            if Seq[StepCounter][pin]!=0:
            #print " Enable GPIO %i" %(xpin)
                GPIO.output(xpin, True)
            else:
                GPIO.output(xpin, False)
            
        StepCounter += StepDir

        # If we reach the end of the sequence
        # start again
        if (StepCounter>=StepCount):
            StepCounter = 0
        if (StepCounter<0):
            StepCounter = StepCount+StepDir

        # Wait before moving on
        time.sleep(WaitTime)
        temp_count -= 1
    
    
    
    # show the frame
    cv2.imshow("Frame", image)
    key = cv2.waitKey(1) & 0xFF
 
    # clear the stream in preparation for the next frame
    rawCapture.truncate(0)
 
    # if the `q` key was pressed, break from the loop
    if key == ord("q"):
        break
GPIO.cleanup()