# 代码候选 先确认再采用

核查日期2026-10-31。以下仅为公开资料阅读、仓库与入口文件索引，没有克隆、安装、集成或运行。标为未确认许可的项目先保持参考状态；HachimoDock为受限源码可见项目。正式采用前核对固定提交、第三方依赖与素材许可。

## PosturePal

仓库：[查看作者仓库](https://github.com/shensquared/PosturePal)

许可证：MIT。参考：个人校准、持续偏离与暂停策略。

适配限制：Python与桌面摄像头环境；不能直接部署为主板姿态固件。

建议：优先评估。状态：待用户确认，未下载或复用。

入口文件：[pose_webcam.py](https://github.com/shensquared/PosturePal/blob/main/pose_webcam.py)；[config.json](https://github.com/shensquared/PosturePal/blob/main/config.json)。

许可原文：[LICENSE](https://github.com/shensquared/PosturePal/blob/main/LICENSE)。

## Smart-Bin

仓库：[查看作者仓库](https://github.com/2black0/Smart-Bin)

许可证：MIT。参考：开关状态与舵机控制示例。

适配限制：Arduino及超声波距离触发，不是摄像头投放识别；引脚、电压与限位须重新设计。

建议：优先评估。状态：待用户确认，未下载或复用。

入口文件：[main.ino](https://github.com/2black0/Smart-Bin/blob/master/Project/main.ino)。

许可原文：[LICENSE](https://github.com/2black0/Smart-Bin/blob/master/LICENSE)。

## Deepgram Vibe Coder

仓库：[查看作者仓库](https://github.com/deepgram/vibe_coder)

许可证：MIT。参考：口述到编码指令的交互组织。

适配限制：依赖Deepgram及编辑器接口；不能替代灵机一动核心语音链路。

建议：按需评估。状态：待用户确认，未下载或复用。

入口文件：[dictation-service.ts](https://github.com/deepgram/vibe_coder/blob/main/src/services/dictation-service.ts)；[voice-agent-service.ts](https://github.com/deepgram/vibe_coder/blob/main/src/services/voice-agent-service.ts)。

许可原文：[LICENSE](https://github.com/deepgram/vibe_coder/blob/main/LICENSE)。

## 小智ESP32

仓库：[查看作者仓库](https://github.com/78/xiaozhi-esp32)

许可证：MIT。参考：唤醒、语音与设备工具的工程分工。

适配限制：当前分支要求的SDK与项目固定SDK不同；不建议整包替换比赛固件。

建议：按需评估。状态：待用户确认，未下载或复用。

入口文件：[application.cc](https://github.com/78/xiaozhi-esp32/blob/main/main/application.cc)；[device_state_machine.cc](https://github.com/78/xiaozhi-esp32/blob/main/main/device_state_machine.cc)；[mcp_server.cc](https://github.com/78/xiaozhi-esp32/blob/main/main/mcp_server.cc)。

许可原文：[LICENSE](https://github.com/78/xiaozhi-esp32/blob/main/LICENSE)。

## VibeKeys App

仓库：[查看作者仓库](https://github.com/second-state/vibekeys_app)

许可证：GPL-3.0。参考：语音、接受、退出等实体快捷入口。

适配限制：复制集成需核对GPL义务；YOLO或按键y映射不能代替本次具体授权。

建议：先看交互。状态：待用户确认，未下载或复用。

许可原文：[LICENSE](https://github.com/second-state/vibekeys_app/blob/main/LICENSE)。

## VibeKeys Firmware

仓库：[查看作者仓库](https://github.com/second-state/vibekeys_firmware)

许可证：本次未确认。参考：实体按键与主机协作方式。

适配限制：仓库元数据无识别许可证，未获得采用许可结论；硬件配置不同。

建议：仅阅读参考。状态：待用户确认，未下载或复用。

## VibeBoard

仓库：[查看作者仓库](https://github.com/zuichen123/VibeBoard)

许可证：本次未确认。参考：编码状态到灯光/实体操作的映射。

适配限制：未确认许可证与本项目板型适配；不是本项目现成组件。

建议：仅阅读参考。状态：待用户确认，未下载或复用。

## HachimoDock

仓库：[查看作者仓库](https://github.com/YizhengWw/HachimoDock)

许可证：自定义非商业源码可见许可。参考：桌面与编码会话状态交接。

适配限制：不是标准开源许可；当前许可对开发独立软件/硬件产品要求另行授权，不能直接拿来做小桶。ESP32-P4也不同。

建议：仅研究产品思路。状态：待用户确认；采用前还需权利人许可，未下载或复用。

许可原文：[LICENSE](https://github.com/YizhengWw/HachimoDock/blob/main/LICENSE)。
