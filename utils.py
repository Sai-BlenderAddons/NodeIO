# coding=UTF-8

'''
2019/06/05 fix 2.8 api change
colorspace setting move to image node from shader node 
'''

import bpy
import os, json ,ntpath, glob
import re
import uuid

from mathutils import Vector, Color

# Can Global use 
def assign_custom_property_key(key: str, value, node):
    node[key] = value
    return node

def remove_custom_property_key(key: str, node):
    if key in node.keys():
        del node[key]
    return node

def collect_files_in_folder(folder: str, extension: str) -> dict:
    file_list_dict = dict()
    if os.path.isdir(folder):
        file_list = glob.glob("%s/*.%s" % (folder, extension) )
        for item in file_list:
            file_list_dict[ntpath.basename(item)] = item

    return file_list_dict

def node_tree_to_dict(name: str, node_tree: bpy.types.NodeTree) -> dict:
    node_tree_dict = dict()
    node_dict_list = list()
    node_link_list = list()
    node_frame_dict = dict()
    
    node_tree_dict['name'] = name
    node_tree_dict['bl_idname'] = node_tree.bl_idname
    node_tree_dict['type'] = node_tree.type
    node_tree_dict['nodes'] = node_dict_list
    node_tree_dict['links'] = node_link_list
    node_tree_dict['frame'] = node_frame_dict

    for node in node_tree.nodes:
        node['NodeIO_ID'] = "%s_%s" % (node.bl_idname, uuid.uuid4().hex)

        if node.parent:
            node_frame_dict[node['NodeIO_ID']] = node.parent['NodeIO_ID']
            node.parent = None

    for node in node_tree.nodes:
        node_dict=dict()
        properties = node.bl_rna.properties
        for name, prop in node.bl_rna.properties.items():
            if prop.is_readonly:
                if name == 'color_ramp':
                    ramp_dict = dict()
                    points_dict = dict()
                    ramp_dict['points'] = points_dict
                    node_dict[name] = ramp_dict
                    value = getattr(node, name)
                    ramp_dict['interpolation'] = value.interpolation
                    ramp_dict['color_mode'] = value.color_mode
                    for element in value.elements:
                        points_dict[element.position] = element.color[:]
            else:
                value = getattr(node, name)
                if type(value) == Color:
                    node_dict[name] = list(value)
                elif type(value) == Vector:
                    node_dict[name] = list(value)
                elif type(value) == str:
                    node_dict[name] = value
                elif type(value) == bool:
                    node_dict[name] = value
                elif type(value) == float:
                    node_dict[name] = value
                elif type(value) == int:
                    node_dict[name] = value
                else:
                    pass
        # save Node unique ID
        node_dict['NodeIO_ID']  = node['NodeIO_ID']
        
        # inputs
        input_dict=dict()
        slots = [slot for slot in node.inputs if slot.enabled]
        for slot in slots:
            if slot.type == 'VALUE':
                input_dict[slot.name] = slot.default_value
            elif slot.type == 'VECTOR':
                input_dict[slot.name] = [slot.default_value[0], slot.default_value[1], slot.default_value[2]]
            elif slot.type == 'RGBA':
                input_dict[slot.name] = [slot.default_value[0], slot.default_value[1], slot.default_value[2], slot.default_value[3]]
            else:
                print (slot.type)

        node_dict['input'] = input_dict
        node_dict_list.append(node_dict)

    for link in node_tree.links:
        link_dict=dict()
        link_dict['from_node'] = link.from_node['NodeIO_ID']   
        link_dict['from_socket'] = link.from_socket.name
        link_dict['to_node'] = link.to_node['NodeIO_ID']   
        link_dict['to_socket'] = link.to_socket.name
        link_dict['is_muted'] = link.is_muted

        node_link_list.append(link_dict)

    # Remove NodeIO custom property
    for node in node_tree.nodes:
        if 'NodeIO_ID' in node.keys():
            del node['NodeIO_ID']

    return node_tree_dict


def dict_to_node_tree(dict_data: dict, node_tree: bpy.types.NodeTree):
    if node_tree.bl_idname == dict_data['bl_idname']:
        # create node
        for node_dict in dict_data['nodes']:
            node = node_tree.nodes.new(node_dict['bl_idname'])
            node.name = node_dict['NodeIO_ID']
            node.label = node_dict['label']
            node.location = node_dict['location']
            node.mute = node_dict['mute']
            node.use_custom_color = node_dict['use_custom_color']
            node.color = node_dict['color']
            
            # store old node name
            node['NodeIO_name'] = node_dict['name']
            
            # load color ramp
            if 'color_ramp' in node_dict.keys():
                ramp_dict = node_dict['color_ramp']
                node.color_ramp.interpolation = ramp_dict['interpolation']
                node.color_ramp.color_mode = ramp_dict['color_mode']
                points_dict = ramp_dict['points']
                # node.color_ramp.elements
                while len(node.color_ramp.elements) < (len(points_dict)):
                    node.color_ramp.elements.new(0)
                
                index=0
                for point in points_dict:
                    node.color_ramp.elements[index].position = float(point)
                    node.color_ramp.elements[index].color = points_dict[point]
                    index += 1

            # load input default_value
            for key in node_dict['input'].keys():
                # print ("%s : %s" % (key, node_dict['input'][key]) )
                node.inputs[key].default_value = node_dict['input'][key]
                
        # link node    
        for link_dict in dict_data['links']:
            from_node = link_dict['from_node']
            from_socket = link_dict['from_socket']
            to_node = link_dict['to_node']
            to_socket = link_dict['to_socket']
            node_tree.links.new(node_tree.nodes[from_node].outputs[from_socket], node_tree.nodes[to_node].inputs[to_socket])

        # parent frame node
        for node, parent in dict_data['frame'].items():
            node_tree.nodes[node].parent = node_tree.nodes[parent]
            node_tree.nodes[parent].update()
    
        # clean temp data    
        for node in node_tree.nodes:
            if 'NodeIO_name' in node.keys():
                node.name = node['NodeIO_name']
                del node['NodeIO_name']
            if 'NodeIO_ID' in node.keys():
                del node['NodeIO_ID']
        
  
    return node_tree

def dict_to_node_tree_old(dict_data: dict, node_tree: bpy.types.NodeTree):
    if node_tree.bl_idname == dict_data['bl_idname']:
        # create node
        for node_dict in dict_data['nodes']:
            node = node_tree.nodes.new(node_dict['bl_idname'])
            node.name = node_dict['NodeIO_ID']
            node.label = node_dict['label']
            node.location = node_dict['location']
            node.mute = node_dict['mute']
            node.use_custom_color = node_dict['use_custom_color']
            node.color = node_dict['color']
            
            # store old node name
            node['NodeIO_name'] = node_dict['name']
            
            for key in node_dict['input'].keys():
                # print ("%s : %s" % (key, node_dict['input'][key]) )
                node.inputs[key].default_value = node_dict['input'][key]
                
        # link node    
        for link_dict in dict_data['links']:
            from_node = link_dict['from_node']
            from_socket = link_dict['from_socket']
            to_node = link_dict['to_node']
            to_socket = link_dict['to_socket']
            node_tree.links.new(node_tree.nodes[from_node].outputs[from_socket], node_tree.nodes[to_node].inputs[to_socket])

        # parent frame node
        for node, parent in dict_data['frame'].items():
            node_tree.nodes[node].parent = node_tree.nodes[parent]
            node_tree.nodes[parent].update()
    
        # clean temp data    
        for node in node_tree.nodes:
            if 'NodeIO_name' in node.keys():
                node.name = node['NodeIO_name']
                del node['NodeIO_name']
            if 'NodeIO_ID' in node.keys():
                del node['NodeIO_ID']
        
  
    return node_tree

def save_dict_to_json(dict_data: dict, json_file: str):
    with open(json_file, "w") as json_data:
        json.dump(dict_data, json_data)
            
    return json_file

def load_json_to_dict(json_file: str) -> dict:
    dict_data = dict()
    if os.path.isfile(json_file):
        with open(json_file) as json_data:
            dict_data = json.load(json_data)
            
    return dict_data

def remove_file(file_path: str):
    if os.path.isfile(file_path):
        os.remove(file_path) 

def context_collect_objects(mode: str, type: str) -> list:
    ''' mode: "ALL/SELECTION"
        type: "MESH/CURVE/SURFACE/LIGHT...etc"
    '''
    objects = None

    if mode == 'ALL':
        objects = [obj for obj in bpy.context.scene.objects if obj.type == type]
    elif mode == 'SELECTION':
        objects = [obj for obj in bpy.context.selected_objects if obj.type == type]

    return objects

def datablock_op_remove_image(images: list) -> list: 
    '''remove image block, if None remove all image block
    '''
    [bpy.data.images.remove(image) for image in images]

    return bpy.data.images

def datablock_op_fix_image_name() -> list:
    '''force image block name as file name
    '''
    images = [image for image in bpy.data.images if image.name !="Render Result"]
    for image in images:
        image.name = ntpath.basename(image.filepath)

    images = [image for image in bpy.data.images if image.name !="Render Result"]
    return images 

def datablock_collect_materials(mode: str) -> list:
    '''mode: "ALL/SELECTION"
    '''
    objects = None
    materials = None

    if mode == 'ALL':
        materials = bpy.data.materials
    elif mode == 'SELECTION':
        objects = bpy.context.selected_objects
        materials = []
        for obj in objects:
            material_slots = obj.material_slots
            for slot in material_slots:
                if slot.material not in materials:
                    materials.append(slot.material)

    return materials

def datablock_collect_images(mode: str) -> list:
    '''mode: "ALL/SELECTION"
    '''
    images = []

    if mode == 'ALL':
        images = [image for image in bpy.data.images if image.name !="Render Result"]
    elif mode == 'SELECTION':
        materials = []
        objects = bpy.context.selected_objects
        for obj in objects:
            material_slots = obj.material_slots
            for slot in material_slots:
                if slot.material not in materials:
                    materials.append(slot.material)
        
        images = []
        for material in materials:
            node_images = [node.image for node in material.node_tree.nodes if node.type == 'TEX_IMAGE' and node.image is not None]
            [images.append(image) for image in node_images if image not in images]

    return images

def get_name_dict(obj):
    data_dict = {}
    data_dict['OBJECT'] = obj
    data_dict['DATA'] = obj.data
    data_dict['MATERIAL'] = None

    if len(obj.material_slots) > 0:
        if obj.material_slots[0].material:
            data_dict['MATERIAL'] = obj.material_slots[0].material

    return data_dict

def get_preferences():
    name = get_addon_name()
    return bpy.context.user_preferences.addons[name].preferences

def get_addon_name():
    return os.path.basename(os.path.dirname(os.path.realpath(__file__)))

def opacity_material(material):
    material.blend_method = "BLEND"

def not_opacity_material(material):
    material.blend_method = "OPAQUE"
    material.show_transparent_back = False

def hide_shader_scoket(shader_node, status=True):
    for input in shader_node.inputs:
        input.hide = status

def offset_node_loaction(origin, x_offset, y_offset):
    new_loaction = (origin.x + x_offset, origin.y + y_offset)
    return new_loaction

## for NodeIO
def nodeio_add_nodes_custom_property(node_tree):
    for node in node_tree.nodes:
        node['NodeIO_ID'] = "%s_%s" % (node.bl_idname, uuid.uuid4().hex)
        
    return node_tree

def nodeio_del_nodes_custom_property(node_tree):
    for node in node_tree.nodes:
        if 'NodeIO_ID' in node.keys():
            del node['NodeIO_ID']
            
    return node_tree

def nodeio_refresh_template_list():
    NODEIO_properties = bpy.context.scene.NODEIO_properties
    NODEIO_template_item = bpy.context.scene.NODEIO_template_item
    NODEIO_template_item.clear()
    
    files_dict = collect_files_in_folder(NODEIO_properties.template_folder, "json")
    for key in files_dict:
        item = NODEIO_template_item.add()
        item.file_name = key