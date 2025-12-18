#!/usr/bin/env python3
"""
CDDA Python 重写版本 - 主程序入口

这是使用 Python 和 PySide6 完全重写的 Cataclysm: Dark Days Ahead。
本项目仅用于学习和研究目的，不作商业用途。

运行方式:
    python main.py [--test]

参数:
    --test  显示项目信息而不启动游戏
"""

import sys
from pathlib import Path

# 将 src 目录添加到 Python 路径
sys.path.insert(0, str(Path(__file__).parent / "src"))


def show_info():
    """显示项目信息"""
    print("=" * 70)
    print("CDDA Python 重写版本 - 开发版")
    print("Cataclysm: Dark Days Ahead - Python Rewrite (Development Version)")
    print("=" * 70)
    print()
    print("项目状态: 第一阶段完成")
    print("Project Status: Phase 1 Completed")
    print()
    print("本项目用于学习 Python 编程和游戏开发，不作商业用途。")
    print("This project is for learning Python and game development only.")
    print()
    print("-" * 70)
    print("已完成功能 / Completed Features:")
    print("-" * 70)
    print("✓ 工具模块 (坐标点、日志、配置、数学工具)")
    print("✓ 数据加载系统 (JSON加载器、数据管理器、数据验证)")
    print("✓ UI 框架 (主窗口、游戏视图、渲染器、输入处理)")
    print("✓ 游戏引擎 (主游戏类、游戏循环、回合管理、事件系统)")
    print()
    print("-" * 70)
    print("运行游戏 / Run Game:")
    print("-" * 70)
    print("python main.py")
    print()
    print("=" * 70)
    print("详细步骤请参考: docs/开发方案.md")
    print("For detailed steps, please refer to: docs/开发方案.md")
    print("=" * 70)


def main() -> int:
    """程序主入口"""
    # 检查是否只是显示信息
    if "--test" in sys.argv or "--info" in sys.argv:
        show_info()
        return 0

    try:
        # 导入 PySide6
        from PySide6.QtWidgets import QApplication

        # 导入游戏模块
        from src.ui.main_window import MainWindow
        from src.engine.game import game
        from src.engine.game_loop import GameLoop
        from src.utils.logger import logger

        logger.info("=" * 50)
        logger.info("CDDA Python 重写版本 启动中...")
        logger.info("=" * 50)

        # 创建 Qt 应用
        app = QApplication(sys.argv)
        app.setApplicationName("CDDA Python")
        app.setOrganizationName("CDDA Python Rewrite")

        # 初始化游戏
        logger.info("初始化游戏...")
        # 注意：如果原游戏数据目录不存在，这里会失败，但不影响 UI 显示
        try:
            game.initialize("../data")
        except Exception as e:
            logger.warning(f"无法加载原游戏数据: {e}")
            logger.info("游戏将以演示模式运行")

        # 创建主窗口
        logger.info("创建主窗口...")
        window = MainWindow()

        # 创建游戏循环
        logger.info("创建游戏循环...")
        game_loop = GameLoop(game)

        # 连接输入处理
        from src.ui.input_handler import InputHandler

        input_handler = InputHandler()
        input_handler.action_signal.connect(lambda action: game.process_action(action))

        # 显示窗口
        window.show()
        logger.info("游戏窗口已显示")

        # 启动游戏循环
        game_loop.start()
        logger.info("游戏循环已启动")

        logger.info("=" * 50)
        logger.info("游戏已准备就绪！")
        logger.info("=" * 50)

        # 运行 Qt 事件循环
        return app.exec()

    except ImportError as e:
        print()
        print("错误: 无法导入 PySide6")
        print("Error: Cannot import PySide6")
        print()
        print("请安装依赖:")
        print("Please install dependencies:")
        print()
        print("  pip install -r requirements.txt")
        print()
        print(f"详细错误: {e}")
        return 1

    except Exception as e:
        print()
        print(f"错误: {e}")
        print(f"Error: {e}")
        print()
        import traceback

        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
