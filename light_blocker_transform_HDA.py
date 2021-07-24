'''
select Arnold Light/s and run the script, it will generate a Light Blocker for all selected lights,
and automatically assign OUT_light in the respective light's light_filter

if you select nothing and run the script, it will still generate a Light Blocker,
which you can manually plug in Arnold Light

'''

import hou

obj = hou.node('/obj')
selection = hou.selectedItems()
arnold_lights = []
for light in selection:
    if light.type().name() == "arnold_light":
        arnold_lights.append(light)
light_blocker_transform_nodes = []
hou.Node.setSelected(hou.node('/obj'), False, clear_all_selected=True)

if len(arnold_lights) == 0:
    light_blocker_transform = obj.createNode('light_blocker_transform')
    hou.Node.setSelected(light_blocker_transform, True)
else:
    light_blocker_transform = obj.createNode('light_blocker_transform')
    for light in arnold_lights:
        hou.parm(light.path()+'/ar_light_filters').set(light_blocker_transform.path()+"/matnet1/light_blocker1/OUT_light")
        light_blocker_transform_nodes.append(light_blocker_transform)
        hou.Node.setSelected(light_blocker_transform, True)

if len(light_blocker_transform_nodes) != 0:
    hou.node('/obj').layoutChildren(items=(light_blocker_transform_nodes))
else:
    pass
