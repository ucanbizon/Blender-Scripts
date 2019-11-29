import bpy
import bgl
import blf
import math
import random

isfirst = 0
intersection_obj = None
intersection_ops = None

for cam in bpy.context.scene.objects:
    if cam.name == 'intersect':
        intersection_obj = cam

for cam in bpy.context.scene.objects:
    if cam.type == 'CAMERA':
        
        #if(int(cam.name[-2:]) < 9):
        #    continue
        #print(cam.name)
        #cam = bpy.data.objects['ACam.000']
        rotcam = cam.rotation_euler


        aspx = bpy.context.scene.render.resolution_x * bpy.context.scene.render.pixel_aspect_x;
        aspy = bpy.context.scene.render.resolution_y * bpy.context.scene.render.pixel_aspect_y;
        ratiox = min(aspx/aspy, 1.0)
        ratioy = min(aspy/aspx, 1.0)



        angleofview = 2.0 * math.atan(cam.data.sensor_width  / (2.0 * cam.data.lens))
        oppositeclipsta = math.tan(angleofview / 2.0) * cam.data.clip_start
        oppositeclipend = math.tan(angleofview / 2.0) * cam.data.clip_end

        box = [[0]*3 for i in range(8)]
        box[2][0] = box[1][0] = -oppositeclipsta * ratiox;
        box[0][0] = box[3][0] = -oppositeclipend * ratiox;
        box[5][0] = box[6][0] = +oppositeclipsta * ratiox;
        box[4][0] = box[7][0] = +oppositeclipend * ratiox;
        box[1][1] = box[5][1] = -oppositeclipsta * ratioy;
        box[0][1] = box[4][1] = -oppositeclipend * ratioy;
        box[2][1] = box[6][1] = +oppositeclipsta * ratioy;
        box[3][1] = box[7][1] = +oppositeclipend * ratioy;
        box[0][2] = box[3][2] = box[4][2] = box[7][2] = -cam.data.clip_end;
        box[1][2] = box[2][2] = box[5][2] = box[6][2] = -cam.data.clip_start;

        verts = [tuple(i) for i in box]

        faces = [(0, 1, 2, 3), (4, 7, 6, 5), (0, 4, 5, 1), (1, 5, 6, 2), (2, 6, 7, 3), (4, 0, 3, 7)]

        mesh = bpy.data.meshes.new("FrustumA")
        mesh.from_pydata(verts, [], faces)

        obj = bpy.data.objects.new("FrustumA", mesh)
        bpy.context.collection.objects.link(obj)

        #bpy.context.scene.objects.active = obj
        #obj.select = True
        obj.rotation_euler = cam.rotation_euler
        obj.location = cam.location
        obj.show_wire = True

        mat = bpy.data.materials.new("MaterialName")
        obj.data.materials.append(mat) #add the mterial to the object
        #mat.alpha = 0.2
        obj.active_material = mat
        gamma = 1/2.2
        obj.active_material.diffuse_color = (random.getrandbits(1), random.getrandbits(1), random.getrandbits(1),0.2)
        obj.active_material.blend_method = 'ADD'


        print("degil")
        
        bpy.context.view_layer.objects.active = intersection_obj
        bpy.ops.object.modifier_add(type='BOOLEAN')
        intersection_obj.modifiers["Boolean"].operation = 'INTERSECT'
        intersection_obj.modifiers["Boolean"].object = obj
        bpy.ops.object.modifier_apply(apply_as='DATA', modifier="Boolean")
        #if cam.name == "ECam.009":
        #    break

        #bpy.ops.object.modifier_add(type='BOOLEAN')
        #bpy.context.object.modifiers["Boolean"].operation = 'INTERSECT'
        #bpy.context.object.modifiers["Boolean"].object = bpy.data.objects["Cube"]
        #bpy.ops.object.modifier_apply(apply_as='DATA', modifier="Boolean")


bpy.ops.object.select_all(action='DESELECT')

for obj in bpy.context.scene.objects:
    if "Frustum" in obj.name:
        obj.select_set(True)
bpy.ops.object.delete() 

'''
bpy.ops.mesh.primitive_cube_add(location=(0,0,0))
cube = bpy.context.selected_objects[0]
cube.name = "FrustumA"


color=(0.0, 0.0, 0.0, 1.0)
bgl.glColor4f(*color)


bgl.glBegin(bgl.GL_QUADS);

bgl.glVertex3f(box[0][0], box[0][1], box[0][2])
bgl.glVertex3f(box[1][0], box[1][1], box[1][2])
bgl.glVertex3f(box[2][0], box[2][1], box[2][2])
bgl.glVertex3f(box[3][0], box[3][1], box[3][2])

bgl.glVertex3f(box[4][0], box[4][1], box[4][2])
bgl.glVertex3f(box[5][0], box[5][1], box[5][2])
bgl.glVertex3f(box[6][0], box[6][1], box[6][2])
bgl.glVertex3f(box[7][0], box[7][1], box[7][2])

bgl.glVertex3f(box[1][0], box[1][1], box[1][2])
bgl.glVertex3f(box[5][0], box[5][1], box[5][2])
bgl.glVertex3f(box[6][0], box[6][1], box[6][2])
bgl.glVertex3f(box[2][0], box[2][1], box[2][2])

bgl.glVertex3f(box[4][0], box[4][1], box[4][2])
bgl.glVertex3f(box[0][0], box[0][1], box[0][2])
bgl.glVertex3f(box[3][0], box[3][1], box[3][2])
bgl.glVertex3f(box[7][0], box[7][1], box[7][2])

bgl.glVertex3f(box[6][0], box[6][1], box[6][2])
bgl.glVertex3f(box[2][0], box[2][1], box[2][2])
bgl.glVertex3f(box[3][0], box[3][1], box[3][2])
bgl.glVertex3f(box[7][0], box[7][1], box[7][2])

bgl.glVertex3f(box[1][0], box[1][1], box[1][2])
bgl.glVertex3f(box[5][0], box[5][1], box[5][2])
bgl.glVertex3f(box[4][0], box[4][1], box[4][2])
bgl.glVertex3f(box[0][0], box[0][1], box[0][2])


bgl.glEnd()

'''