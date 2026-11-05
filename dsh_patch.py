import io
import sys

fails = []

# ---------------------------------------------------------------
# mdss_mdp.c: 关闭 MDP 空闲功耗塌陷
#   1) idle_pc_enabled 强制 false
#   2) footswitch_ctrl 里真正触发塌陷的分支加上 idle_pc_enabled 判断
#      （原来的代码不看这个标志，导致补丁无效）
# ---------------------------------------------------------------
p = 'drivers/video/fbdev/msm/mdss_mdp.c'
s = io.open(p, encoding='utf-8', errors='surrogateescape').read()

old1 = '\tmdata->idle_pc_enabled = of_property_read_bool(pdev->dev.of_node,\n\t\t "qcom,mdss-idle-power-collapse-enabled");'
new1 = ('\t/* DSH: force idle power collapse off */\n'
        '\tmdata->idle_pc_enabled = false;')
if old1 in s:
    s = s.replace(old1, new1, 1)
    print('mdss_mdp: idle_pc_enabled -> false')
elif 'mdata->idle_pc_enabled = false;' in s:
    print('mdss_mdp: idle_pc_enabled already false')
else:
    fails.append('idle_pc_enabled pattern')

old2 = '\t\t\tif (active_cnt != 0) {'
new2 = '\t\t\tif (active_cnt != 0 && mdata->idle_pc_enabled) {'
if old2 in s:
    s = s.replace(old2, new2, 1)
    print('mdss_mdp: footswitch idle_pc guarded')
elif 'active_cnt != 0 && mdata->idle_pc_enabled' in s:
    print('mdss_mdp: footswitch already guarded')
else:
    fails.append('footswitch pattern')

io.open(p, 'w', encoding='utf-8', errors='surrogateescape').write(s)

if fails:
    sys.exit('ERROR: ' + ', '.join(fails))
print('ALL PATCHES OK')
