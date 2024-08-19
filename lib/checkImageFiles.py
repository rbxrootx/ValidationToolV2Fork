import bpy
import os
import glob

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




def checkImageFiles(path, checkMode):  
    wrongFormat = []
    wrongSize = []
    files = []
    if path != "":
        absPath = bpy.path.abspath(path)
        filepath = os.path.join(absPath, "*.png")
        files = glob.glob(filepath)
    
    materials = bpy.data.materials
    for mat in materials:
        nodeTree = mat.node_tree
        if nodeTree != None:
            for node in nodeTree.nodes:
                if node.bl_idname == "ShaderNodeTexImage":
                    if node.image != None:
                        filepath = bpy.path.abspath(node.image.filepath)
                        imageFile = glob.glob(filepath)
                        if len(imageFile) != 0:
                            files.append(node.image.filepath)

    for file in files:
        fileName = os.path.basename(file)
        img = bpy.data.images.load(file)
        
        depth = img.depth
        if ("_ALB" in fileName) or ("_NOR" in fileName):
            if depth != 24:
                wrongFormat.append(fileName + " is not 24bit")
        elif ("_MET" in fileName) or ("_RGH" in fileName):
            if depth != 8:
                wrongFormat.append(fileName + " is not 8bit")
        else:
            if depth != 24:
                wrongFormat.append(fileName + " is not 24bit")
        
        size = img.size[0]
        if (size > 0) and (size & (size - 1 )) == 0:
            if checkMode == "0":
                if (size != 1024) or (size != img.size[1]):
                    wrongSize.append(fileName + " should be 1024 px")
            else:
                if 256 <= size <= 1024:
                    if size != img.size[1]:
                        wrongSize.append(fileName + " should be within 1024 px")  
                else:
                    wrongSize.append(fileName + " is wrong texture size")
        else:
            wrongSize.append(fileName + " is wrong texture size")
        
        iamges = bpy.data.images
        iamges.remove(img, do_unlink=True)


    
    if len(wrongFormat) != 0 or len(wrongSize) != 0:
        return [wrongFormat, wrongSize]
    else:
        return True
        


def checkImagesInFolder(scn, path):
    imageformatResults = checkImageFiles(path, scn.checkMode)
    if imageformatResults == True:
        message = ["Texture format is ok."]
        scn.checkResult_ImageFormat = True
    else:
        message = ["Following image files does not meet image format."]
        scn.checkResult_ImageFormat = False
        wrongDepth = imageformatResults[0]
        wrongSize = imageformatResults[1]
        if len(wrongDepth) != 0:
            message.append("COLOR DEPTH ERRORS")
            for f in wrongDepth:
                message.append(f)
                add_item(scn.custom, "ColorDepth", f)
            message.append(" ")
            
        if len(wrongSize) != 0:
            message.append("SIZE ERRORS")
            for f in wrongSize:
                message.append(f)
                add_item(scn.custom, "ImageSize", f)
            message.append(" ")
        scn.checkResult_All = True
    return message



class Check_ImageFiles(bpy.types.Operator):
    bl_idname = "mesh.checkimagefiles"
    bl_label = "Check ImageFiles data in the scene"
    bl_description = "Check ImageFiles data in the scene"


    def execute(self, context):
        scn = context.scene
        path = context.scene.texture_folder
        remove_item(scn.custom, "ColorDepth")
        remove_item(scn.custom, "ImageSize")
        message = checkImagesInFolder(scn, path)
        if scn.checkingAll == False:
            ShowMessageBox(message)

        return{"FINISHED"}