"""
UI 模块 - 主窗口

游戏的主窗口界面
"""

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QMessageBox,
)
from PySide6.QtGui import QKeyEvent, QAction

from ..utils.logger import logger
from ..utils.config import config


class MainWindow(QMainWindow):
    """游戏主窗口"""

    def __init__(self):
        """初始化主窗口"""
        super().__init__()

        # 设置窗口属性
        self.setWindowTitle("CDDA Python - 学习版本")

        # 从配置读取窗口大小
        window_width = config.get("graphics.window_width", 1024)
        window_height = config.get("graphics.window_height", 768)
        self.resize(window_width, window_height)

        # 创建中央部件
        self._setup_central_widget()

        # 创建菜单栏
        self._create_menus()

        # 创建状态栏
        self.statusBar().showMessage("准备就绪")

        logger.info("主窗口已初始化")

    def _setup_central_widget(self):
        """设置中央部件"""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # 创建主布局
        main_layout = QVBoxLayout()
        central_widget.setLayout(main_layout)

        # 创建游戏视图区域
        from .game_view import GameView

        self.game_view = GameView()
        main_layout.addWidget(self.game_view)

        # 创建底部信息栏
        self._create_info_bar(main_layout)

    def _create_info_bar(self, parent_layout):
        """
        创建底部信息栏

        Args:
            parent_layout: 父布局
        """
        info_layout = QHBoxLayout()

        # 位置信息
        self.position_label = QLabel("位置: (0, 0, 0)")
        info_layout.addWidget(self.position_label)

        info_layout.addStretch()

        # 生命值信息
        self.health_label = QLabel("生命: 100/100")
        info_layout.addWidget(self.health_label)

        # 体力信息
        self.stamina_label = QLabel("体力: 100/100")
        info_layout.addWidget(self.stamina_label)

        parent_layout.addLayout(info_layout)

    def _create_menus(self):
        """创建菜单栏"""
        menubar = self.menuBar()

        # 文件菜单
        file_menu = menubar.addMenu("文件(&F)")

        new_game_action = QAction("新游戏(&N)", self)
        new_game_action.setShortcut("Ctrl+N")
        new_game_action.triggered.connect(self.on_new_game)
        file_menu.addAction(new_game_action)

        load_game_action = QAction("加载游戏(&L)", self)
        load_game_action.setShortcut("Ctrl+O")
        load_game_action.triggered.connect(self.on_load_game)
        file_menu.addAction(load_game_action)

        save_game_action = QAction("保存游戏(&S)", self)
        save_game_action.setShortcut("Ctrl+S")
        save_game_action.triggered.connect(self.on_save_game)
        file_menu.addAction(save_game_action)

        file_menu.addSeparator()

        exit_action = QAction("退出(&X)", self)
        exit_action.setShortcut("Alt+F4")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        # 视图菜单
        view_menu = menubar.addMenu("视图(&V)")

        toggle_fullscreen_action = QAction("全屏(&F)", self)
        toggle_fullscreen_action.setShortcut("F11")
        toggle_fullscreen_action.triggered.connect(self.toggle_fullscreen)
        view_menu.addAction(toggle_fullscreen_action)

        # 调试菜单
        debug_menu = menubar.addMenu("调试(&D)")

        show_fps_action = QAction("显示 FPS(&F)", self)
        show_fps_action.setCheckable(True)
        show_fps_action.triggered.connect(self.toggle_fps)
        debug_menu.addAction(show_fps_action)

        # 帮助菜单
        help_menu = menubar.addMenu("帮助(&H)")

        about_action = QAction("关于(&A)", self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)

    def on_new_game(self):
        """新游戏"""
        logger.info("新游戏")
        self.statusBar().showMessage("开始新游戏...")
        # TODO: 实现新游戏逻辑

    def on_load_game(self):
        """加载游戏"""
        logger.info("加载游戏")
        self.statusBar().showMessage("加载游戏...")
        # TODO: 实现加载游戏逻辑

    def on_save_game(self):
        """保存游戏"""
        logger.info("保存游戏")
        self.statusBar().showMessage("保存游戏...")
        # TODO: 实现保存游戏逻辑

    def toggle_fullscreen(self):
        """切换全屏"""
        if self.isFullScreen():
            self.showNormal()
            logger.info("退出全屏模式")
        else:
            self.showFullScreen()
            logger.info("进入全屏模式")

    def toggle_fps(self, checked: bool):
        """
        切换 FPS 显示

        Args:
            checked: 是否显示
        """
        config.set("debug.show_fps", checked)
        logger.info(f"FPS 显示: {checked}")

    def show_about(self):
        """显示关于对话框"""
        QMessageBox.about(
            self,
            "关于 CDDA Python",
            "CDDA Python 重写版本\n\n"
            "这是一个用于学习的项目，使用 Python 和 PySide6 重写 Cataclysm: Dark Days Ahead。\n\n"
            "仅用于教育目的，不作商业用途。",
        )

    def update_info(self, position, health, stamina):
        """
        更新信息栏

        Args:
            position: 位置 (x, y, z)
            health: 生命值 (current, max)
            stamina: 体力 (current, max)
        """
        self.position_label.setText(f"位置: {position}")
        self.health_label.setText(f"生命: {health[0]}/{health[1]}")
        self.stamina_label.setText(f"体力: {stamina[0]}/{stamina[1]}")

    def keyPressEvent(self, event: QKeyEvent):
        """
        键盘按键事件

        Args:
            event: 键盘事件
        """
        # 将事件传递给游戏视图
        self.game_view.keyPressEvent(event)

    def closeEvent(self, event):
        """
        窗口关闭事件

        Args:
            event: 关闭事件
        """
        # 保存窗口大小
        config.set("graphics.window_width", self.width())
        config.set("graphics.window_height", self.height())
        config.save()

        logger.info("主窗口关闭")
        event.accept()
