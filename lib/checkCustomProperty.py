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


def getChildren(object): 
    children = [] 
    for ob in bpy.data.objects: 
        if ob.parent == object: 
            children.append(ob)
    return children



def getFACsData(Head_Geo):
    frames = []
    RootFaceJoint = []
    currentUVSet = []

    for propertyName in Head_Geo.keys():
        if "Frame" in propertyName:
            if Head_Geo[propertyName] != "":
                frames.append((propertyName, Head_Geo[propertyName]))
            else:
                frames.append((propertyName, None))
        elif "RootFaceJoint" in propertyName:
            RootFaceJoint.append(Head_Geo[propertyName])
        elif "currentUVSet":
            currentUVSet.append(Head_Geo[propertyName])
    
    return frames, RootFaceJoint, currentUVSet




class Check_RootFaceJoint(bpy.types.Operator):
    bl_idname = "mesh.checkrootfacejoint"
    bl_label = "Check Root_joint Properties on Dynamic Head"
    bl_description = "Check root face joint for Dynamic Head settings."


    def checkRootFaceJoint(self, Head_Geo):
        RootFaceJoint = []
        for propertyName in Head_Geo.keys():
            if ("RootFaceJoint" in propertyName):
                if Head_Geo[propertyName] == "":
                    RootFaceJoint.append("")
                else:
                    RootFaceJoint.append(Head_Geo[propertyName])
        
        return RootFaceJoint

    def execute(self, context):
        RootFaceJoint = []
        text_RootFaceJoint = ""



        scn = context.scene
        avatarObj = bpy.context.scene.Object_for_Check
        if avatarObj == None or avatarObj.type != "ARMATURE":
            message = ["Select armature object"]
            ShowMessageBox(message)
            return{"FINISHED"}


        remove_item(scn.custom, "RootFaceJoint")
        avatarObjChildren = getChildren(avatarObj)
        for childObj in avatarObjChildren:
            if childObj.name == "Head_Geo":
                RootFaceJoint = self.checkRootFaceJoint(childObj)
        
        if len(RootFaceJoint) == 0:
            text_RootFaceJoint = "RootFaceJoint property is missing."
            scn.checkResult_RootFaceJoint = False
            scn.checkResult_All = True
            add_item(scn.custom, "RootFaceJoint", text_RootFaceJoint)
        elif (len(RootFaceJoint) != 0) and (RootFaceJoint[0] == ""):
            text_RootFaceJoint = "RootFaceJoint value is missing."
            scn.checkResult_RootFaceJoint = False
            scn.checkResult_All = True
            add_item(scn.custom, "RootFaceJoint", text_RootFaceJoint)
        else:
            remove_item(scn.custom, "RootFaceJoint")
            scn.checkResult_RootFaceJoint = True
            scn.checkResult_All = False
            text_RootFaceJoint += "RootFaceJoint is %s." % RootFaceJoint[0]
        

        message = [text_RootFaceJoint]
        ShowMessageBox(message)

        return {"FINISHED"}


class Check_currentUVSet(bpy.types.Operator):
    bl_idname = "mesh.checkcurrentuvset"
    bl_label = "Check current uv set Properties on Dynamic Head"
    bl_description = "Check current uv set for Dynamic Head settings"


    def checkCurrentUVSet(self, Head_Geo):
        currentUVSet = []
        for propertyName in Head_Geo.keys():
            if ("currentUVSet" in propertyName):
                if Head_Geo[propertyName] == "":
                    currentUVSet.append("")
                else:
                    currentUVSet.append(Head_Geo[propertyName])
        
        return currentUVSet

    def execute(self, context):
        currentUVSet = []
        text_CurrentUVSet = ""

        scn = context.scene
        avatarObj = bpy.context.scene.Object_for_Check
        if avatarObj == None or avatarObj.type != "ARMATURE":
            message = ["Select armature object"]
            ShowMessageBox(message)
            return{"FINISHED"}
        remove_item(scn.custom, "CurrentUVSet")
        avatarObjChildren = getChildren(avatarObj)
        for childObj in avatarObjChildren:
            if childObj.name == "Head_Geo":
                currentUVSet = self.checkCurrentUVSet(childObj)
        
        if len(currentUVSet) == 0:
            text_CurrentUVSet = "currentUVSet property is missing."
            scn.checkResult_CurrentUVSet = False
            scn.checkResult_All = True
            add_item(scn.custom, "CurrentUVSet", text_CurrentUVSet)
        elif (len(currentUVSet) != 0) and (currentUVSet[0] == ""):
            text_CurrentUVSet = "currentUVSet value is missing."
            scn.checkResult_CurrentUVSet = False
            scn.checkResult_All = True
            add_item(scn.custom, "CurrentUVSet", text_CurrentUVSet)
        else:
            remove_item(scn.custom, "CurrentUVSet")
            scn.checkResult_CurrentUVSet = True
            scn.checkResult_All = False
            text_CurrentUVSet += "currentUVSet is %s." % currentUVSet[0]
            
        

        message = [text_CurrentUVSet]

        ShowMessageBox(message)

        return {"FINISHED"}
    
class Check_FacsData(bpy.types.Operator):
    bl_idname = "mesh.checkfacsdata"
    bl_label = "Check for posing and mapping FACS data"
    bl_description = "Check for posing and mapping FACS data"



    baseFacsPoseList = [
        "ChinRaiser",
        "ChinRaiserUpperLip",
        "FlatPucker",
        "Funneler",
        "LowerLipSuck",
        "LipPresser",
        "LipsTogether",
        "MouthLeft",
        "MouthRight",
        "Pucker",
        "UpperLipSuck",
        "LeftCheekPuff",
        "LeftDimpler",
        "LeftLipCornerDown",
        "LeftLowerLipDepressor",
        "LeftLipCornerPuller",
        "LeftLipStretcher",
        "LeftUpperLipRaiser",
        "RightCheekPuff",
        "RightDimpler",
        "RightLipCornerDown",
        "RightLowerLipDepressor",
        "RightLipCornerPuller",
        "RightLipStretcher",
        "RightUpperLipRaiser",
        "JawDrop",
        "JawLeft",
        "JawRight",
        "Corrugator",
        "LeftBrowLowerer",
        "LeftOuterBrowRaiser",
        "LeftNoseWrinkler",
        "LeftInnerBrowRaiser",
        "RightBrowLowerer",
        "RightOuterBrowRaiser",
        "RightInnerBrowRaiser",
        "RightNoseWrinkler",
        "EyesLookDown",
        "EyesLookLeft",
        "EyesLookUp",
        "EyesLookRight",
        "LeftCheekRaiser",
        "LeftEyeUpperLidRaiser",
        "LeftEyeClosed",
        "RightCheekRaiser",
        "RightEyeUpperLidRaiser",
        "RightEyeClosed",
        "TongueDown",
        "TongueOut",
        "TongueUp"
    ]


    def getFacsData(self, Head_Geo):
        facs = []

        for propertyName in Head_Geo.keys():
            if "Frame" in propertyName:
                if Head_Geo[propertyName] != "":
                    facs.append((propertyName, Head_Geo[propertyName]))
                else:
                    facs.append((propertyName, ""))
        return facs
    

    def checkRootFaceJoint(self, Head_Geo):
        RootFaceJoint = []
        for propertyName in Head_Geo.keys():
            if ("RootFaceJoint" in propertyName):
                if Head_Geo[propertyName] == "":
                    RootFaceJoint.append("")
                else:
                    RootFaceJoint.append(Head_Geo[propertyName])
        return RootFaceJoint
    
    def checkCurrentUVSet(self, Head_Geo):
        currentUVSet = []
        for propertyName in Head_Geo.keys():
            if ("currentUVSet" in propertyName):
                if Head_Geo[propertyName] == "":
                    currentUVSet.append("")
                else:
                    currentUVSet.append(Head_Geo[propertyName])
        
        return currentUVSet



    def execute(self, context):
        facsData = []
        text_facsData = ""

        scn = context.scene
        avatarObj = bpy.context.scene.Object_for_Check
        if avatarObj == None or avatarObj.type != "ARMATURE":
            message = ["Select armature object"]
            ShowMessageBox(message)
            return{"FINISHED"}
        remove_item(scn.custom, "FACsData")
        avatarObjChildren = getChildren(avatarObj)
        message = []
        neutralPose = False
        basePoseFound = []
        scn.checkResult_FACSData = True

        for childObj in avatarObjChildren:
            if childObj.name == "Head_Geo":
                # facsData = self.getFacsData(childObj)
                frames, rootFaceJoint, currentUVSet = getFACsData(childObj)



        for frame in frames:
            ##Check if the base pose exist.
            if frame[1] in self.baseFacsPoseList:
                basePoseFound.append(frame[1])
            ##Check FACs data value exist.
            if frame[1] == "":
                text_facsData = "The pose name is missing at %s." % frame[0]
                add_item(scn.custom, "FACsData", text_facsData)
                scn.checkResult_FACSData = False
            if frame[1] == "Neutral":
                neutralPose = True


        if neutralPose == False:
            text_facsData = "Neutral Pose is missing."
            add_item(scn.custom, "FACsData", text_facsData)
            scn.checkResult_FACSData = False
        
        samePoseNames = [k for k, v in collections.Counter(basePoseFound).items() if v > 1]
        for pose in samePoseNames:
            add_item(scn.custom, "FACsData", pose + " is duplicated in FACs data.")
            scn.checkResult_FACSData = False
        
        moreThan3Correctives = []
        for frame in frames:
            frameNameArray =  frame[1].split("_")
            if len(frameNameArray) > 3:
                moreThan3Correctives.append(frame[1])
        
        if len(moreThan3Correctives) != 0:
            for name in moreThan3Correctives:
                add_item(scn.custom, "FACsData", "the pose %s has more than 3 corrective poses." % name)
            scn.checkResult_FACSData = False


        missPosesInCorrectives = {}
        for frame in frames:
            if frame[1] != None:
                if "_" in frame[1]:
                    basePoseNames = frame[1].split("_")
                    missingNames = []
                    for name in basePoseNames:
                        if name not in basePoseFound:
                            missingNames.append(name)
                    if missingNames != []:
                        missPosesInCorrectives[frame[1]] = missingNames
        
        if len(missPosesInCorrectives) != 0:
            for pose in missPosesInCorrectives:
                for name in missPosesInCorrectives[pose]:
                    add_item(scn.custom, "FACsData", "the pose %s is used in corrective pose %s, but it was not found." % (name, pose))
            scn.checkResult_FACSData = False


        if len(rootFaceJoint) == 0:
            text_RootFaceJoint = "RootFaceJoint property slot is missing."
            add_item(scn.custom, "FACsData", text_RootFaceJoint)
            scn.checkResult_FACSData = False
        elif (len(rootFaceJoint) != 0) and (rootFaceJoint[0] == ""):
            text_RootFaceJoint = "RootFaceJoint value is missing."
            add_item(scn.custom, "FACsData", text_RootFaceJoint)
            scn.checkResult_FACSData = False


        if len(currentUVSet) == 0:
            text_CurrentUVSet = "currentUVSet property slot is missing."
            add_item(scn.custom, "FACsData", text_CurrentUVSet)
            scn.checkResult_FACSData = False
        elif (len(currentUVSet) != 0) and (currentUVSet[0] == ""):
            text_CurrentUVSet = "currentUVSet value is missing."
            add_item(scn.custom, "FACsData", text_CurrentUVSet)
            scn.checkResult_FACSData = False

        if len(basePoseFound) < 50:
            message.append("Found only %s base poses. Your character may not be able to express itself." % str(len(basePoseFound)))
        elif len(basePoseFound) > 50:
            message.append("Found %s base poses. Your character may have duplicated base poses." % str(len(basePoseFound)))


        if scn.checkResult_FACSData == False:
            scn.checkResult_All = True
            message.append("FACs Data has some issues")
            message.append("Check the detailed infomation in the output window.")
        else:
            scn.checkResult_FACSData = True
            scn.checkResult_All = False
            remove_item(scn.custom, "FACsData")
            text_facsData = str(len(facsData)) + " FACS data is found on this avatar."
            # message.append("Found %s frames FACs poses. FACs data is ok." % str(len(frames)))
            message.append("FACs data is ok.")
        
        if scn.checkingAll == False:
            ShowMessageBox(message)

        return {"FINISHED"}