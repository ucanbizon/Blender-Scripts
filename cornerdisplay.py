
bl_info = {
    'name': 'Index Visualiser (BMesh)',
    'author': 'Bartius Crouch, CoDEmanX, zeffii, modified by kutay',
    'version': (3, 0, 0),
    'blender': (2, 8, 0),
    'location': 'View3D > Properties panel > Mesh Display tab (edit-mode)',
    'warning': '',
    'description': 'Display indices of verts, edges and faces in the 3d-view',
    'wiki_url': '',
    'tracker_url': '',
    'category': '3D View'}


"""
Display the indices of vertices, edges and faces in the 3d-view.
How to use:
- Select a mesh and go into editmode
- Display the properties panel (N-key)
- Go to the Mesh Display tab, it helps to fold the tabs above it
- Press the 'Visualise indices button'
"""

import bpy
import bgl
import blf
import mathutils
import bmesh
import math
from bpy_extras.view3d_utils import location_3d_to_region_2d as loc3d2d
import os
point_dict = {}
cids = []
cidsonlynum = []

def adjust_list(in_list, x, y):
    return [[old_x + x, old_y + y] for (old_x, old_y) in in_list]


def generate_points(width, height):
    amp = 5  # radius fillet

    width += 2
    height += 4
    width = ((width/2) - amp) + 2
    height -= (2*amp)

    pos_list, final_list = [], []

    n_points = 12
    seg_angle = 2 * math.pi / n_points
    for i in range(n_points + 1):
        angle = i * seg_angle
        x = math.cos(angle) * amp
        y = math.sin(angle) * amp
        pos_list.append([x, -y])

    w_list, h_list = [1, -1, -1, 1], [-1, -1, 1, 1]
    slice_list = [[i, i+4] for i in range(0, n_points, 3)]

    for idx, (start, end) in enumerate(slice_list):
        point_array = pos_list[start:end]
        w = width * w_list[idx]
        h = height * h_list[idx]
        final_list += adjust_list(point_array, w, h)

    return final_list


def get_points(index):
    '''
    index:   string representation of the index number
    returns: rounded rect point_list used for background.
    the neat thing about this is if a width has been calculated once, it
    is stored in a dict and used if another polygon is saught with that width.
    '''
    width, height = blf.dimensions(0, index)
    if not (width in point_dict):
        point_dict[width] = generate_points(width, height)

    return point_dict[width]


# calculate locations and store them as ID property in the mesh
def draw_callback_px(self, context):
    # polling

    # if context.mode != "EDIT_MESH" and context.mode != "PAINT_WEIGHT":
    #     return

    # get screen information

    region = context.region
    mid_x = region.width / 2
    mid_y = region.height / 2
    width = region.width
    height = region.height

    # get matrices

    view_mat = context.space_data.region_3d.perspective_matrix
    ob_mat = context.active_object.matrix_world
    total_mat = view_mat @ ob_mat

    blf.size(0, 13, 72)

    def draw_index(r, g, b, index, center):

        vec = total_mat @ center # order is important

        # dehomogenise

        vec = mathutils.Vector((vec[0] / vec[3], vec[1] / vec[3], vec[2] / vec[3]))
        x = int(mid_x + vec[0] * width / 2)
        y = int(mid_y + vec[1] * height / 2)

        # bgl.glColorMask(1,1,1,1)
        blf.position(0, x, y, 0)

        blf.draw(0, index)


    scene = context.scene
    me = context.active_object.data
    bm = bmesh.from_edit_mesh(me)
    if scene.live_mode:
        me.update()
        

    

    for v in bm.verts:
        if v.select:
            cornerval = str(v.index) + "@" + str(cids[cidsonlynum.index(v.index)][0])
            draw_index(0.0, 1.0, 1.0, cornerval, v.co.to_4d())

    bmesh.update_edit_mesh(me, True) 

# operator
class IndexVisualiser(bpy.types.Operator):
    bl_idname = "view3d.corner_visualiser"
    bl_label = "Corner Visualiser"
    bl_description = "Toggle the visualisation of corners"

    _handle = None

    @classmethod
    def poll(cls, context):
        return context.mode == "EDIT_MESH"

    def modal(self, context, event):
        if context.area:
            context.area.tag_redraw()

        # removal of callbacks when operator is called again
        if context.scene.display_indices == -1:
            bpy.types.SpaceView3D.draw_handler_remove(self._handle, 'WINDOW')
            context.scene.display_indices = 0
            return {"CANCELLED"}

        return {"PASS_THROUGH"}

    def invoke(self, context, event):
        if context.area.type == "VIEW_3D":
            me = context.active_object.data
            bm = bmesh.from_edit_mesh(me)
            for vert in bm.verts:
                if vert.index in cidsonlynum:
                    vert.select = True
                else:
                    vert.select = False    
            
            if context.scene.display_indices < 1:
                # operator is called for the first time, start everything
                context.scene.display_indices = 1
                self._handle = bpy.types.SpaceView3D.draw_handler_add(
                    draw_callback_px, (self, context), 'WINDOW', 'POST_PIXEL')
                context.window_manager.modal_handler_add(self)
                return {"RUNNING_MODAL"}
            else:
                # operator is called again, stop displaying
                context.scene.display_indices = -1
                return {'RUNNING_MODAL'}
        else:
            self.report({"WARNING"}, "View3D not found, can't run operator")
            return {"CANCELLED"}


# defining the panel
def menu_func(self, context):
    self.layout.separator()
    scn = context.scene

    col = self.layout.column(align=True)
    col.operator(IndexVisualiser.bl_idname, text="Visualize corners")
    row = col.row(align=True)
    row.active = (context.mode == "EDIT_MESH" and scn.display_indices == 1)


    #row.prop(context.scene, "live_mode")


def register_properties():
    bpy.types.Scene.display_indices = bpy.props.IntProperty(
        name="Display corners",
        default=0)

    bpy.types.Scene.live_mode = bpy.props.BoolProperty(
        name="Live",
        description="Toggle live update of the selection, can be slow",
        default=False)


def unregister_properties():
    del bpy.types.Scene.display_indices
    del bpy.types.Scene.live_mode


def register():
    register_properties()
    bpy.utils.register_class(IndexVisualiser)
    bpy.types.VIEW3D_PT_view3d_properties.append(menu_func)


def unregister():
    bpy.utils.unregister_class(IndexVisualiser)
    unregister_properties()
    bpy.types.VIEW3D_PT_view3d_meshdisplay.remove(menu_func)



if __name__ == "__main__":
    filename = 'corrected-maya_with_missingCIDs.txt'
    directory =  r'C:\Users\ucanb\Desktop\scan_mov' 
    fullpath = os.path.join(directory, filename)
    with open(fullpath) as f:
        cids = f.readlines()
    cids = [x.strip().rsplit(" ", 1) for x in cids]
    for i in range(len(cids)):
        cids[i][-1] =  int(cids[i][-1])
        cidsonlynum.append(cids[i][-1])
        
        

        
    register()
