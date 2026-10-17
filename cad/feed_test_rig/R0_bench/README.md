# R0 开放进片观察台／可换末端滑架

状态：`R0_FIXTURE_ONLY_PROTOTYPE`，`mode=TEST_FIXTURE_ONLY`。允许制造独立实验台架原型，尚未做物理可靠性验证，未授权制造最终相机后背。所有台架数值为 OWN_DESIGN 的 ESTIMATED/DERIVED；片盒外形、取片边缘／深度、满盒到末片受压高度、实际拾片力与背压继续 `UNKNOWN/null`。

## 交付范围

`feed_bench.py` 和 `config.json` 可重新生成 `exports/feed_bench_R0_fixture_only.step`（17 个单实体）及分件 STL；共用代码在邻接的 `cad/roller_test_rig/R0_bench/`，两目录一起保存。`exports/manifest.json` 登记文件 SHA-256、来源、派生式与几何检查；`manufacturing-spec.json` 给出关键候选加工公差和量测方法。

本台架为开放、可观察的空盒／已显影片几何实验平台。末端只是带两个安装孔的矩形 **blank end plate**，没有对应 Instax Square 片盒的真实拾片爪、止逆边或背压接触头。没有片盒定位腔、相机接口、暗板或最终出片口；默认围栏 opening 不是相盒宽度。

## 坐标与调整

`B_F` 原点为底板下表面中心，X 沿手动滑架前进方向，Y 横向，Z 向上；不代表相机 R 或片盒 P 坐标。滑架支持一个后续可换、需另行测量设计的末端。

|台架名义量|数值／来源|用途|
|---|---|---|
|底板|240 × 160 × 10 mm，OWN_DESIGN/ESTIMATED|独立平台|
|两导轨|130 × 20 × 10 mm，X中心 −35，Y中心 ±55，OWN_DESIGN/ESTIMATED|经过整段滑架行程检查的加工支承|
|滑架 X admissible 范围|−60 到 0 mm，OWN_DESIGN/ESTIMATED|槽圆弧中心间 60 mm；真实螺杆／止挡位置需校准|
|末端支承梁下表面 Z|30–80 mm，OWN_DESIGN/ESTIMATED|50 mm 垂直调整；具体姿态仍须无干涉|
|观察台|80 × 140 × 8 mm，X中心 75，OWN_DESIGN/ESTIMATED|起点 X35，比导轨端点 X30 外移5，避免交叉|
|三垫块上表面 Z|21 mm，OWN_DESIGN/DERIVED|通用支承；不是相盒 datum|
|侧围栏中心的绝对 Y|20–62 mm，OWN_DESIGN/ESTIMATED|独立平台调整范围|
|通用净宽|26–110 mm，OWN_DESIGN/DERIVED|2 × 中心偏置 − 围栏宽14；不可回填相盒 envelope|
|当前围栏净宽|100 mm，OWN_DESIGN/DERIVED|停放值而非物理兼容尺寸|
|当前 blank 下表面到垫块距离|37 mm，OWN_DESIGN/DERIVED|停放值而非实际 pickup depth|

调整量不能任意组合：滑架 X=0、梁下表面 Z=30、围栏中心 |Y|=20 时矩形 blank 会撞围栏；代码明确拒绝这个姿态。已检查宽围栏下的上下／前后端点及窄围栏的抬高末端位置；真实相盒加入后必须重新测量和做全行程扫掠。

## 加工和装配限制

底板、导轨滑动面、滑架、窄竖板、梁、围栏、金属通用垫块和桥柱需要加工。普通 FDM 可用于无载空间样件、编号牌或视觉副本；本输出没有可直接用于承载／精密导向／照片接触的普通 FDM 零件。实际已显影片或未显影片接触的末端／垫面材料要重新选择，避免划伤与污染；没有导出虚假的“普通打印爪”。分件 STL 是网格加工参照，0.05 mm 导出 tessellation 不是加工公差。

先按 `manufacturing-spec.json` 量测导轨槽宽、承载面共面、窄板壁厚、pilot 和孔距，再装配。导轨下面留 10.5 mm 宽、4 mm 深的可俘获头槽；它只是 OWN_DESIGN 候选包络，没有假称标准螺栓头尺寸。自定义 10 × 10 × 3 mm 方头候选或另选经实测适配的夹持件要先在槽内试滑，再把导轨从底板下固定。导轨固定点 X=−90、+20，避开滑移槽。上方锁紧件放松时手推滑架，锁紧后做静态观察；不声明它等同精密直线导轨或有已验证重复定位精度。

两竖板从滑架下方固定，梁从 X方向通过竖槽侧夹，可换 blank 从上方装在梁上。竖板只有 6 mm 宽，通孔／pilot 周围壁薄，所有 screw/pilot、攻丝钻尖余量、实际垫片和啮合长度须由加工方确认；CAD 未建螺纹／真实紧固件。观察台的紧固头要完全落入已预留沉孔，不能高出上表面。通用垫块在 dry setup 可用适合材料的可移除夹具胶固定，再量测三点平面；未选最终相盒压紧方法或照片接触胶材。

桥与两柱只为将来经量测的背压机构提供独立承载安装位置。调整孔是 pilot；实际调压杆、弹簧、压力头、力传感器和力／行程标定未选择，图中没有这些实体。安装满盒、末片、背压头和真实 pickup tip 前，先补齐物理接口参数和整段路径包络，并复验 clamp hardware／刚性；当前装配没有证明真实 Square cartridge 可以定位、抽一张或承受药囊展开力。

建议起步顺序：金属平台空载装配 → 手动扫行程并记录游隙 → 夹持可逆的尺寸样件／空盒只做观察 → 实测片盒出口、拾片深度、满末片位置与受力 → 另制可换末端 → 测量单张拾取和返回过程。当前 CAD 的最终后背与真实片路许可均为 false，不可用本台架通过来代替原片面／暗箱测量。

## 复现与已完成检查

从项目根（PowerShell）：

先按相邻 [滚轮台架说明](../../roller_test_rig/R0_bench/README.md)创建 CAD 环境；本项目交付不携带本机 venv。

```powershell
.\.tools-venv\Scripts\python.exe cad/feed_test_rig/R0_bench/feed_bench.py
.\.tools-venv\Scripts\python.exe -m pytest cad/roller_test_rig/R0_bench/test_roller_bench.py cad/feed_test_rig/R0_bench/test_feed_bench.py -q
```

两台架合计 24 tests，包括 UNKNOWN/null 拒绝、来源／单位拒绝、行程端点、已知碰撞组合拒绝和 STEP 回读。进片装配 17 个单实体，有效且正体积，136 对名义组合无正体积交叉；STEP 回读保留实体，包络差小于 0.001 mm。这是模型文件检查，没有达到实际相盒定位、拾片、力学可靠性或加工精度的证明。

项目内导出清单路径相对项目根，项目外测试导出使用绝对路径。`physical_validation=false`、`final_back_manufacturing_authorized=false`、`fixture_manufacturing_authorized=true` 仅表示本独立台架可以按上述加工／装配限制试制。

CAD 格式方法见 [CadQuery 官方导入导出文档](https://cadquery.readthedocs.io/en/latest/importexport.html)。
