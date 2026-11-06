import io, sys

KS = '.'

# ---------- 1. msm_hdmi_modes.h: 新增 2560x1440p60 ----------
p1 = KS + '/include/uapi/video/msm_hdmi_modes.h'
s = io.open(p1, encoding='utf-8', errors='surrogateescape').read()

anchor = '#define HDMI_VFRMT_MAX\t\t\t(RESERVE_VFRMT_END + 1)'
if anchor not in s:
    sys.exit('anchor1 not found')

add1 = '''/* DSH: 2560x1440p60 (CVT-RB)，复用保留编号 */
#define HDMI_VFRMT_2560x1440p60_16_9		HDMI_VFRMT_RESERVE1

#define HDMI_VFRMT_MAX\t\t\t(RESERVE_VFRMT_END + 1)'''
s = s.replace(anchor, add1, 1)

# 时序宏：插在 1920x1080p60 的 TIMING 之后
anchor2 = '''#define HDMI_VFRMT_720x576p50_4_3_TIMING'''
if anchor2 not in s:
    sys.exit('anchor2 not found')
timing = '''#define HDMI_VFRMT_2560x1440p60_16_9_TIMING				\\
	{HDMI_VFRMT_2560x1440p60_16_9, 2560, 48, 32, 80, false,		\\
	 1440, 3, 5, 33, false, 241500, 60000, false, true, HDMI_RES_AR_16_9, 0}
'''
s = s.replace(anchor2, timing + anchor2, 1)
io.open(p1, 'w', encoding='utf-8', errors='surrogateescape').write(s)
print('1. msm_hdmi_modes.h patched')

# ---------- 2. mdss_hdmi_util.c: 新增 case ----------
p2 = KS + '/drivers/video/fbdev/msm/mdss_hdmi_util.c'
s2 = io.open(p2, encoding='utf-8', errors='surrogateescape').read()
a2 = '''	case HDMI_VFRMT_3840x2160p60_16_9:'''
if a2 not in s2:
    sys.exit('anchor3 not found')
new2 = '''	case HDMI_VFRMT_2560x1440p60_16_9:
		MSM_HDMI_MODES_GET_DETAILS(mode, HDMI_VFRMT_2560x1440p60_16_9);
		break;
	case HDMI_VFRMT_3840x2160p60_16_9:'''
s2 = s2.replace(a2, new2, 1)
io.open(p2, 'w', encoding='utf-8', errors='surrogateescape').write(s2)
print('2. mdss_hdmi_util.c patched')

# ---------- 3. mdss_dp_util.h: DP 链路参数 ----------
p3 = KS + '/drivers/video/fbdev/msm/mdss_dp_util.h'
s3 = io.open(p3, encoding='utf-8', errors='surrogateescape').read()
a3 = '''	{HDMI_VFRMT_3840x2160p24_16_9, 4, 10, 24,'''
if a3 not in s3:
    sys.exit('anchor4 not found')
new3 = '''	{HDMI_VFRMT_2560x1440p60_16_9, 4, 10, 24,
			0x21, 0x0013, false, 0x21, 0x8, 0x1, 0x26},
	{HDMI_VFRMT_3840x2160p24_16_9, 4, 10, 24,'''
s3 = s3.replace(a3, new3, 1)
io.open(p3, 'w', encoding='utf-8', errors='surrogateescape').write(s3)
print('3. mdss_dp_util.h patched')

# ---------- 4. mdss_hdmi_edid.c: 首选模式改成 1440p ----------
p4 = KS + '/drivers/video/fbdev/msm/mdss_hdmi_edid.c'
s4 = io.open(p4, encoding='utf-8', errors='surrogateescape').read()
old4 = '''		return HDMI_VFRMT_1920x1080p60_16_9;'''
if old4 in s4:
    s4 = s4.replace(old4, '''		return HDMI_VFRMT_2560x1440p60_16_9;''', 1)
    print('4. mdss_hdmi_edid.c patched (preferred -> 1440p)')
else:
    # 原始补丁可能还是 3840x2160
    old4b = '''		return HDMI_VFRMT_3840x2160p60_16_9;'''
    if old4b in s4:
        s4 = s4.replace(old4b, '''		return HDMI_VFRMT_2560x1440p60_16_9;''', 1)
        print('4. mdss_hdmi_edid.c patched (preferred -> 1440p, from 4K)')
    else:
        print('4. WARN: sanitize pattern not found, will append force')
io.open(p4, 'w', encoding='utf-8', errors='surrogateescape').write(s4)

print('ALL PATCHES DONE')
