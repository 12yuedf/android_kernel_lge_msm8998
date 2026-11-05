import io
import sys

p = 'drivers/video/fbdev/msm/mdss_mdp.c'
s = io.open(p, encoding='utf-8', errors='surrogateescape').read()

old = '\tmdata->idle_pc_enabled = of_property_read_bool(pdev->dev.of_node,\n\t\t "qcom,mdss-idle-power-collapse-enabled");'
new = ('\t/* DSH: keep MDP powered so the command-mode panel does not idle-collapse\n'
       '\t * (idle collapse drops TE/vsync to ~8Hz, which starves SurfaceFlinger) */\n'
       '\tmdata->idle_pc_enabled = false;')

if 'mdata->idle_pc_enabled = false;' in s and old not in s:
    print('already patched')
elif old in s:
    io.open(p, 'w', encoding='utf-8', errors='surrogateescape').write(s.replace(old, new, 1))
    print('patched ok')
else:
    sys.exit('ERROR: idle_pc pattern not found')
