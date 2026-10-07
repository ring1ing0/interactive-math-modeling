# 可选教材与算法资源

内置 [algorithm-selection.md](../algorithm-selection.md) 和 [algorithm-catalog.yaml](../algorithm-catalog.yaml) 是默认推荐入口；外部算法教材不是硬依赖。

通过项目 `.interactive-mm/resource-overrides.json` 的 algorithm_textbooks 指定资源根目录；项目未配置时可读安装目录的宿主专用 `resources.local.json`。按 [resource-registry.yaml](../resource-registry.yaml) 检查文件存在。只读 routing/index 及当前章节小节，不启动另一套总控。本机路径配置不发布。

已配置两本旧教材时，b2可帮助竞赛题型对齐，b1可补独有主题和代码解释；这不是永久固定优先级。按当前问题覆盖与质量选择来源。AHP覆盖有限，PSO/蚁群/XGBoost/LSTM等可能库外，应查官方资料或核验论文，不能因书中缺少而排除适合本题的方法。

OCR公式/代码需用推导、标准算例、官方文档或实际运行复核；来源记录书名、章/页/位置、OCR复核状态，不能将教材算例作为本题结果。外部资料缺失时回退内置索引与官方资料，仅暂停无法完成的相关读取。

推荐依据仍为题目结构、当前数据、假设和公平验证；教材出处只提供方法解释。资源原文/习题/第三方代码不随 skill 发布，只提交原创规则与引用。
