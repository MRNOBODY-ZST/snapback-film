# 三概念竞争与双电机原型建议

R0，2026-10-07；这是实验平台概念，不是最终后背设计。**推荐 Concept B：电机 A 拾片凸轮 + 电机 B 显影滚轮。** 所有方案都受同一个未解决的原焦平面约束，评分不能消除物理干涉。

## 不可变的系统接口

`型号匹配的 RB67 → 型号匹配的原装旋转接环 → 定制定位/锁扣/真暗板 → 商售完整 Square 片盒 → 独立拾片/滚轮 → 遮光出口`

禁止任何捐献相机或专有 instant-back 模块。片盒内原有弹性结构属于耗材本身，但自制后背仍须提供经测量确认的外部压片支持。电机、轴、轴承、弹簧、齿轮是通用商品件；所有专用 carrier、cam、finger、mount 独立开放 source。普通 FDM 不作显影接触表面或轴承精密基准。

## Concept A — 单电机机械同步

商用减速电机经公开齿轮分两支：一路转凸轮、推动/抬离/回位拾片爪；另一路持续转主动滚轮并驱动从动滚轮。需共轭齿轮/弹簧浮动辊传动，不能让可调 gap 的齿轮强迫轴距固定。可考虑一主动摩擦从动作为试验变量，滑移必须实测。

单个凸轮周转对应一次拾片周期，home 检测停机；S4/S5 仍确认完整出片。定义 `k=ω_roller/ω_cam`，实际捕获角 `θ_bite`。共轴周期的必要条件：

`R_roller·k·(2π−θ_bite)·(1−s_max) ≥ L_remaining + L_margin`。

这是从夹持开始至周期结束的有效传送长度，不能用整周滚轮周长代替。角度由拾片距、cam 运动律和 nip 位置推导，不能硬套每段90°。共同轴力矩近似为 `T_cam_branch/η_cam + k·T_roller/η_roller + T_common_friction`，再乘 SF≥2；峰值和持续负载分别计算。

优点：确定机械相位、较少 actuator。风险：固定相位对打滑/片厚变化敏感；jam 后反转同时影响爪和药包；改 roller speed 会影响 pickup；复杂 cam 与减速级使打样成本提高。必须有拆卸/释放预载的 service 通路。当前不优先整合。

## Concept B — 双电机独立闭环（推荐）

电机 A：可换减速机构与可换 cam，驱动带限力、可调啮合深度和退让路径的 pickup。A 的一个完整 cam 周转对应一次进爪/推进/抬离/归位；允许在可验证 dwell 暂停。电机 B：独立驱动可拆换 roller cartridge，轴承 carrier、弹簧预载和轴线调整独立。

电源：1S 1000–2000 mAh 设计目标，保护、USB-C 充电、真实断电开关；motor 电压是否升压取决于具体型号及全电池区间力矩。两路 H 桥、两路 I(t) 测量，开发板和 USB 诊断优先，用户后续自行绘制 PCB。

建议序列：

1. 检查 S0 pack、S1 door closed、S2 dark slide out、S3 home、S4/S5 clear、电压和 persistent state。
2. 先记录 in-progress 事件；A 开始单张推进。B 在片到达 nip 前进入经实测的低速捕获状态，不能让爪把片硬顶入静止高预载 nip。
3. S4 检测前缘；结合 B 的实测位移/受载/片移动确认夹持。S4 单独不能证明片进入 nip。
4. A 抬离接触区并完成回 home；B 按经验证的速度处理药包与铺展。S5 应出现有序 active→clear。
5. S5 安装点和 roller 的距离决定尾端余量。若 S5 在末 nip 下游且遮挡范围代表整片，clear 可确认脱离；否则需 encoder + 经 slip 验证的余量。不能单用定时断定片清空。
6. A 离开后再次回 home、入口和出口完成合理序列、无故障，才 COMPLETE。黑盖成功时设10；普通片成功时减1；任何不完整事件不减且进入 JAM/SERVICE。

优势：可以分别扫描 pickup depth/stroke 和 roller speed/preload；隔离故障；A 已回 home 时仍可让 B 处理完整片。风险：更多体积/供电通道和控制逻辑；错误 handoff 会起皱或拉伤；需传感器和距离证据。两电机并不保证可靠，必须验收。

## Concept C — 电磁/线性拾片 + 电机滚轮

拾片用通用 solenoid 或小型 linear actuator，经连杆将有效位移传到爪；有回位弹簧、home 及限力机构。滚轮与 B 方案相同独立驱动，电流与 jam 管理分开。

在 M12 得到 stroke `h` 和 `F_sheet(x)` 后，对具体 actuator 的 **整个力—行程曲线** 验证：

`F_actuator(x)·η_link·M(x) ≥ 2·[F_sheet(x)+F_return(x)+F_guide(x)]`，`stroke_output ≥ h`。

其中机械优势 M(x) 增力会减少输出位移，不能同时宣称 force 与 stroke 免费增大。`E_pulse=∫V·I(t)dt`，平均热负载 `P_avg=E_pulse·cycle_rate`；检查厂家 duty cycle、复位时间、最差电池电压和 hold 电流。保持弹簧回程不能反拖正片或触碰下一片。

目前没有带实际所需 stroke/force 和适配包络的合格型号，因此该方案 **未获选型通过**。优势是结构可能简单；风险是起始大气隙拉力弱、冲击/弹跳、保持耗电、峰值电流和尺寸，不能凭“很小的电磁铁”选型。

## 加权评分

用户权重合计100。分数1–5，越高越有利；`total = Σ(weight×score)/5`，满分100。全表属于 **ESTIMATED 的研发判断**，不是成功率、成本报价或试验结果。film-plane 三者都给中性3，因为没有尺寸；这项必须另过硬门槛。

| Criterion | Weight | A 单电机 | B 双电机 | C 线性拾片 |
|---|---:|---:|---:|---:|
| Feed reliability | 25 | 3 | 4 | 2 |
| Developer reliability | 20 | 3 | 4 | 4 |
| Compactness | 15 | 4 | 2 | 3 |
| Film-plane compatibility | 15 | 3 | 3 | 3 |
| Manufacturability | 10 | 2 | 4 | 3 |
| Serviceability | 5 | 2 | 4 | 3 |
| Power consumption | 5 | 4 | 3 | 2 |
| Cost | 5 | 4 | 3 | 3 |
| **Weighted total /100** | **100** | **62** | **69** | **58** |

A 的 feed/developer 分数因耦合调试与 slip 风险降低；B/C 的独立滚轮便于实验；C 的拾片力曲线没有合格依据。B 的紧凑性较低、制造/维修较高；功耗及成本评分只表示 actuator 通道复杂度预期，未量测。若 feed 和 developer 各变动一分，权重影响为5和4分，足以改变排名。因此 **推荐 B 的主要依据是可观测与独立调整，加上用户的双电机研发偏好**；最终可靠性要用数据重评，不以69分制造产品。

## 概念级公差分析

单张拾片允许深度窗口：`depth_min + error_stack ≤ depth_command ≤ depth_max − error_stack`；若无正窗口，必须改末端/导向/压片方案。误差包含 cartridge seat、片堆位置、爪轴承间隙、制造厚度、cam runout 和动态挠曲。两侧 rail 必须能阻止偏转而不划伤图像。

roller 工作 gap 为函数 `g(F,t,pod)`，不是单个零载 gap；总预载 `F_L+F_R`、左右差和 carrier 挠度同时列入。齿轮 `CENTER_DISTANCE=m(z1+z2)/2` 只对标准未变位外啮合齿轮成立；变位、helix、材料收缩、实测 backlash 另记。gear 的 MODULE / PRESSURE_ANGLE / TOOTH_COUNT 在台账未定，不能凭装配图匹配。

## 19 个可替换模块

| 编号 | 模块 | 本阶段界面要点 |
|---|---|---|
| 01 | RB67_Interface | 机身型号与接环版本；原焦平面基准 |
| 02 | Rotating_Adapter_Interface | 独立接口 insert、锁扣、light trap 和 load path |
| 03 | Dark_Slide | 完整覆盖、labyrinth/flocking、正止挡、保持、S2 |
| 04 | Cartridge_Chamber | 三点非弹性定位，可校正 X/Y/Z，完整片盒装取 |
| 05 | Cartridge_Pressure_System | 多点可调压片，不以关门压壳代替片堆定位 |
| 06 | Pickup_Finger | rigid/sprung polymer、spring metal、TPU contact、depth stop 可换 |
| 07 | Pickup_Cam | cam law、抬离、回 home，可换不需重造 chamber |
| 08 | Gear_Train | A/B 独立；公开参数、slot backlash、service 可拆 |
| 09/10 | Roller_Left / Roller_Right | 标准精密轴和可换 sleeve/core，独立编号 |
| 11 | Roller_Bearing_Block | 加工载体/精密衬套；FDM 不定位 bearing axis |
| 12 | Roller_Spring_System | 两端可调、可测预载，防松和快速释放 |
| 13 | Motor_Mount | A/B 有调节槽、力矩反作用载荷路径 |
| 14 | Electronics | 开发板优先，用户画后续 PCB，diagnostic port |
| 15 | Battery | 1S protected，近 mount 降低悬臂，service 可换 |
| 16 | Film_Exit | 防剩余片曝光的持续 light trap、S5 不照 image |
| 17 | Rear_Cover | 正锁止/密封/S1；中途开门会曝光剩余片 |
| 18 | Service_Cover | 不须开片盒门即可接触电机/预载；开 service 不可破坏遮光 |
| 19 | Calibration_Shims | 接口位置可调但保留原焦平面；厚度实测 |

## 使用和联锁边界

相机机械保持原样。用户 cock、取暗板、对焦、快门、再 EJECT。V2 不知道快门是否触发，EJECT 就是处理当前最前片，不能显示伪造“已曝光”；未来 X-sync 必须隔离并测实际触点条件，当前不必接。

S0 无片盒或 S1 后门打开禁止电机；S2 暗板插入禁止启动 EJECT 与自动 LOAD。装新盒时黑盖仍保护片堆，装机后取暗板再按保护式 LOAD，成功才 count10。运动中 S2/S1 变化须转故障策略，不允许软件无条件继续，停/受控结束要经过假片风险试验确认。

整后背 mid-pack 拆下时暗板必须完整插入且有正保持，片盒门持续关闭、出口持续遮光；后门中途打开则正常环境不安全。两类 latch 的位置与触感区分。卸后背不能触发“新片盒”或重置计数；NVM 仅因真实 load/cover/complete/reset 和 in-progress intent 更新。

## 集成尺寸、质量与预算门槛

完整片盒位置由乳剂和 IMAGE_CENTER 决定，不能壳居中。最终 motor、电池、PCB 外轮廓由光学和机构包络给出；倾向重件靠 mount，但接口原厂允许质量/弯矩尚未知。`mass_total=Σm_i`，`CG=Σm_i·r_i/mass_total`，重力力矩 `τ=(r_CG−r_interface)×mass_total·g_vector`，按水平/仰俯及各旋转姿态评估。`mg·CG_Z`仅能在指定水平机身、参考点和轴向分量条件下作局部初算；旋转偏心也要算。携带冲击的系数待试验，不能伪造承载额定值。

prototype 用可调夹具/开发板/诊断硬件，final 去掉仅测试用仪器；成本分别见 requirements.md 的预算。后续 V3 单电机化应保留 transport 性能，再证明同步周期有 margin，不为减少一台电机牺牲验证。
