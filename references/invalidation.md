# 版本失效传播

每次变更记录原因、字段、旧/新版本和影响范围。默认只预览：`python scripts/check_workflow.py invalidate PROJECT_ROOT --question qN --change TYPE`；实际应用显式加 --apply，并追加事件。此命令不代表授权修改用户决策。

| TYPE | 当前问重置 |
|---|---|
| caliber / data | units 的 D1/D2/预处理计划确认、plan_review、参数/图表/执行合同、coded、code/result/caliber_review、frozen |
| algorithm | units D2、plan_review、参数/图表/执行合同、coded 与结果门禁/frozen |
| parameters | 参数/执行合同、coded、code/result/caliber_review、frozen；若改变图需求追加 charts 变更 |
| charts | 图表/执行合同、coded、code/result/caliber_review、frozen |
| manuscript | manuscript_audit；只使以正文为依据的获奖评估失效，不撤销模型冻结 |

项目内 dependencies 表示真实输入依赖，沿其传递闭包撤销相关下游 plan/执行与结果门禁/冻结；需重新讨论受影响算法，caliber/data 还需重新确认口径。保留旧材料作历史，不把历史报告引用当当前有效证据。

任何建模/正式图表变更撤销 modeling_complete、handoff_ready、integration_review、final_figures_audited、award_assessment，生成新快照并重新验收受影响范围。纯文件移位但内容/引用都未变可记录迁移，不伪称实质模型变更。

从快照检测到未经记录的文件漂移时拒绝使用旧 PASS，先查明原因。确认字段、报告身份及哈希一致是条件之一，不是数学正确性证明。
