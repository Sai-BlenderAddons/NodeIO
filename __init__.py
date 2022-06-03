# coding=UTF-8

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTIBILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.
# last update: 2021/08/10


bl_info = {
    "name" : "NodeIO",
    "author" : "Sai Ling",
    "description": "Import/Export Node To Json",
    "version": (0, 1, 0),
    "blender" : (3, 1, 0),
    "location": "Node Editor > Sidebar",
    "warning" : "",
    "wiki_url": "https://github.com/Sai-BlenderAddons/NodeIO",
    "category" : "Generic"
}

import os
import bpy

from . import ui, utils, operators, properties

classes = ()

def register():
    properties.register()
    operators.register()
    ui.register()

    for cls in classes:
        bpy.utils.register_class(cls)

def unregister():
    properties.unregister()
    operators.unregister()
    ui.unregister()
    
    for cls in classes:
        bpy.utils.unregister_class(cls)

if __name__ == '__main__':
    register()
