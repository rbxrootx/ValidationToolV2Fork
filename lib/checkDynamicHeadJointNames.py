import bpy
import collections



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






class Check_DynamicHeadJointNames(bpy.types.Operator):
    bl_idname = "mesh.checkdynamicheadjointnames"
    bl_label = "Check head joints for unique names"
    bl_description = "Check head joints for unique names"

    
    def execute(self, context):

        dynamicHeadBoneParents = [
            "Head",
            "DynamicHead",
            "R_upperEyeLid",
            "R_lowerEyeLid",
            "L_upperEyeLid",
            "L_lowerEyeLid",
            "jaw",
            "TongueRoot",
            "TongueBase",
        ]

        scn = bpy.context.scene
        armature = scn.Object_for_Check
        if armature == None or armature.type != "ARMATURE":
            message = ["Select armature object"]
            ShowMessageBox(message)
            return{"FINISHED"}
        dynamicHeadBones = []

        for pose_bone in armature.pose.bones:
            if pose_bone.parent != None:
                if pose_bone.parent.name in dynamicHeadBoneParents:
                    if "." in pose_bone.name:
                        name = pose_bone.name.split(".")[0]
                        dynamicHeadBones.append(name)
                    else:
                        dynamicHeadBones.append(pose_bone.name)
                    
        sameName  = len(dynamicHeadBones) != len(set(dynamicHeadBones))
        

        if sameName == True:
            sameNames = [k for k, v in collections.Counter(dynamicHeadBones).items() if v > 1]
            scn.checkResult_DynamicHeadJointNames = False
            scn.checkResult_All = True
            add_item(scn.custom, "Duplicated Bone Name", str(sameNames))
            message = ["Follwoing names are duplicated in Dynamic Head rig."]
            for name in sameNames:
                message.append(name)

        else:
            scn.checkResult_DynamicHeadJointNames = True
            scn.checkResult_All = False
            remove_item(scn.custom, "Duplicated Bone Name")
            message = ["Dynamic Head bone names are ok."]

        if scn.checkingAll == False:
            ShowMessageBox(message)
        return {"FINISHED"}
