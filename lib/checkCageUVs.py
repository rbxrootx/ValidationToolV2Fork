import bpy
import os
from pathlib import Path

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


def getChildren(object): 
    children = [] 
    for ob in bpy.data.objects: 
        if ob.parent == object: 
            children.append(ob)
    return children


def getCages(armatureChildren, checkMode):
    checkCages = []
    if checkMode == '0':
        for obj in armatureChildren:
            if "_Geo" in obj.name:
                outerCageName = obj.name.split("_Geo")[0] + "_OuterCage"
                try:
                    outerCage = bpy.data.objects[outerCageName]
                    checkCages.append(outerCage)
                except:
                    pass
    else:
        for obj in armatureChildren:
            if "_Att" not in obj.name:
                outerCageName = obj.name + "_OuterCage"
                try:
                    outerCage = bpy.data.objects[outerCageName]
                    checkCages.append(outerCage)
                except:
                    pass

                innerCageName = obj.name + "_InnerCage"
                try:
                    innerCage = bpy.data.objects[innerCageName]
                    checkCages.append(innerCage)
                except:
                    pass
    

    return checkCages

def importRefFBX(checkMode):
    dirpath = os.path.dirname(os.path.realpath(__file__)).replace("lib", "")
    referenceCages = {}
    if checkMode == "0":
        fbxFilePath = os.path.join(dirpath, "assets","templateCageRef.fbx")
    else:
        fbxFilePath = os.path.join(dirpath, "assets","templateCageRef_LC.fbx")
    bpy.ops.import_scene.fbx(filepath=fbxFilePath)
    for obj in bpy.context.selected_objects:
        referenceCages[obj.name] = obj
    return referenceCages


def checkCageUVs(geometries, referenceCages, checkMode):
    wrongUVCages = {}
    refCageName = ""
    for geo in geometries:
        if not geo.data.uv_layers:
            pass
        else:
            if checkMode == "0":
                refCageName = geo.name + "_ref"
            else:
                if "outercage" in geo.name.lower():
                    refCageName = "OuterCage_ref"
                if "innercage" in geo.name.lower():
                    refCageName = "InnerCage_ref"
            try:
                if referenceCages[refCageName]:
                    for loop in geo.data.loops :
                        uv_coords = geo.data.uv_layers.active.data[loop.index].uv
                        uv_coords_ref = referenceCages[refCageName].data.uv_layers.active.data[loop.index].uv
                        if (uv_coords.x != uv_coords_ref.x) or (uv_coords.y != uv_coords_ref.y):
                            if not geo.name in wrongUVCages.keys():
                                wrongUVCages[geo.name] = [(loop.index, uv_coords_ref)]
                            else:
                                wrongUVCages[geo.name].append((loop.index, uv_coords_ref))
            except:
                pass

    if len(wrongUVCages) != 0:
        return  wrongUVCages
    else:
        return True



def fixCageUVs(geometries, referenceCages, checkMode):
    for geo in geometries:
        if not geo.data.uv_layers:
            pass
        else:
            if checkMode == "0":
                refCageName = geo.name + "_ref"
            else:
                if "outercage" in geo.name.lower():
                    refCageName = "OuterCage_ref"
                if "innercage" in geo.name.lower():
                    refCageName = "InnerCage_ref"
            try:
                if referenceCages[refCageName]:
                    for loop in geo.data.loops :
                        uv_coords = geo.data.uv_layers.active.data[loop.index].uv
                        uv_coords_ref = referenceCages[refCageName].data.uv_layers.active.data[loop.index].uv
                        if uv_coords.x != uv_coords_ref.x:
                            geo.data.uv_layers.active.data[loop.index].uv.x = uv_coords_ref.x
                        if uv_coords.y != uv_coords_ref.y:
                            geo.data.uv_layers.active.data[loop.index].uv.y = uv_coords_ref.y
            except:
                pass
    


class ConfirmBox_CageUVs(bpy.types.Operator):
    bl_idname = "wm.confirmboxcageuvs"
    bl_label = ""


    def execute(self, context):
        scn = context.scene
        avatarObj = bpy.context.scene.Object_for_Check
        if avatarObj == None or avatarObj.type != "ARMATURE":
            message = ["Select armature object"]
            ShowMessageBox(message)
            return{"FINISHED"}
        avatarObjChildren = getChildren(avatarObj)
        checkCages = getCages(avatarObjChildren, scn.checkMode)
        referenceCages = importRefFBX(scn.checkMode)
        fixCageUVs(checkCages, referenceCages, scn.checkMode)
        scn.checkResult_CageUVs = True
        remove_item(scn.custom, "CageUVs")

        for obj in referenceCages:
            bpy.data.objects.remove(referenceCages[obj], do_unlink=True)

        return {'FINISHED'}
    
    def draw(self, context):
        scn = context.scene
        msg = ["Cage UVs have been modified.","Would you like to fix them?"]
        for line in msg:
            self.layout.label(text= line)

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self)



class Check_CageUVs(bpy.types.Operator):
    bl_idname = "mesh.checkcageuvs"
    bl_label = "Check UV modification on cage meshes"
    bl_description = "Check UV modification on cage meshes"


    def execute(self, context):
        scn = context.scene
        remove_item(scn.custom, "CageUVs")
        avatarObj = bpy.context.scene.Object_for_Check
        if avatarObj == None or avatarObj.type != "ARMATURE":
            message = ["Select armature object"]
            ShowMessageBox(message)
            return{"FINISHED"}
        avatarObjChildren = getChildren(avatarObj)
        checkCages = getCages(avatarObjChildren, scn.checkMode)
        referenceCages = importRefFBX(scn.checkMode)
        result = checkCageUVs(checkCages, referenceCages, scn.checkMode)


        if result != True:
            wrongUVs = result
            for geoName in wrongUVs.keys():
                add_item(scn.custom, "CageUVs", geoName)
            scn.checkResult_CageUVs = False
            scn.checkResult_All = True
            if scn.checkingAll == False:
                bpy.ops.wm.confirmboxcageuvs("INVOKE_DEFAULT")
        else:
            message = ["Cage UV is ok"]
            remove_item(scn.custom, "CageUVs")
            scn.checkResult_CageUVs = True
            scn.checkResult_All = False
            if scn.checkingAll == False:
                ShowMessageBox(message)

    
        for obj in referenceCages:
            if referenceCages[obj].data != None:
                bpy.data.meshes.remove(referenceCages[obj].data, do_unlink=True)
            else:
                bpy.data.objects.remove(referenceCages[obj], do_unlink=True)

        

        return{"FINISHED"}