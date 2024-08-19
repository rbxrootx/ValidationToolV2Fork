import os
import sys




bl_info = {
    "name": "Validation Tool",
    "author": "Roblox",
    "version": (2, 0),
    "blender": (3, 00, 0),
    "location": "Sidebar",
    "description": "Validates Avatar and Layered Clothing assets for uploading",
    "warning": "",
    "wiki_url": "",
    "category": "Object",
}


import bpy
import os
import glob
import numpy as np
import mathutils
from mathutils.bvhtree import BVHTree
from bpy.props import *

##This path has to be changed
add_on_directory = os.path.dirname(os.path.realpath(__file__))
sys.path.append(os.path.join(add_on_directory, "lib"))
from .lib.checkLayers import Fix_Layer, ConfirmBox_Layer
from .lib.checkTransform import Fix_Transform, ConfirmBox_Transform
from .lib.checkCustomProperty import Check_FacsData
from .lib.checkDynamicHeadJointNames import Check_DynamicHeadJointNames
from .lib.checkKeyFrames import Check_KeyFrames, ConfirmBox_KeyFrame
from .lib.checkUVs import Check_UVs
from .lib.checkAssetSize import Check_AssetSize
from .lib.checkErrant import Check_Errant, ConfirmBox_UnusedData
from .lib.checkAttachmentPoints import Check_AttPoints, ConfirmBox_AttachmentPoints
from .lib.checkInterSections import Fix_InterSections_Inner
from .lib.checkHoles import Check_Holes
from .lib.checkImageFiles import Check_ImageFiles
from .lib.checkVertexColors import Check_VTXColors, ConfirmBox_VTXColors
from .lib.checkPolygons import Check_Polygons, Check_Ngons, Check_NonManifold
from .lib.checkCageUVs import Check_CageUVs, ConfirmBox_CageUVs
from .lib.checkPositions import Check_Positions, Check_JointPositions

from .lib.checkVisibility import set_Visibility, set_originalVisibility
from .lib.ensureObjectActive import ensureObjectModeandActive


class globalVariables():    
    wrongPositions_Attachment = []
    wrongNames_Attachment = []
    objectsWithKeys = []
    clothingObjs = []
    version = "Version 2.0(Build08072023_B) Roblox"
    originalVisibilitySettings = {}



class CUSTOM_objectCollection(bpy.types.PropertyGroup):
    type: StringProperty()
    message: StringProperty()
    id: IntProperty()

class CUSTOM_OT_clearList(bpy.types.Operator):
    bl_idname = "custom.clear_list"
    bl_label = "Clear List"
    bl_description = "Close the error report panel"

    @classmethod
    def poll(cls, context):
        return bool(context.scene.custom)

    def invoke(self, context, event):
        return context.window_manager.invoke_confirm(self, event)

    def execute(self, context):
        if bool(context.scene.custom):
            context.scene.custom.clear()
            context.scene.checkResult_All = False
            self.report({'INFO'}, "All items removed")
        else:
            self.report({'INFO'}, "Nothing to remove")
        return{'FINISHED'}
    

class MATERIAL_UL_matslots_example(bpy.types.UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname):
        layout.prop(item, "message", text= item.type, emboss=False, icon_value=icon)



class ValidationToolMainPanel(bpy.types.Panel, globalVariables):
    bl_label = "Validation Tool"
    bl_idname = "OBJECT_PT_Validation"
    bl_space_type = 'VIEW_3D'
    bl_category = "Validation Tool"
    bl_region_type = 'UI'
    
    
    checkModeOptions = (('0','Avatar',''),('1','Layered Clothing',''))


    bpy.types.Scene.texture_folder = StringProperty(default = "", subtype='DIR_PATH')
    bpy.types.Scene.Object_for_Check = PointerProperty(type=bpy.types.Object, name = "Target Armature")
    bpy.types.Scene.checkMode = bpy.props.EnumProperty(items = checkModeOptions)

    bpy.types.Scene.checkResult_Layers = BoolProperty( name = "Boolean", description = "None", default = True)
    bpy.types.Scene.checkResult_Transform = BoolProperty( name = "Boolean", description = "None", default = True)
    bpy.types.Scene.checkResult_UVs = BoolProperty( name = "Boolean", description = "None", default = True)
    bpy.types.Scene.checkResult_KeyFrames = BoolProperty( name = "Boolean", description = "None", default = True)
    bpy.types.Scene.checkResult_FACSData = BoolProperty( name = "Boolean", description = "None", default = True)
    bpy.types.Scene.checkResult_DynamicHeadJointNames = BoolProperty( name = "Boolean", description = "None", default = True)
    bpy.types.Scene.checkResult_UnusedData = BoolProperty( name = "Boolean", description = "None", default = True)
    bpy.types.Scene.checkResult_AttPoints = BoolProperty( name = "Boolean", description = "None", default = True)
    bpy.types.Scene.checkResult_InterSections_OUT = BoolProperty( name = "Boolean", description = "None", default = True)
    bpy.types.Scene.checkResult_InterSections_IN = BoolProperty( name = "Boolean", description = "None", default = True)
    bpy.types.Scene.checkResult_Holes = BoolProperty( name = "Boolean", description = "None", default = True)
    bpy.types.Scene.checkResult_ImageFormat = BoolProperty( name = "Boolean", description = "None", default = True)
    bpy.types.Scene.checkResult_VTXColors = BoolProperty( name = "Boolean", description = "None", default = True)
    bpy.types.Scene.checkResult_Polygons = BoolProperty( name = "Boolean", description = "None", default = True)
    bpy.types.Scene.checkResult_Ngons = BoolProperty( name = "Boolean", description = "None", default = True)
    bpy.types.Scene.checkResult_NonManifold = BoolProperty( name = "Boolean", description = "None", default = True)
    bpy.types.Scene.checkResult_CageUVs = BoolProperty( name = "Boolean", description = "None", default = True)
    bpy.types.Scene.checkResult_JointPositions = BoolProperty( name = "Boolean", description = "None", default = True)
    bpy.types.Scene.checkResult_Positions = BoolProperty( name = "Boolean", description = "None", default = True)

    bpy.types.Scene.checkResult_All = BoolProperty( name = "Boolean", description = "None", default = False)

    bpy.types.Scene.checkingAll = BoolProperty( name = "Boolean", description = "None", default = False)

    bpy.types.Scene.wrongTransformObjects = StringProperty(default = "")
    bpy.types.Scene.objectsWithKeys = StringProperty(default = "")
    bpy.types.Scene.wrongPositions_Attachment = StringProperty(default = "")
    bpy.types.Scene.wrongNames_Attachment = StringProperty(default = "")
    bpy.types.Scene.intersections = StringProperty(default = "")


    def draw(self, context):

        
        scn = context.scene
        layout = self.layout
        
        obj = context.object

        row1 = layout.row()
        row1.prop_search(scn, "Object_for_Check", context.scene, "objects")
        layout.prop(context.scene, 'checkMode', expand=True)
        
        row3 = layout.row()
        row3.operator("mesh.checkrunall", text =  "Run all checks")


        row_sceneCheck_Title= layout.row()
        row_sceneCheck_Title.label(text="Individual Checks")
        
        row4 = layout.row()
        labelText_layers = "Layers"
        if scn.checkResult_Layers == True:
            row4.alert = False
        else:
            row4.alert = True
            labelText_layers = "Layer - Click to attempt auto fix"
        row4.operator("mesh.fixlayer", text =  labelText_layers)

        row5 = layout.row()
        labelText_transforms = "Transforms"
        if scn.checkResult_Transform == True:
            row5.alert = False
        else:
            row5.alert = True
            labelText_transforms = "Transforms - Click to attempt auto fix"
        row5.operator("mesh.transform", text =  labelText_transforms)

        row6 = layout.row()
        ##NO AUTO FIX FOR THIS
        if scn.checkResult_UVs == True:
            row6.alert = False
        else:
            row6.alert = True
        row6.operator("mesh.checkuv", text =  "UV")


        row_checkCageUVs = layout.row()
        labelText_cage = "Cage UV Modification"
        if scn.checkResult_CageUVs == True:
            row_checkCageUVs.alert = False
        else:
            row_checkCageUVs.alert = True
            labelText_cage = "Cage UV Modification - Click to attempt auto fix"
        row_checkCageUVs.operator("mesh.checkcageuvs", text = labelText_cage)

        row_checkPositions = layout.row()
        ##NO AUTO FIX FOR THIS
        if scn.checkResult_Positions == True:
            row_checkPositions.alert = False
        else:
            row_checkPositions.alert = True
        row_checkPositions.operator("mesh.checkassetsize", text = "Asset Size")


        row7 = layout.row()
        labelText_unuseddata = "Unused Data"
        if scn.checkResult_UnusedData == True:
            row7.alert = False
        else:
            row7.alert = True
            labelText_unuseddata = "Unused Data - Click to attempt auto fix"
        row7.operator("mesh.checkerrant", text = labelText_unuseddata)

        row8 =layout.row()
        labelText_keyframe = "Keyframes"
        if scn.checkResult_KeyFrames == True:
            row8.alert = False
        else:
            row8.alert = True
            labelText_keyframe = "Keyframes - Click to attempt auto fix"
        row8.operator("mesh.checkkeyframes", text = labelText_keyframe)

        row9 = layout.row()
        labelText_attachmentPoint = "Attachment Points"
        if scn.checkResult_AttPoints == True:
            row9.alert = False
        else:
            row9.alert = True
            labelText_attachmentPoint = "Attachment Points - Click to attempt auto fix"
        row9.operator("mesh.checkattpoints", text =  labelText_attachmentPoint)

        row10 = layout.row()
        ##NO AUTO FIX FOR THIS
        if scn.checkResult_JointPositions == True:
            row10.alert = False
        else:
            row10.alert = True
        row10.operator("mesh.checkjointpositions", text =  "Joint Positions")

        if scn.checkMode == '0':
            row_checkDynamicHeadTitle = layout.row()
            row_checkDynamicHeadTitle.label(text= "Avatar Head")
            row_facs = layout.row()
            if scn.checkResult_FACSData == True:
                row_facs.alert = False
            else:
                row_facs.alert = True
            row_facs.operator("mesh.checkfacsdata", text =  "FACS Data")

            row_jointsName = layout.row()
            if scn.checkResult_DynamicHeadJointNames == True:
                row_jointsName.alert = False
            else:
                row_jointsName.alert = True
            row_jointsName.operator("mesh.checkdynamicheadjointnames", text =  "Head Joint Names")
        else:
            pass

        
        row_checkInterSectionTitle = layout.row()
        row_checkInterSectionTitle.label(text= "Intersections")
        row10 = layout.row()
        ##NO AUTO FIX FOR THIS
        if scn.checkMode != "0":
            row10A = row10.split()
            if scn.checkResult_InterSections_OUT == True:
                row10A.alert = False
            else:
                row10A.alert = True
            outerOP = row10A.operator("mesh.fixintersectionsinner", text =  "Intersections Outer")
            outerOP.checkType = "Outer"
            row10B = row10.split()
            if scn.checkResult_InterSections_IN == True:
                row10B.alert = False
            else:
                row10B.alert = True
            innerOP = row10B.operator("mesh.fixintersectionsinner", text =  "Intersections Inner")
            innerOP.checkType = "Inner"
        else:
            if scn.checkResult_InterSections_OUT == True:
                row10.alert = False
            else:
                row10.alert = True
            row10.operator("mesh.fixintersectionsinner", text =  "Intersections")


        row_checkPolygonTitle = layout.row()
        row_checkPolygonTitle.label(text= "Polygon Data")

        row_checkPolygons = layout.row()
        ##NO AUTO FIX FOR THIS
        row_Holes = row_checkPolygons.split()
        if scn.checkResult_Holes == True:
            row_Holes.alert = False
        else:
            row_Holes.alert = True
        row_Holes.operator("mesh.checkholes", text =  "Holes")

        row_PolyCount = row_checkPolygons.split()
        ##NO AUTO FIX FOR THIS
        if scn.checkResult_Polygons == True:
            row_PolyCount.alert = False
        else:
            row_PolyCount.alert = True
        row_PolyCount.operator("mesh.checkpolygons", text =  "Poly count")
        row_Ngons = row_checkPolygons.split()
        ##NO AUTO FIX FOR THIS
        if scn.checkResult_Ngons == True:
            row_Ngons.alert = False
        else:
            row_Ngons.alert = True
        row_Ngons.operator("mesh.checkngons", text =  "Ngons")

        row_manifold = row_checkPolygons.split()
        ##NO AUTO FIX FOR THIS
        if scn.checkResult_NonManifold == True:
            row_manifold.alert = False
        else:
            row_manifold.alert = True
        row_manifold.operator("mesh.checknonmanifold", text =  "Non-manifold")


        row_vtxcolor = row_checkPolygons.split()
        labelText_vtxcolor = "VTX colors"
        if scn.checkResult_VTXColors == True:
            row_vtxcolor.alert = False
        else:
            row_vtxcolor.alert = True
            labelText_vtxcolor = "VTX colors - Click to attempt auto fix"
        row_vtxcolor.operator("mesh.checkvtxcolors", text = labelText_vtxcolor)

        row_checkTextureFormatTitle = layout.row()
        row_checkTextureFormatTitle.label(text= "Texture format")
        row_checkTextureFormat = layout.row()
        ##NO AUTO FIX FOR THIS
        layout.prop(context.scene, "texture_folder", text="Texture Folder")
        if scn.checkResult_ImageFormat == True:
            row_checkTextureFormat.alert = False
        else:
            row_checkTextureFormat.alert = True
        row_checkTextureFormat.operator("mesh.checkimagefiles", text =  "Texture Format")

           
        if scn.checkResult_All == True:
            layout.template_list("MATERIAL_UL_matslots_example", "", scn, "custom", scn, "custom_index")
            
            row = layout.row()
            row.operator("custom.clear_list", text = "Clear and hide result box")
        

        row16 = layout.row()
        row16.label(text= globalVariables.version)
        
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


class Check_RunAll(bpy.types.Operator):
    bl_idname = "mesh.checkrunall"
    bl_label = "Runs all checks"
    bl_description = "Runs all checks"


    def execute(self, context):
        scn = context.scene
        scn.checkingAll = True
        if scn.Object_for_Check != None:
            if scn.Object_for_Check.type == "ARMATURE":
                try:
                    self.originalVisibilitySettings = set_Visibility()
                    ensureObjectModeandActive(scn.Object_for_Check)
                    bpy.ops.mesh.fixlayer()
                    bpy.ops.mesh.transform()
                    bpy.ops.mesh.checkuv()
                    bpy.ops.mesh.checkassetsize()
                    bpy.ops.mesh.checkerrant()
                    bpy.ops.mesh.checkattpoints()
                    bpy.ops.mesh.checkkeyframes()
                    bpy.ops.mesh.checkjointpositions()
                    if scn.checkMode == "0":
                        bpy.ops.mesh.checkfacsdata()
                        bpy.ops.mesh.checkdynamicheadjointnames()
                    bpy.ops.mesh.checkholes()
                    bpy.ops.mesh.checkvtxcolors()
                    bpy.ops.mesh.checkpolygons()
                    bpy.ops.mesh.checkngons()
                    bpy.ops.mesh.checknonmanifold()
                    bpy.ops.mesh.checkcageuvs()
                    # bpy.ops.mesh.checkpositions()

                    if bpy.types.Scene.texture_folder != "":
                        bpy.ops.mesh.checkimagefiles()
                    set_originalVisibility(self.originalVisibilitySettings)
                except:
                    message = ["Selected armature does not seem an avatar asset."]
                    ShowMessageBox(message)
                    return{"FINISHED"}
            else:
                if scn.checkMode == "0":
                    message = ["Select armature for avatar"]
                    ShowMessageBox(message)
                    return{"FINISHED"}
                else:
                    message = ["Select armature for layer clothing"]
                    ShowMessageBox(message)
                    return{"FINISHED"}
        else:
            if scn.checkMode == "0":
                message = ["Select armature for avatar"]
                ShowMessageBox(message)
                return{"FINISHED"}
            else:
                message = ["Select armature for layer clothing"]
                ShowMessageBox(message)
                return{"FINISHED"}

        message = ["Validation is done. Check the result in the main panel."]
        ShowMessageBox(message)
        scn.checkResult_All = True
        scn.checkingAll = False
        return{"FINISHED"}




classes = [
    CUSTOM_objectCollection,
    CUSTOM_OT_clearList,
    MATERIAL_UL_matslots_example,
    ValidationToolMainPanel,
    Fix_Layer,
    ConfirmBox_Layer,
    Fix_Transform,
    ConfirmBox_Transform,
    Check_FacsData,
    Check_DynamicHeadJointNames,
    Check_KeyFrames,
    ConfirmBox_KeyFrame,
    Check_UVs,
    Check_Errant,
    ConfirmBox_UnusedData,
    Check_AttPoints,
    ConfirmBox_AttachmentPoints,
    Fix_InterSections_Inner,
    Check_Holes,
    Check_ImageFiles,
    Check_VTXColors,
    ConfirmBox_VTXColors,
    Check_AssetSize,
    Check_Polygons,
    Check_Ngons,
    Check_NonManifold,
    Check_CageUVs,
    ConfirmBox_CageUVs,
    Check_Positions,
    Check_JointPositions,
    Check_RunAll
]


def register():
    for c in classes:
        try:
            bpy.utils.register_class(c)
        except:
            pass
    
    bpy.types.Scene.custom = CollectionProperty(type=CUSTOM_objectCollection)
    bpy.types.Scene.custom_index = IntProperty(default = 5)
    
    

def unregister():
    for c in classes:
        bpy.utils.unregister_class(c)
    
    del bpy.types.Scene.custom
    del bpy.types.Scene.custom_index

if __name__ == "__main__":
    register()
