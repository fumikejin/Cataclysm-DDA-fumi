# CDDA Python 重写项目

> 使用 Python 和 PySide6 完全重写的 Cataclysm: Dark Days Ahead  
> **仅用于学习和研究目的，不作商业用途**

## 项目简介

本项目是 Cataclysm: Dark Days Ahead (CDDA) 的 Python 重写版本，使用 PySide6 作为 GUI 框架，保持与原游戏相同的机制和模块。项目的主要目的是学习游戏架构、Python 编程和软件工程实践。

## 特性

- ✅ 使用 Python 3.10+ 编写
- ✅ PySide6 (Qt6) 图形界面
- ✅ 与原游戏兼容的 JSON 数据格式
- ✅ 模块化架构设计
- ✅ 完整的类型提示
- ✅ 单元测试覆盖

## 项目结构

```
python_rewrite/
├── src/                    # 源代码
│   ├── engine/            # 游戏引擎
│   ├── ui/                # 用户界面
│   ├── data/              # 数据管理
│   ├── world/             # 游戏世界
│   ├── entities/          # 游戏实体
│   ├── systems/           # 游戏系统
│   ├── ai/                # AI 系统
│   └── utils/             # 工具模块
├── tests/                 # 单元测试
├── docs/                  # 文档
│   └── 开发方案.md        # 详细开发方案（中文）
├── assets/                # 游戏资源
├── main.py                # 程序入口
├── requirements.txt       # 依赖列表
└── pyproject.toml        # 项目配置
```

## 快速开始

### 环境要求

- Python 3.10 或更高版本
- pip 包管理器

### 安装步骤

1. **克隆仓库**
```bash
cd python_rewrite
```

2. **创建虚拟环境**
```bash
python -m venv venv
```

3. **激活虚拟环境**

Windows:
```bash
venv\Scripts\activate
```

Linux/Mac:
```bash
source venv/bin/activate
```

4. **安装依赖**
```bash
pip install -r requirements.txt
```

5. **运行程序**
```bash
python main.py
```

## 开发计划

详细的开发方案和步骤请查看：[docs/开发方案.md](docs/开发方案.md)

### 开发阶段

| 阶段 | 时间 | 主要内容 |
|------|------|----------|
| 第一阶段 | 第 1-2 周 | 基础框架建设 |
| 第二阶段 | 第 3-4 周 | 游戏世界基础 |
| 第三阶段 | 第 5-6 周 | 实体系统 |
| 第四阶段 | 第 7-8 周 | 游戏机制 |
| 第五阶段 | 第 9-10 周 | 完善和优化 |

### 当前进度

- [x] 项目结构搭建
- [x] 开发方案文档
- [ ] 工具模块实现
- [ ] 数据加载系统
- [ ] UI 基础框架
- [ ] 游戏引擎核心

## 技术栈

- **Python 3.10+**: 主要编程语言
- **PySide6**: Qt6 Python 绑定，用于 GUI
- **pytest**: 测试框架
- **black**: 代码格式化
- **mypy**: 静态类型检查
- **flake8**: 代码风格检查

## 开发规范

### 代码风格

- 遵循 PEP 8 规范
- 使用类型提示
- 编写文档字符串
- 有意义的变量和函数命名

### 提交规范

```
<类型>: <简短描述>

<详细描述>

类型: feat, fix, docs, style, refactor, test, chore
```

## 学习资源

### Python 相关
- [Python 官方文档](https://docs.python.org/zh-cn/3/)
- [PEP 8 风格指南](https://pep8.org/)

### PySide6 相关
- [PySide6 文档](https://doc.qt.io/qtforpython/)
- [Qt for Python 教程](https://doc.qt.io/qtforpython/tutorials/index.html)

### CDDA 相关
- [CDDA 官方仓库](https://github.com/CleverRaven/Cataclysm-DDA)
- [CDDA JSON 文档](https://github.com/CleverRaven/Cataclysm-DDA/blob/master/doc/JSON_INFO.md)

## 许可证

本项目基于 Cataclysm: Dark Days Ahead，遵循 CC-BY-SA 3.0 许可证。

**重要提示**: 本项目仅用于学习和研究目的，不得用于商业用途。

## 贡献

本项目是个人学习项目，欢迎提出建议和讨论。

## 致谢

- 感谢 Cataclysm: Dark Days Ahead 开发团队创造了这款优秀的游戏
- 感谢 Python 和 Qt 社区提供的优秀工具和文档

---

**项目状态**: 🚧 开发中 (基础框架阶段)

**最后更新**: 2025-12-14
