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



def checkUnusedData():
    unusedData = []

    datatypeList = [
                bpy.data.actions,
                bpy.data.armatures,
#                bpy.data.brushes,
                bpy.data.cache_files,
                bpy.data.cameras,
                bpy.data.collections,
                bpy.data.curves,
                bpy.data.fonts,
                bpy.data.grease_pencils,
                bpy.data.images,
                bpy.data.lattices,
                bpy.data.libraries,
                bpy.data.lightprobes,
                bpy.data.lights,
                bpy.data.linestyles,
                bpy.data.masks,
                bpy.data.materials,
                bpy.data.metaballs,
                bpy.data.meshes,
                bpy.data.movieclips,
                bpy.data.node_groups,
                bpy.data.objects,
                bpy.data.paint_curves,
                bpy.data.palettes,
                bpy.data.particles,
                bpy.data.scenes,
                bpy.data.screens,
                bpy.data.shape_keys,
                bpy.data.sounds,
                bpy.data.speakers,
#                bpy.data.texts,
                bpy.data.textures,
                bpy.data.volumes,
                bpy.data.window_managers,
                bpy.data.worlds,
                bpy.data.workspaces,]

    for datatype in datatypeList:
        for bpy_data_iter in datatype:
            if bpy_data_iter.users == bpy_data_iter.use_fake_user:
                unusedData.append(bpy_data_iter)
    
    
    if len(unusedData) == 0:
        return True
    else:
        return unusedData


class ConfirmBox_UnusedData(bpy.types.Operator):
    bl_idname = "mesh.confirmboxunuseddata"
    bl_label =  "Unused Data fix"

    def execute(self, context):
        scn = context.scene
        bpy.data.orphans_purge(do_recursive = True)
        result = checkUnusedData()
        if result == True:
            message = ["Unused data was removed."]
            ShowMessageBox(message)
            remove_item(scn.custom, "Unused")
            scn.checkResult_UnusedData = True
        else:
            message = "Some umused items was not removed. Check Orphan data list."
            add_item(scn.custom, "Unused", message)
            scn.checkResult_UnusedData = False
        return {'FINISHED'}
    
    def draw(self, context):
        msg = ["There are unused item in this scene.", "Would you like to delete them?"]
        for line in msg:
            self.layout.label(text= line)

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self)


class Check_Errant(bpy.types.Operator):
    bl_idname = "mesh.checkerrant"
    bl_label = "Check unused data in the scene"
    bl_description = "Check unused data in the scene"



    def execute(self, context):
        scn = context.scene
        remove_item(scn.custom, "Unused")
        results = checkUnusedData()
        if results != True:
            scn.checkResult_UnusedData = False
            scn.checkResult_All = True
            for obj in results:
                add_item(scn.custom, "Unused", str(obj.name))
            if scn.checkingAll == False:
                bpy.ops.mesh.confirmboxunuseddata("INVOKE_DEFAULT")
        else:
            scn.checkResult_UnusedData = True
            scn.checkResult_All = False
            remove_item(scn.custom, "Unused")
            message = ["No unused data"]
            if scn.checkingAll == False:
                ShowMessageBox(message)


        
        return{"FINISHED"}