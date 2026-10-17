# P2 / R2 独立滚轮实验平台定义

P2 化学展液能力仍待真实片试验。本轮已有 [R0 承载/调整台架](R0_bench/README.md) 的 CadQuery 源、STEP/STL、加工目标与检查清单；自定刚性量规用于对中，真实显影接触滚轮、弹簧/调压器和驱动仍待选，不代表 P2 通过。

必须可更换：整对roller/core/sleeve、bearing carrier、两端弹簧、gap止挡、驱动接口；辊径变化不重造frame，不移动片盒曝光datum。左右独立预载测定和防松、axis adjustment、motor B独立speed、encoder标记、电流测点、遮光进片罩、受控service release。

设计依据和DOE见../../docs/roller-development.md（从本目录解析为项目docs）。各端N、gap状态、mm/s、material/硬度标度、runout、parallelism都记数，未知不能当0。真片必须完整处理，不剪切药包；普通FDM辊仅查空间，不判化学性能。

验收需重复真实film显示consistent rupture/fullspread/no systematic streak；dummy只验traction/transport。CSV见../../experiments/rollers/roller-log.csv。
