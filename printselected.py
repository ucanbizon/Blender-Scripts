import bpy
import bmesh


#index = [23228, 23244, 23234, 23241, 23236, 23215, 23212, 23296, 23209, 23206, 17474, 23295, 23325, 23326, 23327, 23328, 23329, 23330, 23331, 23332,23333, 23334] # here the index you want select please change 
#index = [23259, 23269, 23268, 23263, 14350, 23260, 23335, 23336, 23337, 23338, 23275, 23339, 23247, 23253, 23250, 23340, 23341]
obj = bpy.context.object
me = obj.data
bm = bmesh.from_edit_mesh(me)

vertices= [e for e in bm.verts]
oa = bpy.context.active_object

selected_verts = [v.index for v in bm.verts if v.select]
print(selected_verts)

'''
for vert in vertices:
    if vert.index in index:
        vert.select = True
    else:
        vert.select = False

bmesh.update_edit_mesh(me, True) 

'''