import bpy

scn = bpy.context.scene

scn.unit_settings.system = 'METRIC'
system = scn.unit_settings.system

scn.unit_settings.length_unit = 'CENTIMETERS'
lengthUnit = scn.unit_settings.length_unit

scn.unit_settings.scale_length = 0.1
scale = scn.unit_settings.scale_length



bpy.ops.export_scene.fbx(path_mode ="COPY", batch_mode = "OFF", add_leaf_bones = False, bake_anim = True)