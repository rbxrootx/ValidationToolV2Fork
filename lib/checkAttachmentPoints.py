import bpy
from checkVisibility import set_Visibility, set_originalVisibility
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


def getAttachmentPoints(armature):
    children = []
    attachmentPoints = []

    for ob in bpy.data.objects: 
        if "_Att" in ob.name and ob.type == "MESH":
            attachmentPoints.append(ob)
    

    return attachmentPoints



def checkAttachmentPoints(armature):
    objs =  getAttachmentPoints(armature)

    wrongPositions = []
    wrongNames = []
    attachmentCheck = False

    for obj in objs:
        if obj.name.endswith("_Att"):
            attachPoint = obj
            attachPoint_Name = obj.name
            parentBone = obj.parent_bone
            
            if attachPoint_Name == "FaceFront_Att":
                if parentBone != "Head":
                    wrongPositions.append([attachPoint.name, parentBone, "Head"])
            elif attachPoint_Name == "Hat_Att":
                if parentBone != "Head":
                    wrongPositions.append([attachPoint.name, parentBone, "Head"])
            elif attachPoint_Name == "Hair_Att":
                if parentBone != "Head":
                    wrongPositions.append([attachPoint.name, parentBone, "Head"])
            elif attachPoint_Name == "FaceCenter_Att":
                if parentBone != "Head":
                    wrongPositions.append([attachPoint.name, parentBone, "Head"])
            elif attachPoint_Name == "LeftGrip_Att":
                if parentBone != "LeftHand":
                    wrongPositions.append([attachPoint, parentBone, "LeftHand"])
            elif attachPoint_Name == "LeftShoulder_Att":
                if parentBone != "LeftUpperArm":
                    wrongPositions.append([attachPoint.name, parentBone, "LeftUpperArm"])
            elif attachPoint_Name == "RightGrip_Att":
                if parentBone != "RightHand":
                    wrongPositions.append([attachPoint.name, parentBone, "RightHand"])
            elif attachPoint_Name == "RightShoulder_Att":
                if parentBone != "RightUpperArm":
                    wrongPositions.append([attachPoint.name, parentBone, "RightUpperArm"])
            elif attachPoint_Name == "BodyFront_Att":
                if parentBone != "UpperTorso":
                    wrongPositions.append([attachPoint.name, parentBone, "UpperTorso"])
            elif attachPoint_Name == "BodyBack_Att":
                if parentBone != "UpperTorso":
                    wrongPositions.append([attachPoint.name, parentBone, "UpperTorso"])
            elif attachPoint_Name == "LeftCollar_Att":
                if parentBone != "UpperTorso":
                    wrongPositions.append([attachPoint.name, parentBone, "UpperTorso"])
            elif attachPoint_Name == "Neck_Att":
                if parentBone != "UpperTorso":
                    wrongPositions.append([attachPoint.name, parentBone, "UpperTorso"])
            elif attachPoint_Name == "RightCollar_Att":
                if parentBone != "UpperTorso":
                    wrongPositions.append([attachPoint.name, parentBone, "UpperTorso"])
            elif attachPoint_Name == "LeftFoot_Att":
                if parentBone != "LeftFoot":
                    wrongPositions.append([attachPoint.name, parentBone, "LeftFoot"])
            elif attachPoint_Name == "RightFoot_Att":
                if parentBone != "RightFoot":
                    wrongPositions.append([attachPoint.name, parentBone, "RightFoot"])
            elif attachPoint_Name == "WaistFront_Att":
                if parentBone != "LowerTorso":
                    wrongPositions.append([attachPoint.name, parentBone, "LowerTorso"])
            elif attachPoint_Name == "WaistBack_Att":
                if parentBone != "LowerTorso":
                    wrongPositions.append([attachPoint.name, parentBone, "LowerTorso"])
            elif attachPoint_Name == "WaistCenter_Att":
                if  parentBone != "LowerTorso":
                    wrongPositions.append([attachPoint.name, parentBone, "LowerTorso"])
            elif attachPoint_Name == "Root_Att":
                if parentBone != "Root":
                    wrongPositions.append([attachPoint.name, parentBone, "Root"])
            else:
                wrongNames.append([attachPoint.name, parentBone])

    if len(wrongPositions) != 0 or len(wrongNames) != 0:
        return [wrongPositions, wrongNames]
    else:
        return True

def getAttachmentPointAndKeepPos(wrongPositionsAttachmentList):
    attachmentPoints = {}

    for obj in bpy.data.objects:
        if "_Att" in obj.name:
            obj.hide_viewport = False
    
    
    for name in wrongPositionsAttachmentList.split(","):
        try:
            attPoint = bpy.data.objects[name.split(":")[0]]
            attachmentPoints[attPoint] = name.split(":")[1]
            obj.select_set(True)
            bpy.ops.object.parent_clear(type='CLEAR_KEEP_TRANSFORM')
            obj.select_set(False)
        except:
            pass
    
    return attachmentPoints




def reparentAttachmentPoints(armature, ap, correctBoneName):

    bpy.ops.object.origin_set(type='ORIGIN_GEOMETRY', center='MEDIAN')
    obj = bpy.data.objects[ap.name]

    newobj = obj.copy()
    newobj.data = obj.data.copy()
    newobj.name = obj.name + "_dup"
    bpy.context.collection.objects.link(newobj)
    
    obj.parent = armature
    obj.parent_bone = correctBoneName
    
    obj.constraints.new('COPY_TRANSFORMS')
    obj.constraints.new('COPY_ROTATION')
    for const in obj.constraints:
        const.target = newobj
    
    constraints = obj.constraints
    for const in constraints:
        bpy.context.view_layer.objects.active = obj
        bpy.ops.constraint.apply(constraint=const.name, owner='OBJECT')
    
    for obj in bpy.data.objects:
        if "_Att_dup" in obj.name:
            bpy.data.objects.remove(obj, do_unlink=True)


class ConfirmBox_AttachmentPoints(bpy.types.Operator):
    bl_idname = "wm.confirmboxattpt"
    bl_label =  "Attachment point Check"


    def execute(self, context):
        scn = context.scene
        armature = bpy.context.scene.Object_for_Check
        if len(scn.wrongPositions_Attachment) != 0:
            attachmentPoints = getAttachmentPointAndKeepPos(scn.wrongPositions_Attachment)
            for key in attachmentPoints.keys():
                reparentAttachmentPoints(armature, key, attachmentPoints[key])
            result = checkAttachmentPoints(scn.Object_for_Check)
        else:
            if scn.wrongPositions_Attachment == "" and scn.wrongNames_Attachment == "":
                result = True
            else:
                result = False 
    
        if result == True:
            scn.checkResult_AttPoints = True
            scn.checkResult_All = False
            remove_item(scn.custom, "AttPoint_Position")
            remove_item(scn.custom, "AttPoint_Name")
        else:
            scn.checkResult_AttPoints = False
            scn.checkResult_All = True
              
        return {'FINISHED'}
    
    def draw(self, context):
        scn = context.scene
        message = []
        if len(scn.wrongPositions_Attachment) != 0:
            message.append("There are wrong position attachment points.")
                
        if len(scn.wrongNames_Attachment) != 0:
            message.append("There are wrong name attachments points.")

        message.append("Would you like to fix wrong parented attachment?.")
        message.append("Attachments will be processed based on their name.")
        for line in message:
            self.layout.label(text= line)

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self)



class Check_AttPoints(bpy.types.Operator):
    bl_idname = "mesh.checkattpoints"
    bl_label = "Check attachment points"
    bl_description = "Check attachment point hierarchy in the armature"
    originalVisibilitySettings = {}


    def execute(self, context):
        scn = context.scene
        remove_item(scn.custom, "AttPoint_Position")
        remove_item(scn.custom, "AttPoint_Name")
        wrongPosition_AttNames = ""
        wrongName_AttNames = "" 
        self.originalVisibilitySettings = set_Visibility()
        armature = bpy.context.scene.Object_for_Check
        if armature != None:
            result = checkAttachmentPoints(armature)
            if result != True:
                for wrongPos_Att in  result[0]:
                    wrongPosition_AttNames += wrongPos_Att[0] + ":" + wrongPos_Att[2]
                    wrongPosition_AttNames += ","
                    add_item(scn.custom, "AttPoint_Position", wrongPos_Att[0])
                if wrongPosition_AttNames != "":
                    scn.wrongPositions_Attachment = wrongPosition_AttNames


                for worngName_Att in result[1]:
                    wrongName_AttNames += worngName_Att[0]
                    wrongName_AttNames += ","
                    add_item(scn.custom, "AttPoint_Name", worngName_Att[0])
                # if wrongName_AttNames != "":
                #     scn.wrongNames_Attachment = wrongName_AttNames[0:-1]


                scn.checkResult_AttPoints = False
                scn.checkResult_All = True
                # print(scn.wrongPositions_Attachment)
                if scn.checkingAll == False:
                    bpy.ops.wm.confirmboxattpt("INVOKE_DEFAULT")
            else:
                message = ["Attachment points are ok."]
                if scn.checkingAll == False:
                    ShowMessageBox(message)
                remove_item(scn.custom, "AttPoint_Position")
                remove_item(scn.custom, "AttPoint_Name")
                scn.checkResult_AttPoints = True
                scn.checkResult_All = False
        else:
            if scn.checkingAll == False:
                confirmmessage = ["Select one armature."]
                ShowMessageBox(confirmmessage)


        set_originalVisibility(self.originalVisibilitySettings)
        return {"FINISHED"}