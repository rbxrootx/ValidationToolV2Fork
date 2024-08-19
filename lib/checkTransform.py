import bpy
import math
from checkVisibility import set_Visibility, set_originalVisibility
from ensureObjectActive import ensureObjectModeandActive



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


def getGeometries(armatureChildren, checkMode):
    checkGeometries = []
    if checkMode == '0':
        for obj in armatureChildren:
            if "_Geo" in obj.name:
                checkGeometries.append(obj)
                outerCageName = obj.name.split("_Geo")[0] + "_OuterCage"
                try:
                    outerCage = bpy.data.objects[outerCageName]
                    checkGeometries.append(outerCage)
                except:
                    pass
    else:
        for obj in armatureChildren:
            if "_Att" not in obj.name:
                checkGeometries.append(obj)
                outerCageName = obj.name + "_OuterCage"
                try:
                    outerCage = bpy.data.objects[outerCageName]
                    checkGeometries.append(outerCage)
                except:
                    pass

                innerCageName = obj.name + "_InnerCage"
                try:
                    innerCage = bpy.data.objects[innerCageName]
                    checkGeometries.append(innerCage)
                except:
                    pass
    

    return checkGeometries




def checkTransform(checkGeometries):
    wrongPositionGeos = {}

    for checkGeometry in checkGeometries: 
        wrongValues = []
        lx = round(checkGeometry.location[0], 3)
        if lx != 0.000:
            wrongValues.append((str(lx) + " at location X"))

        ly = round(checkGeometry.location[1], 3)
        if ly != 0.000:
            wrongValues.append((str(ly) + " at location Y"))

        lz = round(checkGeometry.location[2], 3)
        if lz != 0.000:
            wrongValues.append((str(lz) + " at location Z"))
            

        rx = round(checkGeometry.rotation_euler[0], 3)
        if rx != 0.000:
            wrongValues.append((str(round(math.degrees(rx),1)) + " at rotation X"))

        ry = round(checkGeometry.rotation_euler[1], 3)
        if ry != 0.000:
            wrongValues.append((str(round(math.degrees(ry), 1)) + " at rotation Y"))

        rz = round(checkGeometry.rotation_euler[2], 3)
        if rz != 0.000:
            wrongValues.append((str(round(math.degrees(rz), 1)) + " at rotation Z"))
            
            
        sx = round(checkGeometry.scale[0],3)
        if sx != 1.000:
            wrongValues.append((str(sx) + " at scale X"))

        sy = round(checkGeometry.scale[1], 3)
        if sy != 1.000:
            wrongValues.append((str(sy) + " at scale Y"))

        sz = round(checkGeometry.scale[2], 3)
        if sz != 1.000:
            wrongValues.append((str(sz) + " at scale Z"))

        if len(wrongValues) != 0:
            wrongPositionGeos[checkGeometry] = wrongValues
        
        
    if len(wrongPositionGeos) != 0:
        return wrongPositionGeos
    else:
        return True


def deleteTransform(wrongObjsList):
    failed = []
    if len(wrongObjsList)  != 0:
        for obj in wrongObjsList:
            targetObj = bpy.data.objects[obj]
            targetObj.select_set(True)
            bpy.context.view_layer.objects.active = targetObj
            try:
                bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
            except:
                failed.appened(obj)
    if len(failed) == 0:
        return True
    else:
        return False



class ConfirmBox_Transform(bpy.types.Operator):
    bl_idname = "wm.confirmboxtransform"
    bl_label =  "Transform check"
    originalVisibilitySettings = {}


    def deleteTransform(self, wrongObjsList):
        failed = []
        if len(wrongObjsList)  != 0:
            print("Deleting")
            for obj in wrongObjsList:
                clothingObj = bpy.data.objects[obj]
                clothingObj.select_set(True)
                bpy.context.view_layer.objects.active = clothingObj
                try:
                    bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
                except:
                    failed.appened(obj)
        if len(failed) == 0:
            return True
        else:
            return False
    

    def execute(self, context):
        scn = context.scene
        self.originalVisibilitySettings = set_Visibility()
        bpy.ops.object.mode_set(mode='OBJECT')
        wrongObjsList = bpy.types.Scene.wrongTransformObjects.split(",")
        result = self.deleteTransform(wrongObjsList)
        if result == True:
            scn.checkResult_Transform = True
            remove_item(scn.custom, "Transform")
        else:
            scn.checkResult_Transform = False
        set_originalVisibility(self.originalVisibilitySettings)
        return {'FINISHED'}
    
    def draw(self, context):
        msg = ["Some objects have values on transforms.", "Click OK to freeze the object transforms.", "This may result in a change to your rig."]
        for line in msg:
            self.layout.label(text= line)

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self)


class Fix_Transform(bpy.types.Operator):
    bl_idname = "mesh.transform"
    bl_label = "Transform Fix"
    bl_description = "Check if geometries have a transform values"
    originalVisibilitySettings = {}

    
    def execute(self, context):
        scn = context.scene
        armature = scn.Object_for_Check
        if armature == None or armature.type != "ARMATURE":
            message = ["Select armature object"]
            ShowMessageBox(message)
            return{"FINISHED"}
        self.originalVisibilitySettings = set_Visibility()
        armatureChildren = getChildren(armature)
        message = []
        remove_item(scn.custom, "Transform")

        checkGeometries = getGeometries(armatureChildren, scn.checkMode)

        result = checkTransform(checkGeometries)

        if result == True:
            scn.checkResult_Transform = True
            if scn.checkingAll == False:
                message = ["Transform is ok."]
                ShowMessageBox(message)
        else:
            scn.checkResult_Transform = False
            scn.checkResult_All = True
            wrongPosObjNameString = ""
            for obj in result:
                for err in result[obj]:
                    text = "Unexpected transform values for %s (should be frozen at 0.0): %s " % (obj.name, err)
                    add_item(scn.custom, "Transform", text)
                wrongPosObjNameString += obj.name
                wrongPosObjNameString += ","
            wrongPosObjNameString = wrongPosObjNameString[0:-1]
            bpy.types.Scene.wrongTransformObjects = wrongPosObjNameString
            if scn.checkingAll == False:
                bpy.ops.wm.confirmboxtransform("INVOKE_DEFAULT")
            
        set_originalVisibility(self.originalVisibilitySettings)
        return {"FINISHED"}
