# R0 独立滚轮承载／调压实验台架

状态：`R0_FIXTURE_ONLY_PROTOTYPE`，`mode=TEST_FIXTURE_ONLY`。本目录允许制作独立台架原型，未验证实体可靠性，未授权制造最终相机后背。所有自定义尺寸均为 `source=OWN_DESIGN` 的 `ESTIMATED` 或 `DERIVED`；它们没有回填相机、原旋转座、相盒或实际乳剂面参数。

## 交付物与边界

- `roller_bench.py`：CadQuery 参数源；`config.json`：来源／未知值注册。
- `fixture_contract.py`、`bench_geometry.py`：两套台架共用的参数拒绝、干涉和导出检查。
- `manufacturing-spec.json`：独立台架候选加工公差、方法与量测方法。
- `exports/roller_bench_R0_fixture_only.step`：23 个独立实体的名义装配。
- `exports/*.stl`：分件网格，作为加工参考／无载空间样件；轴承标记 `REF_COTS`，仅为外形参照，购买原厂件。
- `exports/manifest.json`：导出路径、SHA-256、字节数、输入来源、派生式、实体检查和 STEP 回读结果。

没有导出经过药囊展开验证的 developer-contact roller。两根直径 30 mm 的金属圆柱是刚性对中量规，名称包含 `rigid_alignment_gauge_NOT_developer_roller`。实际工作辊直径、表面材料、硬度、载荷、速度、预压、工作 nip 仍须实验选择；相机和相盒接口均 `UNKNOWN/null`。默认两量规表面相距 10 mm 是停放位置，不能作为实际 nip。

## 坐标和可调范围

`B_R` 原点为台架底板下表面中心，X 沿轴，Y 沿假定输送方向，Z 向上；它与相机 R 坐标、旋转轴和片盒 P 坐标没有变换关系。

|台架名义量|数值／来源|含义|
|---|---|---|
|底板|180 × 120 × 10 mm，OWN_DESIGN/ESTIMATED|独立加工台架|
|两支承中心 X|±65 mm，OWN_DESIGN/ESTIMATED|非相机接口宽度|
|下量规轴中心 Z|25 mm，OWN_DESIGN/ESTIMATED|独立台架基准|
|裸滑架中心 Z 范围|54–92 mm，OWN_DESIGN/DERIVED|窗口高 66 减滑架高 28 得 38 mm 行程|
|当前 5 mm 限位块装入后的范围|59–92 mm，OWN_DESIGN/DERIVED|当前可用 33 mm，不是最终压缩量|
|可换限位块高度候选|0.5–12 mm，OWN_DESIGN/ESTIMATED|仅可换加工件；必须同时满足量规无碰撞|
|单侧名义滑架侧隙|0.2 mm，OWN_DESIGN/DERIVED|32.4 与 32 宽度的差的一半|
|弹簧座可用包络|直径 14、深 2 mm，OWN_DESIGN/ESTIMATED|没有选定弹簧；座宽超过载体 X 厚度，形成开口浅槽|
|桥上调整孔|直径 5 mm pilot，OWN_DESIGN/ESTIMATED|螺纹、调整杆、弹簧和调压力尚未建模／选定|

当前 5 mm 限位块让直径 30 的量规最小名义表面距离为 4 mm，适合无载支承／滑移检查。减小限位块后可能接近量规相切位置；代码拒绝量规实体相交。所有后续 sleeve、真实弹簧与压缩设置都要重新计算并实测，不能把量规间距作为化学展开许可。

## 制造与装配

底板、框架、滑动轴承座、限位块、桥、盖板、轴向圈和金属量规需要加工。正常 FDM 可用于无载桌面空间检查、编号牌或外观副本；本交付的承载链、精密孔、滑动面、轴颈和实际照片接触面均不允许用普通 FDM 成品代替。STL 的 0.05 mm 线性 tessellation 设置只是网格近似，不能作为加工公差或物理精度达标证明。

原厂试验轴承外形选取 MISUMI `B608ZZ / 608ZZ`，名义 d=8、D=22、B=7 mm，出处为 [MISUMI 官方目录](https://th.misumi-ec.com/pdf/fa/2013/p631.pdf) 与 [MISUMI 608 说明](https://us.misumi-ec.com/blog/ball-bearings/miniature/608-ball-bearings-8x22x7mm-z-zz-2rs/)。四个 CAD 环没有模拟滚珠、保持架、滚道或原厂公差。轴为自行加工候选，没有从 donor 模块取件。

加工前用 `manufacturing-spec.json` 的 nominal/tolerance/manufacturing_method/measurement_method 表与加工方确认。轴承孔 22.020 ±0.010 mm、轴颈 8.000 −0.010/+0 mm 是 OWN_DESIGN 试制目标，不能当作厂家的配合推荐或 H7 规范。购买的实际轴承、实际孔和轴必须逐一量测，再决定是否修孔、磨轴或调整保持方式。

装配顺序：从底板下方固定两个框架；检查下轴座共轴；将上载体、可换限位块装入窗口；装入参考规格的实购轴承和量规，安装外盖与上桥，最后装轴向圈。盲孔均为 pilot，未建螺纹；加工方须核实所选螺纹、最小壁厚、攻丝／钻尖余量、螺栓啮合与紧固强度，不能直接把 pilot 当通孔完成装配。

盖板／孔肩提供轴承外部保持的候选位置，但真实轴承内外圈、倒角和防尘盖的受力接触未被简化环模型验证。轴向圈停放在盖外，名义间距为 3 mm；这没有证明轴向游隙已控制。先测轴窜量，按实际内圈接触面确定隔套／圈位置，保证不擦防尘盖、不锁死轴承，再做手转与指示表检查。未知的内圈／隔套尺寸没有伪造 CAD 输出。

当前没有建实际弹簧、弹簧保持帽、调压杆、电机、齿轮、护罩或力传感器。窗口中的可换止块是静态停放限位；未装合适的弹簧／调整杆时，上载体只用于无载检查，不能启动挤压或输送试验。量测并选择弹簧自由长、外径、刚度和安装高度，配对检查；独立测 N 与位移，建立调整量到载荷的曲线后才有压辊实验设置。两个调整器分别调节，必须测轴平行度，不能默认同步。

## 验证与复现

在项目根使用本地 venv（PowerShell）：

桌面交付不包含庞大的本机运行时。新环境先使用 Python 3.12 创建 venv，并按本次实际安装的 [依赖锁定文件](requirements-lock.txt)安装；其它系统需确认对应 wheel 可用。网络安装是 CAD 依赖，不是供体或专有后背组件。

```powershell
python -m venv .tools-venv
& .\.tools-venv\Scripts\python.exe -m pip install -r cad/roller_test_rig/R0_bench/requirements-lock.txt
```

```powershell
.\.tools-venv\Scripts\python.exe cad/roller_test_rig/R0_bench/roller_bench.py
.\.tools-venv\Scripts\python.exe -m pytest cad/roller_test_rig/R0_bench/test_roller_bench.py cad/feed_test_rig/R0_bench/test_feed_bench.py -q
```

若系统临时目录不可写，可给 pytest 一个项目内专用 `--basetemp=cad/roller_test_rig/R0_bench/.test-temp`；这只改变测试输出位置，项目外导出清单会使用绝对路径，真实项目内清单使用项目根相对 POSIX 路径。

已运行参数拒绝 RED：7 个明确断言失败；接入检查后测试通过。两套合计 24 tests，包括滑架端点、故意实体碰撞拒绝、来源／单位拒绝和 STEP 回读。当前滚轮装配 23 个单实体，有效且正体积，253 对名义组合无正体积交叉；STEP 回读保留全部实体，包络差小于 0.001 mm。没有做实际材料、载荷、跑偏、疲劳、药囊、暗箱或相机装机验证。

所有几何检查仅针对刚体名义 CAD。`physical_validation=false`、`final_back_manufacturing_authorized=false`；独立台架可试制不等于最终后背、真实片路或化学展开通过。

CadQuery 方法参考：[官方导入导出说明](https://cadquery.readthedocs.io/en/latest/importexport.html)、[官方 API](https://cadquery.readthedocs.io/en/latest/classreference.html)。
