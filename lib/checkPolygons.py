import bpy
from checkVisibility import set_Visibility, set_originalVisibility


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


def checkTriangleCount(geometries, checkMode):
    totalTriangleCount = 0
    result = True
    excessPolyGeometries = []

    def checkpolycount(mesh):
        count = 0
        for polygon in mesh.polygons:
            if len(polygon.vertices) == 3:
                count += 1
                polygon.select = True
            elif len(polygon.vertices) == 4:
                count += 2
        return count

    if checkMode == "0":
        for geo in geometries:
            geo.hide_viewport = False
            bpy.context.view_layer.objects.active = geo
            obj = bpy.context.active_object
            mesh = obj.data
            count = checkpolycount(mesh)
            if geo.name == "Head_Geo":
                if count > 4000:
                    result = False
                    excessPolyGeometries.append(["Head", str(count)])
            if geo.name in ["LeftUpperArm_Geo", "LeftLowerArm_Geo", "LeftHand_Geo"]:
                if count > 1248:
                    result = False
                    excessPolyGeometries.append(["LeftArm", str(count)])
            if geo.name in ["RightUpperArm_Geo", "RightLowerArm_Geo", "RightHand_Geo"]:
                if count > 1248:
                    result = False
                    excessPolyGeometries.append(["RightArm", str(count)])
            if geo.name in ["UpperTorso_Geo", "LowerTorso_Geo"]:
                if count > 1750:
                    result = False
                    excessPolyGeometries.append(["Torso", str(count)])
            if geo.name in ["LeftUpperLeg_Geo", "LeftLowerLeg_Geo", "LeftFoot_Geo"]:
                if count > 1248:
                    result = False
                    excessPolyGeometries.append(["LeftLeg", str(count)])
            if geo.name in ["RightUpperLeg_Geo", "RightLowerLeg_Geo", "RightFoot_Geo"]:
                if count > 1248:
                    result = False
                    excessPolyGeometries.append(["RightLeg", str(count)])

        if result:
            return True, excessPolyGeometries
        else:
            return False, excessPolyGeometries

    else:
        if totalTriangleCount < 4000:
            return True, excessPolyGeometries
        else:
            return False, excessPolyGeometries


def checkNgons(geometries):
    objsHaveNgons = {}
    for geo in geometries:
        ngons = []
        geo.hide_viewport = False
        bpy.context.view_layer.objects.active = geo
        obj = bpy.context.active_object
        mesh = obj.data
        for polygon in mesh.polygons:
            if len(polygon.vertices) > 4:
                polygon.select = True
                ngons.append(polygon)
        if len(ngons) != 0:
            objsHaveNgons[geo] = ngons

    if len(objsHaveNgons) != 0:
        return objsHaveNgons
    else:
        return True


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
    bpy.ops.mesh.select_non_manifold(
        extend=False, use_boundary=True, use_multi_face=False, use_non_contiguous=False, use_verts=False)
    selected_edges = [edge for edge in geo.data.edges if edge.select]
    bpy.context.tool_settings.mesh_select_mode = original_mode
    bpy.ops.object.mode_set(mode='OBJECT')

    return selected_edges


def checkNonManifoldPolys(objs):
    nonManifoldElements = []

    for obj in objs:
        if obj.type == 'MESH':
            obj.hide_viewport = False
            obj.hide_set(False)
            obj.select_set(True)
            bpy.context.view_layer.objects.active = obj
            obj = bpy.context.active_object
            bpy.ops.object.mode_set(mode='EDIT')
            bpy.ops.mesh.select_all(action='DESELECT')
            bpy.ops.object.mode_set(mode='OBJECT')

            obj = bpy.context.active_object
            bpy.ops.object.mode_set(mode='EDIT')
            bpy.context.tool_settings.mesh_select_mode[0] = True
            bpy.context.tool_settings.mesh_select_mode[1] = False
            bpy.context.tool_settings.mesh_select_mode[2] = False
            bpy.ops.mesh.select_non_manifold(
                extend=True, use_wire=True, use_boundary=False, use_multi_face=True, use_non_contiguous=True, use_verts=True)
            num_selected_vertices = len(
                [v for v in obj.data.vertices if v.select])
            if num_selected_vertices > 0:
                nonManifoldElements.append(obj)

            bpy.ops.object.mode_set(mode='OBJECT')

    if len(nonManifoldElements) != 0:
        return nonManifoldElements
    else:
        return True


class Check_Polygons(bpy.types.Operator):
    bl_idname = "mesh.checkpolygons"
    bl_label = "Check the number of triangles in the geometries"
    bl_description = "Check the number of triangles in the geometries"
    originalVisibilitySettings = {}

    def execute(self, context):
        scn = context.scene
        remove_item(scn.custom, "Triangles")
        remove_item(scn.custom, "Ngons")
        avatarObj = bpy.context.scene.Object_for_Check
        if avatarObj == None or avatarObj.type != "ARMATURE":
            message = ["Select armature object"]
            ShowMessageBox(message)
            return {"FINISHED"}
        self.originalVisibilitySettings = set_Visibility()
        avatarObjChildren = getChildren(avatarObj)
        avatarObjChildren.append(avatarObj)
        checkGeometries = getAllGeometries(avatarObjChildren, scn.checkMode)

        result_count, exceedsGeometries = checkTriangleCount(
            checkGeometries, scn.checkMode)

        if result_count == True:
            scn.checkResult_Polygons = True
            scn.checkResult_All = False
            message = ["Polygon count is ok."]
        else:
            scn.checkResult_Polygons = False
            scn.checkResult_All = True
            if scn.checkMode == "0":
                message = ["Some parts exceed maximum triangle count."]
                for geoinfo in exceedsGeometries:
                    if geoinfo[0] == "Head":
                        add_item(
                            scn.custom, "Triangles", "Head has %s triangles. (Max is 4000)" % geoinfo[1])
                    if geoinfo[0] == "LeftArm":
                        add_item(
                            scn.custom, "Triangles", "LeftArm has %s triangles. (Max is 1248)" % geoinfo[1])
                    if geoinfo[0] == "RightArm":
                        add_item(
                            scn.custom, "Triangles", "RightArm has %s triangles. (Max is 1248)" % geoinfo[1])
                    if geoinfo[0] == "Torso":
                        add_item(
                            scn.custom, "Triangles", "Torso has %s triangles. (Max is 1750)" % geoinfo[1])
                    if geoinfo[0] == "LeftLeg":
                        add_item(
                            scn.custom, "Triangles", "LeftLeg has %s triangles. (Max is 1248)" % geoinfo[1])
                    if geoinfo[0] == "RightLeg":
                        add_item(
                            scn.custom, "Triangles", "RightLeg has %s triangles. (Max is 1248)" % geoinfo[1])
            else:
                message = ["The total triangle count is more than 4000."]
                add_item(scn.custom, "Triangles",
                         "The total triangle count is more than 4000.")
        if scn.checkingAll == False:
            ShowMessageBox(message)

        set_originalVisibility(self.originalVisibilitySettings)
        return {"FINISHED"}


class Check_Ngons(bpy.types.Operator):
    bl_idname = "mesh.checkngons"
    bl_label = "Check the Ngons in the geometries"
    bl_description = "Check the Ngons in the geometries"
    originalVisibilitySettings = {}

    def execute(self, context):
        scn = context.scene
        remove_item(scn.custom, "Ngons")
        avatarObj = bpy.context.scene.Object_for_Check
        if avatarObj == None or avatarObj.type != "ARMATURE":
            message = ["Select armature object"]
            ShowMessageBox(message)
            return {"FINISHED"}
        self.originalVisibilitySettings = set_Visibility()
        avatarObjChildren = getChildren(avatarObj)
        avatarObjChildren.append(avatarObj)
        checkGeometries = getAllGeometries(avatarObjChildren, scn.checkMode)

        result_ngons = checkNgons(checkGeometries)

        if result_ngons == True:
            scn.checkResult_Ngons = True
            scn.checkResult_All = False
            remove_item(scn.custom, "Ngons")
            message = ["Ngons are not found."]
        else:
            for obj in result_ngons.keys():
                add_item(scn.custom, "Ngons",
                         "%s have a Ngons in the mesh." % obj.name)
            scn.checkResult_Ngons = False
            scn.checkResult_All = True
            message = ["There is Ngons on meshes. Check the details."]
        if scn.checkingAll == False:
            ShowMessageBox(message)
        set_originalVisibility(self.originalVisibilitySettings)
        return {"FINISHED"}


class Check_NonManifold(bpy.types.Operator):
    bl_idname = "mesh.checknonmanifold"
    bl_label = "Check non-manifold polygons in the mesh"
    bl_description = "Check non-manifold polygons in the mesh"
    originalVisibilitySettings = {}

    def execute(self, context):
        scn = context.scene
        remove_item(scn.custom, "Non-Manifold")
        avatarObj = bpy.context.scene.Object_for_Check
        if avatarObj == None or avatarObj.type != "ARMATURE":
            message = ["Select armature object"]
            ShowMessageBox(message)
            return {"FINISHED"}
        self.originalVisibilitySettings = set_Visibility()
        avatarObjChildren = getChildren(avatarObj)
        avatarObjChildren.append(avatarObj)
        checkGeometries = getAllGeometries(avatarObjChildren, scn.checkMode)
        checkCages = getCages(avatarObjChildren, scn.checkMode)

        checkObjs = checkGeometries + checkCages

        result_manifold = checkNonManifoldPolys(checkObjs)

        if result_manifold == True:
            scn.checkResult_NonManifold = True
            scn.checkResult_All = False
            remove_item(scn.custom, "Non-Manifold")
            message = ["Non-Manifold is not found."]
        else:
            for obj in result_manifold:
                add_item(scn.custom, "Non-Manifold",
                         "%s have a Non-Manifold in the mesh." % obj.name)
            scn.checkResult_NonManifold = False
            scn.checkResult_All = True
            message = [
                "Non-Manifold polygons are found in meshes. Check the details."]
            if scn.checkingAll == False:
                bpy.ops.object.mode_set(mode='EDIT')

        if scn.checkingAll == False:
            ShowMessageBox(message)

        set_originalVisibility(self.originalVisibilitySettings)
        return {"FINISHED"}
