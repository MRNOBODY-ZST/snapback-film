# R0 工程准备验证记录

日期 2026-10-07。对象为本仓库源码与独立台架名义 CAD；**物理实测 0、真实片循环 0，所有工程 Gate 仍未通过**。主机软件检查与 CAD 内核有效性不能证明真实驱动/传感器、单张分离、展液、焦面、漏光或旋转适配。

对应 [机器可读摘要与源码指纹](verification-R0-preparation.json)记录本轮测试数量、范围和源码 SHA-256。

| 检查 | 实际执行结果 | 范围 |
|---|---|---|
| Python 工程计算/日志/网格/导出登记 | 36/36 通过 | 含未知输入、单位、区间、外部传动比、能量独立测量、网格闭合和未登记导出拒绝 |
| C++17 Journal | 8/8 通过 | CRC 标准向量、断电截断、发布粒度、损坏与读写失败 |
| C++17 Controller | 29/29 通过 | 黑盖/计数、序列、各阶段超时、A/B 电流、联锁、一次回退、恢复短脉冲、pending reboot |
| C++17 host_sim + Python 分析 | 生成并解析 40 行 TEST_ONLY 合成事件 | 一次黑盖与一次普通片，末尾 READY/9；没有实物电流/电池能量 |
| 两台架 pytest | 24/24 通过，默认系统临时目录 | 来源/空值守卫、故意交叉拒绝、调节端点、实体与 STEP 回读；9.15 s 是本机一次耗时 |
| 原始资产归档 | 19/19 SHA-256 匹配 | STL 有限顶点/包络、STEP 封套、F3D ZIP CRC；未执行 Fusion 原生求解 |
| 相盒参考预览 | 闭合 1576 面、有效单实体 | 分面 STEP/STL，源单位尺度仍假设、曝光层未知 |
| 台架 PCB 坐标库存 | 90×70、4 孔、20 端口、48 逻辑针检查通过 | 数值/孔针在板范围、编号、35 项未知 null；不是 EDA/DRC/装机验证 |

两台架真实主导出清单有 42 个 STEP/STL：进片平台 17 个名义实体（18 文件），滚轮平台 23 个名义实体（24 文件，其中含 4 个商品轴承包络）。STEP 回读最大包络差约 0.000855 mm，**这是 CAD 文件数值一致性，不是零件加工精度或滚轮平行度**。源文件限制普通 FDM 承力/精密轴承面与化学接触使用；刚性量规不是显影滚轮，空白指尖坯不是合格拾片爪。

## 重现命令

在项目根目录运行；Python 标准库工具不需第三方包。C++ 需 g++/clang++ 的 C++17 工具链；本次实际 g++ 15.2.0，以 -Wall -Wextra -Werror -pedantic 编译。CAD 检查需台架 README 定义的依赖；本次 CadQuery 2.8.0 / OCCT 7.9.3.1.1 / pytest 9.1.1。

```powershell
python -X utf8 -B -m unittest discover -s tools/tests -p 'test_*.py'
& .\firmware\build-host.ps1
python -X utf8 -B tools/analyze_cycle_log.py firmware/build/synthetic-transport.csv
python -X utf8 -B -m pytest -p no:cacheprovider cad/feed_test_rig/R0_bench/test_feed_bench.py cad/roller_test_rig/R0_bench/test_roller_bench.py -q
python -X utf8 -B tools/inspect_reference_cad.py
python -X utf8 -B tools/audit_feasibility.py
python -X utf8 -B tools/run_engineering.py
python -X utf8 -B tools/analyze_cycle_log.py experiments/transport/diagnostic-log.csv
```

默认工程配置实跑仍输出 UNKNOWN / UNCERTAIN — MEASUREMENT REQUIRED；实际实验日志实跑 NO_DATA。没有将合成测试作为真实成功率/电流/时限/滚轮参数。所有工具在严格未知输入下保持最终后背制造未解锁。

## 审查与修复记录

独立事件探针发现四处控制边界：最终 ARM 检查可能仅看消抖态；恢复停止阶段可能超出总时限才回退；恰好到期的出口完成可能先提交；恢复等待内短夹持/入口/出口/home 脉冲可能丢失。均补充回归并修正；独立重新编译探针未能复现原四项问题，现有 29 项控制测试包含对应案例。

主审默认 pytest 临时目录另外发现两套导出在项目外使用错误相对路径，修正为项目内根相对 POSIX、项目外明确 ABSOLUTE_PATHS 后，同样命令 24/24 通过。CAD 检查此前发现观察台与导轨相交，调整布局并加入名义碰撞/端点验证。以上为软件与名义几何修复，不能据此宣布真实机构可靠。

最终文件/链接/导出 hash 审计以 [preparation-export-register.json](../cad/preparation-export-register.json)登记来源预览与独立台架；实测 VERIFIED_MEASUREMENT 仍为 0，未知物理参数仍为 105/114，实验 CSV 仍为 0 行。
