# 工程工具

以下命令在项目根目录运行。计算、日志与归档审查只用 Python 3.10+ 标准库；CAD 生成另外需要对应目录说明中的 CadQuery 环境。Windows 建议加 `-X utf8 -B`。

## 数值计算

```powershell
python -X utf8 -B tools/run_engineering.py
python -X utf8 -B tools/run_engineering.py path/to/measured-inputs.json
```

[calculation-inputs.json](calculation-inputs.json)定义单位、来源、量测不确定度和输入键，物理未知保持 null。复制配置填入实测后可以计算：局部轴向焦面干涉区间、滚轮/电机扭矩与转速、简谐拾片升程的峰值速度/扭矩、左右弹簧合力、不变位直齿轮名义尺寸，以及一凸轮周期的剩余滚轮输送长度。

所有输出仅是输入推导。局部轴向间隙不能替代完整三维碰撞检查；扭矩各项须避免重复计算同一实测总负载；弹簧合力不是药包压力；同步距离足够不证明机构能可靠交接。工具不解锁最终制造，也不自动将相盒参考网格包络写入物理参数。默认配置实际输出 UNKNOWN，不能生成 PASS。

## 电流与周期日志

```powershell
python -X utf8 -B tools/analyze_cycle_log.py experiments/transport/diagnostic-log.csv
```

该文件当前仅表头。以后录入同步时间、电流、状态与传感器后，工具报告每周期时长、A/B 峰值及样本 P99；拒绝时间倒序、非法数值和不连续 cycle_id。采样 P99 不能直接作为 JAM_THRESHOLD。

只有独立测得 battery_current_a 与 battery_voltage_v 且本周期所有采样齐全，才积分净能量/电荷；不能把两路 PWM 电机电流相加当电池电流。采样率、滤波、测量误差与缺失事件仍须在试验记录说明。

[synthetic.TEST_ONLY.csv](tests/fixtures/synthetic.TEST_ONLY.csv)是软件测试输入，放在工具 tests 中，不能当作实物试验结果或用于选电机/卡片阈值。

## 文件与导出审查

```powershell
python -X utf8 -B tools/inspect_reference_cad.py
python -X utf8 -B tools/audit_feasibility.py
python -X utf8 -B -m unittest discover -s tools/tests -p 'test_*.py'
```

inspect_reference_cad.py 只读校验第三方 manifest/hash、STL 顶点/包络、STEP 封套/单位声明和 F3D ZIP CRC，不检查原生参数求解或实际装配。

audit_feasibility.py 检查七份核心文档、UNKNOWN/null/来源、链接、SVG 语法、固件状态合同、评分与预算算术、试验行数，以及 [导出登记](../cad/preparation-export-register.json)。只有 hash 匹配的原始参考、限定目录中的参考预览和独立 R0 台架得到接受；未登记的最终后背 CAD/Gerber 报错。本地 .tools-venv、编译 build 与缓存不算交付源文件。

检查通过不证明机械、光学、化学或电子实物可工作。物理样本、零件误差和全部工程门槛仍须实测。
