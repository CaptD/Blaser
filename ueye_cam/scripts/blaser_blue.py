#! /usr/bin/env python
# -*- coding: utf-8 -*-
"""

Copyright (c) 2015 PAL Robotics SL.
Released under the BSD License.

Created on 7/14/15

@author: Sammy Pfeiffer

test_video_resource.py contains
a testing code to see if opencv can open a video stream
useful to debug if video_stream does not work
"""

import cv2
import sys, time
import roslib
import rospy
import numpy as np
#import matplotlib.pyplot as plt
import std_msgs.msg

#from mpl_toolkits.mplot3d import Axes3D
from sensor_msgs.msg import Image
from sensor_msgs.msg import PointCloud
from geometry_msgs.msg import Point32
from cv_bridge import CvBridge

class Blaser:
    #table_red = 0
    table_blue = 0
    pointcloud_1_pub = 0
    #pointcloud_2_pub = 0
    rate = 0
    #point_buffer = 0
    #initialized = False
    def __init__(self):
	# node initialized and constants described here
        with open("/home/jin/boeing/catkin_ws/src/ueye_cam/scripts/blue_table.txt") as file:
    	    Blaser.table_blue = [[float(digit) for digit in line.split(' ')] for line in file]
	
	Blaser.pointcloud_1_pub = rospy.Publisher("/camera_1/PointCloud", PointCloud, queue_size = 5)
	rospy.init_node('blaser_blue_pub', anonymous=True)
	Blaser.rate = rospy.Rate(10) # 10hz
        #Blaser.point_buffer = np.array([])
	
    def subscribe_image(self):
	rospy.Subscriber("/camera_1/image_raw", Image, self.generatePointCloud_blue)
	rospy.spin()

    def generatePointCloud_blue(self,msg):
	br = CvBridge()
	frame = br.imgmsg_to_cv2(msg)
	#cv2.imshow("Display window 2",frame) 
	#cv2.waitKey(0);
    	b,g,r = cv2.split(frame)	
    	lower_red = np.array([0,0,100])
	upper_red = np.array([100,100,255])
	mask = cv2.inRange(frame,lower_red,upper_red)
	temp = np.nonzero(np.transpose(mask))
	point_cloud = PointCloud()
	header = std_msgs.msg.Header()
	header.stamp = rospy.Time.now()
	header.frame_id = 'blaser'
	point_cloud.header = header
        if temp[0].size:
	    pixelpoints = np.array([temp[0],temp[1]])
	    
	    diff_col = np.nonzero(pixelpoints[0,1:]-pixelpoints[0,0:len(pixelpoints[1])-1])
	    diff_col = np.array(np.append(diff_col[0]+1,len(pixelpoints[0])))
            
	    for t in range(0,len(diff_col)):
	        if t == 0:
	            temp = np.mean(pixelpoints[:,0:diff_col[t]],axis = 1)
	        else:
	            temp = np.mean(pixelpoints[:,diff_col[t-1]:diff_col[t]],axis = 1)
	        ind = round(temp[0])*720+round(temp[1])
                point_cloud.points.append(Point32(Blaser.table_blue[int(ind)][0]*10,Blaser.table_blue[int(ind)][1]*10,Blaser.table_blue[int(ind)][2]*10))
            
	else:
            rospy.logwarn("no points detected!!!")
        Blaser.pointcloud_1_pub.publish(point_cloud)
	Blaser.rate.sleep()

'''
    def smoothing(self):
        smoothed_point = (Blaser.point_buffer[0:-10]+Blaser.point_buffer[1:-9]+Blaser.point_buffer[2:-8]+Blaser.point_buffer[3:-7]+Blaser.point_buffer[4:-6]++Blaser.point_buffer[5:-5]+Blaser.point_buffer[6:-4]+Blaser.point_buffer[7:-3]+Blaser.point_buffer[8:-2]+Blaser.point_buffer[9:-1])/10
        Blaser.point_buffer = smoothed_point
    
    def compute_gradient(self):
        N = Blaser.point_buffer.shape[0]
        n_neighbor = 5
        c = np.zeros((N-2*n_neighbor))
        for i in range(n_neighbor,N-n_neighbor-1):
            temp = np.zeros((3))
            for j in range(i-n_neighbor,i+n_neighbor):
                temp = temp + Blaser.point_buffer[i] - Blaser.point_buffer[j] 
            c[i] = np.linalg.norm(temp)/n_neighbor/np.linalg.norm(ds(i,:));
        I = np.argsort(c)[::-1]
        Blaser.point_buffer = Blaser.point_buffer[I,:]
'''

'''
            if not initialized:
                if Blaser.point_buffer.shape[0] < 1:
                    Blaser.point_buffer = np.concatenate((Blaser.point_buffer,[px,py,pz]))
                else:
                    Blaser.point_buffer = np.vstack((Blaser.point_buffer,[px,py,pz]))
        if not initialized:
            smoothing()
            if Blaser.point_buffer.shape[0] < 7:
                if Blaser.point_buffer.shape[0] < 1:
                    Blaser.point_buffer = np.concatenate((Blaser.point_buffer,[px,py,pz]))
                else:
                    Blaser.point_buffer = np.vstack((Blaser.point_buffer,[px,py,pz]))
            else:
                Blaser.point_buffer = np.vstack((Blaser.point_buffer[1:6],[px,py,pz]))
                smoothness(self)
'''
	
if __name__ == '__main__':
    try:
        blaser = Blaser()
        blaser.subscribe_image()
    except rospy.ROSInterruptException:
        pass
