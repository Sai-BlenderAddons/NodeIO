import bpy
from bpy.types import Operator, AddonPreferences, Panel, PropertyGroup
from bpy.props import StringProperty, BoolProperty, IntProperty, CollectionProperty, BoolVectorProperty, PointerProperty, EnumProperty

class ITEM_UL_items(bpy.types.UIList):

    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        self.use_filter_show = True
        self.use_filter_sort_alpha = True
        row = layout.row()
        row.label(text=item.file_name)

class NODEIO_MT_list_menu(bpy.types.Menu):
    bl_idname = 'NODEIO_MT_list_menu'
    bl_label = 'Edit'

    def draw(self, context):
        layout = self.layout


class NODEIO_PT_panel(bpy.types.Panel):
    bl_space_type = "NODE_EDITOR"
    bl_region_type = "UI"
    bl_category = "NodeIO"
    bl_label = "NodeIO"
    # bl_options = {"DEFAULT_CLOSED"}   
    def draw(self,context):
        pass

class NODEIO_PT_manager(bpy.types.Panel):
    bl_label = "NodeIO Manager"
    bl_space_type = "NODE_EDITOR"
    bl_region_type = "UI"
    bl_category = "NodeIO"
    # bl_parent_id = "NODEIO_PT_panel"
    bl_options = {"DEFAULT_CLOSED"}   
    
    def draw(self,context):
        NODEIO_properties = context.scene.NODEIO_properties
        NODEIO_template_item = context.scene.NODEIO_template_item
        layout = self.layout
        layout.use_property_split = True
        row = layout.row(align = True)
        col = row.column()
        col.prop(NODEIO_properties, 'template_folder')
        row = layout.row()
        row.template_list("ITEM_UL_items", "", context.scene, "NODEIO_template_item", NODEIO_properties, "template_list_index", rows=6)
        col = row.column(align=True)
        col.operator("nodeio.export", icon='EXPORT', text="")
        col.operator("nodeio.import", icon='IMPORT', text="")
        col.operator("nodeio.refresh_list", icon='FILE_REFRESH', text="")
        col.operator("nodeio.delete_template", icon='X', text="")
        col.separator()
        col.menu("NODEIO_MT_list_menu", text='', icon='DOWNARROW_HLT')

class NODEIO_PT_tools(bpy.types.Panel):
    bl_label = "NodeIO Tools"
    bl_space_type = "NODE_EDITOR"
    bl_region_type = "UI"
    bl_category = "NodeIO"
    # bl_parent_id = "NODEIO_PT_panel"
    bl_options = {"DEFAULT_CLOSED"}  
    
    def draw(self,context):
        layout = self.layout
        layout.use_property_split = True
        row = layout.row(align = True)
        col = row.column()
        col.operator("nodeio.frame_selected_nodes")
        col.operator("nodeio.select_framed_nodes")

classes = (
    # NODEIO_PT_panel,
    ITEM_UL_items,
    NODEIO_MT_list_menu,
    NODEIO_PT_manager,
    NODEIO_PT_tools,

)

def register():
    for cls in classes:
        bpy.utils.register_class(cls)

def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)

if __name__ == '__main__':
    register()
