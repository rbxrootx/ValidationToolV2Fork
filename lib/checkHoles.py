import bpy
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


def getAllGeometries(armatureChildren, checkMode):
    checkGeometries = []
    avatarObj = bpy.context.scene.Object_for_Check
    if checkMode == '0':
        for obj in armatureChildren:
            if ("_Geo" in obj.name) and ("_Att" not in obj.name):
                checkGeometries.append(obj)
    else:
        for obj in armatureChildren:
            if ("_Att" not in obj.name) and (obj != avatarObj):
                checkGeometries.append(obj)

    return checkGeometries

def checkSkinnedBones(geo, armature):
    IsHeadMesh = False
    vertexgroup = geo.vertex_groups
    for group in vertexgroup:
        try:
            allParents = armature.data.bones[group.name].parent_recursive
            for parentBone in allParents:
                if "DynamicHead" in parentBone.name:
                    IsHeadMesh = True
        except:
            pass

    return IsHeadMesh


def deselectObjects(checkGeometries):
    for obj in checkGeometries:
        bpy.context.view_layer.objects.active = obj
        obj.select_set(True)
        
        bpy.ops.object.mode_set(mode='EDIT')
        bpy.context.tool_settings.mesh_select_mode[0] = True
        bpy.context.tool_settings.mesh_select_mode[1] = False
        bpy.context.tool_settings.mesh_select_mode[2] = False

        bpy.ops.mesh.select_all(action='DESELECT')
        
        bpy.ops.object.mode_set(mode='OBJECT')


def checkHoleEdges(geo):
    bpy.context.view_layer.objects.active = geo
    geo.select_set(True)
    original_mode = bpy.context.tool_settings.mesh_select_mode[:]

    bpy.ops.object.mode_set(mode='EDIT')

    bpy.context.tool_settings.mesh_select_mode[0] = True
    bpy.context.tool_settings.mesh_select_mode[1] = False
    bpy.context.tool_settings.mesh_select_mode[2] = False

    bpy.ops.mesh.select_all(action='DESELECT')
    bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.mesh.select_non_manifold(extend=False, use_boundary=True, use_multi_face=False, use_non_contiguous=False, use_verts=False)
    selected_edges = [edge for edge in geo.data.edges if edge.select]
    bpy.context.tool_settings.mesh_select_mode = original_mode
    bpy.ops.object.mode_set(mode='OBJECT')

    return selected_edges




class Check_Holes(bpy.types.Operator):
    bl_idname = "mesh.checkholes"
    bl_label = "Check for holes in the geometry"
    bl_description = "Check for holes in the geometry"
    originalVisibilitySettings = {}

    result = True

    

    def execute(self, context):
        scn = context.scene
        remove_item(scn.custom, "Mesh Holes")
        objshaveHoles = []
        avatarObj = bpy.context.scene.Object_for_Check
        if avatarObj == None or avatarObj.type != "ARMATURE":
            message = ["Select armature object"]
            ShowMessageBox(message)
            return{"FINISHED"}


        self.originalVisibilitySettings = set_Visibility()
        avatarObjChildren = getChildren(avatarObj)
        avatarObjChildren.append(avatarObj)
        checkGeometries = getAllGeometries(avatarObjChildren, scn.checkMode)
        deselectObjects(checkGeometries)
        bpy.ops.object.mode_set(mode='OBJECT')
        
        for geo  in checkGeometries:
            selected_edges = []
            geo.hide_viewport = False
            selected_edges = checkHoleEdges(geo)
            if len(selected_edges) != 0:
                IsHeadMesh = checkSkinnedBones(geo, avatarObj)
                if IsHeadMesh == False:
                    objshaveHoles.append(geo)
                    self.result = False

        if self.result != True:
            for obj in objshaveHoles:
                message = "%s has a hole in the mesh" % obj.name
                add_item(scn.custom, "Mesh Holes", message)
            scn.checkResult_Holes = False
            scn.checkResult_All = True
            if scn.checkingAll == False:
                bpy.ops.object.mode_set(mode='EDIT')
            message = ["Holes are found. Check selected edges in the viewport."]
        else:
            remove_item(scn.custom, "Mesh Holes")
            scn.checkResult_Holes = True
            scn.checkResult_All = False
            message = ["No holes are found."]
        if scn.checkingAll == False:
            ShowMessageBox(message)
        set_originalVisibility(self.originalVisibilitySettings)
        return{"FINISHED"}