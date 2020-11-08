import bpy
from mathutils import Vector
from bpy_extras.object_utils import world_to_camera_view
import bmesh
import numpy as np
import cv2
import os
import glob



render_path = r'C:\Users\ucanb\Desktop\finalanka\testseq\pics'


scene = bpy.context.scene
viewLayer = bpy.context.view_layer
render_scale = scene.render.resolution_percentage / 100
render_size = ( int(scene.render.resolution_x * render_scale),int(scene.render.resolution_y * render_scale) )


cam = bpy.data.objects['Cam.009']

for frame in range(scene.frame_start, scene.frame_end):

    scene.frame_set(frame)
    viewLayer.update()
    bpy.ops.object.mode_set(mode='OBJECT')
    
    bpy.context.scene.render.filepath = os.path.join(render_path, str(frame) + "newres")
    bpy.ops.render.render(write_still=True)
