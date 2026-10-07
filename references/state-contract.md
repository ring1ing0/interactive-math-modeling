# 状态契约 0.2

项目状态用 JSON，路径相对 PROJECT_ROOT；模板值不是完成证据。初始化复制 [state.json](../templates/state.json)，每次决定/审查/修正追加 events.jsonl。布尔值只表示当前版本，不得继承旧 PASS。

## 主要字段

- schema_version: "0.2"；current_phase/current_question/current_unit/stop_point/next_action 表示恢复位置。
- literature_status: PENDING/CONFIRMED/NOT_REQUIRED；后者必须有 literature_reason。
- modeling_complete、handoff_ready 与稿件是否存在相互独立。
- manuscript_audit: NOT_PROVIDED/PENDING/PASS/FAIL/BLOCKED；只有提供实际正文和版本后可 PASS。
- integration_review、integration_review_ref、project_snapshot_id、project_snapshot_manifest 绑定全题整合；final_figures_audited 表示正式图表已验收，无图时有明确理由。
- final_evidence_refs 登记正式图表审计和交接证据的项目内 path/sha256，必须包含于全题快照；无图时以“无需图表”的经审查理由文件作图表证据。
- award_assessment: PENDING/COMPLETE/INSUFFICIENT_EVIDENCE；award_assessment_ref 指向评估报告。COMPLETE 表示评估动作完成，不表示必然获奖，也不提升任何验证状态。
- questions[qN]：requirement_ids、dependencies、snapshot_id、snapshot_manifest、claim_contract_ref、units、review_refs、四个门禁、确认字段和 frozen。
- review_snapshot_ids 分别记录方案、代码、结果和口径审查各自的阶段快照身份，避免要求运行前的方案审查引用运行后的快照。没有该映射的简单项目可统一使用 qN snapshot_id；显式映射不能留空。
- units[uK]：caliber_decided（D1）、decided（D2）、preprocessing_plan_confirmed；preprocessing_executed 单独记录真实处理状态，不用计划状态替代执行。

## 门禁

plan_review/code_review/result_review/caliber_review/integration_review 使用 PENDING/PASS/FAIL/BLOCKED。PASS 必须有匹配阶段、当前 snapshot_id、独立 reviewer_id、检查范围、证据引用与哈希的 JSON 报告；重大未关闭 finding 不能通过。高级模型检查在方案报告中以触发/不触发及理由表示，不单独制造第二个完成门槛。

逐问冻结要求：units 的 D1/D2 全部确认，执行合同和实际执行有效，四个门禁 PASS、报告有效、快照无漂移，全部题目要求有主张覆盖。最终逐问冻结清单必须包含 claim-contract、阶段报告及各报告必需证据文件的哈希；清单不包含自身，不产生递归哈希。条件结论允许冻结为有条件交付，但必须声明 conditions/limitations，验证义务仍须满足；UNSUPPORTED 不能伪装成核心答案。

所有逐问冻结＋全题快照有效＋整合 PASS＋正式图表审计通过＋handoff_ready 才 modeling_complete。最终代码/结果无法运行时可报告阶段性成果，不得完成。

## 文件契约

- snapshot.json：snapshot_id、files[{path,sha256}]。冻结后改任一受审文件即漂移，必须新版本和复审。全题快照同格式，但身份为 project_snapshot_id。
- claim-contract.json：question/snapshot_id/claims；字段见 [claim-contract.json](../templates/claim-contract.json)。其中 snapshot_id 绑定 result_review 与 caliber_review 共同审查的候选快照，两者身份必须一致；最终 qN 汇总冻结可以有独立身份。每条义务对应报告 check ID，主张的 evidence_refs 精确指向受审材料。
- review-report.json：字段见 [review-report.json](../templates/review-report.json)。每项 required PASS 有证据，stage 使用对应门禁名；integration 使用 question=global 和 project_snapshot_id。
- award-assessment.json：见 [award-assessment.json](../templates/award-assessment.json)，绑定 project_snapshot_id 与 basis。正文未提供时 manuscript_reviewed=false。

## 合法推进和迁移

S4 需要全局约束完成及 S3 返回停止点；qN 需要全题底座有效和文献 CONFIRMED 或带理由 NOT_REQUIRED。unit 算法讨论必须 D1 后；方案审查必须全部 D2 后；编码必须方案 PASS 和参数/图表/执行合同确认后。

变更时遵守 [invalidation.md](invalidation.md)，撤销有关用户确认标志和下游冻结，不能只把一个 review 字段改成 PENDING。脚本 invalidate 默认预览，--apply 只应用有记录的已授权变更；日志记录原因、影响范围和新版本。

从旧0.1恢复时先核查已有材料，将 preprocessing_done 拆为计划/执行记录。paper_complete 仅作为历史字段，不能映射成 modeling_complete、handoff_ready 或独立审查 PASS。没有新门禁证据的旧冻结结果记待验收；不重跑不相关已验证内容。
