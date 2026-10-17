# P1 / R1 单张进片实验平台定义

P1 完整送料功能仍待接口量测。本轮已有 [R0 开放观察/滑架台架](R0_bench/README.md) 的 CadQuery 源、STEP/STL、加工目标与检查清单；它不包含经实测的相盒巢、真实拾片爪、凸轮或电机配合，不代表 P1 通过。

模块：三基准片盒定位巢 + 可控后盖压力 + 可换finger/cam/spring + 单独电机A + 位移标尺/测力计 + 可调nip替代/实际roller cassette接口。透明或开放观察侧适用于dummy/已显影片，真正原始film加独立可拆light shield。

可调参数：PICKUP_DEPTH、PICKUP_STROKE、PICKUP_FORCE、PICKUP_ANGLE、PICKUP_CONTACT_WIDTH、CAM_RADIUS、CARTRIDGE_PRESSURE_*。每次换finger/cam保留同一安装基准，重新量啮合窗口和回程脱离；进片窗和图像区边界由M08给出，不任意挖片盒。

需要先量：M04–M12。目标：100连续单片、0doublefeed、无systematic scratch；首/中/末/黑盖分组，记录F(x)、I_A(t)、视频、nip夹持证据和home。模板见../../experiments/feed/feed-log.csv（路径应从项目根按experiments/feed读取）。
