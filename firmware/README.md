# R0 主机固件核心

这是可编译运行的 C++17 逻辑核心与合成事件测试，**不是最终 MCU 固件、硬件台架验证或真实胶片/成片验证**。不包含 MCU HAL、GPIO 实际管脚、PWM 定时器、ADC 驱动、光学传感器选型或产品时序标定。核心沿用 [行为合同](../docs/firmware.md)；补充状态/阶段不替代其必需语义。

在 Windows PowerShell 从 `snapback-film` 项目根执行 `& .\firmware\build-host.ps1`；也可传 `-Compiler '完整 g++/clang++ 路径'`。脚本用 C++17、严格警告和 `-Werror` 编译，再执行 journal、controller 和 simulation，任一失败即退出。当前实际验证使用已安装 g++ 15.2.0。CMake 文件供后续常规工具链使用；本次没有声称已运行未安装的 CMake/MSVC/MCU 目标。

`src/controller.*` 的 `tick(now_ms, Inputs)` 不 sleep、不忙等；每次返回两路桥 duty/ARM、充电暂停请求及硬件锁存请求。时间单位毫秒，电流单位 A，电池电压 V，duty 为有符号 [-1,1]。调用周期上界是实测配置项；调度迟到、时间倒退、传感/模拟量健康失败、门开、盒移除、桥/轨故障都会 STOP。`Inputs.sensor_valid_mask` 由实际 HAL 的诊断产生；读到六个 bool 并不证明传感器完好。S3/S4/S5 使用有界消抖；S0/S1 原始失效立即停机。

`Config{}` 全为未知，默认 `Mode::Hardware` 拒绝 Unverified 与 TestOnly；每个必需值须有限且满足范围/关系。`Calibration::Measured` 是外部完成审查后的标记，不能把测试值改个标签当标定。只有 `tests/synthetic_fixture.hpp` 中的 **TEST_ONLY 任意值**配合显式 `Mode::HostSimulation` 用于事件测试。真实极性、健康诊断、软/硬电流阈值、startup blank、所有阶段时限、供电边界、占空比、回退路径与位置观测均须实测。没有有效独立回退位置观测或验证路径就不回退。

黑盖与普通片共享输送证明但有独立 CycleKind。显式 `confirmNewPack(true)` 只在无 pending 且静止健康的状态建立新 pack session，保存 cover=false/count=0；黑盖完整 S4 active→clear、S5 active→clear、S3 本循环离位→归位后才提交 count=10。普通片满足同样证明才减 1。S4 必须先于 S5；二者占据时间允许重叠。`capture_confirmed` 为与 S4 分开的、经标定的滚筒夹持证据：启动时须 false，入口前出现视为时序故障。当前核心在 A 拾片初期让 B 正向预转，S4 后停止 A 等夹持证明，随后 A 正向完成凸轮归位；这只是待机械台架验证的调度，不可据此直接驱动未知机构。

S2 插入同时禁止 EJECT 和 LOAD 启动。运动中插入 S2 不触发未经验证的急反转；本循环在其它保护/时限下完成后进入 DARK_SLIDE。EJECT 只代表用户请求输送，不能证明 RB67 已曝光。按钮仅采用新边沿；忙碌期间的边沿丢弃，长按不会排队。两个按钮同 tick 同时按下不启动。

软 JAM 需要对应启用电机超过电流窗口且缺乏阶段进展。流程为 STOP → 有界 coast → 若未曾 S4/S5/夹持且所有联锁/位置观测/路径验证允许，则**先持久保存 reverse_used**再最多一次低 duty A 回退，B 始终禁用 → STOP → 锁存 JAM。持续电流不降、硬电流/健康/门/电源故障、已进入滚筒，均禁止回退。不会自动向前重试。`enterService()` 只停机进入诊断，不清 pending、不重送、不认证计数；未实现人工点动或重新武装。服务运动必须由后续已确认空载/假片安全台架的独立 deadman 流程实施。

每次启动先持久 intent 再进入 EJECT_START；两桥停机时完成写入、CRC 和读回验证，之后请求暂停充电，等待 `charge_pause_ack` 和有界稳定时间再使能。暂停确认运动中失效立即停机。真实 HAL 必须证明暂停充电的硬件效果，不能把 ack 常量接真；若充电器仍为系统供电，SYS/motor rail 的范围及电流上限另需设计验证。

日志采用两个**独立擦除单元**，每记录 40 byte：0 magic、4 version、5 kind、6 flags、7 count、8 sequence、12 pack_session、16 cycle_id、20 保留、24 CRC32(0..23)、28 保留、32..39 独立最终标记与反码。小端序；CRC 为 IEEE CRC32。32 byte payload 验证后才编程最后独立的 8 byte publication unit，适配器仍须核实所选 MCU 实际最小编程粒度/页面/ECC，不能假定本抽象已经是 STM32 Flash HAL。每次只擦除另一个单元；只要任一非空记录失效即保守 Corrupt，不静默以旧 READY 继续。启动遇 pending 即 CYCLE_UNCERTAIN；即使当前 home/入口/出口全清也不能重送。序列满时拒写，未实现 rollover。

Storage 调用同步且两桥已 STOP，**实际 HAL 必须有有限延迟、错误返回与看门狗约束**；Flash 从 SRAM 执行/ISR 阻塞/断电写特性是 MCU 集成待办。本版只证明抽象协议在模拟字节截断和 8 byte 写粒度下的行为。正常每循环 intent+commit 至少 2 次擦写，黑盖也如此，安全回退另写一次；ADC/UI/串口不写 Flash。双页面交替只分摊磨损，不是完整 wear leveling，须按所选 NVM datasheet 寿命计算，后续可换循环日志或 FRAM。

`host_sim` 生成 `build/synthetic-transport.csv`：黑盖一轮加普通片一轮，末尾 READY/9。字段含父项目日志工具所需 `timestamp_s,state,motor_a_current_a,motor_b_current_a,home,entry,exit,dark_slide,door_closed,cartridge_present,battery_voltage_v,frames_remaining,cycle_id,transport_phase`，另含计数可信、pending、fault、duty 和 TEST_ONLY 标签。电流/电压均为合成输入。未生成 `battery_current_a`，也未将两路 PWM 电流相加冒充电池电流；真实能量需独立测量电池电流后积分。串口 HAL 必须非阻塞、不能让日志使控制调度失期。

测试先用安全 stub 跑红，再实现；覆盖 atomic intent/commit、40 个字节切断点、CRC、8 byte 粒度、未知配置、六传感时序/健康、黑盖与 10 张计数、启动联锁、busy 长按、独立 A/B JAM、回退持久性、回退位置/时长、全阶段超时、门开、充电 ACK、ADC、调度、NVM 读写故障及 pending reboot。真实 HAL/台架/真实片的验收仍是后续工作。
