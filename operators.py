import bpy
import os, json ,ntpath, glob
from bpy_extras.io_utils import ExportHelper, ImportHelper
from bpy.props import StringProperty, BoolProperty, CollectionProperty, EnumProperty
from bpy.types import Operator, OperatorFileListElement
from . import utils

class NODEIOR_OT_template_folder(bpy.types.Operator, ExportHelper):
    bl_idname = "nodeio.template_folder"
    bl_label = "Template Folder"
    bl_description = "Template Folder"

    filename_ext = ".json"

    filter_glob: bpy.props.StringProperty(
        default="*.json",
        options={'HIDDEN'},
        maxlen=255,  # Max internal buffer length, longer would be clamped.
    )  

    filepath = bpy.props.StringProperty(
        default="",
    )

    def execute(self,context):
        objects = bpy.data.objects
        mat_dict = {}

        return {'FINISHED'}

class NODEIO_OT_export(bpy.types.Operator):
    bl_idname = "nodeio.export"
    bl_label = "export nodes"
    bl_description = "export nodes"

    file_name: bpy.props.StringProperty(
        name="file Name", default="")

    @classmethod
    def poll(cls, context):
        return context.active_object is not None

    def execute(self, context):
        NODEIO_properties = bpy.context.scene.NODEIO_properties
        folder = NODEIO_properties.template_folder
        node_tree = context.space_data.edit_tree        
        node_dict = utils.node_tree_to_dict(self.file_name, node_tree)
        
        if os.path.isdir(folder):
            json_file = ('%s/%s.%s' % (folder, self.file_name, 'json') )
            utils.save_dict_to_json(dict_data=node_dict, json_file=json_file)
        
        utils.nodeio_refresh_template_list()
                        
        return {'FINISHED'}

    def invoke(self, context, event):
        wm = context.window_manager
        return wm.invoke_props_dialog(self)
    
class NODEIO_OT_import(bpy.types.Operator):
    bl_idname = "nodeio.import"
    bl_label = "import nodes"
    bl_description = "import nodes"

    def execute(self, context):
        NODEIO_properties = bpy.context.scene.NODEIO_properties
        index = NODEIO_properties.template_list_index
        NODEIO_template_item = bpy.context.scene.NODEIO_template_item
        folder = NODEIO_properties.template_folder

        json_file = "%s/%s" % (folder, NODEIO_template_item[index].file_name)
        dict_data = utils.load_json_to_dict(json_file)
        node_tree = context.space_data.edit_tree
        
        for node in node_tree.nodes:
            node.select = False
        
        utils.dict_to_node_tree(dict_data, node_tree)
        
        return {'FINISHED'}

class NODEIO_OT_refresh_list(bpy.types.Operator):
    bl_idname = "nodeio.refresh_list"
    bl_label = "refresh_list"
    bl_description = "refresh list"

    def execute(self, context):
        utils.nodeio_refresh_template_list()
        return {'FINISHED'}

class NODEIO_OT_delete_template(bpy.types.Operator):
    bl_idname = "nodeio.delete_template"
    bl_label = "delete_template"
    bl_description = "delete template"

    def execute(self, context):
        NODEIO_properties = bpy.context.scene.NODEIO_properties
        index = NODEIO_properties.template_list_index
        NODEIO_template_item = bpy.context.scene.NODEIO_template_item
        folder = NODEIO_properties.template_folder

        json_file = "%s/%s" % (folder, NODEIO_template_item[index].file_name)
        
        utils.remove_file(json_file)
        utils.nodeio_refresh_template_list()
        
        return {'FINISHED'}

# tools
class NODEIO_OT_frame_selected_nodes(bpy.types.Operator):
    bl_idname = "nodeio.frame_selected_nodes"
    bl_label = "Frame selected"
    bl_description = "frame selected nodes"

    def execute(self, context):
        node_tree = context.space_data.edit_tree
        frame = node_tree.nodes.new('NodeFrame')
        frame.label = 'NodeIO_Frame'
        for node in node_tree.nodes:
            if node.select:
                 node.parent = frame
        
        return {'FINISHED'}

class NODEIO_OT_select_framed_nodes(bpy.types.Operator):
    bl_idname = "nodeio.select_framed_nodes"
    bl_label = "Select framed"
    bl_description = "select framed nodes"

    def execute(self, context):
        node_tree = context.space_data.edit_tree
        frames = list()
        selected_nodes = [node for node in node_tree.nodes if node.select]
        [frames.append(node) for node in selected_nodes if node.bl_idname == 'NodeFrame']
        [frames.append(node.parent) for node in node_tree.nodes if node.select and node.parent]
        
        for node in node_tree.nodes:
            if node.parent in frames:
                node.select = True
            elif node in frames:
                node.select = True
            else:
                node.select = False
        
        return {'FINISHED'}

classes = (
    NODEIO_OT_export,
    NODEIO_OT_import,
    NODEIO_OT_refresh_list,
    NODEIO_OT_delete_template,
    NODEIO_OT_frame_selected_nodes,
    NODEIO_OT_select_framed_nodes,
)

def register():
    for cls in classes:
        bpy.utils.register_class(cls)

def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)

if __name__ == '__main__':
    register()
