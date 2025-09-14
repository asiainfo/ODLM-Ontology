## ODLM 本体词汇表（Ontology Vocabulary）

- **版本**: 1.0
- **命名空间（base IRI）**: `http://asiainfo.com/odlm#`
- **本体 IRI**: `http://asiainfo.com/odlm`
- **创建日期**: 2025-08-28
- **简述**: 定义数据生命周期管理（Data Lifecycle Management）的核心类、对象属性、数据属性与关键枚举，用于描述数据源、数据集、任务、指标、维度、标准、权限与服务等要素及其血缘关系与管理信息。

### 前缀（Prefixes）

- `rdf`: `http://www.w3.org/1999/02/22-rdf-syntax-ns#`
- `rdfs`: `http://www.w3.org/2000/01/rdf-schema#`
- `owl`: `http://www.w3.org/2002/07/owl#`
- `xsd`: `http://www.w3.org/2001/XMLSchema#`
- `dcat`: `http://www.w3.org/ns/dcat#`
- `prov`: `http://www.w3.org/ns/prov#`
- `dcterms`: `http://purl.org/dc/terms/`
- `odlm`: `http://asiainfo.com/odlm#`
- `ex`: `http://asiainfo.com/odlm-instances#`（示例实例）

---

## 目录
- [ODLM 本体词汇表（Ontology Vocabulary）](#odlm-本体词汇表ontology-vocabulary)
  - [前缀（Prefixes）](#前缀prefixes)
- [目录](#目录)
- [概览与适用范围](#概览与适用范围)
- [类（Classes）](#类classes)
  - [核心与资源](#核心与资源)
  - [基础设施与组织](#基础设施与组织)
  - [对象建模（领域对象）](#对象建模领域对象)
  - [数据源子类](#数据源子类)
  - [数据集与表/字段](#数据集与表字段)
  - [指标与维度](#指标与维度)
  - [服务](#服务)
  - [枚举类（词表）](#枚举类词表)
- [对象属性（Object Properties）](#对象属性object-properties)
- [数据属性（Datatype Properties）](#数据属性datatype-properties)
- [命名个体与枚举（Named Individuals \& Enums）](#命名个体与枚举named-individuals--enums)
  - [请求方法（`odlm:RequestMethod`）](#请求方法odlmrequestmethod)
  - [调用类型（`odlm:CallType`）](#调用类型odlmcalltype)
  - [服务状态（`odlm:ServiceStatus`）](#服务状态odlmservicestatus)
  - [开放等级（`odlm:AccessLevel`）](#开放等级odlmaccesslevel)
  - [Content-Type（`odlm:ContentType`）](#content-typeodlmcontenttype)
- [建模约束与推理规则（Axioms）](#建模约束与推理规则axioms)
- [附录：示例实例说明（ex:）](#附录示例实例说明ex)
- [修订记录](#修订记录)

---

## 概览与适用范围
- **目标**: 提供统一的数据生命周期语义模型，覆盖数据源、表/字段、任务、指标、维度、标准与服务；支持血缘、治理、权限与发布状态管理。
- **对齐标准**: 复用 `PROV-O`（`prov:Entity`/`prov:Activity`）、`DCAT`（数据集与服务）、`Dublin Core`（通用元数据）。

---

## 类（Classes）

下表列出主要类，包含继承关系与中文标签。未显式给出描述的类省略描述列。

### 核心与资源

| 术语 | IRI 后缀 | 继承自 | 标签 | 描述 |
|---|---|---|---|---|
| `odlm:Entity` | Entity | `prov:Entity` | 实体 | 与 PROV-O 对齐的通用实体上位类 |
| `odlm:Activity` | Activity | `prov:Activity` | 活动/任务 | 与 PROV-O 对齐的活动/任务上位类 |
| `odlm:Resource` | Resource | `odlm:Entity`, `dcterms:Resource` | 资源 | 基于 `dcterms:Resource` 的资源性实体上位类，用于统一管理与引用 |
| `odlm:DataSource` | DataSource | `odlm:Resource`, `dcat:Catalog` | 数据源 | 原始数据的来源系统或存储位置 |
| `odlm:Dataset` | Dataset | `dcat:Dataset`, `odlm:Resource` | 数据集 | 对齐 DCAT 的数据集实体，用于承载数据内容与元数据 |
| `odlm:Service` | Service | `dcat:DataService`, `odlm:Resource` | 服务 | 对齐 DCAT 的数据服务，用于对外暴露数据访问能力 |
| `odlm:Task` | Task | `odlm:Activity`, `odlm:Resource` | 任务 | 数据操作流程如 ETL、血缘解析等 |
| `odlm:Dimension` | Dimension | `odlm:Resource` | 维度 | 用于分析指标的上下文属性 |
| `odlm:Metric` | Metric | `odlm:Resource` | 指标 | 可量化的业务度量标准 |
| `odlm:Standard` | Standard | `odlm:Entity` | 标准 | 系统中的标准体系，比如字段标准等 |
| `odlm:Rule` | Rule | `odlm:Entity` | 规则 | 在系统中对不同实体起到特定规范作用的规则 |
| `odlm:ruleTemplate` | ruleTemplate | `odlm:Entity` | 规则模板 | 一个规则模板可包含多个规则 |
| `odlm:Log` | Log | `odlm:Entity` | 日志 | 系统流转、执行过程中产生的日志 |

### 基础设施与组织

| 术语 | IRI 后缀 | 继承自 | 标签 | 描述 |
|---|---|---|---|---|
| `odlm:Engine` | Engine | `prov:SoftwareAgent`, `odlm:Resource` | 引擎 | 数据处理执行引擎 |
| `odlm:Cluster` | Cluster | `prov:Collection`, `odlm:Resource` | 集群 | 资源集合的计算环境 |
| `odlm:Organization` | Organization | `prov:Organization` | 组织 | 与 PROV-O 对齐的组织实体上位类 |
| `odlm:Department` | Department | `odlm:Organization` | 部门 | 组织内的部门 |
| `odlm:Team` | Team | `odlm:Organization` | 团队 | 协作单元 |
| `odlm:User` | User | `prov:Person` | 用户 | 与 PROV-O 对齐的人员实体，用于标识系统用户 |
| `odlm:Role` | Role | `prov:Role` | 角色 | 与 PROV-O 对齐的角色实体，用于权限继承 |
| `odlm:Permission` | Permission | `odlm:Entity` | 权限 | 与角色/用户关联的权限实体（见 `hasPermission`/`hasDirectPermission`） |
| `odlm:Workspace` | Workspace | `odlm:Organization` | 工作空间 | 组织类型，用于承载表/任务等实体的工作域（见 `tableBelongsToWorkspace`/`taskBelongsToWorkspace`） |

### 对象建模（领域对象）

| 术语 | IRI 后缀 | 继承自 | 标签 | 描述 |
|---|---|---|---|---|
| `odlm:Object` | Object | `odlm:Resource` | 本体对象 | 用户创建的本体对象，作为某物理表的语义映射 |
| `odlm:ObjectField` | ObjectField | `odlm:Resource` | 本体对象属性 | 用户创建的本体对象属性/字段，对应某物理表中的字段 |

### 数据源子类

| 术语 | IRI 后缀 | 继承自 | 标签 | 描述 |
|---|---|---|---|---|
| `odlm:KerberosSupport` | KerberosSupport |  | 支持 Kerberos 的数据源 | 	表明数据源支持Kerberos |
| `odlm:MySQL` | MySQL | `odlm:DataSource` | MySQL 数据源 | 基于 MySQL 的关系型数据源 |
| `odlm:Hive` | Hive | `odlm:DataSource`, `odlm:KerberosSupport` | Hive 数据源 | Hadoop/Hive 数据仓库数据源 |
| `odlm:HBase` | HBase | `odlm:DataSource`, `odlm:KerberosSupport` | HBase 数据源 | 分布式列式存储 |
| `odlm:Kafka` | Kafka | `odlm:DataSource`, `odlm:KerberosSupport` | Kafka 数据源 | 消息队列 |
| `odlm:MinIO` | MinIO | `odlm:DataSource` | MinIO 数据源 | 兼容 S3 的对象存储 |

### 数据集与表/字段

| 术语 | IRI 后缀 | 继承自 | 标签 | 描述 |
|---|---|---|---|---|
| `odlm:Schema` | Schema | `odlm:Dataset` | 数据模型 | 逻辑数据模型，包含一组相关的表和字段 |
| `odlm:Table` | Table | `odlm:Dataset` | 表 | 逻辑或物理的数据表 |
| `odlm:tableStandard` | tableStandard | `odlm:Standard` | 表标准 | 表标准实体，一个表标准可以映射多个表 |
| `odlm:HiveTable` | HiveTable | `odlm:Table` | Hive 表 | 存储在 Hive 中的表，拥有属于自己的一些独特属性 |
| `odlm:Field` | Field | `odlm:Resource` | 字段 | 表中的列或字段 |
| `odlm:fieldStandard` | fieldStandard | `odlm:Standard` | 字段标准 | 字段标准实体，一个字段标准可以映射多个字段 |
| `odlm:HiveField` | HiveField | `odlm:Field` | Hive 字段 | Hive 表中的字段 |

### 指标与维度

| 术语 | IRI 后缀 | 继承自 | 标签 | 描述 |
|---|---|---|---|---|
| `odlm:DimensionAttribute` | DimensionAttribute | `odlm:Resource` | 维度属性 | 维度下的一个可分析字段 |
| `odlm:BusinessQualifier` | BusinessQualifier | `odlm:Metric` | 业务限定 | 指标计算规则片段，通过 SQL 逻辑绑定到表与字段 |
| `odlm:AtomicMetric` | AtomicMetric | `odlm:Metric` | 原子指标 | 不可再分的业务度量，基于单表单字段聚合 |
| `odlm:DerivedMetric` | DerivedMetric | `odlm:Metric` | 派生指标 | 基于原子指标、维度与限定条件计算得到的复合度量 |

### 服务

| 术语 | IRI 后缀 | 继承自 | 标签 | 描述 |
|---|---|---|---|---|
| `odlm:APIService` | APIService | `odlm:Service` | API 服务 | 以 REST/SQL 形式对外暴露的查询服务 |

### 枚举类（词表）

| 术语 | IRI 后缀 | 标签 |
|---|---|---|
| `odlm:UpdateCycle` | UpdateCycle | 更新周期枚举 |
| `odlm:DataLayer` | DataLayer | 数据层级枚举 |
| `odlm:ChangeStatus` | ChangeStatus | 变更状态枚举 |
| `odlm:PublishStatus` | PublishStatus | 发布状态枚举 |
| `odlm:DataSourceType` | DataSourceType | 数据来源类型枚举 |
| `odlm:FileFormat` | FileFormat | 文件格式枚举 |
| `odlm:Delimiter` | Delimiter | 分隔符枚举 |
| `odlm:CompressionType` | CompressionType | 压缩类型枚举 |
| `odlm:FieldType` | FieldType | 字段类型枚举 |
| `odlm:SecurityCategory` | SecurityCategory | 安全分类枚举 |
| `odlm:SecurityLevel` | SecurityLevel | 安全分级枚举 |
| `odlm:PartitionKey` | PartitionKey | 分区键枚举 |
| `odlm:TaskPurpose` | TaskPurpose | 任务用途枚举 |
| `odlm:ExecutionMode` | ExecutionMode | 执行模式枚举 |
| `odlm:DevMode` | DevMode | 开发模式枚举 |
| `odlm:ScheduleCycle` | ScheduleCycle | 调度周期枚举 |
| `odlm:MetricCatalog` | MetricCatalog | 指标目录字典 |
| `odlm:Unit` | Unit | 度量单位字典 |
| `odlm:MeasureMethod` | MeasureMethod | 计量方式字典 |
| `odlm:StorageType` | StorageType | 存储类型字典 |
| `odlm:StatPeriod` | StatPeriod | 统计周期字典 |
| `odlm:RequestMethod` | RequestMethod | 请求方法枚举 |
| `odlm:CallType` | CallType | 调用类型枚举 |
| `odlm:ServiceStatus` | ServiceStatus | 服务状态枚举 |
| `odlm:AccessLevel` | AccessLevel | 开放等级枚举 |
| `odlm:ContentType` | ContentType | Content-Type 枚举 |

---

## 对象属性（Object Properties）

以下表格列出主要对象属性，含域（Domain）、值域（Range）、子属性、逆属性与特性。

| 属性 | 标签 | Domain | Range | 子属性于 | 逆属性 | 特性/规则 | 备注 |
|---|---|---|---|---|---|---|---|
| `odlm:followStandard` | 遵循标准 | `odlm:Entity` 等 | `odlm:Standard` |  |  |  | 某一实体遵循某一标准 |
| `odlm:hasRule` | 拥有规则 | `odlm:Entity` | `odlm:Rule` |  |  |  | 实体关联到其生效的规则集合 |
| `odlm:appliesTo` | 应用于 | `odlm:Entity` | `odlm:Entity` |  | `odlm:isAppliedBy` |  | 一个实体的作用目标实体 |
| `odlm:isAppliedBy` | 被应用于 | `odlm:Entity` | `odlm:Entity` |  | `odlm:appliesTo` | 逆属性 | 某实体被另一实体应用（与 appliesTo 互逆） |
| `odlm:belongsToRuleTemp` | 所属规则模板 | `odlm:Rule` | `odlm:ruleTemplate` | `dcterms:isPartOf` |  |  | 规则归属的模板 |
| `odlm:logGeneratedBy` | 由某activity生成的日志 | `odlm:Log` | `odlm:Activity` | `odlm:wasGeneratedBy` |  |  | 将日志与生成它的活动建立关联 |
| `odlm:linkedWith` | 关联关系 | `odlm:Entity` | `odlm:Entity` |  |  | 对称（Symmetric） | 两个实体之间存在非定向的关联关系 |
| `odlm:hasPermission` | 角色拥有权限 | `odlm:Role` | `odlm:Permission` |  |  |  | 指定角色具备的权限集合 |
| `odlm:hasRole` | 一个用户拥有的角色 | `odlm:User` | `odlm:Role` |  |  |  | 指定用户被授予的角色 |
| `odlm:hasDirectPermission` | 用户通过角色继承到的权限 | `odlm:User` | `odlm:Permission` | 链（`hasRole ∘ hasPermission`） |  |  | 通过角色—权限链获得的用户权限 |
| `odlm:delegatedBy` | 团队授权用户 | `odlm:User` | `odlm:Team` |  |  |  | 表示用户由某团队授权委派 |
| `odlm:teamWorkWithSpace` | 团队在空间下工作 | `odlm:Team` | `odlm:Workspace` |  |  |  | 团队所属/工作的工作空间 |
| `odlm:userWorkWithSpace` | 用户在空间下工作 | `odlm:User` | `odlm:Workspace` |  |  |  | 用户所属/工作的工作空间 |
| `odlm:servesDataset` | 服务服务于数据集 | `odlm:Service` | `odlm:Dataset` | `dcat:servesDataset` |  |  | 服务面向的数据集 |
| `odlm:objectOwner` | 对象负责人 | `odlm:Object` | `odlm:User` | `odlm:owner` |  |  | 本体对象的负责人 |
| `odlm:objectCreatedFrom` | 对象创建来源 | `odlm:Object` | `odlm:Table` |  |  |  | 本体对象来源的底层表 |
| `odlm:isObjectFieldOf` | 对象类型字段来自对象 | `odlm:ObjectField` | `odlm:Object` | `dcterms:isPartOf` |  |  | 指明对象字段属于哪个对象 |
| `odlm:isObjectFieldFrom` | 对象类型字段映射的源表字段 | `odlm:ObjectField` | `odlm:Field` |  |  |  | 指明对象字段绑定的底层物理字段 |
| `odlm:generated` | 某个Activity生成了某个Entity | `odlm:Activity` | `odlm:Entity` | `prov:generated` |  |  | 活动的输出实体 |
| `odlm:wasGeneratedBy` | Entity由某个Activity生成 | `odlm:Entity` | `odlm:Activity` | `prov:wasGeneratedBy` |  |  | 实体的生成来源活动 |
| `odlm:used` | 某个Activity使用了某些Entity | `odlm:Activity` | `odlm:Entity` | `prov:used` |  |  | 活动的输入实体 |
| `odlm:containsTable` | 包含表 | `odlm:Schema` | `odlm:Table` | `dcterms:hasPart` | `odlm:belongsToSchema` |  | 数据模型包含的表 |
| `odlm:belongsToTable` | 所属表 | `odlm:Field` | `odlm:Table` | `dcterms:isPartOf` | `odlm:hasField` |  | 字段所属的表 |
| `odlm:hasField` | 包含字段 | `odlm:Table` | `odlm:Field` | `dcterms:hasPart` | `odlm:belongsToTable` |  | 表包含的字段集合 |
| `odlm:belongsToSchema` | 所属数据模型 | `odlm:Table` | `odlm:Schema` | `dcterms:isPartOf` | `odlm:containsTable` |  | 表所属的数据模型 |
| `odlm:relatedSchema` | 关联数据模型 | `odlm:Schema` | `odlm:Schema` |  |  | 链（`containsTable ∘ dependsOn ∘ belongsToSchema`） | 基于表依赖推导的数据模型间关联（对称） |
| `odlm:tableFollowStandard` | 表遵循某一标准 | `odlm:Table` | `odlm:tableStandard` | `odlm:followStandard` |  |  | 表遵循的表标准 |
| `odlm:belongsToDataSource` | 所属数据源 | `odlm:Table` | `odlm:DataSource` |  |  |  | 表关联的数据源 |
| `odlm:tableCycle` | 表周期 | `odlm:Table` | `odlm:UpdateCycle` |  |  |  | 表的更新周期（如日/周/月） |
| `odlm:layer` | 层级 | `odlm:Table` | `odlm:DataLayer` |  |  |  | 表所在的数据层级 |
| `odlm:belongsToTeam` | 所属团队 | `odlm:Table`/`odlm:User`/`odlm:DataSource` | `odlm:Team` |  |  |  | 实体所属团队 |
| `odlm:tableBelongsToWorkspace` | 所属工作空间 | `odlm:Table` | `odlm:Workspace` |  |  |  | 表所在的工作空间 |
| `odlm:belongsToCluster` | 所属集群 | `odlm:Table`/`odlm:DataSource` | `odlm:Cluster` |  |  | 链（`belongsToDataSource ∘ belongsToCluster`） | 表继承数据源的集群归属 |
| `odlm:owner` | 负责人 | `odlm:Table`/`odlm:Task`/`odlm:Standard` | `odlm:User` |  |  |  | 表/任务/标准的负责人 |
| `odlm:changeStatus` | 变更状态 | `odlm:Table` | `odlm:ChangeStatus` |  |  |  | 表的变更状态（变更/审核中/未变更） |
| `odlm:publishStatus` | 发布状态 | `odlm:Table`/`odlm:Task`/`odlm:AtomicMetric`/`odlm:DerivedMetric` | `odlm:PublishStatus` |  |  |  | 发布状态（已发布/未发布/待审） |
| `odlm:dataSourceType` | 数据来源 | `odlm:Table` | `odlm:DataSourceType` |  |  |  | 表的数据来源类型（采集/模型开发） |
| `odlm:sourceSystem` | 来源系统 | `odlm:Table` | `odlm:System` |  |  |  | 表来源的外部系统 |
| `odlm:references` | 引用字段 | `odlm:Field` | `odlm:Field` |  |  | 传递（Transitive） | 字段间外键/引用关系（可传递） |
| `odlm:dependsOn` | 表依赖 | `odlm:Table` | `odlm:Table` |  |  | 传递；链（`hasField ∘ references ∘ belongsToTable`） | 若字段引用另一表字段，则建立表级依赖（可传递） |
| `odlm:fieldFollowStandard` | 字段遵循某一标准 | `odlm:Field` | `odlm:fieldStandard` | `odlm:followStandard` |  |  | 字段遵循的字段标准 |
| `odlm:fieldStandardHasRule` | 字段标准规则 | `odlm:fieldStandard` | `odlm:Rule` | `odlm:hasRule` |  |  | 依据字段标准生成的规则集合 |
| `odlm:securityCategory` | 安全分类 | `odlm:Field` | `odlm:SecurityCategory` |  |  |  | 字段所属的安全分类 |
| `odlm:securityLevel` | 安全分级 | `odlm:Field` | `odlm:SecurityLevel` |  |  |  | 字段所属的安全分级 |
| `odlm:partitionKey` | 分区键 | `odlm:HiveField` | `odlm:PartitionKey` |  |  |  | Hive 字段的分区键标注 |
| `odlm:taskPurpose` | 任务用途 | `odlm:Task` | `odlm:TaskPurpose` |  |  |  | 任务的用途（ETL/加工/稽核等） |
| `odlm:executionMode` | 实时/离线 | `odlm:Task` | `odlm:ExecutionMode` |  |  |  | 任务的执行模式（实时/离线） |
| `odlm:devMode` | 开发模式 | `odlm:Task` | `odlm:DevMode` |  |  |  | 任务开发模式（离线采集/实时采集/FLinkSQL 等） |
| `odlm:taskCycle` | 任务周期 | `odlm:Task` | `odlm:ScheduleCycle` |  |  |  | 调度周期（小时/日/周/月…） |
| `odlm:taskBelongsToWorkspace` | 任务所属空间 | `odlm:Task` | `odlm:Workspace` |  |  |  | 任务所在的工作空间 |
| `odlm:lastUpdateBy` | 最近更新人 | `odlm:Dimension`/`odlm:BusinessQualifier` | `odlm:User` |  |  |  | 维度/业务限定的最近更新人 |
| `odlm:dimensionTable` | 维度表 | `odlm:Dimension` | `odlm:Table` |  |  |  | 该维度所指向的维度表 |
| `odlm:hasAttribute` | 包含维度属性 | `odlm:Dimension` | `odlm:DimensionAttribute` |  | `odlm:belongsToDimension` |  | 维度包含的属性集合 |
| `odlm:belongsToDimension` | 维度归属 | `odlm:DimensionAttribute` | `odlm:Dimension` |  | `odlm:hasAttribute` | 逆属性 | 属性所属的维度 |
| `odlm:dimensionField` | 维度字段 | `odlm:DimensionAttribute` | `odlm:Field` |  |  |  | 维度属性绑定的字段 |
| `odlm:relatedTable` | 关联模型（表） | `odlm:BusinessQualifier` | `odlm:Table` |  |  |  | 限定条件涉及到的表 |
| `odlm:relatedField` | 关联字段 | `odlm:BusinessQualifier` | `odlm:Field` |  |  |  | 限定条件涉及到的字段 |
| `odlm:belongsToCatalog` | 所属目录 | `odlm:AtomicMetric`/`odlm:DerivedMetric` | `odlm:MetricCatalog` |  |  |  | 指标所属的目录 |
| `odlm:createdBy` | 创建人 | `odlm:AtomicMetric`/`odlm:DerivedMetric` | `odlm:User` |  |  |  | 指标的创建人 |
| `odlm:unit` | 度量单位 | `odlm:AtomicMetric`/`odlm:DerivedMetric` | `odlm:Unit` |  |  |  | 指标使用的计量单位 |
| `odlm:sourceTable` | 关联模型（表） | `odlm:AtomicMetric` | `odlm:Table` |  |  |  | 原子指标依赖的数据表 |
| `odlm:measureField` | 计量字段 | `odlm:AtomicMetric` | `odlm:Field` |  |  |  | 原子指标的度量字段 |
| `odlm:measureMethod` | 计量方式 | `odlm:AtomicMetric` | `odlm:MeasureMethod` |  |  |  | 原子指标的统计方式（求和/计数等） |
| `odlm:dateDimension` | 日期维度 | `odlm:AtomicMetric` | `odlm:Dimension` |  |  |  | 指标关联的时间/日期维度 |
| `odlm:storageType` | 存储类型 | `odlm:DerivedMetric` | `odlm:StorageType` |  |  |  | 派生指标的落地/存储类型 |
| `odlm:derivedDimension` | 派生维度 | `odlm:DerivedMetric` | `odlm:Dimension` |  |  |  | 派生指标的分析维度 |
| `odlm:timeDimension` | 时间维度 | `odlm:DerivedMetric` | `odlm:Dimension` |  |  |  | 派生指标的时间维度 |
| `odlm:statPeriod` | 统计周期 | `odlm:DerivedMetric` | `odlm:StatPeriod` |  |  |  | 派生指标的统计周期 |
| `odlm:appliedQualifier` | 业务限定 | `odlm:DerivedMetric` | `odlm:BusinessQualifier` |  |  |  | 指标应用的业务限定 |
| `odlm:serviceAuthTeam` | 团队可访问服务 | `odlm:Service` | `odlm:Team` |  |  |  | 可访问该服务的团队 |
| `odlm:hasRequestMethod` | 请求方法 | `odlm:APIService` | `odlm:RequestMethod` |  |  |  | API 的 HTTP 方法（GET/POST/…） |
| `odlm:hasCallType` | 调用类型 | `odlm:APIService` | `odlm:CallType` |  |  |  | 同步/异步 |
| `odlm:hasStatus` | 状态 | `odlm:APIService` | `odlm:ServiceStatus` |  |  |  | 开发/发布/失效 |
| `odlm:hasAccessLevel` | 开放等级 | `odlm:APIService` | `odlm:AccessLevel` |  |  |  | 快捷开放/严控开放 |
| `odlm:hasOwner` | 负责人 | `odlm:APIService` | `odlm:User` |  |  |  | 服务负责人 |
| `odlm:contentType` | Content-Type | `odlm:APIService` | `odlm:ContentType` |  |  |  | 返回的内容类型（JSON/CSV/XML） |
| `odlm:runsOn` | 运行态集群 | `odlm:APIService` | `odlm:Cluster` |  |  |  | 服务运行所在集群 |
| `odlm:hasSubscriber` | 订阅人 | `odlm:APIService` | `odlm:User` |  |  |  | 订阅该服务的用户 |

---

## 数据属性（Datatype Properties）

| 属性 | 标签 | Domain | Range | 备注 |
|---|---|---|---|---|
| `odlm:alias` | 别名 | 全局 | `xsd:string` | 通用别名属性，适用于所有实体、属性和活动 |
| `odlm:description` | 描述 | 全局 | `xsd:string` | 通用描述属性，适用于所有实体、属性和活动 |
| `odlm:dataSourceId` | ID | `odlm:DataSource` | `xsd:string` | 唯一标识，一般对应系统中资源的英文名 |
| `odlm:version` | 版本 | `odlm:DataSource` | `xsd:string` | 数据源版本标识 |
| `odlm:enableKerberos` | 开启 Kerberos 认证 | `odlm:KerberosSupport` | `xsd:boolean` | 是否启用 Kerberos |
| `odlm:kerberosPrincipal` | Kerberos Principal | `odlm:KerberosSupport` | `xsd:string` | Kerberos 主体 |
| `odlm:keytabFile` | keytab 文件 | `odlm:KerberosSupport` | `xsd:string` | keytab 文件路径 |
| `odlm:krb5File` | krb5 文件 | `odlm:KerberosSupport` | `xsd:string` | krb5 配置文件路径 |
| `odlm:jdbcUrl` | JDBC 连接/访问地址 | `odlm:MySQL`/`odlm:Hive` | `xsd:string` | 数据源的 JDBC 地址（MySQL/Hive） |
| `odlm:userName` | 用户名 | `odlm:MySQL`/`odlm:Kafka`/`odlm:MinIO` | `xsd:string` | 访问数据源的用户名 |
| `odlm:password` | 密码 | `odlm:MySQL`/`odlm:Kafka`/`odlm:MinIO` | `xsd:string` | 访问数据源的密码 |
| `odlm:queueName` | 队列名 | `odlm:Hive` | `xsd:string` | 作业执行队列 |
| `odlm:metaDatabase` | 元数据库 | `odlm:Hive` | `xsd:string` | Hive 元存储库标识 |
| `odlm:storagePath` | 存储路径 | `odlm:Hive` | `xsd:string` | 存储位置/路径 |
| `odlm:configDir` | 配置文件目录 | `odlm:Hive` | `xsd:string` | 配置文件目录 |
| `odlm:hbaseZookeeperQuorum` | hbase.zookeeper.quorum | `odlm:HBase` | `xsd:string` | HBase ZK 集群地址 |
| `odlm:hbaseZookeeperClientPort` | hbase.zookeeper.property.clientPort | `odlm:HBase` | `xsd:string` | HBase ZK 客户端端口 |
| `odlm:zookeeperZnodeParent` | ZooKeeper Znode Parent | `odlm:HBase` | `xsd:string` | ZK 根 Znode |
| `odlm:namespace` | namespace | `odlm:HBase` | `xsd:string` | HBase 命名空间 |
| `odlm:hbaseConf` | HBase 配置 | `odlm:HBase` | `xsd:string` | HBase 配置（序列化） |
| `odlm:bootstrapServers` | 连接地址 | `odlm:Kafka` | `xsd:string` | Kafka bootstrap servers |
| `odlm:kafkaConf` | Kafka 配置 | `odlm:Kafka` | `xsd:string` | Kafka 配置（序列化） |
| `odlm:url` | 协议地址 | `odlm:MinIO` | `xsd:string` | MinIO 访问地址 |
| `odlm:tableId` | ID | `odlm:Table` | `xsd:string` | 表的业务主键 |
| `odlm:ownerContact` | 负责人联系方式 | `odlm:Table` | `xsd:string` | 负责人联系信息 |
| `odlm:processingRule` | 加工口径 | `odlm:Table` | `xsd:string` | 表的加工规则说明 |
| `odlm:functionDesc` | 功能描述 | `odlm:Table` | `xsd:string` | 表的功能描述 |
| `odlm:scenario` | 应用场景 | `odlm:Table` | `xsd:string` | 使用/应用场景 |
| `odlm:importance` | 重要等级 | `odlm:Table` | `xsd:string` | 重要性等级 |
| `odlm:updateMethod` | 更新方式 | `odlm:Table` | `xsd:string` | 更新方式说明 |
| `odlm:updateTime` | 更新时间 | `odlm:Table`/`odlm:Task`/`odlm:Dimension`/`odlm:BusinessQualifier` | `xsd:dateTime` | 最后更新时间 |
| `odlm:isMaterialized` | 是否物化 | `odlm:Table` | `xsd:boolean` | 是否为物化表 |
| `odlm:attrComplete` | 属性是否完整 | `odlm:Table` | `xsd:boolean` | 属性完整性标识 |
| `odlm:rowCount` | 数据条数 | `odlm:Table` | `xsd:string` | 数据行数（文本记录） |
| `odlm:totalSize` | 总存储量 | `odlm:Table` | `xsd:string` | 总占用空间（文本记录） |
| `odlm:hiveTableId` | Hive表ID | `odlm:HiveTable` | `xsd:string` | Hive 表标识 |
| `odlm:isPartitioned` | 是否分区 | `odlm:HiveTable` | `xsd:boolean` | 是否为分区表 |
| `odlm:isExternal` | 是否外部表 | `odlm:HiveTable` | `xsd:boolean` | 是否为外部表 |
| `odlm:externalLocation` | 外部表地址 | `odlm:HiveTable` | `xsd:string` | 外部表数据存放地址（当 `isExternal=true` 必填） |
| `odlm:hdfsPath` | 文件存储路径 | `odlm:HiveTable` | `xsd:string` | HDFS 文件路径 |
| `odlm:fieldId` | ID | `odlm:Field` | `xsd:string` | 字段的业务主键 |
| `odlm:businessMeaning` | 业务含义 | `odlm:Field` | `xsd:string` | 字段的业务意义 |
| `odlm:length` | 长度 | `odlm:Field` | `xsd:string` | 字段长度 |
| `odlm:precision` | 精度 | `odlm:Field` | `xsd:string` | 数值精度 |
| `odlm:isPrimaryKey` | 是否主键 | `odlm:Field` | `xsd:boolean` | 是否为主键 |
| `odlm:isNullable` | 是否为空 | `odlm:Field` | `xsd:boolean` | 是否允许为空 |
| `odlm:defaultValue` | 默认值 | `odlm:Field` | `xsd:string` | 字段默认值 |
| `odlm:isDimension` | 是否维度 | `odlm:Field` | `xsd:boolean` | 是否作为维度使用 |
| `odlm:isMeasure` | 是否度量 | `odlm:Field` | `xsd:boolean` | 是否作为度量使用 |
| `odlm:hiveFieldId` | Hive字段ID | `odlm:HiveField` | `xsd:string` | Hive 字段标识 |
| `odlm:isTimeIdentifier` | 时间标识 | `odlm:HiveField` | `xsd:boolean` | 是否为时间标识字段 |
| `odlm:taskId` | 任务ID | `odlm:Task` | `xsd:string` | 任务业务标识 |
| `odlm:isIncremental` | 采集模式 | `odlm:Task` | `xsd:boolean` | true=增量 / false=全量 |
| `odlm:dimensionId` | 维度ID | `odlm:Dimension` | `xsd:string` | 维度业务标识 |
| `odlm:attributeCount` | 属性数 | `odlm:Dimension` | `xsd:integer` | 维度包含的属性数量 |
| `odlm:attrId` | 维度属性标识 | `odlm:DimensionAttribute` | `xsd:string` | 维度属性业务标识 |
| `odlm:attrName` | 维度属性名称 | `odlm:DimensionAttribute` | `xsd:string` | 维度属性名称 |
| `odlm:attrDesc` | 维度属性描述 | `odlm:DimensionAttribute` | `xsd:string` | 维度属性说明 |
| `odlm:businessQualifierId` | 业务限定ID | `odlm:BusinessQualifier` | `xsd:string` | 业务限定标识 |
| `odlm:calculationLogic` | 计算逻辑 | `odlm:BusinessQualifier` | `xsd:string` | SQL 计算逻辑片段 |
| `odlm:atomicMetricId` | 原子指标ID | `odlm:AtomicMetric` | `xsd:string` | 原子指标标识 |
| `odlm:createdTime` | 创建时间 | `odlm:AtomicMetric`/`odlm:DerivedMetric` | `xsd:dateTime` | 指标创建时间 |
| `odlm:businessFormula` | 业务口径 | `odlm:AtomicMetric`/`odlm:DerivedMetric` | `xsd:string` | 指标业务口径说明 |
| `odlm:derivedMetricId` | 派生指标ID | `odlm:DerivedMetric` | `xsd:string` | 派生指标标识 |
| `odlm:apiServiceId` | API服务ID | `odlm:APIService` | `xsd:string` | API 服务标识 |
| `odlm:apiEndpoint` | 访问地址 | `odlm:APIService` | `xsd:string` | 访问地址（`dcat:endpointURL` 的子属性） |
| `odlm:createdAt` | 创建时间 | `odlm:APIService` | `xsd:dateTime` | 服务创建时间 |
| `odlm:businessDescription` | 业务详述 | `odlm:APIService` | `xsd:string` | 服务的业务说明 |
| `odlm:sqlQuery` | SQL 语句 | `odlm:APIService` | `xsd:string` | 具体查询 SQL（可含模板变量） |
| `odlm:objectDisplayName` | 对象的展示属性 | `odlm:Object` | `xsd:string` | 对象的展示名称 |
| `odlm:objectId` | 对象唯一标识 | `odlm:Object` | `xsd:string` | 对象唯一标识 |
| `odlm:useCase` | 对象使用场景 | `odlm:Object` | `xsd:string` | 对象应用/使用场景 |

---

## 命名个体与枚举（Named Individuals & Enums）

以下是 ODLM 命名空间下的枚举值示例（非穷尽）。

### 请求方法（`odlm:RequestMethod`）
- `odlm:GET`  — GET
- `odlm:POST` — POST
- `odlm:PUT`  — PUT
- `odlm:DELETE` — DELETE
- `odlm:PATCH` — PATCH

### 调用类型（`odlm:CallType`）
- `odlm:Synchronous` — 同步
- `odlm:Asynchronous` — 异步

### 服务状态（`odlm:ServiceStatus`）
- `odlm:Developing` — 开发
- `odlm:Published` — 发布
- `odlm:Deprecated` — 失效

### 开放等级（`odlm:AccessLevel`）
- `odlm:QuickAccess` — 快捷开放
- `odlm:StrictControl` — 严控开放

### Content-Type（`odlm:ContentType`）
- `odlm:JSON` — application/json
- `odlm:CSV` — text/csv
- `odlm:XML` — application/xml

> 其他业务侧字典（如 `UpdateCycle`、`DataLayer`、`MeasureMethod`、`Unit` 等）在业务实例命名空间 `ex:` 中给出样例实例，可按需扩展至 `odlm:` 空间或复用 `ex:`。

---

## 建模约束与推理规则（Axioms）

- **血缘：字段引用与表依赖**
  - `odlm:references` 为传递属性：A 引用 B、B 引用 C，则 A 引用 C。
  - `odlm:dependsOn` 为传递属性，并由链 `odlm:hasField ∘ odlm:references ∘ odlm:belongsToTable` 推断：若表 A 的字段引用表 B 的字段，则 A dependsOn B。
- **模型关联（Schema）**
  - `odlm:relatedSchema` 通过链 `containsTable ∘ dependsOn ∘ belongsToSchema` 推断，并为对称属性。
- **团队/空间与集群归属推理**
  - `odlm:belongsToCluster` 支持链：`odlm:belongsToDataSource ∘ odlm:belongsToCluster`（表继承数据源的集群归属）。
- **权限继承**
  - `odlm:hasDirectPermission` 为 `odlm:hasRole ∘ odlm:hasPermission` 的链式子属性，支持用户通过角色继承权限。
- **PROV-O 对齐**
  - 生产/来源关系复用 `prov:generated`、`prov:wasGeneratedBy`、`prov:used`；Activity/Entity 对齐 PROV 语义。

---

## 附录：示例实例说明（ex:）

- 文件中提供了 `ex:` 命名空间的完整示例，覆盖：
  - 源端 `MySQL` 数据源与表（客户、订单）；
  - 目标端 `Hive` 仓库与汇总表；
  - ETL 任务血缘（`odlm:used` / `odlm:generated`）与表到表血缘（`prov:wasDerivedFrom` / `odlm:dependsOn`）；
  - 维度表与维度、维度属性；
  - 基于汇总表的原子指标与派生指标（含目录、单位、时间维度、统计周期等）；
  - `APIService` 示例，展示接口元数据、调用类型、状态、开放等级、内容类型、SQL 模板与使用的表/指标。

> 这些示例用于演示词汇在典型数据中台场景下的建模与血缘表达方式，业务部署时可替换为真实实例。

---

## 修订记录

- 1.0（2025-08-30）: 初始版本发布。
