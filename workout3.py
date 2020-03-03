"""
Simple example of operating two Vectors in parallel processing routines
Each vector does 'pressups' with random delays between so they don't finish together.
Hopefully others will develope this to produce more elaborate
gaming scripts for two (or more!) Vectors
It's a bit flakey, esp. when Vectors don't connect.

 Read more about multiprocessing here: 
 https://pymotw.com/2/multiprocessing/basics.html
 pip install multiprocessing (pip complains a lot but seems to install ok)

Used intermediate files to get result out of the parallel processing routines as I can't get 
recommended return proceedures to work! Any feedback on this appreciated. 
Also, moving duplicate code in the 'while' loop into a def routine caused system hangs. 
Needs more work, possibly multiprocessing?

Video of 3 games at https://youtu.be/rb18hS9eNgo 

Based on idea from https://github.com/titchy2005/vector_workout

GM 03 Mar 2020
"""

import os,sys,random,time
import anki_vector
from anki_vector.events import Events
from anki_vector.util import degrees
from anki_vector.connection import ControlPriorityLevel
from multiprocessing import Process
import multiprocessing

robot1finished = bool(False)
robot2finished = bool()

lifts = 5
liftrate = random.randint(0,4)
vec1Serial = '00301DC4' #yellow eyes J2M4
vec2Serial = '00804d9e' #green eyes  U1E1

robot1 = anki_vector.Robot(vec1Serial)
robot2 = anki_vector.Robot(vec2Serial)

def liftups1():
    robot1.connect() 
    liftups(robot1) 
    robot1.behavior.say_text("yellow eyes finished",duration_scalar=1.5)  
    f = open("result1.txt", "w")
    f.write("1")
    f.close()  
    
def liftups2():
    robot2.connect()
    liftups(robot2)
    robot2.behavior.say_text("green eyes finished",duration_scalar=1.5)
    f = open("result2.txt", "w")
    f.write("2")
    f.close()      

def liftups(robot):
    time.sleep(3) 		#give time for both to connect    
    print(robot.conn.behavior_control_level)
    robot.behavior.say_text("Lets Go!",duration_scalar=1.5)
    #robot.behavior.drive_off_charger()         
    for number in range(lifts):
        speed = random.randint(1,4)
        print("speed = ",speed)
        time.sleep(speed)
        robot.motors.set_lift_motor(2)
        robot.behavior.say_text(str(number+1))
        robot.motors.set_lift_motor(-2)   

def main():   
    f = open("result2.txt", "w")
    f.write("0")
    f.close()    
    f = open("result1.txt", "w")
    f.write("0")
    f.close() 
    p1 = Process(target=liftups1)   
    p2 = Process(target=liftups2)
    p1.start()			#start parallel processing 
    p2.start()
    
    while True:
          time.sleep(0.2)

          f = open("result1.txt", "r")
          r1 = f.read() 
          if (r1 == "1"):
              robot1.connect()
              time.sleep(2)
              print("Robot 1 won!")
              robot1.behavior.say_text("yellow eyes won")
              break

          f = open("result2.txt", "r")
          r2 = f.read() 
          if (r2 == "2"):
              print("Robot 2 won!")
              robot2.connect()
              time.sleep(2)
              robot2.behavior.say_text("green eyes won")
              break

if __name__ == '__main__':
    main()


