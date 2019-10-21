import bpy
from mathutils import Vector
from bpy_extras.object_utils import world_to_camera_view
import bmesh
import numpy as np
import cv2
import os
import glob


def Distort(camera_,pixelcoord):
        x = (pixelcoord[0] - camera_.central_points_in_pixel[0]) / camera_.focal_lengths_in_pixel[0]
        y = (pixelcoord[1] - camera_.central_points_in_pixel[1]) / camera_.focal_lengths_in_pixel[1]
        r2 = x * x + y * y
        kcoef = 1 + camera_.k1 * r2 + camera_.k2 * r2 * r2 + camera_.k3 * r2 * r2 * r2
        x_ = x * kcoef + 2 * camera_.p1 * x * y + camera_.p2 * (r2 + 2 * x * x)
        y_ = y * kcoef + camera_.p1 * (r2 + 2 * y * y) + 2 * camera_.p2 * x * y
        out_x = x_ * camera_.focal_lengths_in_pixel[0] + camera_.central_points_in_pixel[0]
        out_y = y_ * camera_.focal_lengths_in_pixel[1] + camera_.central_points_in_pixel[1]
        return (int(round(out_x)),int(round(out_y)))


class Camera:
    #
    # the focal lengths (fx, fy) are expressed in pixel units.
    # to fix fx/fy ratio, use CV_CALIB_FIX_ASPECT_RATIO. (ideally, fx == fy)

    # a principal point (cx, cy) is usually at the image center.

    # dim = np.array([600, 880]) # w, h [mm]
    # dim = np.array([300, 300])  # w, h [mm]
    sensor_size = (22, 11.88)  # w, h [mm]
    image_res = (4000, 2160)

    def __init__(self, idx, name, avb):
        self.index = idx
        self.is_available = avb
        self.images = []
        self.name = name
        self.render = True

        # w.r.t. global coordinates system
        self.SE3 = None

        # ret: the mean reprojection error (it should be as close to zero as possible);
        # mtx: the matrix of intrisic parameters;
        # dist: the distortion parameters: 3 in radial distortion, 2 in tangential distortion;
        self.rms_err = -1.0
        self.M = None
        self.d = None
        self.focal_lengths = (0, 0)
        self.central_points = (0,0)
        self.focal_lengths_in_pixel = (0, 0)
        self.central_points_in_pixel = (0,0)
        self.k1 = 0
        self.k2 = 0
        self.k3 = 0
        self.p1 = 0
        self.p2 = 0
        # 3d-2d projection pair (frame x points x 2d)
        self.measured_2d_points = []



    def set_M(self, M_):
        self.M = M_
        self.focal_lengths = (self.M[0, 0] * self.sensor_size[0] / self.image_res[0], self.M[1, 1] * self.sensor_size[1] / self.image_res[1])
        self.central_points = (self.M[0, 2] / self.image_res[0] - 0.5, self.M[1, 2] / self.image_res[1] - 0.5)
        self.focal_lengths_in_pixel = (self.M[0, 0], self.M[1, 1])
        self.central_points_in_pixel = (self.M[0, 2],self.M[1, 2])
    def set_d(self, d_):
        self.d = d_
        self.k1 = self.d[0][0]
        self.k2 = self.d[0][1]
        self.k3 = self.d[0][4]
        self.p1 = self.d[0][2]
        self.p2 = self.d[0][3]

    def set_SE3(self, SE3_):
        self.SE3 = SE3_





# for intrinsic calibration
cameras = [Camera(0, r'\A001_05290330_C001', True), Camera(1, r'\B001_07072140_C001', True),
           Camera(2, r'\C001_06070320_C001', True), Camera(3, r'\D001_05061515_C001', True),
           Camera(4, r'\E001_04210958_C001', True), Camera(5, r'\F001_05151133_C001', True),
           Camera(6, r'\G001_05052127_C001', True), Camera(7, r'\H001_05191504_C001', True)]

cam2char = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H']
directory = r'C:\Users\ucanb\Desktop\scan_mov\cameraset\Calib'
extrinsic_filename = 'coord_sys_output.xml'
se3_xml_path = os.path.join(directory, extrinsic_filename)


bpy.context.scene.render.resolution_x = Camera.image_res[0]
bpy.context.scene.render.resolution_y = Camera.image_res[1]

for camera in cameras:
    if camera.is_available:
        intrinsics_xml_path = directory + "\Intrinsics" + cam2char[camera.index] + '.xml'
        print(intrinsics_xml_path)
        cv_file = cv2.FileStorage(intrinsics_xml_path, cv2.FILE_STORAGE_READ)
        M = cv_file.getNode('M1').mat()
        d = cv_file.getNode('D1').mat()
        camera.set_M(M)
        camera.set_d(d)
        
        cv_file = cv2.FileStorage(se3_xml_path, cv2.FILE_STORAGE_READ)
        se3 = cv_file.getNode('H_w_' + cam2char[camera.index]).mat()

        camera.set_SE3(se3)

        
    else:
        print("* Camera[{}] set as not available")




scene = bpy.context.scene

obj = bpy.context.object
bm = bmesh.from_edit_mesh(obj.data)
me = obj.data
vertices= [e for e in bm.verts]
limit = 0.001

mWorld = obj.matrix_world


directory = r'C:\Users\ucanb\Desktop\scan_mov\cameraset\Calib'



render_path = directory + "\\render_images"

render_scale = scene.render.resolution_percentage / 100
render_size = ( int(scene.render.resolution_x * render_scale),int(scene.render.resolution_y * render_scale) )


for camera_obj in [obj for obj in bpy.data.objects if obj.type == 'CAMERA']:
    bpy.context.scene.camera = camera_obj
    bpy.context.scene.render.filepath = os.path.join(render_path, camera_obj.name)
    bpy.ops.render.render(write_still=True)
    camera = cameras[cam2char.index(camera_obj.name[0])]


    vert_file = open(render_path + '\\' + camera_obj.name + "verts.txt", 'w') 
    for vert in vertices:
        worldvert = mWorld @ vert.co 
        co2D = world_to_camera_view( scene, camera_obj, worldvert )
        co2D.y = 1.0 - co2D.y
        
        if 0.0 <= co2D.x <= 1.0 and 0.0 <= co2D.y <= 1.0 and co2D.z >0: 
            # Try a ray cast, in order to test the vertex visibility from the camera
            location= scene.ray_cast( bpy.context.view_layer, camera_obj.location, (worldvert - camera_obj.location).normalized() )
            # If the ray hits something and if this hit is close to the vertex, we assume this is the vertex
            if location[0] and (worldvert - location[1]).length < limit:
                pixelcoord = (round(co2D.x * render_size[0]),round(co2D.y * render_size[1]))
                distorted_pixelcoord = Distort(camera,pixelcoord)
                vert_file.write(str(vert.index) + '  pixel coordinates: ' + str(distorted_pixelcoord[0]) + ' ' + str(distorted_pixelcoord[1]) +  '\n')

    vert_file.close()
    

    
