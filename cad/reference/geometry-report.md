# 参考文件检查与模型名义几何

2026-10-07。19 个原始资产：10 个 STL、3 个 STEP、3 个 F3D 和 3 个原说明/许可文件。这是文件完整性检查，没有实物验证或 CAD 内核装配验证。

STL 没有单位声明。下表是原始模型坐标的三轴包络；按作者打印情境通常解释为 mm，但这仍须实物校核。原点、XYZ 方向未登记到本项目 R/P 坐标。包络不是接口配合尺寸、相盒尺寸、拾片行程或胶片面深度。

| 原件 | 三角面数 | X × Y × Z 模型单位 | 原许可 |
|---|---:|---|---|
| [Mamiya_Press_G_V2.stl](g_adapter_v2/Mamiya_Press_G_V2.stl) | 772 | 123.519 × 112.000 × 5.150 | CC-BY-4.0 |
| [Mamiya_Press_base_V2.stl](g_adapter_v2/Mamiya_Press_base_V2.stl) | 3108 | 125.987 × 112.000 × 13.716 | CC-BY-4.0 |
| [Latch01_V2.stl](g_adapter_v2/Latch01_V2.stl) | 648 | 80.999 × 17.998 × 2.001 | CC-BY-4.0 |
| [Latch02_V2.stl](g_adapter_v2/Latch02_V2.stl) | 648 | 80.999 × 17.998 × 2.001 | CC-BY-4.0 |
| [LG_square_bar.stl](square_pressure_cc0/LG_square_bar.stl) | 108 | 4.500 × 10.600 × 79.500 | CC0-1.0 |
| [LG_square_cover.stl](square_pressure_cc0/LG_square_cover.stl) | 5068 | 11.200 × 10.850 × 95.250 | CC0-1.0 |
| [Instax_sq_cartridge_v2.stl](square_cartridge_lgpl/Instax_sq_cartridge_v2.stl) | 1576 | 78.026 × 90.499 × 18.572 | LGPL-2.1 |
| [Super67_CAD.step](super67/Super67_CAD.step) | — | 只核查 Part 21 封套和 SI 单位声明 | CC-BY-NC-SA-4.0 |
| [Super67_body_graflok.stl](super67/Super67_body_graflok.stl) | 2696 | 130.000 × 130.000 × 5.000 | CC-BY-NC-SA-4.0 |
| [Super67_body_graflok_latch_bottom.stl](super67/Super67_body_graflok_latch_bottom.stl) | 1760 | 81.000 × 20.000 × 2.000 | CC-BY-NC-SA-4.0 |
| [Super67_body_graflok_latch_top.stl](super67/Super67_body_graflok_latch_top.stl) | 1760 | 81.000 × 20.000 × 2.000 | CC-BY-NC-SA-4.0 |

G 接收座约 123.52 × 112 × 5.15 模型单位，而 Super-67 接收座为 130 × 130 × 5。外侧布局显著不同，不能把任何一组包络当原厂接环尺寸。两组锁条的长边都约 81 模型单位，只能说明名义结构接近，不能据此确定跨距、搭接、预载或互换公差。

Square 压条约 4.5 × 10.6 × 79.5、罩约 11.2 × 10.85 × 95.25 模型单位。它们只是局部压片组件，不是整个 Square 相盒。

C02 的两份 STEP 声明毫米单位，分别有 1078 和 3960 个实体记录；这些记录数不是有效实体或装配测试。三份 F3D 的 ZIP 成员及 CRC 正常，原生几何与单位尚未解析。

C01 的 STL 闭合且三角面绕向一致。另行生成的 [分面 STEP 预览](../cartridge/R0_reference_only/README.md)通过内核有效性检查，保留其参考用途和原许可。78.026 × 90.499 × 18.572 是源网格三轴包络，不能填写到实测 CARTRIDGE_WIDTH/HEIGHT/DEPTH 或乳剂位置参数。

完整 hash、源 URL 和状态见 [source-manifest.json](source-manifest.json)。pending_assets 为空。FEASIBILITY RESULT: **UNCERTAIN — MEASUREMENT REQUIRED**。
