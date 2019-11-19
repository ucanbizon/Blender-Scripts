import bpy
import bmesh
import json
from mathutils import *
import copy
from bpy_extras.object_utils import world_to_camera_view

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


def GetJSON(filePathAndName):
    with open(filePathAndName, 'r') as fp:
        return json.load(fp)


def OutJSON(filePathAndName, data):
    with open(filePathAndName, 'w') as outfile:
        json.dump(data, outfile, indent=2)


def GetImageSize(fileName):
    for obj in bpy.context.scene.objects:
        for s in obj.material_slots:
            if s.material and s.material.use_nodes:
                for n in s.material.node_tree.nodes:
                    if n.type == 'TEX_IMAGE':
                        if n.image.name == fileName:
                            return [float(n.image.size[0]),float(n.image.size[1])]

    
def GetBary(p, tri1, tri2, tri3):
    c_ = tri3 - tri1
    b_ = tri2 - tri1
    p_ = p - tri1

    cc = c_.dot(c_)
    bc = b_.dot(c_)
    pc = c_.dot(p_)
    bb = b_.dot(b_)
    pb = b_.dot(p_)

    denom = cc*bb - bc*bc
    u = (bb*pc - bc*pb) / denom
    v = (cc*pb - bc*pc) / denom
      
    return [u, v, 1.0- u - v]

bpy.ops.object.mode_set(mode = 'EDIT') 

ob = bpy.context.object
me = ob.data
bm = bmesh.from_edit_mesh(me)

verts = copy.deepcopy([vert.co for vert in bm.verts])

oa = bpy.context.active_object

selected_faces = [f.index for f in bm.faces if f.select]

bpy.ops.object.mode_set(mode = 'OBJECT') 


# Loops per face
faces = []


for face in ob.data.polygons:
    if face.index in selected_faces:
        face_vars = [face.index]
        
        for vert_idx, loop_idx in zip(face.vertices, face.loop_indices):
            uv_coords = ob.data.uv_layers.active.data[loop_idx].uv
            face_vars.append((vert_idx, uv_coords.x, 1.0 -  uv_coords.y))
        faces.append(face_vars)



image_res = GetImageSize("texture.png")
jsonData = GetJSON('C:/Users/ucanb/Desktop/scan_mov/tosend/texmesh/suitNoMarginDalition1_5_HandFixed.json')
corners = jsonData.get('corners',[])

bpy.ops.object.mode_set(mode = 'EDIT') 

mWorld = ob.matrix_world
scene = bpy.context.scene
cam = bpy.data.objects['ACam.001']
limit = 0.0001

render_scale = scene.render.resolution_percentage / 100
render_size = ( int(scene.render.resolution_x * render_scale), int(scene.render.resolution_y * render_scale) )

for corner in corners:
    uvvals  = Vector((float(corner['pts'][0])/image_res[0], float(corner['pts'][1])/image_res[1]))
    kontrol = True
    print('x')
    for face in faces:
        print('111')
        tri1 = Vector((face[1][1],face[1][2]))
        tri2 = Vector((face[2][1],face[2][2]))
        tri3 = Vector((face[3][1],face[3][2]))
        
        if(geometry.intersect_point_tri_2d(uvvals, tri1, tri2, tri3)):
            print('a')
            bary = GetBary(uvvals, tri1, tri2, tri3)
            localCoord = verts[face[1][0]]*bary[2] + verts[face[2][0]]* bary[1] + verts[face[3][0]]* bary[0] 
            worldCoord = mWorld @ localCoord
            co2D = world_to_camera_view( scene, cam, worldCoord )
            if 0.0 <= co2D.x <= 1.0 and 0.0 <= co2D.y <= 1.0 and co2D.z >0:
                print('b')
                # Try a ray cast, in order to test the vertex visibility from the camera
                location= scene.ray_cast( bpy.context.view_layer, cam.location, (worldCoord - cam.location).normalized() )
                # If the ray hits something and if this hit is close to the vertex, we assume this is the vertex
                if location[0] and (worldCoord - location[1]).length < limit:
                    print('c')
                    kontrol = False
                    pixelcoord = (round(co2D.x * render_size[0]),round(co2D.y * render_size[1]))
                    #distorted_pixelcoord = Distort(camera,pixelcoord)
                    corner.update({'3D Coordinates':[localCoord[0], localCoord[1], localCoord[2]]}) 
                    corner.update({'Pixel Coordinates':[pixelcoord[0], pixelcoord[1]]}) 
                    
            break
    if(kontrol):
        corner.update({'3D Coordinates':['-','-','-']}) 
        corner.update({'Pixel Coordinates':['-','-']}) 


OutJSON('C:/Users/ucanb/Desktop/scan_mov/tosend/texmesh/suitNoMarginDalition1_5_HandFixedOut5.json', jsonData)






#print(face[1][0],face[2][0],face[3][0])
#print(verts[face[1][0]],verts[face[2][0]],verts[face[3][0]])
#print(realCoord)
#corner.update({'face':face[0]})        
#corner.update({'bary':bary})        
#print(bary)
#corner.update({'face': -1})        
#corner.update({'bary':[-1,-1]})    
