import io, sys
p = 'drivers/soc/qcom/subsystem_restart.c'
s = io.open(p, encoding='utf-8', errors='surrogateescape').read()

old = '''	panic("subsys-restart: Resetting the SoC - %s crashed.",
							dev->desc->name);'''
new = '''	/* DSH: 不 panic，让子系统自行恢复。
	 * 原逻辑是 modem 崩溃就重置整个 SoC，导致 HDMI 热插拔时
	 * USB PD 重新协商引发 modem QLINK 失败 → 整机重启。
	 * 改成只记录错误，modem 由 PIL 单独重启，系统继续运行。 */
	pr_err("subsys-restart: %s crashed, skipping SoC reset (DSH)\\n",
							dev->desc->name);'''

if old not in s:
    sys.exit('pattern not found')

s = s.replace(old, new, 1)
io.open(p, 'w', encoding='utf-8', errors='surrogateescape').write(s)
print('PATCHED: subsystem_restart panic -> pr_err')
