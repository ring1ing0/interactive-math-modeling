# 自动独立评审

自动指当前已授权工作中条件满足即派发和收集评审，不是后台计划任务。调用宿主的子代理/独立会话能力，输入原题、确认记录、当前快照和对应评委规范；不传作者预期答案、评分或私有推理。

作者不能兼任自身输出的独立验收者。默认一个独立评委按数学/数据/题意视角审查，关键领域假设或实质分歧再加针对性评委。有获授权的异构模型可选用；没有独立能力只输出 self_check，独立门禁保持 BLOCKED。可配置 reviewer 模型与修复预算，不硬绑定厂商/API。简单索引和格式整理可下放轻量模型；模型方向、推导、最优性和争议裁决留主代理与具备能力的评委。

## 只读与复现

评委不改模型、原始数据或冻结结果，报告写 reviews/。可在隔离工作目录运行已确认命令，保证输出不覆盖被审对象。优先独立约束复算、小规模手算、边界/反例，不用同一求解器重复运行代替独立数学检查。

## 报告与聚合

JSON 格式见 [review-report.json](../templates/review-report.json)。必需检查项：

每个阶段报告引用自身不可变的输入快照；qN 的 review_snapshot_ids 保留这些身份。验收结束后把阶段报告和必需证据加入最终冻结清单；不是在审查报告中哈希该报告自己。主张的全部义务与支持证据不得为空。只有检查范围和证据未改变时才能复用旧审查。

| stage | 必需 ID |
|---|---|
| plan_review | task_coverage、model_validity、validation_design |
| code_review | execution、reproduction、constraints |
| result_review | task_coverage、evidence_sufficiency、counterexamples，以及当前主张的全部 obligations |
| caliber_review | numeric_units、claim_strength、handoff_consistency |
| integration_review | cross_question、coverage、reproduction |

按題型增加 check，不适用项也要明确理由和证据；不得删除固定检查以规避门禁。证据文件使用项目相对路径及 SHA256，数值定位/重算方法和容差写入 detail。关键公式/最优性判断需说明推导条件，而非一句 PASS。

PASS=必需项有足够证据且无开放 critical/major；FAIL=反例、冲突、约束违反或复现失败；BLOCKED=必需证据/数据/能力不足。非核心局限可以明确限制主张后交付，但不能将未验证的原强主张保留。记录审查范围和未查内容。

主代理根据证据处理分歧；不能以平均分、投票或“用户选了模型”覆盖硬错误。脚本仅检查报告结构、引用、哈希和状态，领域正确性依赖真实验算与语义审查。

默认首审后最多两轮定向修复/复审（项目可调）。复用未变化证据，仅重新验收变动范围。预算耗尽交出未解决问题和状态；需要改变 D1/D2 决定时停在人决策点。流程完成、证据充分和获奖潜力是三个不同判断。
