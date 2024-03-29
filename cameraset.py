import numpy as np
import cv2
import os
import glob
import bpy


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
        self.k1 = self.d[0]
        self.k2 = self.d[1]
        self.k3 = self.d[4]
        self.p1 = self.d[2]
        self.p2 = self.d[3]

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


for camera in cameras:

    name = cam2char[camera.index]

    # create camera data
    cam_data = bpy.data.cameras.new("{}.{:03d}".format(name, 0))

    # create object camera data and insert the camera data
    cam_ob = bpy.data.objects.new("{}Cam.{:03d}".format(name, 0), cam_data)

    transformx180 = [[1,0,0,0],[0,-1,0,0],[0,0,-1,0],[0,0,0,1]]
    cam_ob.matrix_world =  camera.SE3.transpose() 
    cam_ob.data.lens = (camera.focal_lengths[0] + camera.focal_lengths[1] ) *0.5
    cam_ob.data.shift_x = camera.central_points[0]
    cam_ob.data.shift_y = camera.central_points[1]
    print()

    if bpy.context.scene.unit_settings.length_unit == 'MILLIMETERS':
        cam_ob.location[0] = cam_ob.location[0]/1000 
        cam_ob.location[1] = cam_ob.location[1]/1000
        cam_ob.location[2] = cam_ob.location[2]/1000
    else:
        sys.stderr.write("ERROR: CHANGE UNIT LENGTH TO MILLIMETERS")
        sys.exit(1)    
    cam_ob.rotation_euler[0] = cam_ob.rotation_euler[0] + np.pi
    #cam_ob.rotation_euler[0] = cam_ob.rotation_euler[0]
    #cam_ob.rotation_euler[1] = cam_ob.rotation_euler[1] 
    #cam_ob.rotation_euler[2] = cam_ob.rotation_euler[2]

    # link into scene
    bpy.context.collection.objects.link(cam_ob)
