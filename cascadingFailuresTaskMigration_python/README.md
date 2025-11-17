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
# 方法1: 使用运行脚本
cd cascadingFailuresTaskMigration_python
python run.py

# 方法2: 作为模块运行
cd cascadingFailuresTaskMigration_python
python -m main.main
```

## 算法说明

项目实现了以下几种任务迁移算法:

1. **MPFTM** (Multi-layer Potential Field Task Migration): 基于多层势场的任务迁移算法
2. **LTM** (Load-based Task Migration): 基于负载的任务迁移算法
3. **GreedyPath**: 基于贪心路径的任务迁移算法
4. **Opt**: 优化算法

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

程序输出包括:
- meanExecuteCost: 平均执行成本
- meanMigrationCost: 平均迁移成本
- meanSurvivalRate: 平均存活率
- robotLoadStd: 机器人负载标准差
- taskSizeStd: 任务大小标准差
- meanRobotCapacity: 平均机器人容量
- meanTaskSize: 平均任务大小
- targetOpt: 目标优化值

## 开发说明

该Python实现是从原始Java代码一对一转换而来,保持了:
1. 相同的类结构和方法
2. 相同的算法逻辑
3. 相同的变量命名(转换为Python命名风格)
4. 相同的计算公式和参数

## 依赖库

- networkx: 用于图操作,替代JGraphT
- numpy: 用于数值计算(可选)
