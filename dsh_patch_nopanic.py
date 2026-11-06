import io, sys

p = 'drivers/soc/qcom/subsystem_restart.c'
try:
    s = io.open(p, encoding='utf-8', errors='surrogateescape').read()
except IOError:
    p = '/home/yue123/ksrc/drivers/soc/qcom/subsystem_restart.c'
    s = io.open(p, encoding='utf-8', errors='surrogateescape').read()

old = '''	panic("subsys-restart: Resetting the SoC - %s crashed.",
							dev->desc->name);'''

new = '''	/* DSH: 仅对 modem 跳过 SoC 重置。
	 * modem 崩溃（HDMI 热插拔时 USB PD 重协商引发 QLINK 失败）
	 * 会重置整个 SoC 导致整机重启，这里改为只记录错误。
	 * 其它子系统（WCNSS/WiFi、ADSP、CDSP 等）必须保留原来的
	 * SoC 重置逻辑，否则崩溃后无法恢复（WiFi 会打不开）。 */
	if (!strncmp(dev->desc->name, "modem", 5)) {
		pr_err("subsys-restart: %s crashed, skipping SoC reset (DSH)\\n",
							dev->desc->name);
	} else {
		panic("subsys-restart: Resetting the SoC - %s crashed.",
							dev->desc->name);
	}'''

if old not in s:
    sys.exit('panic pattern not found')

s = s.replace(old, new, 1)
io.open(p, 'w', encoding='utf-8', errors='surrogateescape').write(s)
print('PATCHED: no-panic only for modem')
