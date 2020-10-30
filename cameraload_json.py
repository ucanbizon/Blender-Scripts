import numpy as np
import cv2
import os
import glob
import bpy
import sys
import mathutils
import json
import math
sensor_size = (22, 11.88)  # w, h [mm]
image_res = (4000, 2160)


    
input_path = 'C:/Users/ucanb/Downloads/10_rendering/cam_params.json' 
num_cams = 16


def RotationMatrixToEulerAngles(R) :
 

     
    sy = math.sqrt(R[0,0] * R[0,0] +  R[1,0] * R[1,0])
     
    singular = sy < 1e-6
 
    if  not singular :
        x = math.atan2(R[2,1] , R[2,2])
        y = math.atan2(-R[2,0], sy)
        z = math.atan2(R[1,0], R[0,0])
    else :
        x = math.atan2(-R[1,2], R[1,1])
        y = math.atan2(-R[2,0], sy)
        z = 0
 
    return mathutils.Vector((x+ np.pi, y,z))



with open(input_path, 'r') as f:
    j = json.load(f)
    p = j['cam_params']
    for cam_idx in range(num_cams):
        c = p[str(cam_idx)]
        rvec = np.array(c['rvec'])
        tvec = c['tvec']
        fx = c['fx']
        fy = c['fy']
        
        name = str(cam_idx)
        
        # create camera data    
        cam_data = bpy.data.cameras.new("{}.{:03d}".format(name, 0))

        # create object camera data and insert the camera data
        cam_ob = bpy.data.objects.new("{}Cam.{:03d}".format(name, 0), cam_data)       

        rotation, _ = cv2.Rodrigues(rvec)

        translation = -rotation.T.dot(tvec)

        worldMatrix = np.array([[rotation[0][0],rotation[0][1],rotation[0][2],translation[0]],\
        [rotation[1][0],rotation[1][1],rotation[1][2],translation[1]],\
        [rotation[2][0],rotation[2][1],rotation[2][2],translation[2]],[0,0,0,1]])
        
        
        cam_ob.matrix_world =  worldMatrix
        cam_ob.location = mathutils.Vector((translation[0],translation[1],translation[2]))
        cam_ob.rotation_euler[0] = cam_ob.rotation_euler[0] + np.pi

        focal_lengths = (fx * sensor_size[0] / image_res[0], fy * sensor_size[1] / image_res[1])
        cam_ob.data.lens = (focal_lengths[0] + focal_lengths[1] ) *0.5
        cam_ob.data.sensor_fit = 'HORIZONTAL'
        cam_ob.data.sensor_width = 22
        cam_ob.data.sensor_height = 11.88


        if bpy.context.scene.unit_settings.length_unit == 'MILLIMETERS':
            cam_ob.location[0] = cam_ob.location[0]/1000 
            cam_ob.location[1] = cam_ob.location[1]/1000
            cam_ob.location[2] = cam_ob.location[2]/1000
        else:
            sys.stderr.write("ERROR: CHANGE UNIT LENGTH TO MILLIMETERS")

        bpy.context.collection.objects.link(cam_ob)
        
    f.close()
