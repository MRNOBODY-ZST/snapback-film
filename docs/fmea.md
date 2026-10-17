# R0 故障模式分析

这是设计阶段判断，不是故障率数据。S=severity（1轻微，5可能持续运动/电池危险或器材损坏），D=detectability（1较容易检测，5难察觉），两者为 ESTIMATED。Occurrence / probability 全部 UNKNOWN；不计算伪精确 RPN，不把评分当试验成功率。

| Failure mode | S | Probability | D | 预防/检测/恢复与需要的证据 |
|---|---:|---|---:|---|
| Double feed | 4 | UNKNOWN | 4 | 深度窗口/片盒压片/边缘分离；假片高速观察、首末片100循环；单个entry传感器不能证明只有一张 |
| Missed feed | 3 | UNKNOWN | 2 | home离位后entry有界等待，F(x)与末片压片验证；失败不扣片，不自动重送 |
| Film scratched | 3 | UNKNOWN | 4 | 禁止图像区接触、guide毛刺检查、可换finger；完整真片显影后检查 |
| Pod not ruptured | 3 | UNKNOWN | 4 | preload/硬度/速度真实片DOE，检测仅可事后图像；不能用exit证明化学正常 |
| Uneven spread | 3 | UNKNOWN | 4 | 刚性carrier、工作载荷平行度、runout/材质/温度实验；量化full coverage和streak |
| Roller slip | 3 | UNKNOWN | 3 | 实际片速与辊速比，entry/exit progress timeout；PWM或电机encoder不等于片位移 |
| Roller contamination | 3 | UNKNOWN | 3 | 可拆辊盒、清洁维护、污染前后真实片验证；不用未经验证的清洗液 |
| Gear tooth failure | 4 | UNKNOWN | 3 | 材料与齿数/模数/载荷SF，PA/POM或commodity gears，轴距可调；电机转而片不动超时 |
| Motor stall / overheating | 5 | UNKNOWN | 2 | 每路电流限流、最长使能、温升验证；测真实最差堵塞，不以stall torque作连续额定 |
| Low battery mid ejection | 4 | UNKNOWN | 3 | 完整周期能量/压降预检；两轨电压、protected cell、intent日志；不依赖最后瞬间保存 |
| Film stuck halfway | 4 | UNKNOWN | 2 | entry/exit时序和timeout；STOP，夹药包后不自动reverse，service预载释放 |
| Dark slide inserted midcycle | 4 | UNKNOWN | 3 | 正保持/操作区别/S2联锁；假片分析停机风险，启动禁EJECT/LOAD；不未经验证反转 |
| Rear door opened | 4 | UNKNOWN | 2 | 正锁止、与RB拆背锁区别、S1硬件disable；运动必须停安全态；不能软件恢复已fog片 |
| Light leak | 4 | UNKNOWN | 5 | mount/slide/exit/door/service完整光路；photosensitive controls+真实Instax+midpack验证 |
| Incorrect film plane | 4 | UNKNOWN | 5 | 原datum+片盒压片全片堆公差链，ground glass与近/中/远实拍；不后移焦面 |
| Cartridge misalignment | 4 | UNKNOWN | 3 | 三点定位、正锁止、pressure独立，不壳居中；centering/入口方向fixture测量 |
| Sensor stuck / disconnected | 4 | UNKNOWN | 3 | safe polarity、初态自检、离位再home、active→clear时序、timeout；不能仅静态高电平通过 |
| MCU crash / boot pin glitch | 5 | UNKNOWN | 2 | driver硬件默认失能、门控、watchdog、BOR、最长enable；下载/复位故障注入 |
| NVM torn write / wrong counter | 3 | UNKNOWN | 4 | before-motion intent、sequence/CRC/atomiccommit/wear leveling，pending进入SERVICE不READY |
| Optical sensor fogging | 4 | UNKNOWN | 5 | 外缘遮光与发光器默认off；IR也须真实片雾化测试，必要改无发光sensor |
| Roller spring imbalance | 3 | UNKNOWN | 4 | 各端标定力、动态载荷axis变差、调节防松；不能仅合计preload合格 |

最高严重度项目优先硬件失能与供电审查；光学/漏光虽不一定导致器材损坏，但影响整盒结果，必须独立gate。下一版 FMEA 用实测 failure_counts/attempts和置信区间填 occurrence，保留原始版本。
