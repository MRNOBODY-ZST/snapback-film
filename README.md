# SnapBack｜即影背

**Open motorized instant-film backs for interchangeable-back medium-format cameras.**

SnapBack combines **snap** (taking a photograph) and **back** (an interchangeable camera back). The project develops its own pickup, transport and processing mechanism using commodity parts, without a donor instant camera. Original project code, CAD and documentation use the [MIT License](LICENSE); separately licensed references are listed in [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md).

**为可换后背的中画幅相机开发开源电动即时成像后背。** 名字不绑定机身或画幅；当前第一个研究模块是 **Mamiya RB67 / Pro-S / Pro-SD × Instax Square（V2 无供体方案）**。其他机型属于后续适配方向，尚无兼容性验证。平台边界与扩展规则见 [platform.md](docs/platform.md)。

**阶段：R0 工程可行性研究，2026-10-07。未制造、未实测、未完成最终后背。**

**FEASIBILITY RESULT: UNCERTAIN — MEASUREMENT REQUIRED**

目标架构为 `RB67 → 与机身型号匹配的原装旋转接环 → 自制电动后背 → 商售 Instax Square 整盒胶片`。所有拾片、传送、显影滚轮、驱动与控制均自制或使用通用商品件。禁止依赖任何 Instax 捐献相机、专用后背或 Jollylook 显影总成。

当前不能确认片盒在保留原旋转接环时能否到达原焦平面。片盒厚度、接环内部空腔和乳剂位置未取得可信数值，不能把后背向后移来掩盖干涉。本阶段推荐 **双电机实验平台**：A 驱动可更换凸轮与拾片爪，B 独立驱动可换显影滚轮盒。

## 首阶段交付

| 文档 | 内容 |
|---|---|
| [research.md](docs/research.md) | 结论、来源、已知量与证据缺口、下一步决策 |
| [measurements.md](docs/measurements.md) | 给用户的实测清单、基准、工具、记录要求与夹具方案 |
| [architecture.md](docs/architecture.md) | 三套完整概念、加权评分、模块分解、双电机推荐 |
| [film-plane.md](docs/film-plane.md) | 原焦平面约束、干涉判据、公差链、成像中心与旋转包络 |
| [transport.md](docs/transport.md) | 单张分离、拾片、进入滚轮、机械周期和回退风险 |
| [roller-development.md](docs/roller-development.md) | 滚轮制造比较、可调试验机与实验设计 |
| [patents-and-prior-art.md](docs/patents-and-prior-art.md) | 原始专利、参考项目、证据适用范围与独立设计原则 |

新增：[已有 CAD 检索与采用](docs/open-cad-sources.md)、[参考归档](cad/reference/README.md)、[模型几何检查](cad/reference/geometry-report.md)。外形建模从已有模型校核开始；原焦平面及接环空腔仍需实测。

工程准备另提供 [计算与日志工具](tools/README.md)、[相盒参考 STEP 预览](cad/cartridge/R0_reference_only/README.md)、[C++17 双电机控制核心](firmware/README.md)，以及两个独立台架版本目录中的开源 CAD。台架的自定尺寸用于实验平台，不能当作相机或片盒实测尺寸。

这轮交付与待测门槛集中在 [preparation-status.md](docs/preparation-status.md)，台架 PCB 的尺寸和逐针接口见 [R0_bench-interface.md](electronics/pcb/R0_bench-interface.md)。

补充：[PCB 交接规范](electronics/pcb/interface-contract.md)、[电子与供电研究](docs/electronics.md)、[试验门槛](docs/testing.md)、[FMEA](docs/fmea.md)、[需求映射](docs/requirements.md)。用户负责绘制 PCB；项目将提供验证后的机械板框和接口坐标。目前板框、孔位和接口坐标保留为待测。

## 数据纪律

中央参数台账：[cad/parameters.json](cad/parameters.json)。`UNKNOWN` 必须为 `null`，并标注 `MEASUREMENT_REQUIRED`。厂商公布的相纸 86 × 72 mm、图像 62 × 62 mm 不代表片盒外形、拾片接口或乳剂深度。专利附图不是可缩放工程图。

`cad/source/instax_square_cartridge.measurement.json` 是测量状态定义，**不是已完成实物校准的片盒实体模型**。cad/reference 中有独立标注原许可的第三方参考 STEP/STL。自制台架与相盒参考预览的导出分别有清单和用途限制；参考预览不供制造，台架不声明整机适配或显影合格。最终相机后背 CAD、PCB/Gerber 和可刷写产品固件仍未交付。尺寸不足时的相机剖面图为符号示意，不能用于加工。

## 怎样推进

1. 按 [measurements.md](docs/measurements.md) 完成 M01–M06 的第一轮基准和外形测量，记录机身/接环型号、仪器精度和照片。
2. 先闭合原焦平面及片盒空腔尺寸链，再决定 `PASS / PASS WITH MODIFICATION / UNCERTAIN — MEASUREMENT REQUIRED / FAIL — PHYSICAL INTERFERENCE`。
3. 并行开发独立拾片试验机和滚轮试验机；先假片，后完整真实胶片验证显影。
4. 通过门槛后才开发集成后背和最终外壳。所有历史版本和试验失败保留。

任何 99%、99.5%、零漏光或 100 次可靠循环均为要求或目标，当前没有实现证据。

操作准备见 [装配入口](docs/assembly.md)、[标定执行单](docs/calibration.md)、[故障定位原则](docs/troubleshooting.md)。所有工程物理门槛仍开放；主机软件测试和 CAD 内核检查不能替代实物验收。

原创固件、工具、参数化台架 CAD、原创导出与文档按 [MIT](LICENSE) 发布。第三方模型及其派生参考预览适用原许可；其中 Super-67 参考文件为 CC BY-NC-SA，C01 相盒参考与派生预览为 LGPL，不能作为 MIT 原创使用。完整路径与作者见 [第三方声明](THIRD_PARTY_NOTICES.md)。第三方说明书、专利、照片和商品资料保留原权利，不随本项目重新授权。
