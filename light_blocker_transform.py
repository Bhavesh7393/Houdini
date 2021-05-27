'''
select Arnold Light/s and run the script, it will generate a Light Blocker per light,
and automatically assign OUT_light in the respective light's light_filter

if you select nothing and run the script, it will still generate a Light Blocker,
which you can manually plug in Arnold Light

'''

import hou

class LightBlockerTransform(object):
    def __init__(self, name):
        self.name = name
        
    def nodes(self):
        # create subnet
        self.subnet = obj.createNode('subnet', self.name)
        
        # create geo and matnet
        self.geo = self.subnet.createNode('geo', 'light_blocker_shape1')
        self.matnet = self.subnet.createNode('matnet')
        self.subnet.layoutChildren()
        
        # create light blocker
        amb = self.matnet.createNode('arnold_materialbuilder', 'light_blocker1')
        amb.children()[0].destroy()
        self.out_light = amb.createNode('arnold_light')
        self.light_blocker = amb.createNode('arnold::light_blocker')
        self.out_light.setInput(2, self.light_blocker, 0)
        amb.layoutChildren()
        
        # create shapes
        self.box = self.geo.createNode('box')
        self.sphere = self.geo.createNode('sphere')
        self.grid = self.geo.createNode('grid')
        self.tube = self.geo.createNode('tube')
        self.switch = self.geo.createNode('switch')
        self.color = self.geo.createNode('color')
        self.convline = self.geo.createNode('convertline')
        self.null = self.geo.createNode('null', 'OUT')
        
    def set(self):
        # set geo Arnold Visibility values
        self.geo.parm('ar_visibility_camera').set(0)
        self.geo.parm('ar_visibility_shadow').set(0)
        self.geo.parm('ar_visibility_diffuse_transmit').set(0)
        self.geo.parm('ar_visibility_specular_transmit').set(0)
        self.geo.parm('ar_visibility_diffuse_reflect').set(0)
        self.geo.parm('ar_visibility_specular_reflect').set(0)
        self.geo.parm('ar_visibility_volume').set(0)
        self.geo.parm('ar_receive_shadows').set(0)
        self.geo.parm('ar_self_shadows').set(0)
        self.geo.parm('ar_opaque').set(0)
        self.geo.parm('ar_skip').set(1)
        
        # set connections
        self.switch.setInput(0, self.box, 0)
        self.switch.setInput(1, self.sphere, 0)
        self.switch.setInput(2, self.grid, 0)
        self.switch.setInput(3, self.tube, 0)
        self.color.setInput(0, self.switch, 0)
        self.convline.setInput(0, self.color, 0)
        self.null.setInput(0, self.convline, 0)
        self.geo.layoutChildren()
        
        # set shape nodes values
        self.sphere.parm('type').set(2)
        self.sphere.parm('scale').set(0.5)
        self.sphere.parm('rows').set(16)
        self.sphere.parm('cols').set(16)
        self.grid.parm('sizex').set(1)
        self.grid.parm('sizey').set(1)
        self.grid.parm('rx').set(90)
        self.grid.parm('rows').set(2)
        self.grid.parm('cols').set(2)
        self.tube.parm('type').set(1)
        self.tube.parm('cap').set(1)
        self.tube.parm('rad1').set(0.5)
        self.tube.parm('rad2').set(0.5)
        self.tube.parm('cols').set(20)
        self.color.parm('colorr').set(0.8)
        self.color.parm('colorg').set(0.0)
        self.color.parm('colorb').set(0.0)
        self.convline.parm('computelength').set(0)
        self.null.setDisplayFlag(1)
        self.null.setRenderFlag(1)
        
    def ui(self):
        # add Shape Transform folder
        subnet_tg = self.subnet.parmTemplateGroup()
        shp_folder = hou.FolderParmTemplate('shape_transform', 'Shape Transform', folder_type = hou.folderType.Simple)
        
        # add Geometry Type parameter in Shape Transfer folder
        geo_type_menu = ('box', 'sphere', 'plane', 'cylinder')
        geo_type_label = ('Box', 'Sphere', 'Plane', 'Cylinder')
        geo_type = hou.MenuParmTemplate('geometry_type', "Geometry Type", geo_type_menu, menu_labels=(geo_type_label))
        shp_folder.addParmTemplate(geo_type)
        
        # extract default Transform parameters
        trans = subnet_tg.find('t')
        rot = subnet_tg.find('r')
        scale = subnet_tg.find('s')
        
        # delete default Transform parameters
        subnet_tg.remove(trans)
        subnet_tg.remove(rot)
        subnet_tg.remove(scale)
        
        # Transfer default Transform parameters under Shape Transform folder
        shp_folder.addParmTemplate(trans)
        shp_folder.addParmTemplate(rot)
        shp_folder.addParmTemplate(scale)
        subnet_tg.append(shp_folder)
        
        # add Parameters folder
        parm_folder = hou.FolderParmTemplate('parameters', 'Parameters', folder_type = hou.folderType.Simple)
        
        # add parameters under Parameters folder
        density = hou.FloatParmTemplate('density', 'Density', 1, min=0.0, max=1.0)
        roundness = hou.FloatParmTemplate('roundness', 'Roundness', 1, min=0.0, max=1.0)
        width_edge = hou.FloatParmTemplate('width_edge', 'Width Edge', 1, min=0.0, max=1.0)
        height_edge = hou.FloatParmTemplate('height_edge', 'Height Edge', 1, min=0.0, max=1.0)
        ramp = hou.FloatParmTemplate('ramp', 'Ramp', 1, min=0.0, max=1.0)
        
        axis_menu = ('x', 'y', 'z')
        axis_label = ('X', 'Y', 'Z')
        axis = hou.MenuParmTemplate('axis', "Axis", axis_menu, menu_labels=(axis_label))
        
        parm_folder.addParmTemplate(density)
        parm_folder.addParmTemplate(roundness)
        parm_folder.addParmTemplate(width_edge)
        parm_folder.addParmTemplate(height_edge)
        parm_folder.addParmTemplate(ramp)
        parm_folder.addParmTemplate(axis)
        subnet_tg.append(parm_folder)
        
        # hide all default parameters of subnet
        subnet_tg.hideFolder('Transform', 1)
        subnet_tg.hideFolder('Subnet', 1)
        self.subnet.setParmTemplateGroup(subnet_tg)
        
    def connect(self):
        # set relative references
        hou.parm(self.light_blocker.path()+'/geometry_type').set(hou.parm(self.subnet.path()+'/geometry_type'))
        hou.parm(self.switch.path()+'/input').setExpression("""ch("../../geometry_type")
0==box
1==sphere
2==plane
3==cylinder""")
        hou.parm(self.light_blocker.path()+'/density').set(hou.parm(self.subnet.path()+'/density'))
        hou.parm(self.light_blocker.path()+'/roundness').set(hou.parm(self.subnet.path()+'/roundness'))
        hou.parm(self.light_blocker.path()+'/width_edge').set(hou.parm(self.subnet.path()+'/width_edge'))
        hou.parm(self.light_blocker.path()+'/height_edge').set(hou.parm(self.subnet.path()+'/height_edge'))
        hou.parm(self.light_blocker.path()+'/ramp').set(hou.parm(self.subnet.path()+'/ramp'))
        hou.parm(self.light_blocker.path()+'/axis').set(hou.parm(self.subnet.path()+'/axis'))
        
        # set 4x4 matrix
        hou.parm(self.light_blocker.path()+'/geometry_matrix1').setExpression('ch("../../../sx")*(cos(ch("../../../ry"))*cos(ch("../../../rz")))')
        hou.parm(self.light_blocker.path()+'/geometry_matrix2').setExpression('ch("../../../sx")*(cos(ch("../../../ry"))*sin(ch("../../../rz")))')
        hou.parm(self.light_blocker.path()+'/geometry_matrix3').setExpression('-ch("../../../sx")*(sin(ch("../../../ry")))')
        hou.parm(self.light_blocker.path()+'/geometry_matrix5').setExpression('(-ch("../../../sy")*(cos(ch("../../../rx"))*sin(ch("../../../rz"))))+(ch("../../../sy")*(sin(ch("../../../rx"))*sin(ch("../../../ry"))*cos(ch("../../../rz"))))')
        hou.parm(self.light_blocker.path()+'/geometry_matrix6').setExpression('(ch("../../../sy")*(cos(ch("../../../rx"))*cos(ch("../../../rz"))))+(ch("../../../sy")*(sin(ch("../../../rx"))*sin(ch("../../../ry"))*sin(ch("../../../rz"))))')
        hou.parm(self.light_blocker.path()+'/geometry_matrix7').setExpression('ch("../../../sy")*(sin(ch("../../../rx"))*cos(ch("../../../ry")))')
        hou.parm(self.light_blocker.path()+'/geometry_matrix9').setExpression('(ch("../../../sz")*(sin(ch("../../../rx"))*sin(ch("../../../rz"))))+(ch("../../../sz")*(cos(ch("../../../rx"))*sin(ch("../../../ry"))*cos(ch("../../../rz"))))')
        hou.parm(self.light_blocker.path()+'/geometry_matrix10').setExpression('(-ch("../../../sz")*(sin(ch("../../../rx"))*cos(ch("../../../rz"))))+(ch("../../../sz")*(cos(ch("../../../rx"))*sin(ch("../../../ry"))*sin(ch("../../../rz"))))')
        hou.parm(self.light_blocker.path()+'/geometry_matrix11').setExpression('ch("../../../sz")*(cos(ch("../../../rx"))*cos(ch("../../../ry")))')
        hou.parm(self.light_blocker.path()+'/geometry_matrix13').setExpression('ch("../../../tx")')
        hou.parm(self.light_blocker.path()+'/geometry_matrix14').setExpression('ch("../../../ty")')
        hou.parm(self.light_blocker.path()+'/geometry_matrix15').setExpression('ch("../../../tz")')
        
obj = hou.node('/obj')

selection = hou.selectedItems()

arnold_lights = []

for light in selection:
    if light.type().name() == "arnold_light":
        arnold_lights.append(light)
        
light_blocker_transform_nodes = []

hou.Node.setSelected(obj, False, clear_all_selected=True)

if len(arnold_lights) == 0:
    light_blocker_transform = LightBlockerTransform("light_blocker_transform1")
    light_blocker_transform.nodes()
    light_blocker_transform.set()
    light_blocker_transform.ui()
    light_blocker_transform.connect()
    hou.Node.setSelected(light_blocker_transform.subnet, True)
else:
    for light in arnold_lights:
        light_blocker_transform = LightBlockerTransform(light.name()+'_light_blocker_transform1')
        light_blocker_transform.nodes()
        light_blocker_transform.set()
        light_blocker_transform.ui()
        light_blocker_transform.connect()
        light_blocker_transform_nodes.append(light_blocker_transform.subnet)
        hou.Node.setSelected(light_blocker_transform.subnet, True)
        hou.parm(light.path()+'/ar_light_filters').set(light_blocker_transform.out_light.path())

if len(light_blocker_transform_nodes) != 0:
    obj.layoutChildren(items=(light_blocker_transform_nodes))
else:
    pass
