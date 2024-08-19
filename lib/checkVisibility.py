import bpy

def set_Visibility():
    originalVisibilitySettings = {}
    allObjects = bpy.data.objects
    for obj in allObjects:
        originalVisibilitySettings[obj.name] = [obj.hide_viewport, obj.hide_get()]
        obj.hide_viewport = False
        obj.hide_set(False)
    
    return originalVisibilitySettings

def set_originalVisibility(originalVisibilitySettings):
    for key in originalVisibilitySettings:
        obj = bpy.data.objects[key]
        obj.hide_viewport = originalVisibilitySettings[key][0]
        obj.hide_set(originalVisibilitySettings[key][1])