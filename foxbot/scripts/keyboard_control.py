#!/usr/bin/env python
#@package foxbot_node
import rospy
from foxbot.srv import *

import sys, select, termios, tty

msg = """
Reading from the keyboard and Calling foxbot service!
---------------------------
Moving around (captial for larger step):
   a: y--  j: rx--
   d: y++  l: rx++
   w: x--  i: ry--
   s: x++  k: ry++
   q: z++  u: rz--
   e: z--  o: rz++

number key: --
shift + number key: ++ 
anything else : stop

CTRL-C to quit
"""

cartesianBindings = {
		'a':(0,-1,0,0,0,0),
		'd':(0,1,0,0,0,0),
		'w':(-1,0,0,0,0,0),
		's':(1,0,0,0,0,0),
		'q':(0,0,1,0,0,0),
		'e':(0,0,-1,0,0,0),
                'i':(0,0,0,0,-1,0),
		'k':(0,0,0,0,1,0),
		'j':(0,0,0,-1,0,0),
		'l':(0,0,0,1,0,0),
		'u':(0,0,0,0,0,-1),
		'o':(0,0,0,0,0,1)
	       }

jointBindings = {
                '1':(-1,0,0,0,0,0),
                '2':(0,-1,0,0,0,0),
                '3':(0,0,-1,0,0,0),
                '4':(0,0,0,-1,0,0),
                '5':(0,0,0,0,-1,0),
                '6':(0,0,0,0,0,-1),
                '!':(1,0,0,0,0,0),
                '@':(0,1,0,0,0,0),
                '#':(0,0,1,0,0,0),
                '$':(0,0,0,1,0,0),
                '%':(0,0,0,0,1,0),
                '^':(0,0,0,0,0,1)
               }

def getKey():
	tty.setraw(sys.stdin.fileno())
	select.select([sys.stdin], [], [], 0)
	key = sys.stdin.read(1)
	termios.tcsetattr(sys.stdin, termios.TCSADRAIN, settings)
	return key

if __name__=="__main__":
    	settings = termios.tcgetattr(sys.stdin)
	rospy.init_node('keyboard_control')

	try:
		print msg
		while(1):
			key = getKey()
			if key in cartesianBindings.keys():
				x = cartesianBindings[key][0]
				y = cartesianBindings[key][1]
				z = cartesianBindings[key][2]
                                rx = 0.2*cartesianBindings[key][3]
				ry = 0.2*cartesianBindings[key][4]
				rz = 0.2*cartesianBindings[key][5]
                                rospy.wait_for_service('/foxbot/robot_JogCartesian')
				try:
			        	jogCartesian = rospy.ServiceProxy('/foxbot/robot_JogCartesian', robot_JogCartesian)
			        	resp1 = jogCartesian(x, y, z, rx, ry, rz)
					print msg
		        	except rospy.ServiceException, e:
			        	print "Service call failed: %s"%e
			else:
				if key in jointBindings.keys():
					j1 = jointBindings[key][0]
                                        j2 = jointBindings[key][1]
                                        j3 = jointBindings[key][2]
                                        j4 = jointBindings[key][3]
                                        j5 = jointBindings[key][4]
                                        j6 = jointBindings[key][5]
                                        rospy.wait_for_service('/foxbot/robot_JogJoints')
					try:
						jogJoints = rospy.ServiceProxy('/foxbot/robot_JogJoints', robot_JogJoints)
						resp1 = jogJoints(j1, j2, j3, j4, j5, j6)
						print msg
					except rospy.ServiceException, e:
						print "Service call failed: %s"%e
				else:
					if (key == '\x03'):
						break
			


                        
	except:
		print "error"

	finally:
    		termios.tcsetattr(sys.stdin, termios.TCSADRAIN, settings)


