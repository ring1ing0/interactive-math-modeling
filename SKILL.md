---
name: interactive-math-modeling
description: 【仅限显式调用】交互式数学建模与写作口径核对：建立全题底座，逐小问确认口径与算法，整问实现并自动独立验收、交接；全题冻结后评估获奖潜力。论文正文起草、润色、排版和编译交给外部写作者。
metadata:
  version: "0.2.0"
---

# 交互式数学建模与口径核对

目标：形成题意忠实、可计算、可核验的模型，并明确结果能支持哪些文字主张。保留逐问互动；当前轮推进一个节点，用户决策点停下。一个节点可以包含自动检查、已授权运行与定向程序修复，不要求每次工具调用都停一轮。

## 职责和入口

- 仅显式调用或用户明确启动本流程时使用；不同时启动第二个数学建模总控。
- 负责题意形式化、假设/约束、方法比较、推导、代码/运行、结果与图表证据、逐问结论边界及外部文字事实核对。
- 技术记录、公式和结果解释属于建模；摘要/章节正文起草、整段改写、润色、排版和编译交给外部写作者，不由本 skill 完成。
- 初始化 `技术文档.md`、`.interactive-mm/state.json`、`events.jsonl`、`evidence-index.json`。先读 [状态契约](references/state-contract.md)。恢复只读状态→技术文档当前状态→当前节点材料；不得用对话印象替代状态和证据。
- 按当前阶段读取 [工作流](references/workflow.md)、[交互协议](references/interaction-protocol.md)。外部资源按需读取 [依赖配置](references/resource-registry.yaml)，不可默认预读所有资源。

## 全题底座

S0–S2 盘点题面/附件、顶层问题和内部 units、依赖和共享接口、方法族路线及验证总纲；S2 等待确认。S3 区分硬约束、软约束、派生边界、研究假设和交付约束，完成后停在 S3-DONE。S4 审计数据字典、单位、时序与质量；只执行无争议的共同处理。S5 文献按需，候选可核验，在 L1 确认；不需要文献时记录 NOT_REQUIRED 及理由。

## 逐问闭环

1. 初始化 qN，登记题目要求和上游接口；视觉合同只确定共享风格与单位，不提前确定所有图。
2. 每个 unit：目标/输出/数据子集/约束/必要预处理方向→D1 用户口径确认→算法及基线/验证讨论→D2 用户算法确认。口径未确认不展开算法；不提前处理后续 unit、不在 unit 讨论期编码。
3. D2 后轻量核对算法是否仍满足 D1；有冲突回到相应决策点。全部 units 确认后自动 [方案审查](references/reviewers/plan-reviewer.md)。
4. 方案通过后，先确认参数与验证/灵敏度范围，再专门讨论并确认图表，最后确认代码执行合同。无需扰动或图表时写明理由，不凑实验或图数。
5. 在合同范围内编码/运行，执行 [独立代码审查](references/reviewers/code-reviewer.md)。生成候选快照后自动 [结果验收](references/reviewers/result-reviewer.md) 和 [逐问口径核对](references/writing-caliber.md)，形成 claim-contract，全部必需门禁通过才冻结并进入下一问。
6. 自动评审按 [评审协议](references/review-protocol.md) 派发；作者和评委分离。缺少独立委派能力可完成自检，但不得宣称独立验收通过。评委分歧以证据裁决，不以多数票消除核心错误。

## 算法推荐

读 [选择逻辑](references/algorithm-selection.md) 和当前题型对应的 [候选索引](references/algorithm-catalog.yaml)。先识别任务、信息可用性、数学结构、数据和计算预算，排除不满足条件的方案，再比较简单强基线。候选标记 recommended/feasible_comparison/conditional/rejected，注明 PROBLEM/DATA/LITERATURE/ASSUMPTION/BENCHMARK 依据；未运行的增益只标待验证。

内置索引是可扩展的参考而非封闭白名单；外部教材是可选解释来源，不能证明本题适用性。复杂模型和组合模型按证据升级，不强制候选数量或创新类型；组合方案需明确接口和消融。教材接入时读 [算法资源适配器](references/adapters/algorithm-adapter.md)。

## 全题冻结与获奖评估

全部 qN 冻结后，F1 统一规划/确认正式图表；从冻结数据成图并核查真实性、单位、不确定性和来源。执行 [整合审查](references/reviewers/integration-reviewer.md)，完成跨问一致性、全量复现和写作证据交接，才报告 modeling_complete。

然后自动派发 [全题评委与获奖潜力评估](references/reviewers/final-judge.md)：依据竞赛、年份、组别、官方标准、题面和冻结产物，给出粗略获奖潜力、证据允许时的可能档位范围、信心等级、扣分项及优先改进。不以评委分数替代正确性门禁；无校准数据不编造概率。不提供正文也应评估建模潜力，明确表达/格式等未评；缺少关键比较依据时不强行指定奖项。

外部写作者返回正文后走 W1 口径核对，定位数值/单位/方法/主张冲突并给局部修正方向，不接管正文。未提供正文记 NOT_PROVIDED，不阻挡建模完成，不声称论文已经核对。写作与获奖评估更新不能静默改动已冻结模型。

## 状态、停止和完成

- 用户决策点：S2、S3-DONE、L1（需要文献时）、Qn-INIT-D1、Qn.uK-D1、Qn.uK-D2、Qn-PARAM-D1、Qn-CHART-D1、Qn-CODE-CONTRACT、F1（需要新图/取舍时）。Qn-PLAN-DONE 是自动检查节点，W1 是提供文稿后触发的审计入口，不再作为没有决定事项的固定暂停。
- 沉默/模糊回应不算确认；用户明确委托的范围计入决策记录，后续不重复索要同一授权。改变口径/模型方向仍需对应确认。
- 输入/口径/模型/参数/图表变化按 [失效规则](references/invalidation.md) 撤销受影响确认、审查及下游冻结；文稿措辞变化仅使相关文字审计失效。
- 四个逐问门禁 PASS、证据快照有效、主张义务满足、全部问题冻结、整合审查和正式图表审计通过、交接准备完毕，才可建模完成。paper_complete 不再作为完成条件。获奖评估仅是参考判断。
- 用 `python scripts/check_workflow.py check-project PROJECT_ROOT` 检查记录/哈希/覆盖/门禁，用 `check-skill SKILL_ROOT` 检查包结构。脚本验证记录一致性，不能证明题意或数学正确。
