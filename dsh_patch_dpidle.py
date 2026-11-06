import io, sys

p = 'drivers/video/fbdev/msm/mdss_dp.c'
try:
    s = io.open(p, encoding='utf-8', errors='surrogateescape').read()
except IOError:
    p = '/home/yue123/ksrc/drivers/video/fbdev/msm/mdss_dp.c'
    s = io.open(p, encoding='utf-8', errors='surrogateescape').read()

old = '''		mdss_dp_mainlink_push_idle(pdata);
		break;
	case MDSS_EVENT_FB_REGISTERED:'''

new = '''		/* DSH: blank 时不要动 DP 主链路。
		 * 原逻辑会发送 PUSH_IDLE 并等待确认，超时后驱动会关闭再重开
		 * 链路，导致电视短暂显示"无信号"（画面闪一下）。
		 * 这里跳过，让链路保持连接，blank 只关输出即可。 */
		pr_debug("DSH: skip push_idle on blank\\n");
		break;
	case MDSS_EVENT_FB_REGISTERED:'''

if old not in s:
    sys.exit('pattern not found')

s = s.replace(old, new, 1)
io.open(p, 'w', encoding='utf-8', errors='surrogateescape').write(s)
print('PATCHED: skip push_idle on blank')
