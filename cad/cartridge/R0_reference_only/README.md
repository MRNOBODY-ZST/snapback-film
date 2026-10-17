# Square 片盒：参数化参考预览

来源是 [Jocelyn Girard 的 STL](https://www.thingiverse.com/thing:3790489)，原件和作者 LGPL 标识见 [参考归档](../../reference/square_cartridge_lgpl/ATTRIBUTION.md)。这里的派生几何保留 LGPL-2.1 标识，不由项目 MIT 重新授权。

变更日期 **2026-10-07**：SnapBack 项目将原 STL 三角网格转换为分面 BREP/STEP，并重新导出带 SOURCE_REFERENCE 标识的 STL；默认保持源坐标，未重新建立连续曲面或实物校准。原始作者文件保持不变。许可全文见 [LGPL 2.1](../../../LICENSES/LGPL-2.1-only.txt)及其引用的 [GPL 2.0](../../../LICENSES/GPL-2.0-only.txt)，原作者和许可标识随预览一并保留。

源文件：[instax_square_cartridge.py](../../source/instax_square_cartridge.py)；预览设置：[reference-config.json](../../source/instax_square_cartridge.reference-config.json)。可调源轴缩放和平移，默认保持原坐标；这些是参考变换，不是实体片盒公差或相机基准。

使用项目 CAD 环境运行：

```powershell
.\.tools-venv\Scripts\python.exe -X utf8 -B cad/source/instax_square_cartridge.py --preview
```

输出带 SOURCE_REFERENCE 标识的 faceted STEP/STL 和 manifest。先检查原网格闭合/方向，再用 CAD 内核构造名义实体。STEP 是三角面 BREP，保留网格离散误差，并没有恢复原设计的圆角/连续曲面。

STL 无单位，CAD 内核按 mm 解释是待实物确认的假设。**实际片盒外形、出口、拾片窗、受压片面和有效乳剂面仍须 M04–M13/M19。** 不能从此参考几何导出最终片仓、film-plane shim 或拾片深度。两个坐标变换到项目 R/P 尚未建立，禁止默认源原点为光轴。
