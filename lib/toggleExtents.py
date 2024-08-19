import bpy

##THIS IS A TEMPLATE FILE FOR MODULE

def ShowMessageBox(message):
    
    def draw(self, context):
        for line in message:
            self.layout.label(text=line)
            
    bpy.context.window_manager.popup_menu(draw, title="Validation Result", icon = "INFO")


def add_item(collection, itemname, message):
    item = collection.add()
    item.name = itemname
    item.type = itemname
    item.message = message


def remove_item(collection, itemname):
    for i in collection.keys():
        if i == itemname:
            collection.remove(collection.find(itemname))
    
    if len(collection) == 0:
        bpy.context.scene.checkResult_All = False



class TOGGLE_EXTENTS(bpy.types.Operator):
    bl_idname = "mesh.toggleextent"
    bl_label = "Toggle extents visibility for size check."
    bl_description = "Toggle extents visibility for size check."



    def execute(self, context):
        message = ["Toggle extents visibility for size check."]
        ShowMessageBox(message)
        return{"FINISHED"}