import bpy
from mathutils.bvhtree import BVHTree
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



def checkSkinnedBones(geo, armature):
    IsHeadMesh = False
    vertexgroup = geo.vertex_groups
    for group in vertexgroup:
        try:
            allParents = armature.data.bones[group.name].parent_recursive
            for parentBone in allParents:
                if "DynamicHead" in parentBone.name or "Head" in parentBone.name:
                    IsHeadMesh = True
        except:
            pass

    return IsHeadMesh


def getAllGeometries(avatarObj, checkMode):

    excludeGeoList = [
        "LeftEye_Geo",
        "LeftLash_Geo",
        "RightEye_Geo",
        "RightLash_Geo",
        "Tongue_Geo",
        "UpperTeeth_Geo",
        "LowerTeeth_Geo",
    ]

    children = [] 
    for ob in bpy.data.objects: 
        if ob.parent == avatarObj: 
            children.append(ob)

    checkGeometries = []
    if checkMode == '0':
        for obj in children:
            if "_Geo" in obj.name:
                IsDynamicHeadMesh = checkSkinnedBones(obj, avatarObj)
                if IsDynamicHeadMesh == False:
                    checkGeometries.append(obj)
                elif obj.name == "Head_Geo":
                    checkGeometries.append(obj)
    else:
        for obj in children:
            if "_Att" not in obj.name and "_Geo" not in obj.name:
                checkGeometries.append(obj)
    

    return checkGeometries






def checkIntersection(checkType, geo,cehckMode):
    outerCage = None
    innerCage = None
    bvhtree_Geo = None
    collision_Object = None
    list = []
    
    
    if cehckMode == "0":
        outerCage = bpy.data.objects[geo.name.replace("_Geo", "_OuterCage")]
    else:
        outerCage = bpy.data.objects[geo.name + "_OuterCage"]
        innerCage = bpy.data.objects[geo.name + "_InnerCage"]
    
    bpy.context.view_layer.objects.active = geo
    bpy.ops.object.editmode_toggle()
    bpy.ops.mesh.select_all(action='DESELECT')
    bpy.ops.object.editmode_toggle()
    


    depsgraph_1 = bpy.context.evaluated_depsgraph_get()

    if cehckMode == "0":
        collision_Object = outerCage
        bvhtree_Out = BVHTree.FromObject(collision_Object, depsgraph_1)
        depsgraph = bpy.context.evaluated_depsgraph_get()
        bvhtree_Clothing = BVHTree.FromObject(geo, depsgraph)
    else: 
        if checkType == "Inner":
            collision_Object = innerCage
        else:
            collision_Object = outerCage

        bvhtree_Out = BVHTree.FromObject(collision_Object, depsgraph_1)
        depsgraph = bpy.context.evaluated_depsgraph_get()
        bvhtree_Clothing = BVHTree.FromObject(geo, depsgraph) 


    list = bvhtree_Out.overlap(bvhtree_Clothing)
   
    
    if len(list) != 0:
        return list
    else:
        return True
    


class Fix_InterSections_Inner(bpy.types.Operator):
    bl_idname = "mesh.fixintersectionsinner"
    bl_label = "Intersection Fix Inner"
    bl_description = "Check for any intersections between cage and asset mesh. If intersections are detected, the mesh face is selected in the viewport"
    originalVisibilitySettings = {}
    

    checkType: bpy.props.StringProperty(name = 'text', default = "Check Intersections Outer")

    def execute(self, context):
        scn = context.scene
        avatarObj = bpy.context.scene.Object_for_Check
        if avatarObj == None or avatarObj.type != "ARMATURE":
            message = ["Select armature object"]
            ShowMessageBox(message)
            return{"FINISHED"}
        self.originalVisibilitySettings = set_Visibility()
        ensureObjectModeandActive(avatarObj) 
        checkGeoList = getAllGeometries(avatarObj, scn.checkMode)
        result = True

        if len(checkGeoList) != 0:
            for geo in checkGeoList:
                interSectionResult = checkIntersection(self.checkType, geo, scn.checkMode)
            
                if interSectionResult == True:
                    result = True
                else:
                    result = False
                    for f in interSectionResult:
                        geo.data.polygons[f[1]].select = True
            

            if result == False:
                if self.checkType == "Inner":
                    scn.checkResult_InterSections_IN = False
                else:
                    scn.checkResult_InterSections_OUT = False
                bpy.ops.object.select_all(action='DESELECT')
                for i in checkGeoList:
                    clothingObj = bpy.data.objects[i.name]
                    clothingObj.select_set(True)
                    bpy.context.view_layer.objects.active = bpy.data.objects[i.name]
                bpy.ops.object.editmode_toggle()
                message = ["Possible intersections were found. Check selected polygons."]
                ShowMessageBox(message)
            else:
                if self.checkType == "Inner":
                    scn.checkResult_InterSections_IN = True
                else:
                    scn.checkResult_InterSections_OUT = True
                message = ["No intersections were found."]
                ShowMessageBox(message)
                    


            set_originalVisibility(self.originalVisibilitySettings)
            return {"FINISHED"}
        else:
            if scn.checkMode == "0":
                confirmmessage = ["No avatar geometries were found in the scene"]
            else:
                confirmmessage = ["No cloth geometries were found in the scene"]
            ShowMessageBox(confirmmessage)
            set_originalVisibility(self.originalVisibilitySettings)
            return{"FINISHED"}