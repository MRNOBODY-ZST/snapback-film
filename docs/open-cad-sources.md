# 已有 CAD 检索与采用清单

R0 参考资料增补，2026-10-07。检索包含原作者仓库、Thingiverse、Printables、Thangs、Goodman 官方源目录及工业零件原厂图纸。本报告区分“文件可以下载”“作者做过装配/拍摄”和“尺寸具有可追溯的量测与公差”，三者不能互相替代。

## 搜索结果与工程决定

**找到了可以利用的接口与片盒 CAD；没有找到可核实的完整原厂 RB67 旋转适配器测量模型。**

本项目优先采用三组参考：CC BY 4.0 的 Mamiya Press G-adapter 源链、Jocelyn Girard 的 Square 相盒 STL、SPRKPLG 的 CC0 Square 压片组件。采用范围是建立参考实体、读取名义几何、比较装配关系和制作后续配合校核件；不是把原模型尺寸直接宣布为本机实测值。实际成功下载的原件、来源、许可证和 SHA-256 放在 [cad/reference](../cad/reference/README.md)。本次未设计最终后背。

原厂 [Pro-S 手册](https://www.reznitsky.info/Mamiya/Doc/RB67_Pro-S_v7.PDF)印刷第 36 页区分机身 R-lock 与接环后背侧 G-lock。我们保留匹配的原旋转适配器，因此需要自制后背的 **G 接口配合侧**。Press 相机接收现有 RB 后背的模型是同一接口的**接收侧**，能帮助反向识别定位、锁条和避让面，但不能整块当作后背安装板。机身直连 R-lock 后背也不能代替这个接口。

## 优先参考模型

| ID / 原始来源 | 文件、许可与验证状况 | 实际用途 / 仍缺什么 |
|---|---|---|
| G01 [moebot3000：初始 Press G-adapter](https://www.thingiverse.com/thing:3825622) | 原页 CC BY 4.0；最初作者仍在调法兰距离 | 上游署名链与接收座原理；不取其光学基准 |
| G02 [rodgsilva / rodsgear：G-adapter V2](https://www.thingiverse.com/thing:4249403)，[作者 Printables 镜像](https://www.printables.com/model/117680-mamiya-press-universal-g-adapter) | Fusion 源文件和 STL；CC BY 4.0。作者 2020 年 5 月报告用 100 mm f/3.5 镜头拍摄对焦准确、无漏光 | 接收座、两条锁扣与配合关系的名义几何；无原始读数、定位基准与公差 |
| G03 [SPRKPLG / Thnikkamax：G-adapter Template](https://www.thingiverse.com/thing:4269290) | 可编辑 Mamiya_Press_G_Adapter_v4.f3d 和网格；CC BY 4.0。作者报告用毛玻璃检查无穷远对焦 | 优先作为 G 接口参考；仍须核对本机接环、暗板联锁与有效曝光面 |
| C01 [Jocelyn Girard / jclngrrd：Instax Square Cartridge](https://www.thingiverse.com/thing:3790489/files) | Instax_sq_cartridge_v2.stl，2019-08-06；原页 GNU LGPL，链接 LGPL 2.1。为自制 6×6 后背建模，作者后来表示未推进该后背项目 | 优先作为相盒外形参考，先校核而非从零描每条棱；无可追溯实测、公差、乳剂面、片堆和压片力证据 |
| C02 [SPRKPLG：Lomograflok Instax Square Mod](https://www.printables.com/model/276605-lomograflok-instax-square-mod/files) | LG_square_bar.step、LG_square_cover.step、Lomograflok Square.f3d，另有 STL/3MF；CC0。作者报告 Square/Wide 测试片能推出，尚未实际拍摄 | 开放可编辑的 Square 压片条、后盖与座位参考；不使用 Lomograflok 硬件。压包力、曝光面与显影参数仍未知 |

上述文件的存在、文件名和作者许可属于来源事实；通过文件解析得到的尺寸属于 **DERIVED 的模型名义几何**。把这些尺寸用于现实片盒或相机时，其物理适用性先记为 **ESTIMATED**。有完整实物读数与复核后才可标 VERIFIED_MEASUREMENT。几份模型互相吻合也不能自动证明原厂公差。

G02 作者镜像列出的 G 座网格包络为约 123.52 × 112 × 5.15 mm，基座约 125.99 × 112 × 13.72 mm；这只是 [作者 Cults 镜像](https://cults3d.com/en/3d-model/gadget/mamiya-press-universal-g-adapter)的文件包络，**不是原旋转适配器外形、接口配合尺寸或曝光面距离**。STL 本身不储存单位；项目解析报告保留原文件轴和模型单位，不能靠相纸 86 × 72 mm 强行缩放相盒。以实际下载文件的 hash 和解析结果为准。

## 有用但不并入最终结构的参考

| 来源 | 核验结果 | 使用边界 |
|---|---|---|
| [Super-67 作者仓库](https://github.com/DamienHazard/Super-67) | Super67_CAD.step、接收座和锁条 STL；CC BY-NC-SA 4.0，作者说明为 beta；使用 Mamiya Press 镜头和 RB 卷片后背 | 布局与 G 接口对照。有 NC 限制；优先使用上表独立 CC BY 上游，不能把 Super-67 修改重新标 MIT |
| [Goodman 官方源目录](https://drive.google.com/drive/folders/1sg494rklatG5F5E5yP6nZhJtHTwx40PN)，[CAD 子目录](https://drive.google.com/drive/folders/1wFI8hwnrmsJtTZHf3UqQnTqF94a6hn0K) | ZONE_OS_2020.f3d、GOODMAN_ZONE_metric.f3d；[官方 FAQ](https://doragoodman.com/faq/)限制个人用途；README 指出基本款适配 Pro-S，另有 Pro-SD beta mod | 可以比较装配路径和版本，不能当作可自由商业再用的完整开放源 |
| [maf：RB67 Pro-S Square 后背](https://www.printables.com/model/1701418-mamiya-rb67-pro-s-instant-film-back-using-jollyloo/files) | 25 文件，含 12 STEP；CC BY-NC 4.0。使用 Jollylook，并替换原旋转适配器，机身四安装柱直连；另有打印柱版本 | 仅比较外壳/出口/暗板布局。作者披露暗板遮光不充分、构图偏移和对焦误差，不能据此证明本项目光学或中途拆背合格 |
| [Maddiefuzz：Square Adapter](https://thangs.com/designer/maddiefuzz/3d-model/RB67%20Instax%20Square%20Adapter-1381438) | 作者 V1 使用 Jollylook；下载要求登录；具体许可、STEP 清单和原接环保留情况未核实 | 只作先例，免费不等于开放许可；不复制未获文件的尺寸 |
| [DavidB75：Focus checking adapter](https://www.printables.com/model/130759-rb67-focus-checking-adapter/files) | focus checking back RB67 v16.stl；CC BY-NC-SA 4.0；装现有对焦屏 | 借鉴后部毛玻璃夹具的装夹方式；未定义支承面到磨砂面/有效曝光面的偏置，不能直接作为 z_R |
| [Zanfar：RB67 接口盖](https://www.printables.com/model/1192536-mamiya-rb67-pro-pro-s-pro-sd-back-cover/files) | STL/3MF，CC BY-NC-SA 4.0；由校准夹具/背盖修改，新增定位条与暗板联锁触发销 | 用于补充联锁检查点；不是旋转机构或三版本精密测量图 |
| [DavidB75：Square 取景遮罩](https://www.printables.com/model/297447-rb67-mask-for-instax-square-back/files) | FS Mask.stl，CC BY-NC-SA 4.0；无所用后背的实际曝光域和偏心定义 | 可以参考可逆安装；本项目窗口与中心仍按实测捕捉域生成 |
| [Orcuslc：Hasselblad Instax Back](https://github.com/Orcuslc/Hasselblad-Instax-Back) | 13 STL，钩子、齿轮、压片器、插刀；原设计 Instax Mini，未见明确 LICENSE/BOM/测量记录 | 仅研究分离/拾片/手动周期；不能把 Mini 行程、片盒或传动换称 Square 参数 |
| [Kodak Square adapter](https://www.printables.com/model/836515-instax-square-adapter-for-kodak-instant-cameras/files) | 4 STL，CC BY-NC-SA 4.0；作者报告 3 个适配器工作、需手工修配与自制金属件 | 独立交叉核对座位/压片/回位，不采用原 Kodak 显影机构 |
| [Wide → Square 改版](https://www.thingiverse.com/thing:5457312/files) | 页面 CC0，但其 [上游](https://www.thingiverse.com/thing:3383869) 为 CC BY-NC-ND 4.0；后盖 push element 是压包件，非拾片钩 | 许可链未闭合，不重分发衍生几何；可观察压包件圆角与防弯问题 |

[RB67 Hackaday 计划](https://hackaday.io/project/176815-mamiya-rb67-instax-back)的发布者尚未实施 Mini→Wide/Square 修改，不能称作已有可工作的开放 Square 后背。搜索出现的无一手仓库、无量测记录却宣称微米级精度的页面也不采用。

## 其他可以从网上取得的工程尺寸

[MISUMI USRH/USRM/USSRH 原厂图](https://us.misumi-ec.com/pdf/fa/2019/2019_US_1168.pdf)提供可配置聚氨酯包胶轴滚轮：轴径 d 为 8/10/12/15 mm，包胶厚度 T 为 2–5 mm；前三区间总轴长 L 为 50–200 mm，d=15 时为 50–300 mm。USRM 为 Shore A70，USRH/USSRH 为 A90；轴颈 g6，总长公差 0/−0.2 mm。[当前系列页](https://jp.misumi-ec.com/vona2/detail/110300423870/)可查 CAD。这里 d 是轴尺寸，不要误填为包胶工作外径。

这些是候选商品的 **MANUFACTURER_SPEC**，未选定该系列或长度。可以减少轴座与材料制造规范的未知数，不能确定 Instax 辊隙、预载、药包破裂力、转速或合格展液范围。原厂 CAD 未核实开放再分发许可，引用原厂图并独立设计支承结构。现成滚轮也须实测跳动、工作平行度和真片展液，不能因有 CAD 就跳过 P2。

片长/短边 86/72 mm、图像 62 mm 和 10 张曝光数已有 [富士官方数据](https://www.instax.com/squareformat/en/)。电机/驱动/电池候选的原厂尺寸与电气规格见 [electronics.md](electronics.md)，但未知负载仍阻止定型和 PCB 包络冻结。

## 将测量从“全重建”改为“参考模型校核”

| 对象 | 网上模型替我们做什么 | 用户仍须校核的关键点 |
|---|---|---|
| G 接口 | 接收侧名义轮廓、锁条位置与整体配合思路 | 本机接环版本；三个轴向接触点；两条锁定边跨距、厚度与轴向高度；暗板联锁件；锁定重复性 |
| 原旋转适配器 | 手册可确认接口类别/操作；目前没有完整可信 CAD | 后基准 A 到原有效曝光面 z_R；多个 Z 截面的空腔和通光轮廓；旋转轴与允许角度；机身扫掠净空 |
| Square 相盒 | 空盒外形实体、局部开口的候选形状 | 至少复核三轴包络、前壳突出量、出口与拾片窗最小净空；记录实际盒子版本/批号；核查模型遗漏或简化 |
| 曝光面与压片 | 开放压条 STEP 作为可调接触/避让参考 | 满/半/末片在受控压包条件下的最前片高度、倾斜与 F(x)；外层到有效光学面的校准 |
| 拾片/滚轮 | 可以借可换爪与轴座设计原则、商品工程图 | 单张接触位置、啮合深度、F(x)、盖片处理、nip 捕获、真实 pod/展液/滑移与电流曲线 |

第一轮仍按 [M01–M06](measurements.md) 闭合原焦平面冲突，但外壳和接收座的建模可从现有源实体开始。不要再要求把所有非关键圆角从零量一遍；先确认模型尺度与本机匹配，再测决定配合、通光和焦平面的特征。相盒前端与有效曝光面不能只凭总厚度推算。

导入后保留来源原点和原始姿态。再独立建立项目 P/R 坐标系，记录明确的刚体变换，不能默认源模型原点是光轴、旋转轴或乳剂面。未经登记的“缩放以便装上”不得进入参数台账。M02 还应实测原卷片后背的配合侧及锁条搭接，不能只用接收座的网格负形。三点基准必须取实际承载接触面，记录锁紧与密封压缩状态，不能取装饰面、泡棉面或包络极值。可打印配合样块的间隙必须标为可调设计量；打印收缩也不能冒充原件测量。

## 许可与交付边界

CC BY 源链须保留作者、作品链接、许可证和改动说明，见 [官方条款](https://creativecommons.org/licenses/by/4.0/)。本次原始文件不修改。CC0 压片件按 [CC0](https://creativecommons.org/publicdomain/zero/1.0/)记录出处。相盒原件保留 LGPL 2.1 标识与文件，不重新标 MIT；后续若修改/分发其衍生实体，另列对应源与许可记录。具有 NC/ND 或未明许可的项目不作为本项目最终结构的复制来源。

**FEASIBILITY RESULT 仍为 UNCERTAIN — MEASUREMENT REQUIRED。** 本次增加可用参考资产并减少从零建模工作，不产生任何实物量测、单张可靠性、展液或原焦平面通过证据。

## 本次本地采用情况

实际归档 19 个原始资产：10 个 STL、3 个 STEP、3 个 Fusion F3D，以及 3 个原说明/许可文件。包括 G02/G03 可编辑源文件、C02 压条/罩 STEP 和 Fusion 文件、C01 相盒 STL。10 个 STL 已做有限顶点/三角面/包络检查；STEP 检查文件封套与单位声明，F3D 检查 ZIP 成员及 CRC，未声称导入原生 Fusion 参数或验证实际装配。原件 hash 和检查结果见 [geometry-report.md](../cad/reference/geometry-report.md)。

C01 相盒及此前待下载的 6 个 CAD 文件本轮均通过公开下载取得；source-manifest.json 的 pending_assets 现为空。原件不改写；新增 [源码参考预览](../cad/cartridge/R0_reference_only/README.md)以可调坐标变换生成分面 STEP/STL，明确保留原许可、源坐标和单位假设。未用缩略图制造相盒尺寸，也未把参考网格当作实际曝光面。

本地名义几何报告与待测参数台账分开：仍为 114 个工程参数、105 项 UNKNOWN、0 项实物 VERIFIED_MEASUREMENT。本次没有新增任何试验通过记录。
