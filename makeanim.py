
        
import bpy
basis = None

for shapekey in bpy.data.shape_keys:

    for keyblock in shapekey.key_blocks:
        if keyblock.name == "Basis":
            basis = keyblock
            break
            

for shapekey in bpy.data.shape_keys:

    for keyblock in shapekey.key_blocks:
        if keyblock.name == "Basis":
            basis = keyblock
            continue
        keyblock.relative_key = basis 


for shapekey in bpy.data.shape_keys:
    cframe = 1
    bpy.context.scene.frame_set(cframe)
    for keyblock in shapekey.key_blocks:
        if keyblock.name == "Basis":
            continue
        keyblock.value = 0
        keyblock.keyframe_insert('value')




prevkey = basis
for shapekey in bpy.data.shape_keys:
    cframe = 1
    for keyblock in shapekey.key_blocks:
        if keyblock.name == "Basis":
            continue
        else:
            print(keyblock)
            bpy.context.scene.frame_set(cframe)
            keyblock.value = 1
            keyblock.keyframe_insert('value')
            #prevkey.value = 0
            #prevkey.keyframe_insert('value')
            
            for remain in shapekey.key_blocks:
                if remain.name == "Basis" or remain.name == keyblock.name:
                    continue
                remain.value = 0
                remain.keyframe_insert('value')        
            
            cframe = cframe + 1
            #prevkey = keyblock
            #bpy.context.scene.frame_set(cframe)
            #keyblock.value = 0
            #keyblock.keyframe_insert('value')  
            
