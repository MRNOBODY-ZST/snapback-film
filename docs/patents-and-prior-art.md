# 专利与一手先例检索

本文件为 2026-10-07 的第一阶段技术检索记录，范围是 Instax 片盒、单张拾片、运输与显影辊。它不是完整专利检索、法律意见、自由实施（FTO）结论或最终设计许可。专利公开披露可以支持原理研究，但“读到专利”不等于可以复制其全部组合；开放发布也不自动排除第三方权利。

参阅：[研究总览](research.md)、[运输推导](transport.md)、[显影辊 DOE](roller-development.md)、[测量计划](measurements.md)、[架构](architecture.md)。本项目允许原装胶片/片盒作为耗材，运输硬件不使用供体相机或商业专用显影总成。

## 1. 如何使用证据

下面的专利页是原始公开专利文本的转载；引文定位为具体权利要求、图号或说明书标题。技术披露和权利要求分别记录：说明书能证明某个思路曾被披露，不能单凭它判断权利范围；独立权利要求也不能脱离其全部限定、审查历史和国家差异作侵权结论。

专利示意图不是量具。未写明的片盒尺寸、爪尖厚度、辊径、预载、速度、公差与材料牌号不能从图片比例推导成制造规格。公开申请的权利要求也不等同于该族最终授权权利要求。

## 2. 一手证据矩阵

| 文献 | 精确定位与支持的事实 | 可研究的内容 | 未能证明的内容 |
| --- | --- | --- | --- |
| [US5541683A — Instant film pack and instant camera](https://patents.google.com/patent/US5541683A/en) | 摘要及权利要求 1：片盒后部开口接收相机压垫；内部遮光件传递压力使片堆贴曝光口。权利要求 2：拾片爪缺口 | 把片盒、遮光片、后盖压片作为一个受力系统 | 当前 Square 的开口坐标、内部形状与压片力 |
| [US6463213B1 — Film unit picking device](https://patents.google.com/patent/US6463213B1/en) | 权利要求 1：爪有退出/轻接触位置及挂片位置，并与独立停止件配合。图 4 说明：一个凸轮周产生一次往复。图 1 说明：挂住最前张后交给辊并回原点 | 爪尖卸载、单张尾缘挂接和一周机械循环 | 正确的 Square 爪行程和指尖制造尺寸 |
| [US6490414B2 — Instant film unit advancing apparatus](https://patents.google.com/patent/US6490414B2/en) | Related Art：一凸轮周完成拾片、送辊、排出、回原点，且辊打滑会导致排出不足。权利要求 1：正反电机、单向辊传动、带保持位置的往复爪 | 出片长度不等式、原点与出片信号分离、反转隔离辊的原理 | 可以无风险反转已受压药包；本项目具体齿数 |
| [US7195406B2 — Instant film pack](https://patents.google.com/patent/US7195406B2/en) | 权利要求 1、2、3分别涉及爪开口遮光材料/结构。图 6 说明披露爪电机与送片电机分别驱动、随片数减少伸出的压件、钢显影辊 | 双电机概念与进片/显影分工的先例 | 双电机为本项目的新发明；当前 Square 使用该具体结构 |
| [US7502551B2 — Instant film pack](https://patents.google.com/patent/US7502551B2/en) | 权利要求 1：出口两端防冲出件；权利要求 5：分两次爪往复打开的遮光板。图 2 说明：药包—图像—吸液端排列 | 出口挡片、黑盖初始化、片盒本身参与防双张 | 所有当前 Square 盒都执行两次开板；黑盖与胶片阻力相同 |
| [US20180231893A1 — Developer spreading device](https://patents.google.com/patent/US20180231893A1/en) | 图 7、9、17—22说明方形胶片结构、外部压件、输送辊与展开辊。权利要求 1：两辊对之间带中央凸出的展开控制件 | 辊与片盒协同、避免提前破包、跨宽布液 | 0.01—0.5 mm 是辊隙；该申请文本是各国最终授权范围 |
| [EP3361310B1](https://patents.google.com/patent/EP3361310B1/en) | 权利要求 1包含输送辊、展开辊和中央凸出控制件；权利要求 2给出控制件中心凸出 0.01—0.5 mm；权利要求 4涉及宽度 70—95% | 欧洲授权文本与 US 申请的区分 | 这些数值为 Square 自制辊的试验建议 |
| [CN108415225B](https://patents.google.com/patent/CN108415225B/zh) | 中国授权权利要求 1包含中央凸出控制件、其宽度为曝光面 70—95% 及其相对夹持位置；权利要求 2涉及中心凸出范围 | 针对中国文本逐项比较实际设计特征 | 可以仅因 US 同族申请放弃而自由复制 |
| [US12291419B2 — Transport device for instant film](https://patents.google.com/patent/US12291419B2/en) | 2025-05-06 授权；权利要求 1涉及两种不同宽度胶片的刺状辊成员、其间辅助辊和对向压辊组合 | 新近输送专利、单制式与多制式结构的差别 | 所有普通单制式辊对都落入其范围；本项目当然不侵权 |

部分说明书描述的是打印机或旧胶片形式，研究价值在原理，不将它们贴成“富士 Square 工厂构造”。实例中的曝光头、数字成像和额外进片辊也不能无分析地复制到已经整张曝光的 RB67 后背。

## 3. 家族与法律状态的必要边界

2017-02-10 优先权的展开控制件文献包括 US20180231893A1、EP3361310B1、CN108415225B 和 JP6779152B2。US 公开页显示放弃，而相关国家存在授权文本；同族在不同国家的权利要求不同，上表已经可见 CN 把某些几何限定并入权利要求 1。参考：[US 页面 Country Status](https://patents.google.com/patent/US20180231893A1/en)、[中国授权文本](https://patents.google.com/patent/CN108415225B/zh)、[欧洲授权文本](https://patents.google.com/patent/EP3361310B1/en)。

Google Patents 法律状态标签自身说明它是推定、不是法律结论。本文不据其“Expired”“Abandoned”“Active”标签宣布可商用或不可商用，也不输出确定的到期日期结论。制造、销售、出口或开源发布前如需判断实施自由，应以具体目标国家官方登记、实际授权权利要求、续费/无效情况、同族和分案、审查历史以及实际设计特征为依据，再取得合适的专业审查。

本阶段的实际动作是：建立来源和特征对照；按功能从测量独立推导结构；保存原创设计记录；不复制已知专利的整套图纸；不要把“单电机凸轮”“双电机”“可换辊”这些一般功能当作已获新颖性证明。是否规避或构成等同需要另外判断，不能由此文档保证。

## 4. 原作者/制造商先例与开放程度

| 一手出处 | 能确认的范围 | 与本项目的关系 |
| --- | --- | --- |
| [Kevin Kadooka，Instax SQ6 Lens Transplant 项目](https://hackaday.io/project/158654-instax-sq6-lens-transplant)及[其原作者 ejection circuitry log](https://hackaday.io/project/158654-instax-sq6-lens-transplant/log/147833-5-revised-eject-circuitry-or-ramblings-on-sharing-open-source) | 原作者公开 SQ6 改装和原点开关/制动经验；文中警告制动不足会越过原点继续出片 | 这是供体机构改装，不能作为无供体制造方案；仅参考停止过冲故障原理 |
| [Jollylook SQUARE Development Unit 制造商产品页](https://jollylook.com/products/jollylook-instax-square-film-development-unit) | 制造商出售手摇、兼容 SQUARE 的独立显影单元，并提供用于外形匹配的 3D 模型 | 可说明专用显影模块路线存在；商业专用总成不在本项目范围，外形模型不等于内部全套开放制造资料 |
| [Toast，3D Printable Polaroid Camera 原作者产品页](https://toastchannel.gumroad.com/l/ngeiz?layout=profile) | 后续读取原作者页确认使用 Instax Mini，提供打印文件与 ReadMe；未见明确开放硬件许可、完整 Square BOM 或验证记录 | 只作后续核验线索，不用二手文章的“全打印/钢辊成功”叙述证明 Square 工程可行或开放授权 |

此次所核验的一手资料中，没有取得一套同时满足“原生 SQUARE、完整运输/辊制造文件、允许复制的明确开放许可证、无供体/商业专用总成、可复做验证记录”的现成方案。这是本次证据覆盖范围，不是声称全世界没有这种项目。作者说“计划开源”、发布外壳 STL、或提供商业组件的外形模型，均不能独立证明运输核心已开放。

如果后续取得第三方 CAD、代码或数据，先核对许可证、作者/版本及修改传播要求。自行绘制只是避免直接抄文件的一种记录方式，不能替代专利范围判断。

## 5. 已知数值与防误读清单

| 数值/标签 | 实际含义 | 不可误读为 |
| --- | --- | --- |
| 86 × 72 mm；62 × 62 mm | [富士 Square 单片/图像规格](https://www.fujifilm.com/us/en/consumer/instax/film/square-film) | 片盒三维包络、槽长、辊长或机构行程 |
| 一张黑盖 + 10 张 | [富士 SP-3 手册](https://asset.fujifilm.com/www/jp/files/2023-08/aad7a0d673c4dde6dc3c5170cd7b0410/instax_sp-3_manual_01.pdf)，英文第 33 页 | 11 次相同负载/同样时序的照片循环 |
| 控制件中心凸出 0.01—0.5 mm | EP3361310B1 权利要求 2、同族说明 | 辊隙、片厚、轴跳动允许值或可抄用 DOE 窗口 |
| 控制件宽为曝光面 70—95% | EP 权利要求 4、CN 权利要求 1 | 显影辊有效宽或药包宽 |
| 产品页的整机/模块尺寸 | 某商业总成的外形说明 | 片盒尺寸或内部制造尺寸；本项目不用其作为 datum |

本项目的辊径、预载、速度、粗糙度、硬度及容差范围继续明确为未知，按 [roller-development.md](roller-development.md) 建立实测窗口。

## 一手来源目录

所有链接为直接页面，不是搜索结果页。专利使用公开文本原文，正文以有限释义说明，不大段复制专利。

- https://patents.google.com/patent/US5541683A/en
- https://patents.google.com/patent/US6463213B1/en
- https://patents.google.com/patent/US6490414B2/en
- https://patents.google.com/patent/US7195406B2/en
- https://patents.google.com/patent/US7502551B2/en
- https://patents.google.com/patent/US20180231893A1/en
- https://patents.google.com/patent/EP3361310B1/en
- https://patents.google.com/patent/CN108415225B/zh
- https://patents.google.com/patent/US12291419B2/en
- https://www.fujifilm.com/us/en/consumer/instax/film/square-film
- https://asset.fujifilm.com/www/jp/files/2023-08/aad7a0d673c4dde6dc3c5170cd7b0410/instax_sp-3_manual_01.pdf
- https://hackaday.io/project/158654-instax-sq6-lens-transplant
- https://hackaday.io/project/158654-instax-sq6-lens-transplant/log/147833-5-revised-eject-circuitry-or-ramblings-on-sharing-open-source
- https://jollylook.com/products/jollylook-instax-square-film-development-unit
- https://toastchannel.gumroad.com/l/ngeiz?layout=profile

## 第三方 CAD 源链增补

[open-cad-sources.md](open-cad-sources.md)列出已核验原页许可与版本。G 接口 moebot3000→rodgsilva→SPRKPLG 三个上游均显示 CC BY 4.0；本地 G02 STL 可作带署名的名义结构起点。CC0 Square 压条/罩也可参考，但不要求 Lomograflok 总成。相盒 C01 显示 LGPL 2.1，目前只登记原文件页与未下载状态。Super-67 的 NC 修改只作对照，不能重新标 MIT 后并入最终开放制造文件。公开源码标记、免费按钮或商品外形 CAD 不证明完整运输核心开放。
