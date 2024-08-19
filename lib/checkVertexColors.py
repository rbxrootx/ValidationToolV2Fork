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
            if "_Geo" in obj.name:
                checkGeometries.append(obj)
    else:
        for obj in armatureChildren:
            if "_Att" not in obj.name:
                checkGeometries.append(obj)


    return checkGeometries


def checkVTXColorData(geometries):
    meshHasVertexColors = {}

    for geo in geometries:
        visibility = geo.visible_get()
        if not visibility:
            geo.hide_viewport = True
        geo.hide_viewport = False
        bpy.context.view_layer.objects.active = geo
        obj = bpy.context.active_object

        if geo.type == 'MESH':
            mesh = geo.data
            mesh_name = geo.name
        
            if mesh.color_attributes:
                vertex_color_names = [vc.name for vc in mesh.color_attributes]
                meshHasVertexColors[mesh_name] = vertex_color_names
        
        if not visibility:
            geo.hide_viewport = True

    

    if len(meshHasVertexColors) > 1:
        return meshHasVertexColors
    else:
        return True
    

def deleteVTXColor(geometries):

    for geo in geometries:
        visibility = geo.visible_get()
        if not visibility:
            geo.hide_viewport = True
        bpy.context.view_layer.objects.active = geo
        obj = bpy.context.active_object

        if obj.type == 'MESH':
            mesh = obj.data
            mesh_name = obj.name
        
            if mesh.color_attributes:
                for vc in mesh.color_attributes:
                    mesh.color_attributes.remove(vc)
        
        if not visibility:
            geo.hide_viewport = True


class ConfirmBox_VTXColors(bpy.types.Operator):
    bl_idname = "mesh.confirmvtxcolors"
    bl_label = "Check vertex color data in geometries"
    bl_description = "Check vertex color data in geometries"
    originalVisibilitySettings = {}

    def execute(self, context):
        scn = context.scene
        avatarObj = scn.Object_for_Check
        if avatarObj == None or avatarObj.type != "ARMATURE":
            message = ["Select armature object"]
            ShowMessageBox(message)
            return{"FINISHED"}
        self.originalVisibilitySettings = set_Visibility()
        children = getChildren(avatarObj)
        allGeo = getAllGeometries(children, scn.checkMode)

        deleteVTXColor(allGeo)
        result = checkVTXColorData(allGeo)

        if result != True:
            meshHasVertexColors = result
            for meshName, vtxColNames in meshHasVertexColors.items():
                message = "%s has vtx color %s" % (meshName, vtxColNames)
                add_item(scn.custom, "VertexColor", message)
            scn.checkResult_VTXColors = False
            scn.checkResult_All = True
            message = ["Some geometries have vertex colors. Check the details."]
        else:
            remove_item(scn.custom, "VertexColor")
            scn.checkResult_VTXColors = True
            message = ["Vertex Colors are removed."]
        ShowMessageBox(message)


        set_originalVisibility(self.originalVisibilitySettings)
        return {'FINISHED'}
    
    def draw(self, context):
        scn = context.scene
        msg = ["Some geometries have vertex colors.", "Would you like to remove them?"]
        for l in msg:
            self.layout.label(text= l)

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self)


class Check_VTXColors(bpy.types.Operator):
    bl_idname = "mesh.checkvtxcolors"
    bl_label = "Check vertex color data in geometries"
    bl_description = "Check vertex color data in geometries"
    originalVisibilitySettings = {}

    def execute(self, context):
        scn = context.scene
        remove_item(scn.custom, "VertexColor")
        avatarObj = scn.Object_for_Check
        if avatarObj == None or avatarObj.type != "ARMATURE":
            message = ["Select armature object"]
            ShowMessageBox(message)
            return{"FINISHED"}
        self.originalVisibilitySettings = set_Visibility()
        children = getChildren(avatarObj)
        allGeo = getAllGeometries(children, scn.checkMode)


        result = checkVTXColorData(allGeo)

        if result != True:
            meshHasVertexColors = result
            for meshName, vtxColNames in meshHasVertexColors.items():
                message = "%s has vtx color %s" % (meshName, vtxColNames)
                add_item(scn.custom, "VertexColor", message)
            scn.checkResult_VTXColors = False
            scn.checkResult_All = True
            if scn.checkingAll == False:
                bpy.ops.mesh.confirmvtxcolors("INVOKE_DEFAULT")
        else:
            remove_item(scn.custom, "VertexColor")
            scn.checkResult_VTXColors = True
            message = ["Vertex Color is ok."]
            if scn.checkingAll == False:
                ShowMessageBox(message)
        
        set_originalVisibility(self.originalVisibilitySettings)
        return{"FINISHED"}