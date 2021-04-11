'''
select Arnold Light/s and run the script, it will generate a Light Blocker per light,
and automatically assign OUT_light in the respective light's light_filter

if you select nothing and run the script, it will still generate a Light Blocker,
which you can manually plug in Arnold Light

'''

import hou

obj = hou.node('/obj')
lgt_list = hou.selectedItems()
lbt_nodes = []
hou.Node.setSelected(hou.node('/obj'), False, clear_all_selected=True)

if len(lgt_list) == 0:
    lbt = obj.createNode('light_blocker_transform')
    hou.Node.setSelected(lbt, True)
else:
    for lgt in lgt_list:
        lbt = obj.createNode('light_blocker_transform', 'light_blocker_transform_'+lgt.name())
        lbt_nodes.append(lbt)
        hou.Node.setSelected(lbt, True)
        hou.parm(lgt.path()+'/ar_light_filters').set(lbt.path()+"/matnet1/light_blocker1/OUT_light")

if len(lbt_nodes) != 0:
    hou.node('/obj').layoutChildren(items=(lbt_nodes))
