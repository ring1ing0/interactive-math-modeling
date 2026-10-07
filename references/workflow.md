# 工作流

状态与合法推进见 [state-contract.md](state-contract.md)，用户决策见 [interaction-protocol.md](interaction-protocol.md)。

## 全局 S0–S5

S0 确定项目根、题面与附件，创建状态/事件/证据/技术文档。S1 登记题面原文位置、要求 ID、顶层问题和 units，记录歧义与依赖。S2 形成目标、共享接口、方法族与验证总纲并确认。S3 约束账本完成后停止。S4 共同数据审计；保留原始数据，区分“计划”与“实际处理”。S5 文献筛选按需；需要时 L1 用户确认，不需要时记录 NOT_REQUIRED、理由及适用范围。

## 每个顶层问题

1. 创建题目要求覆盖表及 visual-contract，引用全局风格。确认上游冻结版本、单位/变换、误差状态和适用范围。
2. 逐 unit 分析目标、输出、信息时点、数据子集、局部约束、必要预处理。在 D1 确认口径。
3. 读 [algorithm-selection.md](algorithm-selection.md)，只取当前任务的候选。解释基线、适配、证据、验证、计算成本和风险，在 D2 确认；轻量对照 D1，冲突回退。不在此阶段编码。
4. 全部 units 确认后自动派发 plan-reviewer，PASS 后在 Qn-PARAM-D1 确认参数及验证/灵敏度。再单独讨论图表并在 Qn-CHART-D1 确认；无必要图表也要记录理由。
5. Qn-CODE-CONTRACT 确认唯一执行入口、允许的输入/输出目录、依赖、资源预算、验证资产和失败处置。确认包含约定范围的运行/检查授权，不再额外确认相同命令。
6. 编码并真实运行；按计划检查硬约束、基线、误差及灵敏度。独立代码审查在隔离目录复现，不覆盖被审输出。
7. 方案审查时已有独立的计划阶段快照；运行后建立 candidate snapshot，登记阶段 snapshot_id 及项目内文件 SHA256，覆盖题面/数据/模型/参数/代码/结果/必需图表和当前 claim-contract。评委报告放独立 review 目录，报告不把自己纳入其被审快照。review_snapshot_ids 登记各阶段身份，未变方案证据可以复用，不必重新生成方案。
8. 自动结果审查与逐问口径审查。报告引用 candidate snapshot，补证据/修复后创建新版本，旧报告失效。形成 claim-contract 及六项聊天摘要。
9. 所有必需门禁通过后形成最终逐问冻结清单，包含模型/结果、claim-contract、四个报告及其必需证据文件，清单不包含自身。保留各阶段快照身份，将最终 qN snapshot_id/snapshot_manifest 与这些报告关联。核查四个报告及冻结清单，登记输出接口再进入下一问。

## 全题收尾

全部 qN 冻结后 F1 统一确认正式图表；生成独立全题快照与 project_snapshot_id，登记正式图表、共享约束、每问版本及交接材料。执行 integration-reviewer 与全量复现；交接包就绪才 modeling_complete。

之后自动 final-judge 给粗略获奖潜力，不等待正文才开始建模潜力评估。若缺少评奖依据给宽范围/低信心或 INSUFFICIENT_EVIDENCE，不把报告分数写回模型正确性状态。

外部正文回来后 W1 审计实际文字版本。若发现源结果错误，返回受影响建模节点；只改文字错误则只复审文字及以正文为依据的获奖评估。
