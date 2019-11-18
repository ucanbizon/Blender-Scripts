import bpy
import bmesh
import json
from mathutils import *
import copy

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

ob = bpy.context.object
assert ob.type == "MESH", "Selected object not a mesh"
me = ob.data
bm = bmesh.new()
bm.from_mesh(me)
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

 
for corner in corners:
    uvvals  = Vector((float(corner['pts'][0])/image_res[0], float(corner['pts'][1])/image_res[1]))
    kontrol = True
    for face in faces:
        tri1 = Vector((face[1][1],face[1][2]))
        tri2 = Vector((face[2][1],face[2][2]))
        tri3 = Vector((face[3][1],face[3][2]))
        if(geometry.intersect_point_tri_2d(uvvals, tri1, tri2, tri3)):
            kontrol = False
            bary = GetBary(uvvals, tri1, tri2, tri3)
            realCoord = verts[face[1][0]]*bary[2] + verts[face[2][0]]* bary[1] + verts[face[3][0]]* bary[0] 
            #print(face[1][0],face[2][0],face[3][0])
            #print(verts[face[1][0]],verts[face[2][0]],verts[face[3][0]])
            #print(realCoord)
            corner.update({'realCoord':[realCoord[0], realCoord[1], realCoord[2]]}) 
            #corner.update({'face':face[0]})        
            #corner.update({'bary':bary})        
            #print(bary)
            break
    if(kontrol):
        #corner.update({'face': -1})        
        #corner.update({'bary':[-1,-1]})    
        corner.update({'realCoord':['-','-','-']}) 


OutJSON('C:/Users/ucanb/Desktop/scan_mov/tosend/texmesh/suitNoMarginDalition1_5_HandFixedOut.json', jsonData)


