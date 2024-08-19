from os import error
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


def getChildren(object): 
    children = [] 
    for ob in bpy.data.objects: 
        if ob.parent == object: 
            children.append(ob)
    return children


def getAllGeometries(armatureChildren, checkMode):
    checkGeometries = []
    if checkMode == '0':
        for obj in armatureChildren:
            if "_Geo" in obj.name and obj.type == "MESH":
                checkGeometries.append(obj)
                outerCageName = obj.name.split("_Geo")[0] + "_OuterCage"
                try:
                    outerCage = bpy.data.objects[outerCageName]
                    checkGeometries.append(outerCage)
                except:
                    pass
            else:
                if obj.type == "MESH":
                    checkGeometries.append(obj)
    else:
        for obj in armatureChildren:
            if "_Att" not in obj.name and obj.type == "MESH":
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
            else:
                if obj.type == "MESH":
                    checkGeometries.append(obj)
    

    return checkGeometries





def checkKeyframes(avatarObj, objs):   
    objectsWithKeys = []

    animData = avatarObj.animation_data
    dynamicHeadBones = getDynamicHeadBoneList(avatarObj)
    errorBones = []

    if animData != None:
        fcurves = animData.action.fcurves
        for fc in fcurves:
            fc.update()
            kps = []
            path = str(fc.data_path)
            bone_name = path.split('"')[1]
            property_name = path.split('.')[-1]
            if bone_name not in dynamicHeadBones:
                keyframedAttributeName = fc.data_path.split(".")[-1]
                if keyframedAttributeName == "rotation_quaternion":
                    keyframedAttributeName = "rotation"
                if (bone_name, keyframedAttributeName) not in objectsWithKeys:
                    objectsWithKeys.append((bone_name, keyframedAttributeName))

    for obj in objs:
        if obj.animation_data != None:
            location = False
            rotation = False
            scale = False
            for fcu in obj.animation_data.action.fcurves:
                if "location" in fcu.data_path:
                    if location == False:
                        location = True
                        objectsWithKeys.append((obj.name, fcu.data_path))
                elif "rotation" in fcu.data_path:
                    if rotation == False:
                        rotation = True
                        objectsWithKeys.append((obj.name, fcu.data_path))
                elif "scale" in fcu.data_path:
                    if scale == False:
                        scale = True
                        objectsWithKeys.append((obj.name, fcu.data_path))
                else:
                    objectsWithKeys.append((obj.name, fcu.data_path))
    if len(objectsWithKeys) != 0:
        return  objectsWithKeys
    else:
        return  True

def deleteKeyFrames(objList, avatarObj):
    result = False
    if len(objList) != 0:
        for name in objList:
            if name != "":
                try:
                    obj = bpy.data.objects[name]
                    if obj.animation_data != 0:
                        obj.animation_data_clear()
                        result = True
                except:
                    animData = avatarObj.animation_data
                    fcurves = animData.action.fcurves
                    path = 'pose.bones["%s"]' % name
                    for fc in fcurves:
                        if fc.data_path.startswith(path):
                            action = fc.id_data
                            action.fcurves.remove(fc)
                    result = True

        for name in objList:
            if name != "":
                try:
                    obj = bpy.data.objects[name]
                    if obj.animation_data:
                        result = False
                    else:
                        result = True
                except:
                    pass
                
    return result


def getDynamicHeadBoneList(armature):
    dynamicHeadBones = []


    allBones = armature.data.bones
    for bone in allBones:
        parentBones = bone.parent_recursive
        for parentBone in parentBones:
            if "DynamicHead" in parentBone.name:
                dynamicHeadBones.append(bone.name)
        ##dynamic head joint can be keyframed
        if bone.name == "DynamicHead":
           dynamicHeadBones.append(bone.name) 
    return dynamicHeadBones



def getFACsPoses(avatarObjChildren):
    frames = []
    Head_Geo = None
    for childObj in avatarObjChildren:
        if childObj.name == "Head_Geo":
            Head_Geo = childObj

    for propertyName in Head_Geo.keys():
        if "Frame" in propertyName:
            if Head_Geo[propertyName] != "":
                frameNum = propertyName.split("Frame")[1]
                frames.append(int(frameNum))
    
    if frames != []:
        frames.remove(0)
    return frames



class ConfirmBox_KeyFrame(bpy.types.Operator):
    bl_idname = "wm.confirmboxkeyframe"
    bl_label =  "Keyframe Check"

    def execute(self, context):
        scn = context.scene
        avatarObj = bpy.context.scene.Object_for_Check
        objectsWithKeysList = scn.objectsWithKeys.split(",")
        result = deleteKeyFrames(objectsWithKeysList, avatarObj)      
        bpy.data.orphans_purge()
        if result == True:
            scn.checkResult_KeyFrames = True
            remove_item(scn.custom, "KeyFrames")

        return {'FINISHED'}
    
    def draw(self, context):
        scn = context.scene
        msg = ["There are extra keyframes on some objects.", "Click OK to remove keyframes."]
        for line in msg:
            self.layout.label(text= line)

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self)




class Check_KeyFrames(bpy.types.Operator):
    bl_idname = "mesh.checkkeyframes"
    bl_label = "Check for non-FACS related keyframes"
    bl_description = "Check for non-FACS related keyframes"


    def execute(self, context):
        result = True
        scn = context.scene
        remove_item(scn.custom, "KeyFrames")
        scn.objectsWithKeys = ""
        avatarObj = bpy.context.scene.Object_for_Check
        if avatarObj == None or avatarObj.type != "ARMATURE":
            message = ["Select armature object"]
            ShowMessageBox(message)
            return{"FINISHED"}
        avatarObjChildren = getChildren(avatarObj)
        avatarObjChildren.append(avatarObj)
        checkGeometries = getAllGeometries(avatarObjChildren, scn.checkMode)
        message = []

        result = checkKeyframes(avatarObj, checkGeometries)

        if result != True:
            scn.checkResult_KeyFrames = False
            scn.checkResult_All = True
            objectsWithKeyNameString = ""

            for obj in result:
                text = "The keyframe is at " + str(obj[1] +  " on " + obj[0]) + "."
                add_item(scn.custom, "KeyFrames", text)
                objectsWithKeyNameString += obj[0]
                objectsWithKeyNameString += ","
            objectsWithKeyNameString = objectsWithKeyNameString[0:-1]
            scn.objectsWithKeys = objectsWithKeyNameString
            
            if scn.checkingAll == False:
                bpy.ops.wm.confirmboxkeyframe("INVOKE_DEFAULT")
        else:
            scn.checkResult_KeyFrames = True
            scn.checkResult_All = False
            if scn.checkMode == "0":
                message.append("KeyFrame check is ok.")
            else:
                message.append("KeyFrame check is ok.")
            remove_item(scn.custom, "KeyFrames")
        
        if scn.checkingAll == False and result == True:
            ShowMessageBox(message)

        return{"FINISHED"}
