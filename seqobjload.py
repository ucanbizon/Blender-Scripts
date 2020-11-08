import bpy, os
from bpy.props import *




for number in range(1, 100):
    fp = "C:/Users/ucanb/Desktop/finalanka/testseq/" +  "AA" + "{0:0=8d}".format(number) + ".obj"
    print(fp)
    bpy.ops.import_scene.obj(filepath=fp,split_mode='OFF',axis_forward='Y', axis_up='Z')
    
    


objects = bpy.context.scene.objects
bpy.ops.object.select_all(action='DESELECT')
for obj in objects:
    print(obj.name)
    if obj.type == "MESH":
        print(obj)
        obj.select_set(state=True)
        
        
bpy.ops.object.join_shapes()


bpy.ops.object.select_all(action='DESELECT')
for obj in objects:
    print(obj.name)
    if obj.type == "MESH":
        print(obj)
        
        name = obj.name
        print(int(name[2:10]))
        if int(name[2:10]) > 0:
            obj.select_set(state=True)

bpy.ops.object.delete()

#for number in range(2851, 2860):
