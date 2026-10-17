# 需求追踪、预算和交付边界

版本R0，用户的V2条款1–66及“PCB我自己画”说明为本项目输入。当前交付工程研究，后续最终CAD/电子硬件/产品固件和实物验收均未完成。

## 需求映射

| 用户条款 | 研究文件 | 当前状态 / 后续门槛 |
|---|---|---|
| 1–3 无供体架构/原理研究 | research、architecture、patents-and-prior-art | 已建立原则；最终source和通用BOM未实现 |
| 4 片盒参数与未知量 | measurements、cad/parameters.json | 量测计划完成；实体片盒模型需M04–M13 |
| 5–6 三类拾片/真实机械相位 | transport | 符号推导及比较完成；stroke/force/angles需实测 |
| 7–9 精密滚轮/可调压/平行度 | roller-development、measurements | DOE边界方案；没有Square来源支持的绝对规格 |
| 10–11 电机SF≥2/开放齿轮 | electronics、architecture、transport | 厂商候选与推导；负载/ratio/continuous torque未定 |
| 12–13 jam/home/exit | electronics、firmware、transport | STOP→至多一次安全回退→STOP→JAM；无自动重推；需P4 |
| 14–17 暗板/midpack/接环/原焦面 | film-plane、measurements | UNCERTAIN — MEASUREMENT REQUIRED；必须先量测 |
| 18–21 控制/1S/USB-C/状态/计数 | electronics、firmware、PCB接口合同 | C++17 主机控制核心与 journal、合成测试；未投板/未接入真实 MCU 与机电 |
| 22–23 模块/参数CAD/STEP/STL | architecture、cad/parameters.json | 19模块及114参数登记；制造导出受未知量阻塞 |
| 24–29 P0–P8/实验机/目录 | testing、cad各目录README、experiments | 目录/空模板与计划完成；0物理试验 |
| 30 维度来源 | measurements、parameters.json | 六级分类；UNKNOWN=null、可追溯过程；无假测量 |
| 31 A/B/C几何与明确结果 | research、film-plane、measurements | 明确不确定；已知/未知分开，不给虚构mm间隙 |
| 32–33 三完整概念/权重/双电机 | architecture | A62、B69、C58（ESTIMATED）；推荐B，硬几何gate独立 |
| 34–35 roller DOE/五制造法 | roller-development | 替换cassette、取边界/块化试验；工艺需真实片验证 |
| 36 pickup五末端/观察平台 | transport、feed_test_rig/README | 可换设计变量；透明观察只用假片/废片 |
| 37–41 黑盖/S0/S1/门/持久计数 | electronics、firmware、architecture | cover完成设10；midpack卸背不reset；door不自动newpack |
| 42–44 手动曝光/UI/避免伪检测 | architecture、firmware | V2用户负责快门；EJECT不等于已曝光 |
| 45–49 service/USB/log/current/sensors/devboard | electronics、PCB接口、testing | S0–S5、两路I(t)、保护式点动；阈值未量测 |
| 50–55 公差/调整/光学/漏光/旋转/centering | measurements、film-plane、testing | 准备名义/公差/工艺/测法；最终光学容差待定义 |
| 56–57 可逆取景遮片/成片方向 | film-plane、accessories/README | 有打印比例靶；完整遮片需真实capture polygon，不假造STL |
| 58–59 质量/载荷/外壳 | architecture、下表 | 给预算推导；质量与接口承载需实测，最终外观延后 |
| 60–63 完整source/证据/版本/gates | README、testing | 此阶段只是R0文件；未把未来目录当完成交付 |
| 64–65 FMEA/商业胶片/化学处理 | fmea、roller-development、measurements | 风险与清洁试验路径；不剪破/调配胶片化学品 |
| 66 final USD100–150目标 | 下表、electronics | 估算与供应商候选价分开；目标未证明可达 |
| PCB由用户绘制 | electronics/pcb/interface-contract.md | 提供功能/针序；板框、孔位、J位置待M22冻结 |

## 成本：预算区间，不是报价

下面是 **ESTIMATED 研发预算分配**，币种USD；不是厂商售价和可直接购买的确定BOM。排除RB67、lens、film、量具、测试仪器、税费和运费；台架/迭代支出包含原型机械重做的预算，不包括开发工时。现查Pololu候选两台约47.90美元的具体事实见electronics.md，提示通用优质电机可能超过最终电机分配，必须重算而不能用低预算强行选不够力的产品。

| 类别 | 可调原型预算 | 最终一台预算 | 不确定性 |
|---|---:|---:|---|
| 两电机与减速 | 30–60 | 20–50 | 真实扭矩/连续额定/供应渠道 |
| 滚轮芯/套/加工 | 30–90 | 15–40 | 真实显影要求与加工批量 |
| bearings / shafts | 12–30 | 8–15 | 跨距、精度、轴径未定 |
| gear / cam / finger | 10–30 | 5–12 | 材料/负载/机构路线 |
| controller / PCB / H桥 / sense | 20–45 | 10–20 | 开发板或定制量产/调试桥 |
| sensors / UI / connectors | 12–30 | 6–15 | sensor方式与线束电流 |
| 1S battery / charger / protection | 15–30 | 10–20 | cell放电能力、power-path容量 |
| mount / door / seal / fasteners | 30–80 | 15–30 | 精密接口加工和darkslide方案 |
| 独立台架/重复零件 | 40–100 | 0 | 不进入最终便携后背 |
| **合计预算** | **199–495** | **89–202** | 需实测选型和供应报价收敛 |

最终89–202区间和100–150目标有交叠，**不证明能达到目标**。滚轮/接口/电机是优先证据项目，不能为了低于150取消精密bearing carrier、保护和诊断。

## 质量：先给分配，再称重

缺片盒、滚轮和外壳实体，当前不能给物理总质量的可信预测。下面用 **ESTIMATED 的质量分配目标** 帮助约束方案，不能写成“本后背重400g”。bench fixture、临时电源和仪器不计便携后背。

| 便携模块 | 预算分配 g |
|---|---:|
| 两电机/减速 | 40 |
| 滚轮/轴/bearing carrier | 110 |
| cam/gear/finger | 40 |
| protected battery | 45 |
| PCB/UI/线束 | 30 |
| mount/chamber/door/darkslide/fasteners | 180 |
| 商售满片盒 | 55 |
| **合计分配目标** | **500** |

55g片盒项是预算占位，**不是测得的片盒质量**。量测后每项改为实物质量/密度×实测CAD体积。重心靠mount的设计意图与承载验证独立；例如预算500g对应重量约4.905N（g=9.81m/s²的初算），弯矩仍为 `4.905×CG_Z(m)`，由于CG与接口承载未知，不宣布强度通过。原型可因可调性超预算，但必须列清实际质量与受力，避免相机作为破坏性测试夹具。

## 本阶段缺口和后续真实交付

FreeCAD实体/STEP/STL、实尺寸视屏遮片、机构装配/爆炸图、最终rollers/springs/gears/shafts明细、schematic/PCB/Gerber/BOM、firmware source/build/flash、assembly/maintenance/service手册都将在对应gate通过后提供。目录建立不代表已具备这些物料。最终交付必须包括供应替代、材料工艺、公差、测法与实验依据，让他人能复做；当前不使用空的platformio.ini营造固件完成状态。
