import bpy



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



class ConfirmBox_Layer(bpy.types.Operator):
    bl_idname = "wm.confirmboxlayer"
    bl_label =  "Layer Check"

    def deleteViewLayers(self):
        layerCheck = False
        for scene in bpy.data.scenes:
            if len(scene.view_layers) >= 2:
                for layer in scene.view_layers:
                    if len(scene.view_layers) != 1 and layer.name != bpy.context.view_layer.name:
                        try:
                            bpy.context.scene.view_layers.remove(layer)
                            layerCheck = True
                        except:
                            layerCheck = False
            else:
                layerCheck = True
        return layerCheck

    def remove_item(self, collection, itemname):
        for i in collection.keys():
            if i == itemname:
                collection.remove(collection.find(itemname))
        
        if len(collection) == 0:
            bpy.context.scene.checkResult_All = False
        


    def execute(self, context):
        scn = context.scene
        result = self.deleteViewLayers()
        if result == True:
            scn.checkResult_Layers = True
            remove_item(scn.custom, "Layer")
        else:
            scn.checkResult_Layers = False
        return {'FINISHED'}
    
    def draw(self, context):
        msg = ["There are more than 1 layers.", "Would you like to delete them?"]
        for line in msg:
            self.layout.label(text= line)

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self)
        
class Fix_Layer(bpy.types.Operator):
    bl_idname = "mesh.fixlayer"
    bl_label = "Layer Fix"
    bl_description = "Check if there are extra view layers, deletes all view layers except the current active layer"
    

    def checkViewLayers(self):
        layerCheck = False
        for scene in bpy.data.scenes:
            if len(scene.view_layers) >= 2:
                for layer in scene.view_layers:
                    layerCheck = False
            else:
                layerCheck = True
        return layerCheck
    
    def execute(self, context):
        scn = context.scene
        remove_item(scn.custom, "Layer")
        result = self.checkViewLayers()
        if result == True:
            message = ["Layer is ok."]
            if scn.checkingAll == False:
                ShowMessageBox(message)
            scn.checkResult_Layers = True
            remove_item(scn.custom, "Layer")
        else:
            if scn.checkingAll == False:
                bpy.ops.wm.confirmboxlayer("INVOKE_DEFAULT")
            message = "Layers"
            add_item(scn.custom, "Layer", message)
            scn.checkResult_Layers = False
            scn.checkResult_All = True

        return {"FINISHED"}
 

