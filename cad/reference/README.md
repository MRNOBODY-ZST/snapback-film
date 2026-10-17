# 第三方 CAD 参考归档

R0，2026-10-07。这里是有出处的原始参考文件，**不是本项目制造导出或通过实测的模型**。项目 LICENSE 不重新授权本目录的第三方文件。

- [source-manifest.json](source-manifest.json)：作者、原页、资产 URL、固定版本/资产标识、原许可、SHA-256、使用范围。
- [geometry-report.json](geometry-report.json) / [geometry-report.md](geometry-report.md)：文件完整性和网格名义包络；不是相机或片盒实测。
- [g_adapter_v2](g_adapter_v2/ATTRIBUTION.md)：rodgsilva / rodsgear 的 CC BY 4.0 接收座、Press 基座和两锁条。只借 G 接口接收侧名义结构；Press M 口不用于 RB 机身。
- [g_adapter_v4](g_adapter_v4/ATTRIBUTION.md)：SPRKPLG 的 CC BY 4.0 Fusion V4 源文件；未执行 Fusion 原生参数求解。
- [square_cartridge_lgpl](square_cartridge_lgpl/ATTRIBUTION.md)：Jocelyn Girard 的 Square 相盒 STL、原 README 和 LGPL 许可说明；供测量校核。
- [square_pressure_cc0](square_pressure_cc0/ATTRIBUTION.md)：SPRKPLG 的 CC0 压片条/罩参考；不使用 Lomograflok 实物总成。
- [super67](super67/ATTRIBUTION.md)：Damien A.W. Humby 的 CC BY-NC-SA 4.0 完整 STEP 与 G 接收座/锁条，用于比较，不复制其 NC 修改进入最终开放结构。

文件保持原字节，模型原点/轴未改动。参考文件里的 Z=0 不代表本项目光轴、接环定位面或 Instax 有效曝光面。STL 不编码单位；预期打印单位为 mm 仍须核对。包络不是配合尺寸。

本轮已归档 19 个原始资产，pending_assets 为空；包括相盒 STL 和原页提供的 G02/G03/C02 可编辑源文件。详见 [检索报告](../../docs/open-cad-sources.md)。相盒的衍生分面 STEP 位于 [参考预览](../cartridge/R0_reference_only/README.md)，与本目录原始资产分开。

在项目根目录运行 `python -B tools/inspect_reference_cad.py` 只读核验。原件检查包含 STL 三角面和有限坐标、STEP 文件封套/单位声明、F3D ZIP CRC、文件 hash；没有用 CAD 内核导入这些原生 STEP/F3D，不能据此宣称实体装配通过。单独生成的相盒预览通过了 CadQuery/OCCT 内核有效性检查，仍未经实物校准。
