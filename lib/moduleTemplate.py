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



class Check_TEMPLATE(bpy.types.Operator):
    bl_idname = "mesh.checkerrant"
    bl_label = "Check unused data in the scene"
    bl_description = "Check unused data in the scene"



    def execute(self, context):
        message = ["This is errant Data"]
        ShowMessageBox(message)
        return{"FINISHED"}