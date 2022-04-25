import logging
import time
from random import randint
import bpy
from bpy.types import Operator
from .lib.labyrinthe import Labyrinthe
from .lib.node import Node

class NXLabIssueProperty(bpy.types.PropertyGroup):
    axe: bpy.props.StringProperty(name="axe", default="N")
    number: bpy.props.IntProperty(name="number", default=0, min=0)


bpy.utils.register_class(NXLabIssueProperty)
  
class NXLabyrinthe:
  x: bpy.props.IntProperty(name="X", default=0)
  y: bpy.props.IntProperty(name="Y", default=0)
  cellSize: bpy.props.FloatProperty(name="cellSize", default=0)
  corner: bpy.props.BoolProperty(name="corner", default=False)
  radius: bpy.props.FloatProperty(name="radius", default=0)
  segments: bpy.props.IntProperty(name="segments", default=0)
  height: bpy.props.FloatProperty(name="height", default=0)
  thickness: bpy.props.FloatProperty(name="thickness", default=0)
  orientation: bpy.props.EnumProperty(
        name='Orientation',
        items={
            ('NONE', 'None', '', '', 0),
            ('X', 'X', '', '', 1),
            ('Y', 'Y', '', '', 2)
        },
        default='NONE'
  )
  orientationStrength: bpy.props.IntProperty(name='Orientation Strength', default=1)
  issues: bpy.props.BoolProperty(name='issues', default=False)
  entrance: bpy.props.PointerProperty(type=NXLabIssueProperty)
  exit: bpy.props.PointerProperty(type=NXLabIssueProperty)

  offset = 50
  obj = None
  laby = None
  lastSelector = None

  def edgeSelect(self, nodeGroup):
    if 'Group Input' in nodeGroup.nodes:
      nodeGroup.nodes.remove(nodeGroup.nodes['Group Input'])
    
    _in = Node(nodeGroup, 'NodeGroupInput')

    b = Node(nodeGroup, 'FunctionNodeBooleanMath', values={'operation': 'OR'})
    b.location(x=(_in.x() + b.width() + self.offset), y=b.height())
    b.link(1, _in.output(0))

    c = Node(nodeGroup, 'FunctionNodeCompare', values={'operation': 'EQUAL'})
    c.location(x=(_in.x() + c.width() + self.offset), y=-(c.height()))
    c.link(0, _in.output(1))
    c.link(1, _in.output(2))
    
    b.link(0, c.output(0))  
    
    _out = Node(nodeGroup, 'NodeGroupOutput')
    _out.location(x=(c.x() + _out.width() + self.offset))
    _out.link(0, b.output(0))
    _out.link(1, _in.output(1))
  
  def edgesRange(self, nodeGroup):
    if 'Group Input' in nodeGroup.nodes:
      nodeGroup.nodes.remove(nodeGroup.nodes['Group Input'])
    
    _in = Node(nodeGroup, 'NodeGroupInput')

    _or = Node(nodeGroup, 'FunctionNodeBooleanMath', values={'operation': 'OR'})
    _or.link(1, _in.output(0))

    greaterEqual = Node(nodeGroup, 'FunctionNodeCompare', values={'operation': 'GREATER_EQUAL'})
    greaterEqual.location(x=(_in.x() + greaterEqual.width() + self.offset), y=greaterEqual.height())
    greaterEqual.link(0, _in.output(1))
    greaterEqual.link(1, _in.output(2))

    lessEqual = Node(nodeGroup, 'FunctionNodeCompare', values={'operation': 'LESS_EQUAL'})
    lessEqual.location(x=(_in.x() + lessEqual.width() + self.offset), y=-(lessEqual.height()))
    lessEqual.link(0, _in.output(1))
    lessEqual.link(1, _in.output(3))

    _and = Node(nodeGroup, 'FunctionNodeBooleanMath', values={'operation': 'AND'})
    _and.location(x=(greaterEqual.x() + _and.width() + self.offset), y=greaterEqual.y())
    _and.link(0, greaterEqual.output(0))
    _and.link(1, lessEqual.output(0))

    _or.location(x=(_and.x() + _or.width() + self.offset))
    _or.link(0, _and.output(0))

    _out = Node(nodeGroup, 'NodeGroupOutput')
    _out.location(x=(_or.x() + _out.width() + self.offset))
    _out.link(0, _or.output(0))
    _out.link(1, _in.output(1))

  def labCorner(self, nodeGroup):
    if 'Group Input' in nodeGroup.nodes:
      nodeGroup.nodes.remove(nodeGroup.nodes['Group Input'])

    _in = Node(nodeGroup, 'NodeGroupInput')

    delGeo = Node(nodeGroup, 'GeometryNodeDeleteGeometry', values={'domain': 'EDGE'})
    delGeo.location(x=(delGeo.width() + self.offset), y=-(1*delGeo.height()))
    delGeo.link(0, _in.output(0))
    delGeo.link(1, _in.output(1))

    mtc = Node(nodeGroup, 'GeometryNodeMeshToCurve')
    mtc.location(x=(delGeo.x() + mtc.width() + self.offset), y=delGeo.y())
    mtc.link(0, delGeo.output(0))

    filet = Node(nodeGroup, 'GeometryNodeFilletCurve', values={'mode': 'POLY'})
    filet.location(x=(mtc.x() + filet.width() + self.offset), y=mtc.y())
    filet.link(0, mtc.output(0))

    ctm = Node(nodeGroup, 'GeometryNodeCurveToMesh')
    ctm.location(x=(filet.x() + ctm.width() + self.offset), y=filet.y())
    ctm.link(0, filet.output(0))

    _switch = Node(nodeGroup, 'GeometryNodeSwitch', values={'input_type': 'GEOMETRY'})
    _switch.location(x=(ctm.x() + _switch.width() + 2*self.offset))
    _switch.link(1, _in.output(2))
    _switch.link(14, delGeo.output(0))
    _switch.link(15, ctm.output(0))

    filet.link(1, _in.output(3))
    filet.link(2, _in.output(4))

    _out = Node(nodeGroup, 'NodeGroupOutput')
    _out.location(x=(_switch.x() + _out.width() + self.offset))
    _out.link(0, _switch.output(6))

  def getEdgesToDelete(self):
    
    ids = []
    for i in range(self.laby.w):
      for j in range(self.laby.h):
        cell = (self.laby.getCell(i,j))
        if i < self.laby.w - 1 and cell['E']:
          id = (i + 1) * self.laby.h + j
          if id not in ids:
            ids.append(id)
        if j < self.laby.h -1 and cell['N']:
          id = (((self.laby.w + 1) * self.laby.h)) + (j + 1) * self.laby.w + i 
          if id not in ids:
            ids.append(id) 
    
    ids.sort()
    ids_group = []

    print('NUMBER EDGES TO DELETE', len(ids))

    for id in ids:
      if (id - 1) in ids_group:
        ids_group.append((id - 1, id))
        ids_group.remove(id -1)
      else:
        increase = False
        for key, id_group in enumerate(ids_group):
          if not isinstance(id_group, int) and id_group[1] == id - 1:
            ids_group[key] = (id_group[0], id)
            increase = True
            break
        if not increase:
          ids_group.append(id)

    return ids_group

  def trace1(self, node_group):

    start_time = time.time()
    print('TRACE 1...')
    nodes = node_group.nodes
    links = node_group.links
    
    prevNode = None

    ids = self.getEdgesToDelete()

    for id in ids:
      if isinstance(id, int):
        ng = Node(node_group, 'GeometryNodeGroup',
          name='NX_EdgeSelector', nodeGroup='NX_EdgeSelector', callback=(self, 'edgeSelect'))
        ng.node().inputs[2].default_value = id
      else:
        ng = Node(node_group, 'GeometryNodeGroup',
          name='NX_EdgesRange', nodeGroup='NX_EdgesRange', callback=(self, 'edgesRange'))
        ng.node().inputs[2].default_value = id[0]
        ng.node().inputs[3].default_value = id[1]

      if prevNode is None:
        dg = nodes['Delete Geometry']
        index = Node(node_group, 'GeometryNodeInputIndex')
        index.location(x=dg.location.x, y=(dg.location.y - index.height() - (2*self.offset)))
        output_index = index.output(0) 
        ng.location(x=(index.x() + dg.width + self.offset), y=index.y())
      else:
        output_index = prevNode.output(1)
        output_bool = prevNode.output(0)
        input_bool = ng.input(0)
        links.new(output_bool, input_bool)
        ng.location(x=(prevNode.x() + dg.width + self.offset), y=prevNode.y())
        
      links.new(output_index, ng.input(1))
        
      prevNode = ng

    if prevNode is not None:
      dg = nodes['Delete Geometry']
      
      corner = nodes['LabCorner']
      corner.location.x = prevNode.x() + corner.width + self.offset

      links.new(corner.inputs[0], dg.outputs[0])
      links.new(corner.inputs[1], prevNode.output(0))
      
      out = nodes['Group Output']
      out.location.x = corner.location.x + out.width + self.offset
      out.location.y = corner.location.y
      links.new(out.inputs[0], corner.outputs[0])    
      prevNode.node().name = 'NX_Last'
    
    print("--- %s seconds ---" % (time.time() - start_time))
    print('END TRACE 1')
  
  def addIssues(self, node_group):      
      corner = node_group.nodes['LabCorner']
      last = node_group.nodes['NX_Last']

      entrance = self.createIssue(node_group, 'ENTRANCE')
      entrance.location(x=(last.location.x + entrance.width() + self.offset), y=last.location.y)
      entrance.link(0, last.outputs[0])
      entrance.link(1, last.outputs[1])

      exit = self.createIssue(node_group, 'EXIT')
      exit.location(x=(entrance.x() + exit.width() + self.offset), y=entrance.y())
      exit.link(0, entrance.output(0))
      exit.link(1, entrance.output(1))

      corner.location.x = exit.x() + corner.width + self.offset
      node_group.links.new(corner.inputs[1], exit.output(0))

      out = node_group.nodes['Group Output']
      out.location.x = corner.location.x + out.width + self.offset

  def issueIndex(self, axe, number):
    index = None
    x = self.x
    y = self.y
    
    if axe == 'W':
      index = number
    if axe == 'E':
      index = y * x + number
    if axe == 'S':
      index = y * (x + 1) + number
    if axe == 'N':
      index = y * (x + 1) + x * y + number
    
    return index

  def createIssue(self, node_group, way):  
      ng = None
      if way in node_group:
        ng = node_group[way]
      else:
        ng = Node(node_group, 'GeometryNodeGroup',
        name=way, nodeGroup='NX_EdgeSelector', callback=(self, 'edgeSelect'))
    
      if ng is not None:
        if not self.issues:
          if way == 'ENTRANCE':
            ng.node().inputs[2].default_value = -1
          else:
            ng.node().inputs[2].default_value = -1
        else:  
          if way == 'ENTRANCE':
            ng.node().inputs[2].default_value = self.issueIndex(self.entrance.axe, self.entrance.number)
          else:
            ng.node().inputs[2].default_value = self.issueIndex(self.exit.axe, self.exit.number)
        
      return ng

  def clampOverlap(self):
    if self.thickness > self.cellSize:
      self.thickness = self.cellSize
    if self.radius > self.cellSize / 2:
      self.radius = self.cellSize / 2
    if self.radius < (self.thickness / 2) + (self.thickness * 0.1):
      self.radius = (self.thickness / 2) + (self.thickness * 0.1)

  def adjustModifiers(self):
    screw = self.obj.modifiers['NX_SCREW']
    if self.height == 0:
      screw.show_viewport = False
    else:
      screw.show_viewport = True

  def randomIssues(self):
    # entrance
    axes = ['N', 'W']
    axe = axes[randint(0,1)]
    self.entrance.axe = axe

    if axe == 'W':
      borne = self.y - 1
    else:
      borne = self.x - 1

    self.entrance.number = randint(0, borne)

    # exit
    if axe == 'W':
      self.exit.axe = 'E'
      borne = self.y - 1
    else:
      self.exit.axe = 'S'
      borne = self.x - 1
    
    self.exit.number = randint(0, borne)

  
class OBJECT_OT_Create_Labyrinthe(Operator, NXLabyrinthe):
  bl_idname = "object.create_labyrinthe"
  bl_label = "Create Labyrinthe"

  def execute(self, context):
    self.clampOverlap()  
    self.randomIssues()

    scene = context.scene
    m = bpy.data.meshes.new('NxLab')
    self.obj = bpy.data.objects.new('NxLab', m)

    context.collection.objects.link(self.obj)
    context.view_layer.objects.active = self.obj
    self.obj.select_set(True)

    self.obj.NXLab.x = self.x
    self.obj.NXLab.y = self.y
    self.obj.NXLab.cellSize = self.cellSize
    self.obj.NXLab.corner = self.corner
    self.obj.NXLab.radius = self.radius
    self.obj.NXLab.segments = self.segments
    self.obj.NXLab.height = self.height
    self.obj.NXLab.thickness = self.thickness
    self.obj.NXLab.orientation = self.orientation
    self.obj.NXLab.orientationStrength = self.orientationStrength 
    self.obj.NXLab.issues = self.issues
    self.obj.NXLab.entrance.axe = self.entrance.axe
    self.obj.NXLab.entrance.number = self.entrance.number
    self.obj.NXLab.exit.axe = self.exit.axe
    self.obj.NXLab.exit.number = self.exit.number

    self.obj.modifiers.new(type="NODES", name="NX_LABYRINTHE")
    node_group = self.obj.modifiers['NX_LABYRINTHE'].node_group
    nodes = self.obj.modifiers['NX_LABYRINTHE'].node_group.nodes
    links = self.obj.modifiers['NX_LABYRINTHE'].node_group.links

    group_input = nodes['Group Input']
    group_input.location.x += -250
    group_input.location.y += 250

    valueX = Node(node_group, 'FunctionNodeInputInt', name='valueX', values={'integer': self.x})      

    valueY = Node(node_group, 'FunctionNodeInputInt', name='valueY', values={'integer': self.y})
    valueY.location(y=(valueX.y() - valueY.height()/2 - self.offset))

    cellSize = Node(node_group, 'ShaderNodeValue', 
      name='cellSize', values={'output': (0, 'default_value', self.cellSize)})
    cellSize.location(y=(valueX.y() + cellSize.height()/2 + self.offset))

    addX = Node(node_group, 'ShaderNodeMath',
      values={'operation': 'ADD', 'input': (1, 'default_value', 1)})
    addX.location(x=(valueX.x() + addX.width() + 2*self.offset), y=-(addX.height()))
    addX.link(0, valueX.output(0))   
    
    addY = Node(node_group, 'ShaderNodeMath',
      values={'operation': 'ADD', 'input': (1, 'default_value', 1)})
    addY.location(x=addX.x(), y=(addX.y() - addY.height() - 1.5*self.offset))
    addY.link(0, valueY.output(0))   
    
    multiplyY = Node(node_group, 'ShaderNodeMath', values={'operation': 'MULTIPLY'})
    multiplyY.location(x=addX.x(), y=(addX.y() + addY.height() + 1.5*self.offset))
    multiplyY.link(0, valueY.output(0))
    multiplyY.link(1, cellSize.output(0))

    multiplyX = Node(node_group, 'ShaderNodeMath', values={'operation': 'MULTIPLY'})
    multiplyX.location(x=addX.x(), y=(multiplyY.y() + multiplyX.height() + 1.5*self.offset))
    multiplyX.link(0, valueX.output(0))
    multiplyX.link(1, cellSize.output(0))

    grid = Node(node_group, 'GeometryNodeMeshGrid')
    grid.location(x=multiplyY.x() + grid.width() + 2*self.offset)
    grid.link(0, multiplyX.output(0))
    grid.link(1, multiplyY.output(0))
    grid.link(2, addX.output(0))
    grid.link(3, addY.output(0))
    
    delFace = Node(node_group, 'GeometryNodeDeleteGeometry', values={'mode': 'ONLY_FACE'})
    delFace.location(x=grid.x() + delFace.width() + self.offset, y=grid.y())
    delFace.link(0, grid.output(0))

    corner = Node(node_group, 'GeometryNodeGroup',
          name='LabCorner', nodeGroup='LabCorner', callback=(self, 'labCorner'))
    corner.node().inputs[2].default_value = self.corner
    corner.node().inputs[3].default_value = self.segments
    radius = self.radius
    if self.radius > self.cellSize / 2:
      radius = self.cellSize / 2
    corner.node().inputs[4].default_value = radius

    group_output = nodes['Group Output']
    group_output.location.x = delFace.x() + group_output.width + self.offset
    group_output.location.y = delFace.y()
    input = group_output.inputs[0]
    links.new(input, corner.output(0))
    
    weld = self.obj.modifiers.new(type='WELD', name="NX_WELD")
    weld.show_expanded = False

    screw = self.obj.modifiers.new(type='SCREW', name="NX_SCREW")    
    screw.angle = 0
    screw.screw_offset = self.height
    screw.steps = 1
    screw.render_steps = 1
    screw.show_expanded = False

    solid = self.obj.modifiers.new(type='SOLIDIFY', name="NX_SOLIDIFY")
    solid.solidify_mode = 'NON_MANIFOLD'
    solid.offset = 0
    solid.thickness = self.thickness
    solid.show_expanded = False

    edgeSplit = self.obj.modifiers.new(type='EDGE_SPLIT', name="NX_EDGE_SPLIT")
    edgeSplit.show_expanded = False

    self.adjustModifiers()
    
    self.laby = Labyrinthe()
    self.laby.init(self.x, self.y, self.orientation, self.orientationStrength)

    # laby_str5 = self.Laby.toString(5)

    # print('STR 5:', len(laby_str5))
    # print('STR 5:', laby_str5)

    # obj.NXLab_laby = laby_str5

    self.trace1(node_group)
    self.addIssues(node_group)
    
    return {'FINISHED'}


class OBJECT_OT_New_Labyrinthe(Operator, NXLabyrinthe):
  bl_idname = "object.new_labyrinthe"
  bl_label = "New Labyrinthe"

  def execute(self, context):

    logging.info('OPERATOR NEW LAB EXECUTE')
    self.clampOverlap()
    self.randomIssues()

    self.obj = context.object

    self.obj.NXLab.x = self.x
    self.obj.NXLab.y = self.y
    self.obj.NXLab.cellSize = self.cellSize
    self.obj.NXLab.corner = self.corner
    self.obj.NXLab.radius = self.radius
    self.obj.NXLab.segments = self.segments
    self.obj.NXLab.height = self.height
    self.obj.NXLab.thickness = self.thickness  
    self.obj.NXLab.orientation = self.orientation 
    self.obj.NXLab.orientationStrength = self.orientationStrength 
    self.obj.NXLab.issues = self.issues
    self.obj.NXLab.entrance.axe = self.entrance.axe
    self.obj.NXLab.entrance.number = self.entrance.number
    self.obj.NXLab.exit.axe = self.exit.axe
    self.obj.NXLab.exit.number = self.exit.number

    if 'NX_LABYRINTHE' not in self.obj.modifiers:
      return {'CANCELLED'}

    node_group = self.obj.modifiers['NX_LABYRINTHE'].node_group
    nodes = self.obj.modifiers['NX_LABYRINTHE'].node_group.nodes

    gns = [node for node in nodes if node.name.startswith('NX_')]
    for gn in gns:
      nodes.remove(gn)
      
    nodes.remove(nodes['Index'])

    valueX = nodes['valueX']
    valueX.integer = self.x
    
    valueY = nodes['valueY']
    valueY.integer = self.y
    
    cellSize = nodes['cellSize']
    cellSize.outputs[0].default_value = self.cellSize

    corner = nodes['LabCorner']
    corner.inputs[2].default_value = self.corner
    corner.inputs[3].default_value = self.segments
    corner.inputs[4].default_value = self.radius

    screw = self.obj.modifiers['NX_SCREW']
    screw.screw_offset = self.height
    
    solid = self.obj.modifiers['NX_SOLIDIFY']
    solid.thickness = self.thickness

    self.adjustModifiers()

    logging.info('BEFORE SELF.LABY')

    self.laby = Labyrinthe()
    self.laby.init(self.x, self.y, self.orientation, self.orientationStrength)

    self.trace1(node_group)
    self.addIssues(node_group)

    return {'FINISHED'}

class OBJECT_OT_Update_Labyrinthe(Operator, NXLabyrinthe):
  bl_idname = "object.update_labyrinthe"
  bl_label = "Update Labyrinthe"

  def execute(self, context):

    self.clampOverlap()
    
    self.obj = context.object
    node_group = self.obj.modifiers['NX_LABYRINTHE'].node_group

    self.obj.NXLab.cellSize = self.cellSize
    self.obj.NXLab.corner = self.corner
    self.obj.NXLab.radius = self.radius
    self.obj.NXLab.segments = self.segments
    self.obj.NXLab.height = self.height
    self.obj.NXLab.thickness = self.thickness 
    self.obj.NXLab.issues = self.issues

    self.x = self.obj.NXLab.x
    self.y = self.obj.NXLab.y
    self.entrance.axe = self.obj.NXLab.entrance.axe
    self.entrance.number = self.obj.NXLab.entrance.number
    self.exit.axe = self.obj.NXLab.exit.axe
    self.exit.number = self.obj.NXLab.exit.number
    
    if 'NX_LABYRINTHE' not in self.obj.modifiers:
      return {'CANCELLED'}    

    nodes = self.obj.modifiers['NX_LABYRINTHE'].node_group.nodes

    cellSize = nodes['cellSize']
    cellSize.outputs[0].default_value = self.cellSize

    corner = nodes['LabCorner']
    corner.inputs[2].default_value = self.corner
    corner.inputs[3].default_value = self.segments
    radius = self.radius
    corner.inputs[4].default_value = self.radius

    screw = self.obj.modifiers['NX_SCREW']
    screw.screw_offset = self.height
    
    solid = self.obj.modifiers['NX_SOLIDIFY']
    solid.thickness = self.thickness

    self.adjustModifiers()
    self.addIssues(node_group)

    return {'FINISHED'}
