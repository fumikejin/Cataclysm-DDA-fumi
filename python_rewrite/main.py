#!/usr/bin/env python3
"""
CDDA Python 重写版本 - 主程序入口

这是使用 Python 和 PySide6 完全重写的 Cataclysm: Dark Days Ahead。
本项目仅用于学习和研究目的，不作商业用途。

运行方式:
    python main.py
"""

import sys
from pathlib import Path

# 将 src 目录添加到 Python 路径
sys.path.insert(0, str(Path(__file__).parent / "src"))


def main() -> int:
    """程序主入口"""
    print("=" * 70)
    print("CDDA Python 重写版本 - 开发版")
    print("Cataclysm: Dark Days Ahead - Python Rewrite (Development Version)")
    print("=" * 70)
    print()
    print("项目状态: 基础框架已建立")
    print("Project Status: Basic Framework Established")
    print()
    print("本项目用于学习 Python 编程和游戏开发，不作商业用途。")
    print("This project is for learning Python and game development only.")
    print()
    print("-" * 70)
    print("下一步操作 / Next Steps:")
    print("-" * 70)
    print()
    print("1. 查看开发方案文档:")
    print("   View development plan:")
    print("   docs/开发方案.md")
    print()
    print("2. 设置虚拟环境:")
    print("   Setup virtual environment:")
    print("   python -m venv venv")
    print()
    print("3. 激活虚拟环境:")
    print("   Activate virtual environment:")
    print("   Windows: venv\\Scripts\\activate")
    print("   Linux/Mac: source venv/bin/activate")
    print()
    print("4. 安装依赖:")
    print("   Install dependencies:")
    print("   pip install -r requirements.txt")
    print()
    print("5. 开始第一阶段开发:")
    print("   Start Phase 1 development:")
    print("   - 工具模块 (utils/)")
    print("   - 数据加载器 (data/)")
    print("   - UI 框架 (ui/)")
    print("   - 游戏引擎 (engine/)")
    print()
    print("=" * 70)
    print("详细步骤请参考: docs/开发方案.md")
    print("For detailed steps, please refer to: docs/开发方案.md")
    print("=" * 70)

    return 0


if __name__ == "__main__":
    sys.exit(main())
