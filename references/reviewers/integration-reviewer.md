# 全题整合审查

全部 qN 冻结、全题快照形成后自动执行，不只把此文件列作备用。按 [评审协议](../review-protocol.md) 输出 integration_review，question=global，snapshot_id=project_snapshot_id。

- cross_question：共享硬约束/假设版本一致；局部约束不错误扩散；上下游字段/单位/变换/误差及范围一致；使用当前上游版本并考虑误差传播。
- coverage：全题要求与逐问主张齐全，claim-contract、结果表、正式图表和交接材料一致，没有孤立/陈旧结果；同一变量定义和展示精度一致。
- reproduction：唯一全量入口或按明确依赖顺序的运行计划可复现；正式图表由冻结结果数据生成，未隐藏缺失/异常/不确定性；全题快照无漂移。

正文未提供时只检查写作证据交接，稿件状态 NOT_PROVIDED。实际正文回来后另行口径核对。整合 PASS 不等于获奖；之后派发 [final-judge.md](final-judge.md)。
