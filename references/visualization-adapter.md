# 内置轻量图表规则

趋势用折线；比较/排名用条形或点图；分布用直方/箱线/小提琴并显示小样本点；关系用散点；相关矩阵用热图。避免装饰图和未经说明的3D/双轴。标单位、样本量、缺失/排除规则及必要不确定性。

每张图记录 purpose、claim_id、source_data/版本/哈希、transformations、units、missing/outlier_policy、statistical_summary、颜色语义、输出/验收。诊断图输出 questions/qN/figures-diagnostic/，不是正式图证据；全题冻结后需要入稿的图必须从冻结数据重绘，记录可复现脚本。

先确定参数/验证范围再确认图表；新增正式图或论证目的变化回图表决策点。外部图表资源见 [adapters/viz-adapter.md](adapters/viz-adapter.md)。
