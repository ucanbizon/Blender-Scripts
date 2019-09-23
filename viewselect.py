import bpy
from mathutils import Vector
from bpy_extras.object_utils import world_to_camera_view
import bmesh


scene = bpy.context.scene
cam = bpy.data.objects['Camera']

obj = bpy.context.object
bm = bmesh.from_edit_mesh(obj.data)

vertices= [e for e in bm.verts]
limit = 0.0001


mWorld = obj.matrix_world



for vert in vertices:
    worldvert = mWorld @ vert.co 
    co2D = world_to_camera_view( scene, cam, worldvert )
    vert.select = False
    
    if 0.0 <= co2D.x <= 1.0 and 0.0 <= co2D.y <= 1.0 and co2D.z >0: 
        # Try a ray cast, in order to test the vertex visibility from the camera
        location= scene.ray_cast( bpy.context.view_layer, cam.location, (worldvert - cam.location).normalized() )
        # If the ray hits something and if this hit is close to the vertex, we assume this is the vertex
        if location[0] and (worldvert - location[1]).length < limit:
            vert.select = True

bmesh.update_edit_mesh(me, True)