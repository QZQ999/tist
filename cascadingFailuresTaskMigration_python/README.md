# Cascading Failures Task Migration - Python Implementation

这是ACM TIST论文的Python实现版本,从Java代码转换而来。

## 项目结构

```
cascadingFailuresTaskMigration_python/
├── input/              # 数据输入和基础数据类
├── main/               # 主程序和初始化模块
├── MPFTM/              # MPFTM算法实现
├── LTM/                # LTM算法实现
├── greedyPath/         # 贪心路径算法实现
├── opt/                # 优化算法实现
├── evaluation/         # 评估模块
├── run.py              # 运行脚本
├── requirements.txt    # Python依赖
└── *.txt               # 测试数据文件
```

## 安装依赖

```bash
pip install -r requirements.txt
```

## 运行

```bash
# 方法1: 使用运行脚本 (推荐)
cd cascadingFailuresTaskMigration_python
python run.py

# 方法2: 作为模块运行
cd cascadingFailuresTaskMigration_python
python -m main.main
```

**注意**:
- 默认运行3个benchmark算法: CATM (LTM), KBTM (GreedyPath), HCTM-MPF (MPFTM)
- OPT算法由于计算复杂度高(指数级),默认不运行
- 如需运行OPT算法,请在`main.py`中设置`run_opt=True`,或使用更小的测试集(如Task6.txt)

## 算法说明

项目实现了论文中的所有benchmark算法:

1. **HCTM-MPF** (MPFTM): 论文提出的算法 - 基于多层势场的任务迁移
2. **CATM** (LTM): Context-Aware Task Migration - 基于上下文的任务迁移
3. **KBTM** (GreedyPath): Key-Based Task Migration - 基于关键节点的任务迁移
4. **OPT**: Optimal Solution - 使用整数规划求最优解(计算密集)

## 主要特性

- ✅ 与Java版本算法逻辑完全一致
- ✅ 使用NetworkX替代JGraphT进行图操作
- ✅ 使用dataclasses替代Lombok
- ✅ 保持原有的代码结构和命名约定
- ✅ 支持相同的输入数据格式

## 测试数据

项目包含多组测试数据:
- Task*.txt: 任务数据 (taskId, size, arriveTime)
- RobotsInformation*.txt: 机器人数据 (robotId, capacity, groupId)
- Graph*.txt: 图数据 (vertex1, vertex2, weight)

## 输出结果

程序会输出每个算法的详细结果和对比表格:

```
====================================================================================================
COMPARISON TABLE OF ALL ALGORITHMS
====================================================================================================
Algorithm       Runtime(ms)  ExecCost     MigrCost     SurvRate     TotalCost    TargetOpt
----------------------------------------------------------------------------------------------------
CATM            0            43.4515      16.4903      0.7161       59.9417      5.3497
KBTM            1            47.4214      18.0000      0.6948       65.4214      5.9168
HCTM-MPF        4            44.2643      20.3267      0.7293       64.5910      5.8028
====================================================================================================

Best Algorithm: CATM (Lowest TargetOpt)
====================================================================================================
```

指标说明:
- **Runtime**: 算法运行时间(毫秒)
- **ExecCost**: 平均执行成本
- **MigrCost**: 平均迁移成本
- **SurvRate**: 平均存活率
- **TotalCost**: 总成本 (ExecCost + MigrCost)
- **TargetOpt**: 目标优化值 (a × TotalCost - b × SurvRate),越小越好

## 开发说明

该Python实现是从原始Java代码一对一转换而来,保持了:
1. 相同的类结构和方法
2. 相同的算法逻辑
3. 相同的变量命名(转换为Python命名风格)
4. 相同的计算公式和参数

## 依赖库

- networkx: 用于图操作,替代JGraphT
- numpy: 用于数值计算(可选)
