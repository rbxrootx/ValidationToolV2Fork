import bpy


def ensureObjectModeandActive(avatarObj):
    if bpy.context.view_layer.objects.active == None:
        bpy.context.view_layer.objects.active = avatarObj

    if bpy.context.active_object.mode == "EDIT":
            bpy.ops.object.editmode_toggle()
            
    bpy.context.view_layer.objects.active = avatarObj
    bpy.ops.object.mode_set(mode='OBJECT')