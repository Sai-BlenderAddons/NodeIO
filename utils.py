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
    # node_tree init
    node_tree_dict = dict()
    node_tree_dict['name'] = name
    node_tree_dict['bl_idname'] = node_tree.bl_idname
    node_tree_dict['type'] = node_tree.type
    # node tree nodes
    node_dict_list = list()
    node_link_list = list()
    node_tree_dict['nodes'] = node_dict_list
    node_tree_dict['links'] = node_link_list
    # generate unique node id and temp data
    nodes = node_tree.nodes
    for node in nodes:
        node['NodeIO_ID'] = "%s_%s" % (node.bl_idname, uuid.uuid4().hex)
        # node.name = node['NodeIO_ID']
        
    # save node links    
    for link in node_tree.links:
        link_dict=dict()
        link_dict['from_node'] = link.from_node['NodeIO_ID']   
        link_dict['from_socket'] = link.from_socket.name
        link_dict['to_node'] = link.to_node['NodeIO_ID']   
        link_dict['to_socket'] = link.to_socket.name
        link_dict['is_muted'] = link.is_muted

        node_link_list.append(link_dict)
        
    for node in nodes:
        node_dict=dict()
        # save parent
        if node.parent:
            node_dict['NodeIO_parent'] = node.parent['NodeIO_ID']
            node['NodeIO_parent'] = node.parent.name
        node.parent = None
        
        properties = node.bl_rna.properties
        for attr_name, prop in node.bl_rna.properties.items():
            if prop.is_readonly:
                # ramp
                if attr_name == 'color_ramp':
                    ramp_dict = dict()
                    points_dict = dict()
                    ramp_dict['points'] = points_dict
                    node_dict[attr_name] = ramp_dict
                    ramp = getattr(node, attr_name)
                    ramp_dict['interpolation'] = ramp.interpolation
                    ramp_dict['color_mode'] = ramp.color_mode
                    for element in ramp.elements:
                        points_dict[element.position] = element.color[:]
                # curve
                elif attr_name == 'mapping':
                    # print (attr_name, type(value))
                    mapping_dict = dict()
                    curve_dict = dict()
                    node_dict[attr_name] = mapping_dict
                    mapping_dict['curves'] = curve_dict
                    mapping = getattr(node, attr_name)
                    mapping_dict['use_clip'] = mapping.use_clip
                    mapping_dict['clip_max_x'] = mapping.clip_max_x
                    mapping_dict['clip_max_y'] = mapping.clip_max_y
                    mapping_dict['clip_min_x'] = mapping.clip_min_x
                    mapping_dict['clip_min_y'] = mapping.clip_min_y
                    mapping_dict['extend'] = mapping.extend
                    mapping_dict['tone'] = mapping.tone
                    mapping_dict['black_level'] = mapping.black_level[:]
                    mapping_dict['white_level'] = mapping.white_level[:]
                    for curve_index in range(0, len(mapping.curves)):
                        curve = mapping.curves[curve_index]
                        points = curve.points
                        points_list = list()
                        for point_index in range(0, len(points)):
                            point_dict = dict()
                            point_dict['location'] = points[point_index].location[:]
                            point_dict['handle_type'] = points[point_index].handle_type
                            point_dict['select'] = points[point_index].select
                            points_list.append(point_dict)
                        curve_dict[curve_index] = points_list
            else:
                value = getattr(node, attr_name)
                if type(value) == Color:
                    node_dict[attr_name] = list(value)
                elif type(value) == Vector:
                    node_dict[attr_name] = list(value)
                elif type(value) == str:
                    node_dict[attr_name] = value
                elif type(value) == bool:
                    node_dict[attr_name] = value
                elif type(value) == float:
                    node_dict[attr_name] = value
                elif type(value) == int:
                    node_dict[attr_name] = value
                elif attr_name == 'object':
                    string = ''
                    if type(value) == bpy.types.Object:
                        string = value.name
                    node_dict[attr_name] = string
                elif attr_name == 'particle_system':
                    string = ''
                    if type(value) == bpy.types.ParticleSystem:
                        string = value.name
                    node_dict[attr_name] = string
                else:
                    # print (type(value))
                    pass
        # save inputs
        inputs_dict=dict()
        inputs = [inputa for inputa in node.inputs if inputa.enabled]
        for inputa in inputs:
            if inputa.type == 'VALUE':
                inputs_dict[inputa.name] = inputa.default_value
            elif inputa.type == 'VECTOR':
                inputs_dict[inputa.name] = [inputa.default_value[0], inputa.default_value[1], inputa.default_value[2]]
            elif inputa.type == 'RGBA':
                inputs_dict[inputa.name] = [inputa.default_value[0], inputa.default_value[1], inputa.default_value[2], inputa.default_value[3]]
            elif inputa.type == 'STRING':
                inputs_dict[inputa.name] = inputa.default_value
            else:
                # print (node.name, inputa.type)
                pass
        
        outputs_dict=dict()
        outputs = [output for output in node.outputs if output.enabled]
        for output in outputs:
            if output.type == 'VALUE':
                outputs_dict[output.name] = output.default_value
            elif output.type == 'VECTOR':
                outputs_dict[output.name] = [output.default_value[0], output.default_value[1], output.default_value[2]]
            elif output.type == 'RGBA':
                outputs_dict[output.name] = [output.default_value[0], output.default_value[1], output.default_value[2], output.default_value[3]]
            elif output.type == 'STRING':
                outputs_dict[output.name] = output.default_value
            else:
                # print (node.name, value.type)
                pass
        # store data to dict
        node_dict['inputs'] = inputs_dict
        node_dict['outputs'] = outputs_dict
        node_dict['NodeIO_ID']  = node['NodeIO_ID']
        node_dict_list.append(node_dict)
            
    # clear temp data
    for node in nodes:
        if 'NodeIO_parent' in node.keys():
            node.parent = nodes[node['NodeIO_parent']]
            del node['NodeIO_parent']
        if 'NodeIO_ID' in node.keys():
            del node['NodeIO_ID']
            
    return node_tree_dict


def dict_to_node_tree(dict_data: dict, node_tree: bpy.types.NodeTree):
    if node_tree.bl_idname == dict_data['bl_idname']:
        # create node
        for node_dict in dict_data['nodes']:
            node = node_tree.nodes.new(node_dict['bl_idname'])
            properties = node.bl_rna.properties
            for attr_name, prop in node.bl_rna.properties.items():
                if prop.is_readonly:
                    pass
                else:
                    value = getattr(node, attr_name)
                    if attr_name in node_dict.keys():
                        # by attribute type
                        if type(value) == Color:
                            setattr(node, attr_name, node_dict[attr_name])
                        elif type(value) == Vector:
                            setattr(node, attr_name, node_dict[attr_name])
                        elif type(value) == str:
                            setattr(node, attr_name, node_dict[attr_name])
                        elif type(value) == bool:
                            setattr(node, attr_name, node_dict[attr_name])
                        elif type(value) == float:
                            setattr(node, attr_name, node_dict[attr_name])
                        elif type(value) == int:
                            setattr(node, attr_name, node_dict[attr_name])
                        # by attribute.name
                        elif attr_name == 'object':
                            obj = bpy.data.objects.get(node_dict[attr_name])
                            setattr(node, attr_name, obj)
                        elif attr_name == 'particle_system':
                            obj = bpy.data.particles.get(node_dict[attr_name])
                            setattr(node, attr_name, obj)

                        else:
                            print (attr_name, type(value), node_dict[attr_name])
                            pass
            # store temp data in node
            if 'NodeIO_parent' in node_dict.keys():
                node['NodeIO_parent'] = node_dict['NodeIO_parent']
            node['NodeIO_ID'] = node_dict['NodeIO_ID']
            
            # load color ramp
            if 'color_ramp' in node_dict.keys():
                ramp_dict = node_dict['color_ramp']
                node.color_ramp.interpolation = ramp_dict['interpolation']
                node.color_ramp.color_mode = ramp_dict['color_mode']
                points_dict = ramp_dict['points']
                # node.color_ramp.elements 
                elements = node.color_ramp.elements
                while len(elements) < (len(points_dict)):
                    elements.new(0)
                index=0
                for point in points_dict:
                    elements[index].position = float(point)
                    elements[index].color = points_dict[point]
                    index += 1
                elements.update()
            if 'mapping' in node_dict.keys():
                mapping_dict = node_dict['mapping']
                mapping = node.mapping
                mapping.use_clip = mapping_dict['use_clip']
                mapping.clip_max_x = mapping_dict['clip_max_x']
                mapping.clip_max_y = mapping_dict['clip_max_y']
                mapping.clip_min_x = mapping_dict['clip_min_x']
                mapping.clip_min_y = mapping_dict['clip_min_y']
                mapping.extend = mapping_dict['extend']
                mapping.tone = mapping_dict['tone']
                mapping.black_level = mapping_dict['black_level']
                mapping.white_level = mapping_dict['white_level']
                # node.mapping.curves.points 
                curves = node.mapping.curves
                curves_dict = mapping_dict['curves']
                for curve_index in range(0, len(curves)):
                    curve = curves[curve_index]
                    point_list = curves_dict[str(curve_index)]
                    while len(curve.points) < (len(point_list)):
                        curve.points.new(0, 0)
                    index=0
                    for point in point_list:
                        curve.points[index].location = point['location']
                        curve.points[index].handle_type = point['handle_type']
                        curve.points[index].select = point['select']
                        index += 1
                mapping.update()
                
            # load input default_value
            for key in node_dict['inputs'].keys():
                # print ("%s : %s" % (key, node_dict['input'][key]) )
                node.inputs[key].default_value = node_dict['inputs'][key]
            for key in node_dict['outputs'].keys():
                # print ("%s : %s" % (key, node_dict['input'][key]) )
                node.outputs[key].default_value = node_dict['outputs'][key]

        # link node    
        for link_dict in dict_data['links']:
            from_node = get_node_by_NodeIO_ID(link_dict['from_node'], node_tree.nodes)
            from_socket = link_dict['from_socket']
            to_node = get_node_by_NodeIO_ID(link_dict['to_node'], node_tree.nodes)
            to_socket = link_dict['to_socket']
            node_tree.links.new(from_node.outputs[from_socket], to_node.inputs[to_socket])

        # parent frame node
        children =  [node for node in node_tree.nodes if 'NodeIO_parent' in node.keys()]
        frames = [node for node in node_tree.nodes if 'NodeIO_ID' in node.keys() and node.bl_idname == 'NodeFrame']
        for node in children:
            frame = [frame for frame in frames if frame['NodeIO_ID'] == node['NodeIO_parent']][0]
            node.parent = frame
            
        # clean temp data    
        for node in node_tree.nodes:
            if 'NodeIO_parent' in node.keys():
                del node['NodeIO_parent']
            if 'NodeIO_ID' in node.keys():
                del node['NodeIO_ID']
        
  
    return node_tree

def get_node_by_NodeIO_ID(node_io_id: str, nodes: list) -> object:
    result_node = None
    for node in nodes:
        if 'NodeIO_ID' in node.keys():
            if node['NodeIO_ID'] == node_io_id:
                result_node = node 
    return result_node

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