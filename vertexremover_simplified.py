import bpy, bmesh
import os

def getNeighbourVertexIndices(mesh, index): 
    retlist = [e.vertices[e.vertices[0] == index] for e in mesh.edges if index in e.vertices]
    if index in retlist:
        retlist.remove(index)
    return retlist    
    
def unique(vertexlist):
    unique_list = []
    for x in vertexlist:
        if x not in unique_list:
            unique_list.append(x)
        else:
            print("error stop")
    return unique_list

def indexdec(val, verlist):
    return [x-1 if x > val else x for x in verlist]



filename = 'CIDToMeshVID.txt'
directory =  r'C:\Users\ucanb\Desktop\scan_mov' 
fullpath = os.path.join(directory, filename)

with open(fullpath) as f:
    vertices2Preserve = f.readlines()

vertices2Preserve = [int(x.strip()) for x in vertices2Preserve]
vertices2Preserve = [x for x in vertices2Preserve if x >= 0]
vertices2Preserve = unique(vertices2Preserve)
#vertices2Preserve.sort()

me = bpy.context.edit_object.data
#vertices2bRemoved = list(range(len(me.vertices)))
#vertices2bRemoved = [value for value in vertices2bRemoved if value not in vertices2Preserve]

bm = bmesh.from_edit_mesh(me)
vertices2bRemoved = [v.index for v in bm.verts if v.select]
vertices2bRemoved = [value for value in vertices2bRemoved if value not in vertices2Preserve]
#vertices2bRemoved.sort()
#leftfootedge = [16640, 16641, 16665, 17474, 17494, 17495, 17636, 17637, 17648, 17697, 17730, 17735, 17761, 17762, 17764, 17765, 17766, 17769, 17770, 17771, 17774, 17776, 23173, 23198, 23199, 23200, 23201, 23202, 23203, 23204, 23205, 23206, 23207, 23208, 23209, 23210, 23211, 23212, 23213, 23214, 23215, 23216, 23217, 23218, 23219, 23220, 23221, 23222, 23223, 23224, 23225, 23226, 23227, 23228, 23229, 23230, 23231, 23232, 23233, 23234, 23235, 23236, 23237, 23238, 23239, 23240, 23241, 23242, 23243, 23244, 23245, 23256, 23257, 23280, 23285, 23290, 23291, 23293, 23296, 23297]

#leftfootsole = [23241, 23279, 23281, 23282, 23283, 23284, 23286, 23287, 23288, 23289, 23292, 23294, 23295, 23325, 23326, 23327, 23328, 23329, 23330, 23331, 23332, 23333, 23334]

#rightfootedge = [14068, 14071, 14073, 14074, 14129, 14130, 14165, 14216, 14349, 14350, 14363, 14368, 14444, 14446, 14451, 14452, 14455, 18713, 18723, 18737, 18739, 22786, 22886, 22901, 22920, 22928, 22930, 23174, 23175, 23176, 23177, 23178, 23179, 23180, 23181, 23182, 23183, 23184, 23185, 23186, 23187, 23188, 23189, 23190, 23191, 23192, 23193, 23194, 23195, 23196, 23197, 23246, 23247, 23248, 23249, 23250, 23251, 23252, 23253, 23254, 23255, 23262, 23265, 23267, 23269, 23270, 23271, 23272, 23276, 23278]

#rightfootsole = [23258, 23259, 23260, 23261, 23263, 23264, 23266, 23268, 23273, 23274, 23275, 23277, 23335, 23336, 23337, 23338, 23339, 23340, 23341]

#footedge = leftfootedge + rightfootedge
#footsole = leftfootsole + rightfootsole
footedge = [1473, 1474, 1475, 1478, 1479, 1480, 1449, 1450, 1451, 1453, 1486, 1455]
footsole = [1448,1457,1452]
#foot = [value for value in foot if value not in vertices2Preserve]

vertices2bRemoved =[1457,1448,1452,417,416,1478,1382,1359,1480,1381,1479,116,290,293,115,114,113,556,542,540,1474,1473,1475,1486,515,516,172,23,713,1453,428,429,182,26,1455,712,645,644,641,640,621,620,1450,548,547,1451,1284,1449,1291,1303,1309,1316,1329,1258,1232,1335,1358,1126,1379,1380,1102,1079,1055,1006,967,1393,1394,940,901,1409,1414,1415,1423,873,771,752,749]



for i in footedge:
    vertices2bRemoved.sort(key = i.__eq__) 


vertices2bRemoved.reverse()
#vertices2bRemoved = foot
#vertices2bRemoved = [value for value in vertices2bRemoved if value not in foot]

#vertices2bRemoved = list(set(temp1) - set(temp2))


print(len(vertices2bRemoved))
print(vertices2bRemoved)
goneV = 0
deleted = []




for v in vertices2bRemoved:
    try:
        print(v)
        realV = v - sum(dv < v for dv in deleted)
        deleted.append(v)
        footedge = indexdec(realV, footedge)
        footsole = indexdec(realV, footsole)
        bpy.ops.mesh.select_mode(type="VERT")
        try:
            bpy.ops.mesh.select_all(action='DESELECT')
        except:
            print("already all deselected")
            
        
        bpy.ops.object.mode_set(mode = 'OBJECT')
        neighborVertices = getNeighbourVertexIndices(me, realV)
        me.vertices[realV].select = True
        bpy.ops.object.mode_set(mode = 'EDIT') 

        

        bpy.ops.mesh.delete(type='VERT')
        
        bpy.ops.object.mode_set(mode = 'OBJECT')

 
        mergefoot = []
        if realV in footedge:
            footedge.remove(realV)
            for i in neighborVertices:
                ozv = i-1
                if(i < realV):
                    ozv = i
                if ozv in footedge:
                    mergefoot.append(ozv)
            
            
 
        #print(neighborVertices)   
        #print(mergefoot)
        if len(mergefoot) == 2:
            me.vertices[mergefoot[0]].select = True
            me.vertices[mergefoot[1]].select = True
            bpy.ops.object.mode_set(mode = 'EDIT') 
            bpy.ops.mesh.edge_face_add()
            bpy.ops.object.mode_set(mode = 'OBJECT')
            alt = mergefoot.copy()
            ust = mergefoot.copy()
            for i in neighborVertices:
                ozv = i-1
                if(i < realV):
                    ozv = i
                if ozv in footsole:
                    alt.append(ozv)
                else:
                    ust.append(ozv)
            
            alt = unique(alt)
            ust = unique(ust)
            
            for i in alt:        
                me.vertices[i].select = True
            bpy.ops.object.mode_set(mode = 'EDIT') 
            bpy.ops.mesh.beautify_fill()
            bpy.ops.mesh.fill()
                
            try:
                bpy.ops.mesh.select_all(action='DESELECT')
            except:
                print("already all deselected")
                
            bpy.ops.object.mode_set(mode = 'OBJECT')
            for i in ust:        
                me.vertices[i].select = True
            bpy.ops.object.mode_set(mode = 'EDIT') 
            bpy.ops.mesh.beautify_fill()
            bpy.ops.mesh.fill()
            

        
        else:
            for i in neighborVertices:
                ozv = i-1
                if(i < realV):
                    ozv = i
                me.vertices[ozv].select = True
            bpy.ops.object.mode_set(mode = 'EDIT') 

            bpy.ops.mesh.beautify_fill()
            bpy.ops.mesh.fill()
        

        
    except:
        
        pass
