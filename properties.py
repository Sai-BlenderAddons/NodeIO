import bpy
from bpy.props import StringProperty, BoolProperty, EnumProperty, FloatProperty, IntProperty, BoolVectorProperty
from . import utils

def update_items(self, context):
    utils.nodeio_refresh_template_list()


class NODEIO_properties(bpy.types.PropertyGroup):

    template_folder : StringProperty(
        default = r"//NodeTemplate\\",
        subtype="DIR_PATH",
        name = "Template Folder",
        update = update_items,
    )
    template_list_index: IntProperty(default=-1)
    
class NODEIO_template_item(bpy.types.PropertyGroup):
    file_name: StringProperty(default= "")

classes = (
    NODEIO_properties,
    NODEIO_template_item,
)

def register():
    for cls in classes:
        bpy.utils.register_class(cls)

    bpy.types.Scene.NODEIO_properties = bpy.props.PointerProperty(type=NODEIO_properties)
    bpy.types.Scene.NODEIO_template_item = bpy.props.CollectionProperty(type=NODEIO_template_item)

def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)

    del bpy.types.Scene.NODEIO_properties
    del bpy.types.Scene.NODEIO_template_item

if __name__ == '__main__':
    register()
