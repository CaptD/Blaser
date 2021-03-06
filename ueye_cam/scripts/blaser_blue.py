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
import std_msgs.msg

from matplotlib import pyplot as plt
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
    edge = 0
    #point_buffer = 0
    #initialized = False
    def __init__(self):
	# node initialized and constants described here
        with open("/home/jin/boeing/catkin_ws/src/blaser/ueye_cam/scripts/blue_table.txt") as file:
    	    Blaser.table_blue = [[float(digit) for digit in line.split(' ')] for line in file]
        # The calibrated look up table is loaded to memory when initialization

	Blaser.table_blue = np.around(Blaser.table_blue,decimals = 4)
	Blaser.pointcloud_1_pub = rospy.Publisher("/camera_1/PointCloud", PointCloud, queue_size = 5)
	rospy.init_node('blaser_blue_pub', anonymous=True)
	Blaser.rate = rospy.Rate(100) # 100hz
        #Blaser.point_buffer = np.array([])
	
    def subscribe_image(self):
	rospy.Subscriber("/camera_1/image_raw", Image, self.generatePointCloud_blue)
	rospy.spin()

    def thinning_edge(self):
        # I implemented a thinning edge algorithm, but the noise is significant, so I didn't use this function at demo
        dilated = cv2.dilate(self.mask, np.ones((5, 5)))
        self.edge = cv2.erode(dilated, np.ones((5, 5)))
        height, width = self.edge.shape[:2]
        self.edge[0,:] = 0
        self.edge[-1,:] = 0
        self.edge[:,0] = 0
        self.edge[:,-1] = 0
        self.edge = self.edge/255
        #print height, width
        #print self.edge[334][1279]
        #print self.edge[333][1279]
        not_empty = np.sum(self.edge)
        #print not_empty
        if not_empty:
            #pixelpoints = np.array([temp[0],temp[1]])
            bDone = False
            count = 0
            while bDone != True:
                # first subiteration
                new_edge = self.edge
                temp = np.nonzero(new_edge)
                #print temp
                
            	for i in range(0,temp[0].size):
                    #print "--------------"
                    #print i
                    #print temp[0][i]-1
                    #print temp[1][i]-1
                    p0 = new_edge[temp[0][i]-1,temp[1][i]-1]
                    p1 = new_edge[temp[0][i]-1,temp[1][i]]
                    p2 = new_edge[temp[0][i]-1,temp[1][i]+1]
                    p3 = new_edge[temp[0][i],temp[1][i]+1]
                    p4 = new_edge[temp[0][i]+1,temp[1][i]+1]
                    p5 = new_edge[temp[0][i]+1,temp[1][i]]
                    p6 = new_edge[temp[0][i]+1,temp[1][i]-1]
                    p7 = new_edge[temp[0][i],temp[1][i]-1]
                    c = int(not p1 and (p2 or p3)) + int(not p3 and (p4 or p5)) + int(not p5 and (p6 or p7)) +int(not p7 and (p0 or p1))
                    #print p1, p2, p3, p4, p5, p6, p7
                    #print c
                    if c == 1:
                        N1 = int(p0 or p1) + int(p2 or p3) + int(p4 or p5) + int(p6 or p7)
                        N2 = int(p1 or p2) + int(p3 or p4) + int(p5 or p6) + int(p7 or p0)
                        N = min(N1,N2)
                        #print N
                    	if N == 2 or N == 3:
                            c3 = (p1 or p2 or not p4) and p3
                            #print c3
                            if c3 == 0:
                                new_edge[temp[0][i]][temp[1][i]] = 0
                # second subiteration
                temp = np.nonzero(new_edge)
                for i in range(0,temp[0].size):
                    p0 = new_edge[temp[0][i]-1,temp[1][i]-1]
                    p1 = new_edge[temp[0][i]-1,temp[1][i]]
                    p2 = new_edge[temp[0][i]-1,temp[1][i]+1]
                    p3 = new_edge[temp[0][i],temp[1][i]+1]
                    p4 = new_edge[temp[0][i]+1,temp[1][i]+1]
                    p5 = new_edge[temp[0][i]+1,temp[1][i]]
                    p6 = new_edge[temp[0][i]+1,temp[1][i]-1]
                    p7 = new_edge[temp[0][i],temp[1][i]-1]
                    c = int(not p1 and (p2 or p3)) + int(not p3 and (p4 or p5)) + int(not p5 and (p6 or p7)) +int(not p7 and (p0 or p1))
                    #print c
                    if c == 1:
                        N1 = int(p0 or p1) + int(p2 or p3) + int(p4 or p5) + int(p6 or p7)
                        N2 = int(p1 or p2) + int(p3 or p4) + int(p5 or p6) + int(p7 or p0)
                        N = min(N1,N2)
                        #print N
                        if N == 2 or N == 3:
                            E = (p5 or p6 or not p0) and p7
                            #print E
                            if E == 0:
                                new_edge[temp[0][i]][temp[1][i]] = 0
                # compare
                edge_diff = np.sum(self.edge - new_edge)
                #print edge_diff
                self.edge = new_edge
                count = count + 1
                if edge_diff == 0:
                    bDone = True
        
        #print count
        #self.edge = cv2.GaussianBlur(self.edge,(5,5),3,3)
        #self.edge = cv2.erode(self.edge, np.array([[0,0,0],[0,1,0],[0,0,0]]))
        #self.edge = cv2.blur(self.edge,(7,7))
        #print np.amax(self.edge)
        """
        plt.subplot(121),plt.imshow(dilated)
        plt.title('Original Image'), plt.xticks([]), plt.yticks([])
        plt.subplot(122),plt.imshow(self.edge)
        plt.title('Edge Image'), plt.xticks([]), plt.yticks([])
        plt.show()
	cv2.waitKey(0)
        """

    def generatePointCloud_blue(self,msg):
        # core component
	br = CvBridge()
	frame = br.imgmsg_to_cv2(msg) # read image into opencv format
        #edges = cv2.Canny(frame,280,300)
        
	#cv2.imshow("Display window 2",frame) 
	#cv2.waitKey(0);
    	b,g,r = cv2.split(frame) # split into r, g, b three channels
    	lower_red = np.array([0,0,100]) # define threshold for red laser pixels
	upper_red = np.array([100,100,255])
	self.mask = cv2.inRange(frame,lower_red,upper_red)
        #self.thinning_edge() # I commented this function out at demo
	#temp = np.nonzero(np.transpose(self.edge > 0.3))
        temp = np.nonzero(np.transpose(self.mask))
	point_cloud = PointCloud()
	header = std_msgs.msg.Header() # create ros msg
	header.stamp = rospy.Time.now()
	header.frame_id = 'blaser'
	point_cloud.header = header
        if temp[0].size:
	    pixelpoints = np.array([temp[0],temp[1]])
            """
            for t in range(0,temp[0].size):

                ind = temp[0][t]*720+temp[1][t]
                #print ind
                point_cloud.points.append(Point32(Blaser.table_blue[ind][0]*10,Blaser.table_blue[ind][1]*10,Blaser.table_blue[ind][2]*10))
                
	    """
	    diff_col = np.nonzero(pixelpoints[0,1:]-pixelpoints[0,0:len(pixelpoints[1])-1])
	    diff_col = np.array(np.append(diff_col[0]+1,len(pixelpoints[0])))
            
	    for t in range(0,len(diff_col)): 
                # I thin the edge by averaging the column coordinates for each row
	        if t == 0:
	            temp = np.mean(pixelpoints[:,0:diff_col[t]],axis = 1)
	        else:
	            temp = np.mean(pixelpoints[:,diff_col[t-1]:diff_col[t]],axis = 1)
            
	        ind = int(round(temp[0])*720+round(temp[1]))
                point_cloud.points.append(Point32(Blaser.table_blue[ind][0]*10-0.045,Blaser.table_blue[ind][1]*10,Blaser.table_blue[ind][2]*10-0.1))
                
            
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
