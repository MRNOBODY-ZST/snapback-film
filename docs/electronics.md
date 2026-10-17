# 电子与控制可行性研究

资料核对日期：2026-10-07。用途：完全自制、无 donor 的 RB67 → Instax Square 电动后背第一阶段设计研究。首样主架构为电机 A 驱动拾片拨片/凸轮、电机 B 驱动显影滚筒；两路独立 H 桥、独立电流观测。本文是器件候选和待验证控制要求，不是最终 BOM、原理图或已验证固件。

## 1. 选电机之前必须得到的量

电机额定电压和空载转速并不能证明能推片或压破药包。分别实测黑盖与第 1–10 片的拾片阻力、进入滚筒峰值阻力、破包峰值、稳定输送阻力及滚筒空载阻力；覆盖目标温度、电池最低工作电压、制造公差与重复循环。不得以持续堵转来测小齿轮箱能力。

以滚筒半径 `r`、轴角速度 `ω_B` 表示滚筒轴负载：

```text
T_B(θ,t) = r·[F_transport(θ,t) + F_pod(θ,t)]
           + T_bearings + T_seals + T_roller_hysteresis + J_B·α_B
T_B,design ≥ SF·max(T_B), SF ≥ 2
ω_B = v_film/r; n_B = 60·v_film/(2πr)
```

`F_pod` 是沿输送方向的额外破包阻力；如果使用直接测得的总拉力 `F_total`，则用 `r·F_total`，不可再重复加一次 `F_pod`。压紧弹簧的法向力决定摩擦、变形与破包条件，不能直接把法向力全部乘半径当成轴转矩。`v_film` 与药液铺展质量之间的可接受窗口须通过实际片材试验确定。

拨片凸轮由虚功计算，而不是只按凸轮外半径乘力：

```text
T_A(φ) = F_pick(x)·dx/dφ + F_return(x)·dx/dφ
         + T_cam_friction(φ) + T_A_bearings + J_A·α_A
T_A,design ≥ SF·max(|T_A|), SF ≥ 2
```

上式的弹簧与拾片力分别按实际行程方向计符号；设计峰值以阻碍运动的最坏组合为准。若电机减速箱输出与负载轴之间还有外部减速 `g = ω_output/ω_load`，则电机减速箱输出所需转矩为 `T_load/(g·η_external)`，转速为 `g·ω_load`。厂家表中的齿轮电机输出转矩已经包含内置减速箱，不能再次乘其减速比。

单电机共轴备选必须把凸轮负载折算到同一轴：令 `φ = k·θ`，则 `T_common = T_B + k·T_A/η_cam_branch + T_common_loss + J_common·α`。`k` 是凸轮轴与滚筒轴速度比，凸轮相位决定负载峰值是否叠加。不能把两根轴的转矩直接相加，也不能假定黑盖与破包峰值总不重叠。双电机可改变时间调度，但交接阶段可能两路同时运行，电源仍按实际重叠峰值核算。

如果 C 方案指电磁铁拾片：设 `m_displacement = 拨片位移/电磁铁位移`，必须验证全行程最弱点 `F_solenoid(x,V_min,T_hot)·η_link/m_displacement ≥ SF·[F_pick(x)+F_return(x)+F_friction(x)]`，且有效行程满足 `s_solenoid·m_displacement ≥ s_pick`；机械位移放大会减小力。分别核算 `E_actuation=∫V·I dt`、线圈热量 `∫I²R dt`、释放/回位时间和弹簧失效状态。保持型或脉冲型电磁铁均需单独驱动与续流安排；没有力—行程—温升实测曲线，不给出最终型号。

## 2. 有明确供应商型号的电机候选

扭矩统一使用 `mN·m`；`1 kgf·cm = 98.0665 mN·m`。以下仅是对照，不表示其中任一型号已满足滚筒或拨片负载。电机 A 与 B 不必同型号。

| 候选 | 厂家参考条件、输出速度 | 堵转电流/转矩 | 持续或间歇能力 | 外形与资料 |
|---|---|---|---|---|
| FingerTech/CASFAB **N10 Micro Spark 12mm，50:1** | 额定 6V，工作范围 3–9V；厂家产品表在 **7.4V** 给出空载 740rpm | 6V 0.85A；7.4V 1.05A、1.02kgf·cm ≈ **100.0mN·m** | 产品页没有给出持续输出额定转矩，不能用堵转值作为工作值 | 齿箱 12×10×9.1mm；电机长13mm；前轴Ø3mm、长10mm；不计焊线的机体轴向长由两段相加为22.1mm。[供应商原始规格](https://mail.fingertechrobotics.com/proddetail.php?prod=N10-Micro-Spark)，[50:1 PDF](https://www.fingertechrobotics.com/prodimages/drivemotors/Micro_Spark_N10_50_1.pdf) |
| Pololu **#2367，100:1 Micro Metal Gearmotor MP 6V**；外形相当于常称的 N20/GM12 类，按 #2367 下单 | 6V；精确减速100.37:1；空载220rpm、70mA | 0.67A；0.94kgf·cm ≈ **92.2mN·m**，厂家说明为外推堵转值 | 最大效率点170rpm、0.19kgf·cm ≈18.6mN·m、0.17A；这不是独立的连续额定保证 | 商品页列10×12×25mm；专用尺寸图无编码器 MP/HP 的 OL 最大25.6mm，前轴标注10mm，Ø3mm；商品页脚另出现26mm，应按专门图纸和实物统一长度基准。[原始产品规格](https://www.pololu.com/product/2367/specs)，[尺寸 PDF](https://www.pololu.com/file/0J949/micro-metal-gearmotors-dimensions.pdf) |
| Pololu **#1101，100:1 Micro Metal Gearmotor HP 6V** | 6V；100.37:1；空载310rpm、100mA | 1.6A；1.7kgf·cm ≈ **166.7mN·m**，外推堵转值 | 需根据厂家负载曲线和实际工作时间验证温升，不以高功率名称代替持续能力 | 同10×12mm截面，按无编码器 HP 尺寸图处理轴向包络。[原始产品页](https://www.pololu.com/product/1101)，[现行 Micro Metal 数据表](https://www.pololu.com/file/0J1487/pololu-micro-metal-gearmotors.pdf) |
| Precision Microdrives **206-10C，699.5:1 Nano Planetary** | 3V；空载47rpm；额定负载速度37rpm | 最大瞬时堵转/启动235mA；2026年表的典型堵转转矩 **32mN·m** | 额定持续10mN·m；最大间歇25mN·m；最大额定负载电流95mA；最大工作电压4V | Ø6×20.8mm机体；Ø2×3.6mm前轴。2026年表仍标“Samples available”，早期详细表标SAMPLING；需取得批次合格与交期确认。[2026年厂家规格 PDF](https://www.precisionmicrodrives.com/datasheets/206-10C-V0.pdf)，[详细样品数据表](https://precisionmicrodrives.com/cdn/catalog_product/808490dd-caee-47f6-a1e0-68704768dd8d/206-10c-datasheet.pdf) |

N10/N20/GA12-N20 是尺寸或市场类别，不能识别绕组、齿轮比、刷型与可承受电流；采购条目必须绑定供应商料号、版本、实物轴向尺寸和测试电压。表中 N10 的740rpm与100mN·m是7.4V条件，不能拿来当1S直驱数据。Pololu 的一般建议是连续负载控制在约25%堵转电流/转矩以内，同时不能超过齿箱自身上限；这只能作为早期筛选依据，实际间歇循环仍需验证温升与齿寿命。[Pololu 堵转/连续负载 FAQ](https://www.pololu.com/product/2367/faqs)

206-10C 当前商品网页出现“Nominal current(A)=95 A”和电感“75mH”的字段值，而对应 PDF 明确为95mA和75µH；本文采用 PDF。网页还列0.19A堵转电流，而2026年 PDF 列最大235mA；按最大值预估供电，取得供方批次规格后再冻结。[发生冲突的原始网页](https://www.precisionmicrodrives.com/products/342a0fa3-b655-4f25-8f45-240ef142e8dc/206-10c-6mm-dc-coreless-gearmotor)

## 3. MCU 与双路 H 桥

| 候选控制器 | 已核对特性 | 对本方案的取舍 |
|---|---|---|
| **STM32C031K6** 或需要更多接口时 C6 | Cortex-M0+最高48MHz，32KB Flash、12KB SRAM、12位ADC、PWM定时器、SWD；供电2.0–3.6V；K封装系列30 GPIO，C系列45 GPIO；具可配置 BOR；Flash耐久下限10k擦写周期。[ST 数据表](https://www.st.com/resource/en/datasheet/stm32c031c6.pdf) | 对双PWM、六传感器、三路ADC、联锁与调试接口较宽裕；使用受控3V3，不能接满电4.2V电池。C031无原生USB外设，USB调试需串口桥或外置适配器。暂优先评估，尚未冻结封装/管脚。 |
| **ATtiny1616** | 16KB Flash、2KB SRAM、**256B EEPROM**、10位ADC、PWM、WDT/BOD、UPDI；供电1.8–5.5V；20MHz需≥4.5V，3V3按≤10MHz；EEPROM耐久100k周期、Flash10k。[Microchip 完整数据表](https://ww1.microchip.com/downloads/aemDocuments/documents/MCU08/ProductDocuments/DataSheets/ATtiny1614-16-17-DataSheet-DS40002204A.pdf) | 可做精简控制器，片内EEPROM便利；20脚型号的可用I/O要逐脚核算，完整独立联锁、充电故障、双电流和调试可能超预算。产品页简介的128B与PDF/参数栏不一致，以PDF256B为依据。 |
| **ESP32-C3-MINI-1-N4X** | RISC-V最高160MHz、4MB Flash、400KB SRAM；15 GPIO含3 strapping脚；3.0–3.6V供电，电源须具至少0.5A供应能力；模组13.2×16.6×2.4mm；有USB Serial/JTAG。[Espressif 当前模组数据表](https://documentation.espressif.com/esp32-c3-mini-1_datasheet_en.pdf) | 若要无线遥测可考虑，首样无需无线时增加面积、电源瞬态与启动管脚约束；15 GPIO对完整接口不足，要外扩并保留关键联锁直连，故不是无条件替换C0的方案。 |

所有方案均需先完成管脚/复用分配表。运动控制、门联锁、home/entry/exit和电流采样不依赖慢速I/O扩展器。日志存储形式见第6节。

| 驱动候选 | 1S/升压兼容与功能 | 限制 |
|---|---|---|
| **DRV8213RTE**，每台电机独立一颗 | VM 0–11V、VCC1.65–5.5V；4A**峰值**；240mΩ典型桥路电阻；IN1/IN2正反转、IPROPI电流镜、VREF限流、nFAULT/nSTALL；3×3mm WQFN。[TI 数据表，表5-1/7.3/8.4](https://www.ti.com/lit/ds/symlink/drv8213.pdf) | 4A不是可不经散热验证持续输出的额定电流。RTE具可调VREF和启动忽略时间，较适合研究；DSG 2×2mm版本无nSTALL/nFAULT且参考固定，不能当成相同接口。低电流高GAINSEL会提高低侧电阻，须计压降。 |
| **DRV8837** + 每路独立外部电流检测 | VM0–11V、逻辑VCC1.8–7V；1.8A**峰值**；280mΩ典型；有nSLEEP；2×2mm WSON。[TI 数据表](https://www.ti.com/lit/ds/symlink/drv8837.pdf) | 无集成电流观测/可调工作限流，须增加合适分流与放大；单测电池总电流不能判断A、B哪个卡住。HP6V的1.6A堵转距1.8A峰值较近，不能未经最坏条件测试采用。 |

DRV8213RTE 的小封装没有独立nSLEEP引脚；独立 `A_ARM/B_ARM` 必须通过外部门控把对应IN1/IN2同时强制为0，或采用经验证的独立电源关断路径，不能在接口中虚构芯片使能脚。外部门控在MCU复位/掉电、门开或锁存故障时立即失能；驱动内部自动重试不能造成反复推片。电流用于识别负载和触发保护，不能单独证明“已出片”。

每路保留 `ADC_I_A/ADC_I_B`，经电流镜的电阻/增益和ADC参考校准为安培。约束 `V_IPROPI` 在数据表许可范围内，低电池时不能假定能输出完整3.3V。阈值分别实测：空载、启动、拾片、交接、破包与稳定输出。启动峰有独立短暂忽略窗口，窗口结束后必须结合“电流高且无传感器进展”判断卡滞；硬件限流与安全最长通电时间在窗口内仍有效。

## 4. 单节锂电、USB-C 与供电预算

功能路径建议为 `USB-C 5V → 输入保护/电流预算 → 单节充电及power-path → SYS → 3V3逻辑 + 可控电机电源 → A/B H桥`，电芯端另有匹配电芯规格的独立保护。USB充电、充电路径保护与电芯保护是不同职能。

**BQ25185** 候选支持单节、最高1A充电、power-path、NTC及输入/电池故障保护；电池至SYS推荐放电上限3.125A，BATOCP典型约3.13A且精度±18%；选4.2V充电配置时，有USB供电的SYS典型可为4.5V。[TI 当前BQ25185数据表，2026-08 Rev B](https://www.ti.com/lit/ds/symlink/bq25185.pdf) 因此不能把SYS直接接最大4V的206-10C，也不能把“1S系统”理解为每一节点始终≤4.2V。数据表的推荐输入、正文输入描述存在范围差异，本项目只评估5V USB条件，未授权任意高压输入。

**BQ29700 + 背靠背保护MOSFET** 是独立1S保护候选：OVP4.275V、UVP2.800V，具有充/放过流与短路检测；这两个电压和保护电流必须核对最终电芯。保护电流通过MOSFET压降检测，受FET电阻与温度影响，不等于固定“几安培保险丝”。[TI BQ297xx数据表，器件比较表](https://www.ti.com/lit/ds/symlink/bq2970.pdf) 原型也可使用具有可追溯电芯和保护规格的成品受保护电池；不得仅凭“带保护板”四字核定峰值能力。

USB-C受电端CC1、CC2分别设置Rd，典型5.1kΩ，不能并为一个节点。Rd只建立受电关系，不自动许可1A/3A充电；若需要超过来源允许的默认电流，必须读取CC通告、相应调节**总输入**预算，USB枚举等要求也须按连接类型处理。[Espressif USB-C硬件设计指南](https://docs.espressif.com/projects/esp-iot-solution/en/latest/usb/usb_overview/usb_typec_hardware_guide.html) 第一阶段没有完成CC/USB功率识别时采用保守固定低输入限流；充电电流小于电芯允许值、输入可用预算减去系统负载、以及散热允许值三者中的最小值。不能把500mA描述为所有未枚举PC端口普遍无条件可取的额度。

运动前允许有USB供电，但充电控制在循环前暂停充电；完成循环后再恢复。该策略便于稳定预算和测量，不代替power-path设计。5V USB与电池补流共同工作时仍有充电器路径、电芯和电机电源的上限，插USB不能证明电机一定不会欠压。充电器NTC随电芯布置，不能用板温代替；首次PCB仍需热测试。

能量和峰值电流必须分开：

```text
E_cycle = ∫[V_A·I_A + V_B·I_B]dt / η_motor_supply + E_logic + E_sensors
E_pack = E_black_cover + Σ(i=1..10)E_cycle,i + E_idle
Q_needed_Ah ≥ (N_packs·E_pack / 3600) / (V_nom·η_usable)
I_cell,peak ≥ (V_A·I_A,limit + V_B·I_B,limit + P_logic) / (V_cell,min·η_supply)
ΔV_sag ≈ I_cell,peak·(R_cell + R_protection + R_connector + R_wire)
```

仅作算术示例，假设6V电机、3.0V电池、85%升压效率：#2367在0.67A堵转时输入约1.58A；#1101在1.6A堵转时约3.76A。两台相同电机同时堵转约3.15A或7.53A，尚未加逻辑功耗。这些是按数据表堵转数算出的电源压力，**不是正常循环需求，也不是允许工作点**。前者已贴近BQ25185路径上限，后者明显超出；需限流/错峰或重新选择路径，不能直接套用同一充电模块。

只有实测表明最低电池电压直驱不满足扭矩/速度窗口，才决定升压。升压提高电池输入电流、引入效率与启动瞬态；6V/7.4V资料不能替代3.0–4.2V实测。需6V时可研究**TPS61089**：输入2.7–12V、输出4.5–12.6V、2.0×2.5mm VQFN，范围覆盖1S→6V；“7A”是连续开关电流能力，不能作为6V输出7A保证。其EN关闭后输入仍可经体二极管到输出，不能代替H桥独立失能；电感饱和、限流、补偿、反电动势与温升需一起验证。[TI TPS61089数据表，7.3及8.3.2](https://www.ti.com/lit/ds/symlink/tps61089.pdf) 第一阶段没有冻结升压器或外围数值。

3V3逻辑可研究TPS63802降升压（输入1.3–5.5V、输出1.8–5.2V，输出能力受输入与热条件限制），使逻辑供电跨过电池电压下降过程；这不允许把电芯放至该芯片最低输入电压。[TI TPS63802数据表](https://www.ti.com/lit/ds/symlink/tps63802.pdf) 持续容量、C倍率、最低可用电压、保护阈值、连接器额定、铜箔与熔断/限流安排都留到实测峰值与电芯资料匹配后冻结。

## 5. 状态机要求，不是固件实现

本节是电子控制所需的诊断和运输子阶段说明；正式固件状态名称及转换契约以[主固件说明](firmware.md)为准，不能把这些补充子阶段当成另一套顶层状态机。卡片故障恢复统一为`STOP → 一次已验证安全的有限回退（若允许） → STOP → 显示JAM并锁存`，没有自动前进重试。

统一传感器：S0=`pack_present`，S1=`door_closed`，S2=`dark_slide_inserted`（相机暗板），S3=`pickup_home`，S4=`roller_entry`，S5=`film_exit`。S4/S5为有片占据各自检测位置时有效。片盒黑盖不是S2相机暗板。

| 状态 | 进入条件及动作 | 允许出口 |
|---|---|---|
| `OFF / BOOT_SAFE` | A/B硬件失能、两桥IN1/IN2拉低；读取复位原因、传感器与日志，禁止上电自转 | 自检正常→静止状态；未完成intent→`CYCLE_UNCERTAIN` |
| `NO_PACK / DOOR_OPEN` | 无片盒/门未关；失能电机，READY禁止；门开不自动重置计数或认定新盒 | 明确新盒安装/确认→`LOAD_PENDING`；原盒重合门→核对原日志，不重装计数 |
| `LOAD_PENDING` | 用户明确确认完整未使用新盒，黑盖仍保护片材；计数显示`LOAD`而不是10 | S0/S1有效、S2无效、S3有效、S4/S5清空、电量合格、明确LOAD→`LOAD_BLACK_COVER` |
| `LOAD_BLACK_COVER` | 先持久化cover intent，再执行与片材匹配的A/B有界交接；不占用照片计数 | 完整S4/S5通片事件且A归home→原子提交`cover_done=true,count=10`；否则故障/不确定 |
| `READY / SLIDE_BLOCKED` | cover_done、count>0、A在home且S4/S5清空。S2插入时显示联锁阻止启动；只接受新的按钮边沿，不接受上电时已按下按钮 | S0/S1有效且S2无效、低电量检查合格、明确EJECT→`PRECHECK` |
| `PRECHECK / JOURNAL_INTENT` | 锁定cycle_id/count_before，确认传感器初态；**写完并校验未完成intent后**才能开桥 | 成功→`PICK_ADVANCE`；写入失败→锁存故障，不运动 |
| `PICK_ADVANCE` | A按软启动和限流离开home；B可按经实测的交接提前量启动。必须看到S3有效→无效 | 有界时间内S4进入有片→`HANDOFF`；离位/入口超时→卡滞判断 |
| `HANDOFF` | S4证实到达滚筒入口后，B承接；A按照不会再次拾片的已验证回程归home；A、B可重叠但电源按叠加峰值设计 | S5出现有片→`EJECT_ROLL`；S4→S5超时→锁存故障 |
| `EJECT_ROLL` | B持续滚压输出；验证S4、S5各自有片→无片，S5必须先出现再释放 | S5清空且S4清空→`WAIT_PICK_HOME`；电流/总运动超时→故障 |
| `WAIT_PICK_HOME / VERIFY` | 若A尚未归home，按限定的安全回程等待S3；停B方式/余量由滚筒实测冻结 | 已离位后重新稳定home、所有通片事件有效→`COMMIT`；否则故障/不确定 |
| `COMMIT` | 同cycle_id只提交一次；普通片`count=count_before−1`，黑盖`count=10`；记录完整终结状态、校验成功才显示结果 | count>0→READY/SLIDE_BLOCKED；count=0→`EMPTY` |
| `EMPTY` | 禁止普通EJECT；门开仅更换流程，不默认新盒 | 新盒明确确认→LOAD_PENDING |
| `LOW_BATTERY` | 启动前禁止运动；运动中触及保护边界则关断并将循环记不确定 | 静止电压恢复不自动重试，需要重新核对状态 |
| `JAM_STOP / RECOVERY_ONCE` | 两桥停止，保存故障/逆转标志；仅在第7节安全区有条件进行一次A有限回退 | 回退后再次STOP→显示JAM并进入`FAULT_LATCHED`；无安全回退条件则直接锁存；不自动前进或补送 |
| `FAULT_LATCHED / CYCLE_UNCERTAIN` | 包括次序不可能、传感器粘连、运动中门开/片盒消失、欠压、复位、日志损坏、部分出片 | 不再自动喂片，不自动扣/增计数；服务模式明确处理后退出 |
| `SERVICE` | 双电机默认禁用；检查、移除/隔离卡片并证明机构空载或只有安全dummy后，才允许明确人工触发的单电机有界低限流死手点动；不能连续强推卡片 | 人工处理记录并核对状态后才可重新arm；无自动进片、无卡片前进重试，不用服务按钮假造通片成功 |

默认首阶段S2插入禁止普通EJECT及LOAD黑盖运输启动。装盒流程为：插盒关门并保留黑盖→装机→取出相机暗板→确认LOAD→黑盖完整退出及A归位→10/READY。只有几何实测证明暗板与运输完全独立，后续版本才能放宽LOAD联锁。运动中插入S2应阻止下一循环；当前动作按预先验证的停机策略处理，不能因没有分析的突然反转/急停再损坏半出片。

S4与S5距离和片长决定两路占据区间是否重叠，不预设“S4必须先清空才能触发S5”。必须证明每一路完整的无片→有片→无片过程以及S4进入早于S5进入；异常反弹经消抖后才成为事件。`S3=true`静态电平不能当作归位证明，本循环必须先看见离home，再看见返回。设独立 `t_leave_home_max、t_entry_max、t_exit_enter_max、t_exit_clear_max、t_return_home_max、t_total_max`，并有硬件最长使能/看门狗；全部为`MEASUREMENT_REQUIRED`，不发布猜测的“几秒”定值。没有入口/出口进展但电流偏低也可能断线或传动打滑，不能只监控过流。

## 6. 掉电、计数与存储磨损

`count`从黑盖循环成功提交后才设10；普通照片只有**完整退出证据 + 本循环A离位后归home**均有效才减1。黑盖不执行“10→9”；按下EJECT、到达S4、S5开始占据、经过固定时间或电流下降都不能扣片。

必须保存具CRC/版本/递增序号/pack_session/cycle_id的日志，至少包含 `count_before、cycle_kind、in_progress、cover_done、reverse_used、commit_status`。顺序：准备并校验intent→执行运动→成功后提交count与终结记录。每次逆转前先持久化`reverse_used=true`；掉电后不能重新获得一次逆转名额。双槽/追加记录及最后写入有效标记应防止撕裂写入；仅在一个RAM变量上减1不能防掉电重复扣片。

重启若最后有效记录为未完成intent，**即使S3=home且S4/S5清空，也不能推定未出片或完整出片**：片可能已离开，事件历史已丢失。进入CYCLE_UNCERTAIN，保留原数并明确显示“计数未确认”，禁止READY和自动补送。必须由用户/服务流程根据可核查事件处理；无法核查就接受计数未知或在安全暗条件下按更换流程处理，不能靠猜测返回READY。相机曝光本身也不由运输传感器自动证明，首样EJECT依赖用户明确操作。

日志磨损是安全换来的代价：正常每片至少一条启动intent、一条完成记录，黑盖也如此；不要对每个ADC采样/毫秒状态反复写Flash。ATtiny EEPROM与STM32 Flash的厂家耐久不同，需按`预期循环×每循环记录数/均衡槽数`核算，Flash擦除按页次数算而非按写字节次数；保留空间、垃圾回收和重启校验的断电安全性须验证。启用BOR/BOD并预留逻辑供电余量，但不依赖“掉电中断总来得及保存”；关键intent在运动前已完成。外置FRAM可作为后续方案，当前未选型号。

## 7. 一次恢复的边界

默认不允许对进入显影滚筒的片材反转。一次有限回退仅可在：S0/S1有效、S2无效、S4/S5仍清空、日志证明尚未进入交接、reverse_used=false、无欠压/热故障，且机械台架证明A反转不会第二次拨片或卡损时执行。停止→等待电流/转速消退→持久保存reverse_used→A低限流有限回退→再次停止→显示JAM并锁存FAULT。回退可在安全home事件或已冻结的回退边界先达到时停止，不以强行归home为目标；核对S3及S4/S5并保存实际位置。B在A回退期间始终失能。没有自动前进重试，也不因回退成功自动恢复READY。

回退必须有独立时间/行程/电流边界；出现异常立即停止锁存。没有A位置观测或没有已验证的回退机械路径，恢复功能保持禁用。S4已占据、S5出现、S4/S5次序矛盾、双张嫌疑或复位后相位不明均进入FAULT/CYCLE_UNCERTAIN；驱动能反转不代表此时机械/片材允许反转。人工服务必须先检查并安全处理卡片、核对计数与机构位置，再明确解除锁存/重新arm；后续空载或dummy测试是新的人工测试操作，不能借服务模式反复强推故障片。

## 8. 第一阶段电子验收与费用口径

先无片台架验证：断电/复位两桥失能、门/片盒联锁、S2启动限制、双路ADC电流校准、启动与限流、各阶段传感器超时、传感器断开/粘连、驱动故障、日志写失败、intent/commit各位置断电注入。再用黑盖和废片验证单张拾取与交接，最后用真实片验证铺药、最高/最低电量、重叠负载、温升和十片计数。以上均为待执行试验，没有原型通过记录。

2026-10-07 Pololu产品页单件标价#2367/#1101各US$23.95，两台为US$47.90，未计运费税费；这只是已核对候选价格。[#2367价格](https://www.pololu.com/product/2367)，[#1101价格](https://www.pololu.com/product/1101) 首样电子可拆模块/测试连接预算暂估US$70–140；集成电子与两电机暂估US$45–85，均是设计预算、未取得报价。整机US$100–150是目标，是否达到仍取决于滚筒加工、壳体迭代、供应渠道和电机最终选择；原型多轮试错、工具及耗片另计，不将目标价冒充现成可购BOM。

PCB作者为用户；几何边界、孔位、USB与连接器坐标当前全部待测。逻辑电气口径见[PCB接口契约](../electronics/pcb/interface-contract.md)。
