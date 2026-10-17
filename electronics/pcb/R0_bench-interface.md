# R0 独立台架载板交接

PCB 作者是用户。本文、[JSON](R0_bench-interface.json) 和 [SVG](R0_bench-interface.svg) 提供可画板的功能/逻辑针序/自定台架坐标；**尚无 PCB CAD、Gerber、板级 ERC/DRC、实物验证或 RB67 装机适配声明**。自定尺寸为 OWN_DESIGN，器件/插头外形预留为 ESTIMATED；原 [整机接口契约](interface-contract.md) 的全部安装尺寸仍为 null / MEASUREMENT_REQUIRED。此载板通过电缆连接外部 MCU daughterboard，J_CTRL 是逻辑端口，不冒充 MCU 封装焊盘或已冻结 pinmux。

JSON 使用用户指定六类来源 **VERIFIED_MEASUREMENT / MANUFACTURER_SPEC / RELIABLE_SOURCE / DERIVED / ESTIMATED / UNKNOWN**。`provenance_defaults` 明确覆盖范围：自定 board/holes/connector centers/pitch/envelope 为 **ESTIMATED，source=OWN_DESIGN**；各针 XY 为 **DERIVED，source=所列中心/间距公式**；固定 R0 逻辑针序为自定接口选择 **ESTIMATED**；未定安装变换、料号、电流/标定/阈值/时限为 **UNKNOWN，source=MEASUREMENT_REQUIRED 或 PART_SELECTION_REQUIRED**；候选器件的边界为 **MANUFACTURER_SPEC，source=各自 datasheet URL**。OWN_DESIGN 说明设计者选择，不替代六类 provenance；本文件没有 VERIFIED_MEASUREMENT 整机坐标。TEST_ONLY 只是固件模拟范围标签，不是来源类别。JSON/SVG 为无 BOM UTF-8。

## 台架坐标与线束端口

板局部原点为元件面俯视的左下角；+X 向右、+Y 向上、+Z 朝元件面外。单位 mm。自定板外形 90×70；拟定板厚 1.6 为 ESTIMATED 制板选择。四个自定 Ø3.2 通孔位于 (4,4)、(86,4)、(86,66)、(4,66)，只是台架安装孔。板到整机的刚体变换、整机可用空间/高度/暗板/门/滚筒禁布区均未知。连接器中心 Z=0 为接口坐标参考，不代表实体高度；真实封装高度、插头/线束拔插包络、pad 尺寸及公差需正式供应商图纸。

单排接口 pin1 在最小 X，随后沿 +X 编号，拟定直针插合 +Z。J_CTRL 为 2×24、间距 2.54：奇数针 Y=57.73，偶数针 Y=60.27，每列沿 +X 前进 2.54；pin1=(15.79,57.73)，pin2=(15.79,60.27)，最后列 X=74.21。SVG 方形点为 pin1，仅画接口中心，不是厂商 footprint。下表针序是冻结的 **R0 逻辑合同**；每一正式插头料号/pad 编号仍须映射，不能靠线色或通用“JST”推定防错与承流。

| 接口 | 中心 XY mm | 拟定间距 mm | 顺序 pin1→末针 |
|---|---:|---:|---|
| J_MA | 12,30 | 5.08 | A_OUT1, A_OUT2；两端都是桥开关节点 |
| J_MB | 12,42 | 5.08 | B_OUT1, B_OUT2；两端都不是固定 GND |
| J_VM | 12,18 | 5.08 | VM_EXT, POWER_GND；外部限流台架电机供电 |
| J_BAT | 27,10 | 5.08 | PROTECTED_P_PLUS, PROTECTED_P_MINUS, CELL_NTC |
| J_LOGIC | 27,18 | 5.08 | LOGIC_3V3_IN, GND；外部稳压 3V3，仅台架供电 |
| J_SYS_MON | 27,26 | 5.08 | CHARGER_SYS, GND；power-path 测量输出 |
| J_UI | 54,12 | 2.54 | GND, BTN_EJECT_N, BTN_LOAD_N, LED_READY_DRV, LED_FAULT_DRV |
| J_UART | 54,22 | 2.54 | GND, LOGIC_3V3_REF, MCU_TX, MCU_RX |
| J_SWD | 54,32 | 2.54 | GND, LOGIC_3V3_REF, SWDIO, SWCLK, NRST |
| J_ARM | 54,42 | 2.54 | GND, HW_ARM_AUTH, KILL_SENSE, MANUAL_KILL_CLEAR_N |
| J_PROOF | 32,47 | 2.54 | GND, CAPTURE_PROOF, REVERSE_POSITION_VALID, REVERSE_LIMIT_REACHED |
| J_DISPLAY | 32,39 | 2.54 | GND, LOGIC_3V3_REF, I2C_SCL, I2C_SDA |
| J_S0…S5 | X=78；Y=15,22,29,36,43,50 | 2.54 | 每口 GND, 对应 Sx_N, SENSOR_3V3 |
| J_CTRL | 45,59 | 2.54 | 2×24 详见下一表和 JSON 每针 XY |
| J_USB | 45,3 | 正式 footprint 待选 | 插入方向 -Y；预留 11×8 ESTIMATED，非厂商尺寸 |

功率插头必须独立防错：J_VM/J_MA/J_MB/J_BAT 不得任意互插；此处相同间距不代表相同连接器系列或键位。所有端子/导线的额定电流、线径和实际热升目前 PART_SELECTION_REQUIRED。J_LOGIC 使用自定输入条件 **3.3V ±5%**，不是从电芯/USB/SYS直接取电。MCU daughterboard 与载板应由同一受控 3V3 源分别供电，J_CTRL pin2/J_UART pin2/J_SWD pin2 只作电平参考，不能以 USB 适配器反向供电。未供电的一侧需避免 GPIO 箝位反灌，ARM 门控必须仍保持禁用。

## J_CTRL 逻辑针序

方向以外部主控为中心；输出为 MCU→载板，输入为载板→MCU。未列模拟/电源的信号统一 3V3。全部 MCU 封装 pad 值保持 null；主控板作者须完成可用 GPIO、ADC、PWM、SWD、USART/I2C 的复用及启动状态审核。完整接口不能无审核套入 GPIO 不足的小封装。

| 针 | 信号 | 类型/默认 |
|---:|---|---|
| 1 | GND | 参考 |
| 2 | LOGIC_3V3_REF | 参考，不作反向供电 |
| 3 / 4 | A_IN1 / A_IN2 | 输出；硬件下拉，正/反/STOP 映射由 HAL 实物校核 |
| 5 / 6 | B_IN1 / B_IN2 | 输出；同上，独立桥 |
| 7 / 8 | A_ARM / B_ARM | 输出；默认低，外部门控，分别使能 |
| 9 | PACK_PRESENT_N（S0） | 输入低=盒在位；断线高=盒不在 |
| 10 | DOOR_CLOSED_N（S1） | 输入低=门闭；同时进入硬件门控，断线禁用 |
| 11 | DARK_SLIDE_INSERTED_N（S2） | 输入低=暗板插入；禁止 LOAD/EJECT 启动 |
| 12 | PICKUP_HOME_N（S3） | 输入低=home；本循环离位后返回才有效 |
| 13 | ROLLER_ENTRY_N（S4） | 输入低=入口占据；不是独立夹持证明 |
| 14 | FILM_EXIT_N（S5） | 输入低=出口占据；须 active→clear |
| 15 / 16 | ADC_I_A / ADC_I_B | 独立 ADC 电流测量，各有增益/偏置/带宽标定 |
| 17 / 18 | ADC_VBAT / ADC_VM | 分压/滤波 ADC；禁止原始电池/VM直入 |
| 19 / 20 | A_FAULT_N / B_FAULT_N | 开漏输入、3V3 上拉；独立硬件故障锁存 |
| 21 / 22 | A_STALL_N / B_STALL_N | 开漏输入；芯片 stall 仅辅助，不替代两 ADC/时序 |
| 23 / 24 | BTN_EJECT_N / BTN_LOAD_N | 输入低=按钮；去抖后形成新边沿，忙时不排队 |
| 25 / 26 | LED_READY_DRV / LED_FAULT_DRV | 输出到限流/驱动，不直接承担未知 LED 电流 |
| 27 | CHARGE_PAUSE | 输出高=暂停充电请求；默认高较保守，由硬件实现 |
| 28 | CHARGE_PAUSE_ACK | 输入高=已验证暂停路径到位；默认低，禁止常量接真 |
| 29 / 30 | CHG_STAT1_N / CHG_STAT2_N | 3V3 上拉开漏状态；按充电器状态表解码 |
| 31 | VBUS_PRESENT | 经正确分压/电平转换的 3V3 输入，非 5V VBUS |
| 32 | SENSOR_PWR_EN | 输出，默认低；诊断后可给有源传感器供电 |
| 33 | EMITTER_EN | 输出，默认低；台架初版发射器默认不安装 |
| 34 | KILL_REQUEST | 输出高请求硬件故障锁存；不能自动清锁存 |
| 35 | KILL_SENSE | 输入高=已经锁存禁用；健康电平/断线诊断须实现 |
| 36 | HW_ARM_AUTH | 输入高=物理钥匙/开关授权；硬件下拉、开路禁用 |
| 37 / 38 | MCU_TX / MCU_RX | 3V3 UART；TX接适配器RX，RX接适配器TX |
| 39 / 40 | I2C_SCL / I2C_SDA | 双向/开漏 3V3；可用于显示/额外诊断，但不作唯一门联锁 |
| 41 / 42 | SWDIO / SWCLK | STM32 候选调试；由探针及 MCU 定义方向，非固定 GPIO 输出 |
| 43 | NRST | 调试复位；复位必须令 ARM 低 |
| 44 | HW_WDI | 输出至独立硬件看门狗；超时限值待标定，失联禁用 |
| 45 | CAPTURE_PROOF | 输入高=独立滚筒夹持证明，默认低；启动时需低 |
| 46 | REVERSE_POSITION_VALID | 输入高=独立可信 A 回退位置观测；默认低 |
| 47 | REVERSE_LIMIT_REACHED | 输入高=已达回退边界；边界/观测方法待机械标定 |
| 48 | GND | 参考 |

J_PROOF 是工程台架位置/夹持测量接口，不替代 S0–S5、不声称现有六个传感器已提供这些证明。S4→nip 的输送距离、捕获条件和回退边界未验证时，45/46 信号不能由软件时间常量伪造。R0 核心需要独立有效 proof；不能缺少 proof 就提高时间强推。

## 双桥、硬件门控与 ADC

候选每路一颗 **DRV8213RTE**：RTE 接口有 IPROPI、VREF、nFAULT/nSTALL，包体 3×3 mm；4A 是峰值，不是未验证 PCB 上的连续电流。VM/VCC 边界与 RTE 引脚应读正式数据表，芯片没有可虚构的独立 nSLEEP 接口，外部门控须将对应 IN1/IN2 同时强制 0。[TI 数据表](https://www.ti.com/lit/ds/symlink/drv8213.pdf)、[TI 当前产品信息](https://www.ti.com/product/DRV8213)

每路硬件允许条件为 `ARM && HW_ARM_AUTH && raw_DOOR_OK && RAIL_OK && watchdog_OK && !KILL_LATCHED`。门、桥危险故障、轨欠压/看门狗走独立失能链，默认阻断；桥内部 auto-retry 不允许自行恢复推片。raw_DOOR_OK 由 S1 闭合信号经正确逻辑得到，开路立即禁止两桥。S2 是启动联锁，不加入未经机械验证的突然急停/反转硬件路径。

软 JAM 先两桥 STOP，不立即借硬件 latch 阻止唯一经验证安全回退；经过持久 reverse_used、位置/夹持证明和上限检查后，最多一次 A 低 duty 反向，B 保持禁用，然后 STOP 与 JAM/FAULT 硬件锁存。恢复 coast 期间出现过任何夹持/入口/出口/home 不允许证据，立即锁存，短脉冲也不能被忽略后重新回退；总运动 deadline 覆盖 coast 与 reverse。硬危险故障不执行回退。J_ARM pin4 只接**物理人工**清除按钮，须 ARM_AUTH=0、A_ARM=B_ARM=0、门闭且轨健康并经人工检查处理片材；固件不连自动清除输出。清锁存不能清 NVM pending，不能自动重新向前试送。

ADC_I_A/ADC_I_B 各自取得真实电机电流信息；IPROPI 增益、RIPROPI、VREF、采样滤波/续流状态/模拟限流都待负载测量与 datasheet 电路计算，不填任意实机阈值。ADC 电压接口目标 0…3V3，仍需与 MCU VREF/输入范围及保护核对。VBAT 分压自定候选为上 150kΩ、下 100kΩ，理想系数 0.4：`Vbat=Vadc×2.5`；这只是 OWN_DESIGN 被动网络，无实际误差校准。高源阻抗需验证 ADC acquisition 或缓冲/电容，不能直接把公式当精确读数。ADC_VM 分压值待 motor VM 冻结前保持 null，必须禁接未经分压的 VM。独立电池电流未在载板接口中伪造；若测能量用外部电池电流仪，不能把两路 PWM 电流相加。

输入低有效只定义线束语义。尤其 S2/S4/S5 断线会呈暗板退出/通道清空，三线口无法独自证明健康。用户须另做终端电阻窗口/双触点/可信有源诊断等，或通过额外 ADC/诊断接口冻结健康方法；HAL 对未诊断通道不得置 sensor_valid_mask。S4/S5 若用光学方案，须验证波长/光路/封装漏光与材料雾化；发射器须独立限流驱动，不能用 MCU 针直接供电或以“红外”推断安全。首版 EMITTER_EN=0、无默认暗腔照明。

## 1S 保护、USB 与开发

MCU HAL 应把每个低有效线转换成核心的逻辑 bool，例如 `pack_present=!PACK_PRESENT_N`，把两个独立 ADC 经校准转换为 A。HW_ARM_AUTH/KILL_SENSE/硬件 watchdog 的状态必须由真实板级适配层处理：未物理授权或锁存未解除时过滤启动请求，两桥仍靠独立硬件门控禁用；运动中这些条件失效要向核心提供停止故障（例如聚合入 bridge_fault），不能仅忽略按钮或保留旧健康值。复位/手动清锁存后的重新检查，不得越过 NVM pending。主机核心未包含这些真实 GPIO/硬件适配；用户画板与后续 HAL 实施必须补齐，模拟输入不是连线证明。

R0 台架把 VM_EXT、LOGIC_3V3_IN、charger SYS **分别测量**；J_SYS_MON 不默认短接 J_VM/J_LOGIC。真正以 1S 支撑逻辑/双电机、稳压或升压、最大同时电流尚未冻结。首样 USB-C 是 5V 受电充电口，开发日志走 J_UART 的外置 3V3 USB-UART，STM32 候选下载走 J_SWD；此载板未放置假定存在的原生 USB MCU 外设。STM32C031 数据表供电 2.0…3.6V 且列 ADC/PWM/UART/SWD 等功能，实际 MCU pinmux 仍待用户选择。[ST 数据表](https://www.st.com/resource/en/datasheet/stm32c031c6.pdf)

USB CC1/CC2 分别用独立 5.1kΩ Rd，不合并；D+/D− 在此仅充电载板 NC。输入总预算须遵守 CC/连接类型/枚举条件，不能因为有 USB-C 或 Rd 就默认可取 1A/3A。[Espressif USB-C 设计指南](https://docs.espressif.com/projects/esp-iot-solution/en/latest/usb/usb_overview/usb_typec_hardware_guide.html) 用外部 UART 适配器时仍需电平参考/GND及反灌保护，插 USB 不启动输送。

充电候选 **BQ25185** 为 1S power-path，最高 1A 充电，USB 条件 SYS 典型 4.5V，BAT→SYS 推荐上限 3.125A；/CE 高暂停充电，STAT1/2 开漏。上述是器件条件，不是最终电机或电池允许值，SYS 不能直接当 3V3/最大4V电机电源。[TI 当前数据表 Rev.B](https://www.ti.com/lit/ds/symlink/bq25185.pdf) R0 CHARGE_PAUSE 高应映射至 /CE 高；ACK 至少验证门控控制节点与实机暂停效果，节点回读本身也不能证明充电电流为零，实际效果须台架测量。运动前暂停，运动中必须保持 ACK，完成并静止才允许恢复。NTC置于电芯，不用板温替代；充电电压/电流/ISET/ILIM/VSET 按电芯、USB总预算和温升共同确定。

J_BAT 接可追溯受保护 1S 电池包。若改裸电芯则另建 RAW 口，加入 **BQ29700+匹配背靠背 MOSFET** 或其它匹配保护；它是独立电压/电流保护，不能以充电器替代，具体阈值/延迟与 FET 温变电阻需核对最终电芯。[TI BQ297xx 数据表](https://www.ti.com/lit/ds/symlink/bq2970.pdf) 当前电芯容量、放电峰值、持续电流、保险/线束/端子/升压器、同时启动预算全部 UNKNOWN。电机软 jam、硬限流和充电器路径保护是不同边界。

## 交接与可重现检查

暂停充电控制的硬件默认值须保持 /CE 高；若其默认上拉取自可达 4.5V 的 SYS，必须经适当隔离/电平转换，禁止将该上拉直接连到 3V3 MCU GPIO。应验证 MCU 复位/未供电时充电默认暂停，且供电节点不会通过 /CE/状态/GPIO 反灌。核心 `Outputs.charge_pause` 在未配置启动、故障和 SERVICE 时保留 true；只有健康静止路径才允许请求恢复。

运行 `& .\electronics\pcb\generate-R0-bench-interface.ps1`（项目根）可重生成 JSON/SVG；这不是 EDA 输出。JSON 逐针记录 XY/方向/电气类型/状态，所有 motor VM/current/标定/阈值/时限与实际元件号保留 null，安装变换亦 null。用户画板前应选择所有正式料号、核对封装图和针序、完成原理图/PCB ERC/DRC、验证功率铜/回流/散热/插拔空间以及默认失能链，再进行限流空载与假片台架测试。

对应 [C++17 核心](../../firmware/README.md) 已有主机事件测试和 TEST_ONLY 合成 CSV，但缺 MCU HAL 与硬件标定时默认 fail closed。主机测试只能证明被输入的事件/电流/故障下逻辑行为；不证明采集真实、桥关断正确、机械安全、成片或本载板可直接制造。最终装机 PCB 仍由片面/片盒/运动包络解算后另行冻结。
