import bpy


blockNum = 4
imageRes = 1024

bpy.ops.object.mode_set(mode = 'OBJECT') 

obj = bpy.data.objects["Grid"]


blockLength = 1.0 / (imageRes / 16.0)


print(blockLength)


mesh = obj.data
count = 0
vertIndex = []
for poly in mesh.polygons:
    for loop_index in poly.loop_indices:
        uv = mesh.uv_layers.active.data[loop_index].uv
        if (uv.x < blockLength) and (uv.y < blockLength):
            count += 1
            vertIndex.append(mesh.loops[loop_index].vertex_index)


bpy.ops.object.mode_set(mode = 'EDIT') 
bpy.ops.mesh.select_mode(type="VERT")
bpy.ops.mesh.select_all(action = 'DESELECT')
bpy.ops.object.mode_set(mode = 'OBJECT')
for v in vertIndex:
    obj.data.vertices[v].select = True
bpy.ops.object.mode_set(mode = 'EDIT')



print(count)