import bpy
import mathutils
from checkVisibility import set_Visibility, set_originalVisibility
from ensureObjectActive import ensureObjectModeandActive


def ShowMessageBox(message):

    def draw(self, context):
        for line in message:
            self.layout.label(text=line)

    bpy.context.window_manager.popup_menu(
        draw, title="Validation Result", icon="INFO")


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


def getAllGeometries(armatureChildren):
    checkGeometries = {}
    head = []
    leftArm = []
    rightArm = []
    torso = []
    rightLeg = []
    leftLeg = []
    avatarObj = bpy.context.scene.Object_for_Check
    for obj in armatureChildren:
        if ("_Geo" in obj.name) and ("_Att" not in obj.name):
            if "Head" in obj.name:
                head.append(obj)
            elif "Right" in obj.name:
                if "Arm" in obj.name or "Hand" in obj.name:
                    rightArm.append(obj)
                if "Leg" in obj.name or "Foot" in obj.name:
                    rightLeg.append(obj)
            elif "Left" in obj.name:
                if "Arm" in obj.name or "Hand" in obj.name:
                    leftArm.append(obj)
                if "Leg" in obj.name or "Foot" in obj.name:
                    leftLeg.append(obj)
            elif "Torso" in obj.name:
                torso.append(obj)

    checkGeometries = {"Head": head, "RightArm": rightArm, "LeftArm": leftArm,
                       "RightLeg": rightLeg, "LeftLeg": leftLeg, "Torso": torso}
    return checkGeometries


def getChildren(object):
    children = []
    for ob in bpy.data.objects:
        if ob.parent == object:
            children.append(ob)
    return children


minsize = {
    "Head": [0.5, 0.5, 0.5],
    "LeftArm": [0.25, 1.5, 0.25],
    "RightArm": [0.25, 1.5, 0.25],
    "Torso": [1.0, 2.0, 0.7],
    "LeftLeg": [0.25, 2, 0.5],
    "RightLeg": [0.25, 2, 0.5],
    "The total": [1.5, 4.5, 0.7]
}

maxsize_normal = {
    "Head": [3, 2, 2],
    "LeftArm": [2, 4.5, 2],
    "RightArm": [2, 4.5, 2],
    "Torso": [4, 3, 2.25],
    "LeftLeg": [1.5, 3, 2],
    "RightLeg": [1.5, 3, 2],
    "The total": [8, 8, 2.5]
}


def checkMeshSize(checkGeometries, avatarObj, checkMode):
    if checkMode == "0":
        errorMeshes = []
        wholeGeo = None
        x, y, z = [1.0, 1.0, 1.0]
        if avatarObj.scale < mathutils.Vector((1.0, 1.0, 1.0)):
            x = x / avatarObj.scale.x
            y = y / avatarObj.scale.y
            z = z / avatarObj.scale.z

        for key in checkGeometries:
            for obj in bpy.data.objects:
                obj.select_set(False)
            if checkGeometries[key]:
                for obj in checkGeometries[key]:
                    obj.select_set(True)

                context_override = bpy.context.copy()
                context_override['selected_objects'] = checkGeometries[key]
                context_override['active_object'] = checkGeometries[key][0]

                try:
                    with bpy.context.temp_override(**context_override):
                        bpy.ops.object.duplicate(linked=False)
                    duplicatedGeo = bpy.context.selected_objects
                    bpy.context.view_layer.objects.active = duplicatedGeo[0]
                    bpy.ops.object.join()
                    bpy.ops.object.parent_clear(type='CLEAR_KEEP_TRANSFORM')
                    bpy.ops.object.transform_apply(
                        location=True, rotation=True, scale=True)
                    joinedGeo = bpy.context.selected_objects

                    if joinedGeo and joinedGeo[0]:
                        Width, Depth, Height = joinedGeo[0].dimensions
                        minWidth, minHeight, minDepth = minsize[key]
                        maxWidth, maxHeight, maxDepth = maxsize_normal[key]

                        if minWidth >= Width * x:
                            errorMeshes.append(
                                [key, "minX", Width, minWidth, "width"])
                        if minHeight >= Height * y:
                            errorMeshes.append(
                                [key, "minY", Height, minHeight, "height"])
                        if minDepth >= Depth * z:
                            errorMeshes.append(
                                [key, "minZ", Depth, minDepth, "depth"])

                        if Width * x >= maxWidth:
                            errorMeshes.append(
                                [key, "maxX", Width, maxWidth, "width"])
                        if Height * y >= maxHeight:
                            errorMeshes.append(
                                [key, "maxY", Height, maxHeight, "height"])
                        if Depth * z >= maxDepth:
                            errorMeshes.append(
                                [key, "maxZ", Depth, maxDepth, "depth"])

                        bpy.data.objects.remove(joinedGeo[0], do_unlink=True)
                        bpy.data.orphans_purge(do_recursive=True)
                except Exception as e:
                    print(f"Error processing {key}: {str(e)}")

        # Check the whole geometry
        for obj in bpy.data.objects:
            obj.select_set(False)

        all_objects = [obj for objs in checkGeometries.values()
                       for obj in objs if obj]
        for obj in all_objects:
            obj.select_set(True)

        context_override = bpy.context.copy()
        context_override['selected_objects'] = all_objects
        context_override['active_object'] = next(
            (obj for obj in all_objects if obj.type == 'MESH'), None)

        if context_override['active_object']:
            try:
                with bpy.context.temp_override(**context_override):
                    bpy.ops.object.duplicate(linked=False)
                duplicatedGeo = bpy.context.selected_objects
                bpy.context.view_layer.objects.active = duplicatedGeo[0]
                bpy.ops.object.join()
                bpy.ops.object.parent_clear(type='CLEAR_KEEP_TRANSFORM')
                bpy.ops.object.transform_apply(
                    location=True, rotation=True, scale=True)
                wholeGeo = bpy.context.selected_objects

                if wholeGeo and wholeGeo[0]:
                    Width, Depth, Height = wholeGeo[0].dimensions
                    minWidth, minHeight, minDepth = minsize["The total"]
                    maxWidth, maxHeight, maxDepth = maxsize_normal["The total"]

                    if minWidth >= Width * x:
                        errorMeshes.append(
                            ["The total", "minX", Width, minWidth, "width"])
                    if minHeight >= Height * y:
                        errorMeshes.append(
                            ["The total", "minY", Height, minHeight, "height"])
                    if minDepth >= Depth * z:
                        errorMeshes.append(
                            ["The total", "minZ", Depth, minDepth, "depth"])

                    if Width * x >= maxWidth:
                        errorMeshes.append(
                            ["The total", "maxX", Width, maxWidth, "width"])
                    if Height * y >= maxHeight:
                        errorMeshes.append(
                            ["The total", "maxY", Height, maxHeight, "height"])
                    if Depth * z >= maxDepth:
                        errorMeshes.append(
                            ["The total", "maxZ", Depth, maxDepth, "depth"])

                    bpy.data.objects.remove(wholeGeo[0], do_unlink=True)
                    bpy.data.orphans_purge(do_recursive=True)
            except Exception as e:
                print(f"Error processing whole geometry: {str(e)}")

        return errorMeshes if errorMeshes else True
    else:
        return True


class Check_AssetSize(bpy.types.Operator):
    bl_idname = "mesh.checkassetsize"
    bl_label = "Check mesh size in the scene"
    bl_description = "Check mesh size in the scene"
    originalVisibilitySettings = {}
    originalLengthUnit = ""

    def execute(self, context):
        result = True
        scn = context.scene
        avatarObj = bpy.context.scene.Object_for_Check
        if scn.checkMode == '0':
            if avatarObj == None or avatarObj.type != "ARMATURE":
                message = ["Select armature object"]
                ShowMessageBox(message)
                return {"FINISHED"}
            self.originalVisibilitySettings = set_Visibility()
            ensureObjectModeandActive(avatarObj)
            self.originalLengthUnit = bpy.context.scene.unit_settings.length_unit
            if self.originalLengthUnit != "CENTIMETERS":
                bpy.context.scene.unit_settings.length_unit == "CENTIMETERS"
            remove_item(scn.custom, "AssetSize")
            allChildren = getChildren(avatarObj)
            checkGeometries = getAllGeometries(allChildren)
            result = checkMeshSize(checkGeometries, avatarObj, scn.checkMode)
        else:
            return {"FINISHED"}

        if result != True:
            message = ["Some parts are not appropriate size.",
                       "Check the details."]
            for part in result:
                if "min" in part[1]:
                    text = part[0] + " " + part[4] + " is below the minimum limit (%s). The minimum is %s." % (
                        str(round(part[2], 2)), str(part[3]))
                else:
                    text = part[0] + " " + part[4] + " exceeds the maximum limit (%s). The maximum is %s." % (
                        str(round(part[2], 2)), str(part[3]))
                add_item(scn.custom, "AssetSize", text)
                scn.checkResult_Positions = False
                scn.checkResult_All = True
        else:
            remove_item(scn.custom, "AssetSize")
            message = ["Asset size is ok."]
            scn.checkResult_Positions = True
            scn.checkResult_All = False
        if scn.checkingAll == False and scn.checkMode == "0":
            ShowMessageBox(message)
        bpy.context.scene.unit_settings.length_unit = self.originalLengthUnit
        set_originalVisibility(self.originalVisibilitySettings)
        return {"FINISHED"}
