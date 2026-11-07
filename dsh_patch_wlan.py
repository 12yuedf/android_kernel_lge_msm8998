import io, sys

p = 'drivers/staging/qcacld-3.0/core/hdd/src/wlan_hdd_main.c'
try:
    s = io.open(p, encoding='utf-8', errors='surrogateescape').read()
except IOError:
    p = '/home/yue123/ksrc/' + p
    s = io.open(p, encoding='utf-8', errors='surrogateescape').read()

old = '''		rc = wait_for_completion_timeout(&wlan_start_comp,
				msecs_to_jiffies(HDD_WLAN_START_WAIT_TIME));
		if (!rc) {
			pr_err("Timed-out in wlan_hdd_state_ctrl_param_write");
			ret = -EINVAL;
			return ret;
		}
		hdd_start_complete(0);'''

new = '''		rc = wait_for_completion_timeout(&wlan_start_comp,
				msecs_to_jiffies(HDD_WLAN_START_WAIT_TIME));
		if (!rc) {
			/* DSH: 驱动会卡在 recovering 状态出不来，导致 WiFi
			 * 永久无法开启（只能重启手机）。这里清除卡死状态
			 * 并完成 start 信号，让下一次 enable 能正常继续。 */
			pr_err("Timed-out in wlan_hdd_state_ctrl_param_write "
			       "(DSH: clearing stuck recovering state)\\n");
			cds_set_recovery_in_progress(false);
			hdd_start_complete(0);
			ret = -EINVAL;
			return ret;
		}
		hdd_start_complete(0);'''

if old not in s:
    sys.exit('pattern not found')

s = s.replace(old, new, 1)
io.open(p, 'w', encoding='utf-8', errors='surrogateescape').write(s)
print('PATCHED: wlan recovering state recovery')
