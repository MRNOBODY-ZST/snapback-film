# 原型、验收和实验记录

R0 文档、主机软件测试和 CAD 内核检查不等于任何物理 gate 通过。当前物理循环测试计数为 0，所有可靠性和光学指标未验证。软件检查按 [tools/README.md](../tools/README.md) 与 [firmware/README.md](../firmware/README.md)重现，合成输入与真实试验日志分开。

## 阶段映射与准入

| 用户 P 阶段 | Revision | 活动 | 必须的证据 |
|---|---|---|---|
| P0 | R0 | cartridge/RB 基准测量 | 同基准数字公差链、UNKNOWN 闭合、可行性结果 |
| P1 | R1 | 独立单张 feeder | 先100连续单张且0 double-feed目标；至少100次 ≥99% single，无系统损伤 |
| P2 | R2 | 独立显影 roller rig | 多片盒、重复真实胶片，pod rupture/full coverage/no systematic streak，指标预先固定 |
| P3 | R3 | 双电机 combined transport | ≥100完整循环，无 destructive jam；验证 entry/exit/home 和 jam 检测 |
| P4 | R3E | 控制及供电 | 所有 sensor 断线/卡住、low battery、掉电、限时、一次 jam recovery 验证 |
| P5 | R4 | passive RB67 | 原焦面、image center 和实测光学容差确认，先不整合 motor |
| P6 | R5 | integrated | P3+P5 保持各指标，midpack 密封 |
| P7 | R6 | rotating | 仅实际许可角度，空/满盒、暗板两状态、光学与 transport 均确认 |
| P8 | R7 | field candidate | 至少10完整片盒/100曝光，逐次完整失败记录 |

Gate 1–7 对应：feeder、roller、combined/jam、optical、light seal、mid-pack removal、rotation。P1 的100连续无 double-feed是前述更严格目标，不被后文99%下限替代。黑盖另测，末片/首片/中片分层记录，不把11次出片混算10次曝光成功率。

## 指标与统计

Single-feed success≥99%、ejection≥99%、double-feed<1%、light leaks0、home100%、motor damage0，最终 complete cycle目标99.5%。100次零失败只是样本结果；以单侧95%二项分布下限，`p_lower=0.05^(1/n)`，n=100 得97.05%。若要在独立同分布假设下以零失败证明 p≥99.5%，需 `n≥ceil(log(0.05)/log(0.995))=598`。十盒100片是工程筛选，不是99.5%统计保证；不同片盒/温度/电压相关性还需分层，不能盲用 IID。

区分 missed pickup、double-feed、未抓 nip、pod 未裂、spread失败、jam、nohome、counter错误、光漏/焦错。complete success 的分母是全部尝试，包括失败、取消与掉电；分系统指标另列。100循环假片不能替代真实化学成功率。

## 假片与真实片

假片尺寸按厂商86/72已知长短边；厚度/刚度/摩擦按 M10/M11匹配，至少三类介质夹逼，不写“PET等同胶片”。边框凸起/药包模拟件仅验证送料力变化。开放试验 fixture 可以高速视频观察；真片必须用遮光罩和完整 commercially manufactured film，不制造药液。

roller 真片测试优先有统一曝光的靶图，另拍可区分图像/化学条纹的均匀场。扫描/摄影必须固定曝光、白平衡、距离、光源、显影等待、温度和相纸批号；记录 full spread ratio、未覆盖边缘宽度、条纹对比、roller mark。判据在 DOE 前制定，不在看到照片后改变门槛。

## 光学和漏光

按 film-plane.md 校准：真实 datum 的磨砂面、满开光圈、固定靶距、near/portrait/far，记录最佳 shim 和中心/角部偏差。不能使用随意拍照或相机取景能对焦替代实际片焦平面。

先在 intended plane 放与光谱相关的 photosensitive paper，遮光侧作 negative control，并做已知微漏的 positive control。日晒、缝隙手电、长时、rotate、暗板插拔分别测；覆盖 darkslide slot、exit、rear door、mount、service covers。纸类阴性只对该灵敏度和光谱有效，最终用真实 Instax 验证 fog，目标为0可检测漏光。

Midpack 专门做：曝光若干片→插暗板→拆整后背→明亮环境保持和操作→装回→取暗板→余片逐张曝光处理，与同批未拆对照。不得打开 rear door，不能用换回黑盖代替真实 dark slide。

## jam、电流和掉电

采样记录 A/B nofilm/dummy/normal/pod/partialjam/hardjam，包含电池最差允许电压。堵转用限流/限力 fixture，不拿真实相纸反复硬顶。JAM_CURRENT_THRESHOLD 与 JAM_TIME_THRESHOLD 来源于波形分离与验证，不是随意选毫安/毫秒。

故障最多一次有界反向；只有 M12/M16 证明当前 phase 允许反向才执行，pod 夹住或部分 rupture 可直接 STOP/JAM。相纸未明确回到可识别状态则 SERVICE，绝不自动再次 EJECT。可机械释放 roller spring，先插暗板封光、断电，再 service；开后门只能空盒或安全避光条件。

NVM 在动作前写 transport intent（含 sequence/CRC），完成后 commit；启动发现 pending 一律不假装 READY。counter 在这时可能不确定，进入人工恢复，不因为 HOME true而再次拾下一片。对 each phase注入 reset/brownout，确认 driver disable默认、无假计数和无无限 motor run。

## 记录格式

所有实验只追加：`REVISION, DATE, CHANGE, HYPOTHESIS, TEST, RESULT, FAILURE_MODE, NEXT_ACTION`。还记录原料 lot、参数 register snapshot/hash、sheet position、darkcover flag、motor/roller/cam ID、计数和完整原始日志。模板位于 [experiments](../experiments/README.md)。R0→R7历史不可覆盖。
