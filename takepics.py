import numpy as np
import cv2
import os
import glob
import bpy


directory = r'C:\Users\ucanb\Desktop\scan_mov\cameraset\Calib'




render_path = directory + "\\render_images"
print(render_path)
for camera_obj in [obj for obj in bpy.data.objects if obj.type == 'CAMERA']:
    bpy.context.scene.camera = camera_obj
    bpy.context.scene.render.filepath = os.path.join(render_path, camera_obj.name)
    bpy.ops.render.render(write_still=True)
    bpy.context.scene.render.filepath = render_path
