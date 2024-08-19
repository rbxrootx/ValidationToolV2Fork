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
    if checkMode == '0':
        for obj in armatureChildren:
            if "_Geo" in obj.name:
                checkGeometries.append(obj)
            else:
                checkGeometries.append(obj)
    else:
        for obj in armatureChildren:
            if "_Att" not in obj.name:
                checkGeometries.append(obj)
            else:
                checkGeometries.append(obj)
    

    return checkGeometries




def checkUVs(objs):
    wrongUVs = []


    for obj in objs:
        isUVin0to1 = True
        if obj.type == 'MESH':
            mesh = obj.data
            for poly in mesh.polygons:
                for loop_index in poly.loop_indices:
                    uv = mesh.uv_layers.active.data[loop_index].uv
                    if (uv.x > 1.0) or (uv.y > 1.0) or (uv.x < 0.0) or (uv.y < 0.0):
                        isUVin0to1 = False
                       
        if isUVin0to1 != True:
            wrongUVs.append(obj.name)


    if wrongUVs != []:
        return wrongUVs
    else:
        return True




class ConfirmBox_UVs(bpy.types.Operator):
    bl_idname = "mesh.confirmboxuv"
    bl_label =  "UV Check"
    bl_description = "Checks UV coordinates are within 0.0, 1.0"

    def execute(self, context):
        scn = context.scene
        return {'FINISHED'}
    
    def draw(self, context):
        scn = context.scene
        msg = ["Some geometries have wrong UV coordinates. Check the details."]
        for line in msg:
            self.layout.label(text= line)

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self)




class Check_UVs(bpy.types.Operator):
    bl_idname = "mesh.checkuv"
    bl_label =  "UV Check"
    bl_description = "Check if UV coordinates are within 0.0, 1.0"
    originalVisibilitySettings = {}


    def execute(self, context):
        scn = context.scene
        remove_item(scn.custom, "UVPosition")
        avatarObj = bpy.context.scene.Object_for_Check
        if avatarObj == None or avatarObj.type != "ARMATURE":
            message = ["Select armature object"]
            ShowMessageBox(message)
            return{"FINISHED"}
        self.originalVisibilitySettings = set_Visibility()
        # bpy.ops.object.mode_set(mode='OBJECT')
        # print("Test line")
        
        armatureChildren = getChildren(avatarObj)
        geometries = getAllGeometries(armatureChildren, scn.checkMode)

 
        result = checkUVs(geometries)
        if result != True:
            scn.checkResult_UVs = False
            scn.checkResult_All = True
            for obj in result:
                text = str(obj) + " has a UV coordinate out side of 0 to 1."
                add_item(scn.custom, "UVPosition", text)
            message = ["Some wrong UV coordinates are found. Check the details."]
            if not scn.checkingAll:
                ShowMessageBox(message)
        else:
            scn.checkResult_UVs = True
            scn.checkResult_All = False
            message = ["UVs are ok."]
            if not scn.checkingAll:
                ShowMessageBox(message)

        set_originalVisibility(self.originalVisibilitySettings)
        return{"FINISHED"}
