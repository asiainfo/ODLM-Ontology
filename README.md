![ontology build](https://img.shields.io/badge/status-draft-blue)

## ODLM：数据管治本体（Ontology for Data Lake Management）

### 简介
数据管治本体（Ontology for Data Lake Management，ODLM）是基于本体论构建的标准化语义模型，为数据湖提供端到端的数据治理框架。它系统化定义数据源、数据集、加工任务、指标、血缘关系与权限策略等核心要素，构建可机读、可推理的数据本体地图。ODLM不仅实现元数据的统一管理，更使AI能深度理解数据资产的上下文与关联。通过融合底层加工血缘与业务语义关系，可自动发现对象间的隐性关联，揭示跨域数据逻辑，支撑智能数据检索、影响分析与合规管控，释放数据湖的深层价值


### 版本
- 命名空间（base IRI）：`http://asiainfo.com/odlm#`
- 本体 IRI：`http://asiainfo.com/odlm`
- 当前版本：1.0（与 `odlm.ttl` 及文档保持一致）

### 制品
- 主本体（Turtle）：`odlm.ttl`
- 示例实例（Turtle）：`example.ttl`
- 词汇文档：`ODLM_Vocabulary.md`（核心类、对象/数据属性与枚举）
- 最佳实践与快速上手：`ODLM_BestPractice.md`（端到端环境与用法）

### 变体
当前提供一份完整本体文件（`odlm.ttl`）与一份示例实例文件（`example.ttl`）。若需要 base/simple/minimal 等发行风味，可在后续构建流程中派生生成。

### 快速开始
1) 阅读 `ODLM_Vocabulary.md` 理解核心概念与关系。
2) 按 `ODLM_BestPractice.md` 搭建环境（Neo4j、MySQL、Milvus、Python），并运行 `code/` 下的初始化脚本。
3) 参考 `example.ttl` 学习如何实例化数据源、表/字段、任务血缘与对象映射。

### 文件/目录总览（docs/）
- `odlm.ttl`：ODLM 核心本体（Turtle）。定义了 `odlm:Table`、`odlm:Field`、`odlm:Task` 等类，以及 `odlm:used`、`odlm:wasGeneratedBy`、`odlm:belongsToDataSource`、`odlm:dependsOn`、`odlm:references` 等关键关系，并包含对象建模（`odlm:Object`、`odlm:ObjectField`）。作为语义权威来源。
- `example.ttl`：最小可用的实例图，演示一个 MySQL 数据源、多张表/字段和任务到表的血缘关系。适合在加载真实数据前用于查询和工具链验证。
- `ODLM_Vocabulary.md`：人类可读的词汇参考，汇总主要类、对象/数据属性与命名个体/枚举（如 `UpdateCycle`、`DataLayer`、`ServiceStatus`），便于与 DCAT/PROV/DC Terms 对齐。
- `ODLM_BestPractice.md`：实践指南，含 Neo4j/MySQL/Milvus 的 Docker Compose 启动，Poetry Python 环境，以及初始化与验证脚本（含 Agent 演示）。
- `images/`：最佳实践文档配图（环境、控制台、示例 Cypher 输出等）。
- `code/`：可运行脚本与最小应用代码：
  - `graph_init.py`：在 Neo4j 中创建 ODLM 概念/类/属性结构及必要的标签/索引。
  - `mysql_init.py`：创建演示用 MySQL 表结构与样例数据。
  - `milvus_init.py`：初始化 Milvus（或兼容向量库）以支持标签/别名的语义检索。
  - `example.py`：写入示例实例（表/字段/任务/对象绑定），用于血缘演示。
  - `auto_agent.py` 与 `tools.py`：最小化 Agent 验证与工具封装（Neo4j/MySQL 查询、名称消歧）。
  - `config/`：示例配置（`config.development.example.yaml`），用于连接本地服务。

### 如何配合使用
- 先按 `ODLM_BestPractice.md` 启动各项服务并就绪 Python 环境。
- 加载本体：将 `odlm.ttl` 导入三元组库，或使用 `graph_init.py` 在 Neo4j 中程序化创建结构。
- 参考或加载 `example.ttl` 实例；或运行 `example.py` 程序化创建等价实例。
- 基于本体中定义的关系（`used`、`generated/wasGeneratedBy`、`dependsOn`、`references`）编写 Cypher 进行血缘探索与验证。

### 标准对齐
ODLM 对齐并复用：PROV‑O（`prov:Entity`/`prov:Activity`、`used`、`wasGeneratedBy`）、DCAT（数据集/服务）与 Dublin Core（通用元数据）。详见 `ODLM_Vocabulary.md`。

### 参与贡献
欢迎通过 Issue/PR 提出新术语、报告问题或完善文档与本体模型。

### 许可协议
请在仓库根目录添加 `LICENSE` 文件并在此声明协议（例如：本体文本使用 CC BY 4.0；示例代码使用 Apache‑2.0）。


