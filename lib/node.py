import bpy

class Node:
  def __init__(self, 
    node_group, 
    type, 
    name=None,
    label=None,
    nodeGroup=None,
    callback=None,
    values=None
  ):
  
    if node_group is None or type is None:
      raise ValueError('nodes, type or name are empty')

    self.nodes = node_group.nodes
    self.links = node_group.links
    self._node = None

    try:
      self._node = self.nodes.new(type)
    except KeyError as err:
      print(err)    
    
    if type == 'GeometryNodeGroup':
      if nodeGroup is not None:
        if nodeGroup not in bpy.data.node_groups:
          ng = bpy.data.node_groups.new(nodeGroup, 'GeometryNodeTree')          
          
          ng.nodes.new('NodeGroupInput')
          self._node.node_tree = ng

          if callback is not None:
            if isinstance(callback, str):
              callback(ng)
            else:
              getattr(callback[0], callback[1])(ng)
        else:
          self._node.node_tree = bpy.data.node_groups[nodeGroup]  
      else:
        raise ValueError('When type is GeometryNodeGroup, nodeGroup must be filled in')
    
    if name is not None:
      self._node.name = name
      if label is not None:
        self._node.label = label
      else:
        self._node.label = self._node.name

    if values is not None:
      for key in values:
        if key == 'input':
          setattr(self._node.inputs[values[key][0]], values[key][1], values[key][2])
        elif key == 'output':
          setattr(self._node.outputs[values[key][0]], values[key][1], values[key][2])
        else:
          setattr(self._node, key, values[key])
          
  def node(self):
    return self._node

  def input(self, index=None):
    if index is None or index < 0 or index > len(self._node.inputs.items()):
      return None
    return self._node.inputs[index]

  def output(self, index=None):
    if index is None or index < 0 or index > len(self._node.outputs.items()):
      return None
    return self._node.outputs[index]
  
  def link(self, index_input, output):
    self.links.new(self.input(index_input), output)
  
  def x(self):
    return self._node.location.x
  
  def y(self):
    return self._node.location.y
  
  def width(self):
    return self._node.width
  
  def height(self):
    return self._node.height

  def location(self, x=None, y=None):
    if x is not None:
      self._node.location.x = x
    if y is not None:
      self._node.location.y = y  
