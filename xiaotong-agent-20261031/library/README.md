# 小桶知识库使用说明

名称：vibe coding桌面伙伴。昵称：小桶。版本：2026-10-31 v2。

在线入口：https://shuyanxiao50.github.io/xiaotong-agent-20261031/library/

先用knowledge-handbook.pdf、knowledge.txt或docs中的7篇分题文档创建产品知识库。平台支持的文件类型、大小与切片方式需以实际界面验证；先上传一份并检查检索正文，再批量上传。不要把产品参考中他人的功能当作小桶已经实现。

xiaotong-knowledge.xlsx为总表：2400条状态少样本、120条常见编码问题、23项资料参考、8个代码候选、64条未运行验收题与100个场景索引。2400条主样例的口径是100场景×6种说法×4种运行条件，共600种独立输入；新增120个不同编码问题另计。它们是自编合成设计资料，不是真实用户数据、训练结果或通过率。

examples.csv与examples.jsonl是2400条的交换格式；faq.csv、faq.jsonl与faq.md对应120条编码问题。表格能否直接作为平台知识源需小批验证；先挑少量有代表性的正反例，不把全部内容塞进角色框。

reference-review.pdf、references.md、sources.md和codes.md用于团队研究与选型，建议放入独立资料库。代码文件入口已列供查看，全部尚未采用。用户选定后仍需满足许可和平台约束，再决定是否集成。

在线网页提供可直接阅读的正文、FAQ筛选与文件下载，不需要登录。平台URL抓取应使用knowledge.md等正文地址并核对预览，网页可打开不等于平台已成功入库。

当前交付没有修改线上Agent或挂载插件，没有接通新的编码事件、语音回传、审批、视觉投放或设备动作。硬件实际状态仍以队友与硬件聊天的实测记录为准。


可直接编辑的Word：knowledge-handbook.docx、reference-review.docx；Excel：xiaotong-knowledge.xlsx。动态网页支持搜索、分类筛选和下载。
