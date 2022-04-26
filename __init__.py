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

bl_info = {
    "name" : "NX_Labyrinthe",
    "author" : "neXXen",
    "description" : "",
    "blender" : (3, 1, 0),
    "version" : (1, 1, 0),
    "location" : "",
    "warning" : "",
    "category" : "Generic"
}

import time
import bpy
from bpy.types import Panel
from . nxlab_op import OBJECT_OT_Create_Labyrinthe, OBJECT_OT_New_Labyrinthe, OBJECT_OT_Update_Labyrinthe


class NXLAB_PT_control_panel(Panel):
    """Creates a Panel in the Object properties window"""
    bl_label = "NX Labyrinthe"
    bl_idname = 'NXLAB_PT_control_panel'
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'NX_Tools'
    
    @classmethod
    def poll(cls, context):
        return context.mode == 'OBJECT'

    def draw(self, context):
        scene = context.scene
        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = False
        
        col = layout.column()

        if self.is_laby(context):
            obj = context.object
            nodes = obj.modifiers['NX_LABYRINTHE'].node_group.nodes
            
            col.prop(obj.NXLab, 'x', text="Cells X")
            col.prop(obj.NXLab, 'y', text="Cells Y")
            col.prop(obj.NXLab, 'cellSize', text="Cell Size")
            col.separator()

            row = layout.row()
            row.prop(obj.NXLab, 'orientation', text="Orientation", expand=True)

            col = layout.column()
            if obj.NXLab.orientation != 'NONE':
                col.enabled = True
            else:
                col.enabled = False
            col.prop(obj.NXLab, 'orientationStrength', text="Orientation Strength")

            col = layout.column()

            col.separator()
            col.prop(obj.NXLab, 'height', text="Wall Height")
            col.prop(obj.NXLab, 'thickness', text="Wall Thickness")

            col.separator()
            col.prop(obj.NXLab, 'corner', text="Corner")
            col = layout.column()
            if obj.NXLab.corner:
                col.enabled = True
            else:
                col.enabled = False
            col.prop(obj.NXLab, 'radius', text="Radius")
            col.prop(obj .NXLab, 'segments', text="Segments")

            col = layout.column()
            col.separator()
            col.prop(obj.NXLab, 'issues', text="Exits")

            col.separator()
            row = layout.row(align=False)
            
            op = row.operator('object.update_labyrinthe', text="Update")
            op.cellSize = obj.NXLab.cellSize
            op.corner = obj.NXLab.corner
            op.radius = obj.NXLab.radius
            op.segments = obj.NXLab.segments
            op.height = obj.NXLab.height
            op.thickness = obj.NXLab.thickness
            op.issues = obj.NXLab.issues

            op = row.operator('object.new_labyrinthe', text="New Labyinthe")
            op.x = obj.NXLab.x
            op.y = obj.NXLab.y
            op.orientation = obj.NXLab.orientation
            op.orientationStrength = obj.NXLab.orientationStrength
            op.cellSize = obj.NXLab.cellSize
            op.corner = obj.NXLab.corner
            op.radius = obj.NXLab.radius
            op.segments = obj.NXLab.segments
            op.height = obj.NXLab.height
            op.thickness = obj.NXLab.thickness
            op.issues = obj.NXLab.issues
        else:
            col.prop(scene.NXLab, 'x', text="Size X")
            col.prop(scene.NXLab, 'y', text="Size Y")
            col.prop(scene.NXLab, 'cellSize', text="Cell Size")
            col.separator()

            row = layout.row()
            row.prop(scene.NXLab, 'orientation', text="Orientation", expand=True)

            col = layout.column()
            if scene.NXLab.orientation != 'NONE':
                col.enabled = True
            else:
                col.enabled = False
            col.prop(scene.NXLab, 'orientationStrength', text="Orientation Strength")

            col = layout.column()
            col.separator()
            col.prop(scene.NXLab, 'height', text="Wall Height")
            col.prop(scene.NXLab, 'thickness', text="Wall Thickness")

            col.separator()
            col.prop(scene.NXLab, 'corner', text="Corner")
            col = layout.column()
            if scene.NXLab.corner:
                col.enabled = True
            else:
                col.enabled = False
            col.prop(scene.NXLab, 'radius', text="Radius")
            col.prop(scene.NXLab, 'segments', text="Segments")

            col = layout.column()
            col.separator()
            col.prop(scene.NXLab, 'issues', text="Exits")

            col = layout.column()
            op = col.operator('object.create_labyrinthe')
            op.x = scene.NXLab.x
            op.y = scene.NXLab.y
            op.orientation = scene.NXLab.orientation
            op.orientationStrength = scene.NXLab.orientationStrength
            op.cellSize = scene.NXLab.cellSize
            op.corner = scene.NXLab.corner
            op.radius = scene.NXLab.radius
            op.segments = scene.NXLab.segments
            op.height = scene.NXLab.height
            op.thickness = scene.NXLab.thickness
            op.issues = scene.NXLab.issues
            op.entrance.axe = scene.NXLab.entrance.axe
            op.entrance.number = scene.NXLab.entrance.number
            op.exit.axe = scene.NXLab.exit.axe
            op.exit.number = scene.NXLab.exit.number

    
    def is_laby(self, context):
        if context.object is not None and 'NX_LABYRINTHE' in context.object.modifiers:
            return True
        return False


class NXLabIssueProperty(bpy.types.PropertyGroup):
    axe: bpy.props.StringProperty(name="axe", default="N")
    number: bpy.props.IntProperty(name="number", default=0, min=0)


bpy.utils.register_class(NXLabIssueProperty)


class NXLabPropertyGroup(bpy.types.PropertyGroup):
    x: bpy.props.IntProperty(name="X", default=2, min=2)
    y: bpy.props.IntProperty(name="Y", default=2, min=2)
    cellSize: bpy.props.FloatProperty(name="cellSize", default=0.25, min=0, step=10)
    corner: bpy.props.BoolProperty(name="corner", default=False)
    radius: bpy.props.FloatProperty(name="radius", default=0, min=0, step=1)
    segments: bpy.props.IntProperty(name="segments", default=1, min=1, max=1000, step=1)
    height: bpy.props.FloatProperty(name="height", default=0, min=0, step=10)
    thickness: bpy.props.FloatProperty(name="thickness", default=0, min=0, step=1)
    orientation: bpy.props.EnumProperty(
        name='Orientation',
        items={
            ('NONE', 'None', '', '', 0),
            ('X', 'X', '', '', 1),
            ('Y', 'Y', '', '', 2)
        },
        default='NONE'
    )
    orientationStrength: bpy.props.IntProperty(name="Orientation Strength", default=1, min=1, max=10)
    issues: bpy.props.BoolProperty(name='issues', default=False)
    entrance: bpy.props.PointerProperty(type=NXLabIssueProperty)
    exit: bpy.props.PointerProperty(type=NXLabIssueProperty)


bpy.utils.register_class(NXLabPropertyGroup)

bpy.types.Scene.NXLab = bpy.props.PointerProperty(type=NXLabPropertyGroup)
bpy.types.Object.NXLab = bpy.props.PointerProperty(type=NXLabPropertyGroup)

classes = [
    OBJECT_OT_Create_Labyrinthe,
    OBJECT_OT_New_Labyrinthe,
    OBJECT_OT_Update_Labyrinthe,
    NXLAB_PT_control_panel,
]

def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    

def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)

if __name__ == "__main__":
    register()
