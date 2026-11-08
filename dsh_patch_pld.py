import io, sys

p = 'drivers/staging/qcacld-3.0/core/cds/src/cds_api.c'
try:
    s = io.open(p, encoding='utf-8', errors='surrogateescape').read()
except IOError:
    p = '/home/yue123/ksrc/' + p
    s = io.open(p, encoding='utf-8', errors='surrogateescape').read()

old = '''	/* first, try target assert inject via pld */
	errno = cds_force_assert_target_via_pld(qdf);
	if (!errno)
		return QDF_STATUS_SUCCESS;
	if (errno != -EOPNOTSUPP)
		return QDF_STATUS_E_FAILURE;'''

new = '''	/* first, try target assert inject via pld */
	errno = cds_force_assert_target_via_pld(qdf);
	if (!errno)
		return QDF_STATUS_SUCCESS;
	if (errno != -EOPNOTSUPP) {
		/* DSH: modem 崩溃后，modem 内的 wlan_pd 保护域无法重启，
		 * PLD 断言会超时（-110）。原逻辑此时直接返回失败，不调度
		 * 任何恢复，导致 WiFi 永久死亡（只能重启手机）。
		 * 这里改为仍然调度恢复流程，让 WLAN 自行复位。 */
		cds_err("PLD assert failed (%d), scheduling recovery anyway",
			errno);
		pld_schedule_recovery_work(qdf->dev, PLD_REASON_DEFAULT);
		return QDF_STATUS_SUCCESS;
	}'''

if old not in s:
    sys.exit('pattern not found')

s = s.replace(old, new, 1)
io.open(p, 'w', encoding='utf-8', errors='surrogateescape').write(s)
print('PATCHED: pld assert failure schedules recovery')
