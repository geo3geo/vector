"""
Line-Following Vector 

Basically it analyses the video camera feed by converting it to lines, and then working out angle and offset from centre. Vector's direction of travel is then adjusted by angle and offset.
It's been structured for possible future expansion to have two vectors going at the same time using multiprocessing.
Good lighting is required for this, and reflections off the base can upset things. But it's a start!

I didn't want to write this code, my Vectors made me do it as they were getting bored being in lockdown. 
https://youtu.be/JIopoX9kDQI 

Geo - 18 April 2020
"""

import cv2
import numpy as np
import time, math
import anki_vector
robot1finished = bool(False)
robot2finished = bool(False)
robot1 = anki_vector.Robot(name="Vector-J2M4")
robot2 = anki_vector.Robot(name="Vector-U1E1")

#https://docs.opencv.org/2.4/doc/tutorials/imgproc/imgtrans/hough_lines/hough_lines.html

dev = bool(True)
degOffset = 0		#compensate for any cv2 detection system
dev = bool(True)	#development traces
ofactor = .1		#offset adjustment for track speed
afactor = .1		#angle adjustment for track speed
speed = 10 		#rate of travel
motorsOn = bool(True)	#enable track motors - off to stop roaming

def follow1():
    robot1.connect() 
    angle = follow(robot1)
    return angle

def follow(robot):
    cv2ImageId = 0
    robot.camera.init_camera_feed()
    robot.behavior.say_text("go vector")
    robot.motors.set_head_motor(-5.0) 		# move head to look at ground
    time.sleep(2)
    while (True):
        cv2ImageId = robot.camera.latest_image_id
        tmpImage = robot.camera.latest_image.raw_image.save('temp.png')
        img = cv2.imread('temp.png')
        ##img = cv2.imread('temp10left.jpg') 	#for testing
        gray = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
        edges = cv2.Canny(gray,50,150,apertureSize = 3)
        cv2.imwrite('rawedges.jpg',edges)	#save diagnostic image
        maskArea = np.array([[(150, 250), (150,160), (450, 160), (450, 250)]], dtype=np.int32)
        blank = np.zeros_like(gray)
        mask = cv2.fillPoly(blank, maskArea, 255)
        maskedImage = cv2.bitwise_and(edges, mask)
        cv2.imwrite('maskedImage.jpg',maskedImage)  
        edges = maskedImage

        cv2.imwrite('edges.jpg',edges)		#diagnostic image
        dun = False
        for m in range(1,25):               	#autoselect MinLineGap 
            if (dun==True): break
            lines = cv2.HoughLinesP(edges,rho=6,
                theta=np.pi/30,  	
                threshold=20, 		#100
                lines=np.array([]),
                minLineLength=30,	#50
                maxLineGap=m) 
            #print("============")
            #print("m = ",m)       
            if (lines is not None):                
                if (dev):
                    print("id = ",cv2ImageId)
                    print("num lines = ", len(lines))
                radAngle = 0
                xoffset = 0
                for i in range(0, len(lines)):
                    if dun == True: break
                    for x1,y1,x2,y2 in lines[i]:                        
                        if (abs(y2-y1) > 10):	  #ignore near horizontals
                            if (dev): print("found x1,y1,x2,y2 = ",x1,y1,x2,y2)
                            cv2.line(img,(x1,y1),(x2,y2),(0,0,255),2) #add line to image
                            radAngle = np.arctan2(x2 - x1, y2 - y1)
                            xoffset = 320-(x1+x2)/2
                            dun = True
                print("xoffset = ",xoffset)
                degAngle = math.trunc(np.rad2deg(radAngle))
                if (y1>y2): degAngle -=180
                degAngle -=degOffset    
                print("degrees = ",degAngle) 
                cv2.imwrite('houghlines'+str(cv2ImageId)+'.jpg',img) #save image
                disp=cv2.imread('houghlines.jpg')
                cv2.imshow('hough_lines', disp)	  #display on laptop
                cv2.waitKey(200)                  #refresh display   
                #leftTrack  = int(speed-(degAngle*afactor))
                #rightTrack = int(speed+(degAngle*afactor))
                leftTrack  = int(speed-(xoffset*ofactor)-(degAngle*afactor))
                if leftTrack < 5: leftTrack = 5
                rightTrack = int(speed+(xoffset*ofactor)+(degAngle*afactor))
                if rightTrack < 5: rightTrack = 5
                print("left/right speed = ",leftTrack,rightTrack)
                if motorsOn:
                    robot.motors.set_wheel_motors(leftTrack,rightTrack) 
                    time.sleep(1)		 #adjust for a second	
                    robot.motors.set_wheel_motors(10,10) #straighten up
                c=cv2.waitKey(500)               #refresh display
                if (chr(c & 0xff) == 'q'): exit()
            else:
                #print("none")
                c=cv2.waitKey(100)               #refresh display
                if (chr(c & 0xff) == 'q'): exit()
                continue

def allDone(robot):
	print('[allDone] Cleaning up')
	robot.motors.set_wheel_motors(0, 0)
	cv2.destroyAllWindows()
	robot.disconnect()
	 
def main():
    print("==================================== START ====================================")
    angle = follow1()
    print("Return = ",angle)  
    allDone(robot1)

    c = cv2.waitKey(100)		
    if (chr(c & 0xff) == 'q'):
        allDone(robot1)
        exit()
        
if __name__ == '__main__':
    main()


