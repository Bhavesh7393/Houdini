'''
select Arnold Light/s and run the script, it will generate a Light Blocker per light,
and automatically assign OUT_light in the respective light's light_filter

if you select nothing and run the script, it will still generate a Light Blocker,
which you can manually plug in Arnold Light

'''

import hou

lgt_list = hou.selectedItems()

def lightBlockerTransform():
   
    # create subnet
    obj = hou.node('/obj')
    lightBlockerTransform.subnet = obj.createNode('subnet', 'light_blocker_transform1')
   
    # create geo and matnet
    geo = lightBlockerTransform.subnet.createNode('geo', 'light_blocker_shape')
    matnet = lightBlockerTransform.subnet.createNode('matnet')
    lightBlockerTransform.subnet.layoutChildren()
   
    # create light blocker
    amb = matnet.createNode('arnold_materialbuilder', 'light_blocker1')
    amb.children()[0].destroy()
    lightBlockerTransform.out_lgt = amb.createNode('arnold_light')
    lgtblk = amb.createNode('arnold::light_blocker')
    lightBlockerTransform.out_lgt.setInput(2, lgtblk, 0)
    amb.layoutChildren()

    # create shapes
    box = geo.createNode('box')
    sphere = geo.createNode('sphere')
    grid = geo.createNode('grid')
    tube = geo.createNode('tube')
    switch = geo.createNode('switch')
    color = geo.createNode('color')
    convline = geo.createNode('convertline')
    null = geo.createNode('null', 'OUT')

    # set connections
    switch.setInput(0, box, 0)
    switch.setInput(1, sphere, 0)
    switch.setInput(2, grid, 0)
    switch.setInput(3, tube, 0)
    color.setInput(0, switch, 0)
    convline.setInput(0, color, 0)
    null.setInput(0, convline, 0)
    geo.layoutChildren()

    # set shape nodes values
    sphere.parm('type').set(2)
    sphere.parm('scale').set(0.5)
    sphere.parm('rows').set(16)
    sphere.parm('cols').set(16)
    grid.parm('sizex').set(1)
    grid.parm('sizey').set(1)
    grid.parm('rx').set(90)
    grid.parm('rows').set(2)
    grid.parm('cols').set(2)
    tube.parm('type').set(1)
    tube.parm('cap').set(1)
    tube.parm('rad1').set(0.5)
    tube.parm('rad2').set(0.5)
    tube.parm('cols').set(20)
    color.parm('colorr').set(0.8)
    color.parm('colorg').set(0.0)
    color.parm('colorb').set(0.0)
    convline.parm('computelength').set(0)
    null.setDisplayFlag(1)
    null.setRenderFlag(1)

    # set geo Arnold Visibility values
    geo.parm('ar_visibility_camera').set(0)
    geo.parm('ar_visibility_shadow').set(0)
    geo.parm('ar_visibility_diffuse_transmit').set(0)
    geo.parm('ar_visibility_specular_transmit').set(0)
    geo.parm('ar_visibility_diffuse_reflect').set(0)
    geo.parm('ar_visibility_specular_reflect').set(0)
    geo.parm('ar_visibility_volume').set(0)
    geo.parm('ar_receive_shadows').set(0)
    geo.parm('ar_self_shadows').set(0)
    geo.parm('ar_opaque').set(0)
    geo.parm('ar_skip').set(1)

    # add Shape Transform folder
    subnet_tg = lightBlockerTransform.subnet.parmTemplateGroup()
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
    lightBlockerTransform.subnet.setParmTemplateGroup(subnet_tg)

    # set relative references
    hou.parm(lgtblk.path()+'/geometry_type').set(hou.parm(lightBlockerTransform.subnet.path()+'/geometry_type'))
    hou.parm(switch.path()+'/input').setExpression("""ch("../../geometry_type")
0==box
1==sphere
2==plane
3==cylinder""")
    hou.parm(lgtblk.path()+'/density').set(hou.parm(lightBlockerTransform.subnet.path()+'/density'))
    hou.parm(lgtblk.path()+'/roundness').set(hou.parm(lightBlockerTransform.subnet.path()+'/roundness'))
    hou.parm(lgtblk.path()+'/width_edge').set(hou.parm(lightBlockerTransform.subnet.path()+'/width_edge'))
    hou.parm(lgtblk.path()+'/height_edge').set(hou.parm(lightBlockerTransform.subnet.path()+'/height_edge'))
    hou.parm(lgtblk.path()+'/ramp').set(hou.parm(lightBlockerTransform.subnet.path()+'/ramp'))
    hou.parm(lgtblk.path()+'/axis').set(hou.parm(lightBlockerTransform.subnet.path()+'/axis'))

    # set 4x4 matrix
    hou.parm(lgtblk.path()+'/geometry_matrix1').setExpression('ch("../../../sx")*(cos(ch("../../../ry"))*cos(ch("../../../rz")))')
    hou.parm(lgtblk.path()+'/geometry_matrix2').setExpression('ch("../../../sx")*(cos(ch("../../../ry"))*sin(ch("../../../rz")))')
    hou.parm(lgtblk.path()+'/geometry_matrix3').setExpression('-ch("../../../sx")*(sin(ch("../../../ry")))')
    hou.parm(lgtblk.path()+'/geometry_matrix5').setExpression('(-ch("../../../sy")*(cos(ch("../../../rx"))*sin(ch("../../../rz"))))+(ch("../../../sy")*(sin(ch("../../../rx"))*sin(ch("../../../ry"))*cos(ch("../../../rz"))))')
    hou.parm(lgtblk.path()+'/geometry_matrix6').setExpression('(ch("../../../sy")*(cos(ch("../../../rx"))*cos(ch("../../../rz"))))+(ch("../../../sy")*(sin(ch("../../../rx"))*sin(ch("../../../ry"))*sin(ch("../../../rz"))))')
    hou.parm(lgtblk.path()+'/geometry_matrix7').setExpression('ch("../../../sy")*(sin(ch("../../../rx"))*cos(ch("../../../ry")))')
    hou.parm(lgtblk.path()+'/geometry_matrix9').setExpression('(ch("../../../sz")*(sin(ch("../../../rx"))*sin(ch("../../../rz"))))+(ch("../../../sz")*(cos(ch("../../../rx"))*sin(ch("../../../ry"))*cos(ch("../../../rz"))))')
    hou.parm(lgtblk.path()+'/geometry_matrix10').setExpression('(-ch("../../../sz")*(sin(ch("../../../rx"))*cos(ch("../../../rz"))))+(ch("../../../sz")*(cos(ch("../../../rx"))*sin(ch("../../../ry"))*sin(ch("../../../rz"))))')
    hou.parm(lgtblk.path()+'/geometry_matrix11').setExpression('ch("../../../sz")*(cos(ch("../../../rx"))*cos(ch("../../../ry")))')
    hou.parm(lgtblk.path()+'/geometry_matrix13').setExpression('ch("../../../tx")')
    hou.parm(lgtblk.path()+'/geometry_matrix14').setExpression('ch("../../../ty")')
    hou.parm(lgtblk.path()+'/geometry_matrix15').setExpression('ch("../../../tz")')

lbt_nodes = []

hou.Node.setSelected(hou.node('/obj'), False, clear_all_selected=True)

if len(lgt_list) == 0:
    lightBlockerTransform()
    hou.Node.setSelected(lightBlockerTransform.subnet, True)
else:
    for lgt in lgt_list:
        lightBlockerTransform()
	lbt_nodes.append(lightBlockerTransform.subnet)
	hou.Node.setSelected(lightBlockerTransform.subnet, True)
        hou.parm(lgt.path()+'/ar_light_filters').set(lightBlockerTransform.out_lgt.path())

if len(lbt_nodes) != 0:
    hou.node('/obj').layoutChildren(items=(lbt_nodes))
