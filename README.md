# Cataclysm: Dark Days Ahead - Python Rewrite

## 项目说明

这是一个完全用 Python 和 PySide6 重写的 Cataclysm: Dark Days Ahead 项目。

**目的**: 学习游戏架构、Python 编程和软件工程实践  
**性质**: 仅用于研究和学习，不作商业用途

## 项目结构

```
Cataclysm-DDA-fumi/
├── python_rewrite/       # Python 重写项目
│   ├── src/             # 源代码
│   ├── tests/           # 单元测试
│   ├── assets/          # 游戏资源
│   ├── docs/            # 文档
│   ├── main.py          # 入口文件
│   └── README.md        # 项目说明
├── .github/             # CI/CD 配置
└── .gitignore          # Git 忽略配置
```

## 开发进度

✅ **Phase 1-5 全部完成** (100%)

已实现 46/84 核心系统 (55%)：
- 基础框架
- 游戏世界（地图、地形、家具）
- 实体系统（物品、角色、怪物）
- 游戏机制（移动、战斗、制作）
- 高级功能（AI、任务、派系、车辆）

详细进度请查看 `python_rewrite/docs/plan.md`

## 快速开始

```bash
cd python_rewrite
pip install -r requirements.txt
python main.py
```

## 许可

本项目仅用于学习和研究目的，不作商业用途。

原版 Cataclysm: Dark Days Ahead 版权归原作者所有。
