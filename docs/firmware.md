# V2 固件行为合同

本阶段实现可在主机编译和测试的 C++17 双电机控制核心；它尚不是已接入 MCU/HAL、可刷写并驱动真实后背的产品固件。MCU/引脚/电机/时序阈值未冻结，未知校准必须拒绝启动。此文档定义产品行为合同，控制细节见 [electronics.md](electronics.md)，接口见 [interface-contract.md](../electronics/pcb/interface-contract.md)。实际源代码、构建和主机测试说明位于 firmware 目录，后续须实现硬件适配并验证。

## 必须保留的状态名称

| 用户要求状态 | 行为 / 可细分子状态 |
|---|---|
| POWER_OFF | 物理switch断电；硬件A/B默认disable，charge路径与运行路径设计区分 |
| BOOT | 读复位原因、先disable、读persistent journal；pending→SERVICE而非重送 |
| SELF_TEST | sensors初态、两路current零点/轨电压、NVM CRC、bridge faults；不动片自检 |
| DARK_SLIDE | S2插入禁止启动LOAD/EJECT；显示联锁，不伪造曝光状态 |
| READY | 已出黑盖、frames>0、S0/S1有效、S3home、S4/S5clear、无故障、电量足够 |
| EJECT_START | 新按钮边沿、所有联锁、先持久intent再enable，区分cover或normalcycle |
| PICKUP | A离home；有界单张推进；B可提前低速capture，独立电流限流 |
| ROLLER_CAPTURE | S4与夹持证据；A脱离并归home，B接管；entry alone不证明nip夹持 |
| EJECTING | B铺展；S4/S5完整active→clear顺序；不把低电流/时间当完成证据 |
| RETURN_HOME | A本cycle离home后必须返回；B尾端clear证据不足时有界继续；禁止下次pickup |
| COMPLETE | 完整出片+Ahome+无故障才atomiccommit；normal减1，cover成功设10 |
| EMPTY | frames0禁normalEJECT；保护式新盒LOAD确认，不因door open自动reset |
| JAM | STOP→至多一次经phase验证安全回退→STOP→锁存JAM；无自动forward重试 |
| LOW_BATTERY | 启动禁动作；动作中保护需记录不确定；电压恢复不自动重送 |
| SERVICE | 人工核对与保护式点动/传感器读数/电流读取/归home/明确pack reset；无伪完成 |

补充状态：NO_CARTRIDGE、DOOR_OPEN、NEW_PACK/LOAD_PENDING、LOAD_BLACK_COVER、CYCLE_UNCERTAIN。BOOT_SAFE/PRECHECK/JOURNAL_INTENT/HANDOFF/VERIFY/COMMIT 等电子研究子阶段是上述状态的细分，不替换必需语义。

## 调度与计数

循环采用event/tick非阻塞调度；每个motion phase独立absolute deadline和总deadline；home sensor需真实离位再归位。传感器消抖、current过滤和startup_blank也必须有边界，不能屏蔽真jam直至无穷。每路电流threshold和持续window由 traces确定，未量测时保持配置未完成并禁止产品运行。

NVM保存PACK_STATE / FRAMES_REMAINING / COVER_DONE / PACK_SESSION / CYCLE_ID / IN_PROGRESS / REVERSE_USED / CRC。正常动作写intent和commit，ADC和UI刷新不写Flash。真实packload确认、成功blackcover、normalcomplete、人工reset产生记录。掉电pending即使所有sensor当前清空也仍未知，不能以home推定counter正确。

EJECT不证明已快门曝光。用户负责RB67 cock与shutter；此版本不需X-sync、自动曝光检测或相机电气改装。

## 诊断和服务

USB serial日志字段及模板见 [transport-log.csv](../experiments/transport-log.csv)，至少含timestamp、state、I_A、I_B、S0–S5、batteryV、cycle_duration、frames、packstate、fault。ADC采样频率、日志频率可不同；控制不得因串口阻塞失去限时。LED/UI分别显示READY、NO PACK、DOOR OPEN、DARK SLIDE、LOAD确认、EJECTING、JAM、LOW BATTERY、SERVICE、计数不确定。

SERVICE入口保护式组合/长按后明确确认，不自动从JAM释放到READY。read-only diagnostics可在关门静止时进入；点动只在经过验证的安全fixture/状态执行，有deadman和限力限时；门开电机仍禁止。reset pack不能用来掩盖不明片堆。手动释放预载和光学遮光优先于强迫重送。
