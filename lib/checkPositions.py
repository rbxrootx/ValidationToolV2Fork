import bpy
import mathutils
from checkVisibility import set_Visibility, set_originalVisibility



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


def checkIfOutofBoundary(avatarObj, meshObjects):
    
    scale = avatarObj.scale
    boundarySizeX = 4/(1.0/scale[0])
    boundarySizeY = 4/(1.0/scale[1])
    boundarySizeZ = 4/(1.0/scale[2])

    meshesWithVerticesOutsideBoundary = []

    for obj in meshObjects:
        mesh = obj.data

        for v in mesh.vertices:
            worldCoords = obj.matrix_world @ v.co
            if (worldCoords[0] < -boundarySizeX or worldCoords[0] > boundarySizeX or
                worldCoords[1] < -boundarySizeY or worldCoords[1] > boundarySizeY or
                worldCoords[2] < -boundarySizeZ or worldCoords[2] > boundarySizeZ):
                meshesWithVerticesOutsideBoundary.append(obj.name)
                break

    if len(meshesWithVerticesOutsideBoundary) != 0:
        return meshesWithVerticesOutsideBoundary
    else:
        return True
    


def missPositionedBones(armature):
    possibleMissPositionedBone = []

    if armature and armature.type == 'ARMATURE':
        for pb in armature.pose.bones:
            tail = armature.matrix_world @ pb.tail 
            head = armature.matrix_world @ pb.head

    if armature and armature.type == 'ARMATURE':
        for bone in armature.pose.bones:
            tail_location = armature.matrix_world @ bone.tail 
            head_location = armature.matrix_world @ bone.head
            if "right" in bone.name.lower():
                if not head_location.x < 0.000001:
                    possibleMissPositionedBone.append((bone.name + "_Head"))
                    # print(bone.name, "Head Location: ", head_location)
                if not tail_location.x < 0.000001:
                    possibleMissPositionedBone.append((bone.name + "_Tail"))
                    # print(bone.name, "Tail Location: ", tail_location)
            if "left" in bone.name.lower():
                if not head_location.x > -0.000009:
                    possibleMissPositionedBone.append((bone.name + "_Head"))
    #                print(bone.name, "Head Location: ", head_location)
                if not tail_location.x > -0.000009:
                    possibleMissPositionedBone.append((bone.name + "_Tail"))
    #                print(bone.name, "Tail Location: ", tail_location)
    
    if len(possibleMissPositionedBone) != 0:
        return possibleMissPositionedBone
    else:
        return True
    

def bonePositionCheck(armature):
    errors = {}
    rootBone = False
    humanoidRootNode = False
    if armature and armature.type == 'ARMATURE':
        for bone in armature.data.bones:
            if bone.name == "Root":
                rootBone = True
                head_location = bone.head
                if not head_location == mathutils.Vector((0.0, 0.0, 0.0)):
                    errors["wrongPos"] = str(round(head_location[0], 2)) + " , " +  str(round(head_location[1], 2)) + " , " + str(round(head_location[2], 2))
            if bone.name == "HumanoidRootNode":
                humanoidRootNode = True
       
    if not rootBone:
       errors["missing"] = "Root bone is missing."

    if not humanoidRootNode:
       errors["missing_humanoid"] = "humanoidRootNode bone is missing."                      
                    

    if len(errors) != 0:
        return errors
    else:
        return True



class Check_Positions(bpy.types.Operator):
    bl_idname = "mesh.checkpositions"
    bl_label = "Check if the assets is within a maximum size"
    bl_description = "Check if the assets is within a maximum size"
    originalVisibilitySettings = {}

    def execute(self, context):

        scn = context.scene
        avatarObj = bpy.context.scene.Object_for_Check
        if avatarObj == None or avatarObj.type != "ARMATURE":
            message = ["Select armature object"]
            ShowMessageBox(message)
            return{"FINISHED"}
        self.originalVisibilitySettings = set_Visibility()
        avatarObjChildren = getChildren(avatarObj)
        cages = getCages(avatarObjChildren, scn.checkMode)

        result = checkIfOutofBoundary(avatarObj, cages)
        if result != True:
            objsOutsideofBoundary = result
            message = ["Some meshes are outside of maximum size.", "Check the details."]
            for name in objsOutsideofBoundary:
                add_item(scn.custom, "MaxSize", name)
                scn.checkResult_Positions = False
                scn.checkResult_All = True
        else:
            remove_item(scn.custom, "MaxSize")
            message = ["Assets are within the maximum size."]
            scn.checkResult_Positions = True
            scn.checkResult_All = False
        if scn.checkingAll == False:
            ShowMessageBox(message)
        set_originalVisibility(self.originalVisibilitySettings)
        return{"FINISHED"}


class Check_JointPositions(bpy.types.Operator):
    bl_idname = "mesh.checkjointpositions"
    bl_label = "Check if joints are at the correct positions"
    bl_description = "Check if joints are at the correct positions"
    originalVisibilitySettings = {}

    def execute(self, context):

        scn = context.scene
        remove_item(scn.custom, "JointPosition")
        avatarObj = bpy.context.scene.Object_for_Check
        if avatarObj == None or avatarObj.type != "ARMATURE":
            message = ["Select armature object"]
            ShowMessageBox(message)
            return{"FINISHED"}
        self.originalVisibilitySettings = set_Visibility()
        result_LRCheck = missPositionedBones(avatarObj)
        result_RootPos = bonePositionCheck(avatarObj)


        if (result_LRCheck != True) or (result_RootPos != True):
            message = ["Some joints are possibly at wrong position", "Check the details."]
            if result_LRCheck != True:
                wrongLRPos = result_LRCheck
                for msg in wrongLRPos:
                    add_item(scn.custom, "JointPosition", msg + " is in an incorrect or opposite position.")
            if result_RootPos != True:
                for key in result_RootPos.keys():
                    if key == "wrongPos":
                        add_item(scn.custom, "JointPosition", "Root bone is at wrong position (should be 0, 0, 0). Currently: " + result_RootPos[key])
                    elif key == "missing":
                        add_item(scn.custom, "JointPosition", "Root bone is missing or wrong naming convention.")
                    elif key == "missing_humanoid":
                        add_item(scn.custom, "JointPosition", "humanoidRootNode bone is missing or wrong naming convention.")
            scn.checkResult_JointPositions = False
            scn.checkResult_All = True
        else:
            remove_item(scn.custom, "JointPosition")
            message = ["Joints positions are ok."]
            scn.checkResult_JointPositions = True
            scn.checkResult_All = False
        if scn.checkingAll == False:
            ShowMessageBox(message)
        set_originalVisibility(self.originalVisibilitySettings)
        return{"FINISHED"}



