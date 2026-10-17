# CAD阶段与目录

当前R0，有参数/测量状态、符号图和第三方参考归档。尚无本项目可制造片盒、后背或显影机模型。不得从未闭合物理参数生成制造STEP/STL；参考原件不受此称号。

- `parameters.json`：中央114参数台账；UNKNOWN必须null。
- `source/instax_square_cartridge.measurement.json`：片盒量测所需参数清单，不是实体。
- `cartridge/`：P0通过后放商售完整片盒的参数实体与基准图。
- `feed_test_rig/`：独立透明/开放假片平台；真片另加遮光罩。
- `roller_test_rig/`：独立可换辊/两端调压/速度/轴线调整实验平台。
- `prototype/`：R1–R7分版本；`final/`只有全部gate通过才填。
- `step/`、`stl/`：必须有source、revision和制造公差对应，当前无导出。
- `accessories/`：打印比例/方向靶；实际取景mask仍待捕捉域与屏测量。

轴承载体使用精密轴/衬套/加工孔；FDM孔只作粗定位壳。滚轮最终contact surface禁止普通FDM，最终高载gear禁止普通PLA。

## 第三方参考实体

[reference/README.md](reference/README.md)索引 11 个保持原字节的来源资产及原许可；[几何报告](reference/geometry-report.md)仅是名义包络。实际物理参数仍在 parameters.json 中保持 UNKNOWN/null。相盒原件与部分可编辑源的未下载状态明确记录，不用缩略图构造实体。
