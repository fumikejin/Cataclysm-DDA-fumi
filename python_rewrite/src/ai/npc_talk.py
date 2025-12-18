"""
AI系统 - NPC 对话系统

实现NPC对话、交易和任务交互
"""

from typing import Dict, List, Optional, Callable
from enum import Enum

from ..utils.logger import logger
from ..entities.npc import NPC
from ..entities.player import Player


class DialogueResponseType(Enum):
    """对话响应类型"""
    GREETING = "greeting"  # 问候
    TRADE = "trade"  # 交易
    MISSION = "mission"  # 任务
    INFO = "info"  # 信息
    LEAVE = "leave"  # 离开
    ATTACK = "attack"  # 攻击
    FOLLOW = "follow"  # 跟随
    WAIT = "wait"  # 等待


class DialogueOption:
    """对话选项"""
    
    def __init__(
        self,
        text: str,
        response_type: DialogueResponseType,
        condition: Optional[Callable] = None,
        effect: Optional[Callable] = None
    ):
        """
        初始化对话选项
        
        Args:
            text: 选项文本
            response_type: 响应类型
            condition: 条件函数（返回bool，判断选项是否可用）
            effect: 效果函数（选择该选项后执行）
        """
        self.text = text
        self.response_type = response_type
        self.condition = condition
        self.effect = effect
    
    def is_available(self, npc: NPC, player: Player) -> bool:
        """
        检查选项是否可用
        
        Args:
            npc: NPC实例
            player: 玩家实例
            
        Returns:
            是否可用
        """
        if self.condition:
            return self.condition(npc, player)
        return True
    
    def execute(self, npc: NPC, player: Player) -> bool:
        """
        执行选项效果
        
        Args:
            npc: NPC实例
            player: 玩家实例
            
        Returns:
            是否成功执行
        """
        if self.effect:
            return self.effect(npc, player)
        return True


class DialogueNode:
    """对话节点"""
    
    def __init__(
        self,
        node_id: str,
        npc_text: str,
        options: Optional[List[DialogueOption]] = None
    ):
        """
        初始化对话节点
        
        Args:
            node_id: 节点ID
            npc_text: NPC说的话
            options: 可选的对话选项列表
        """
        self.node_id = node_id
        self.npc_text = npc_text
        self.options = options or []
    
    def get_available_options(self, npc: NPC, player: Player) -> List[DialogueOption]:
        """
        获取可用的对话选项
        
        Args:
            npc: NPC实例
            player: 玩家实例
            
        Returns:
            可用选项列表
        """
        return [opt for opt in self.options if opt.is_available(npc, player)]


class NPCTalk:
    """NPC 对话系统"""
    
    def __init__(self):
        """初始化NPC对话系统"""
        self.dialogues: Dict[str, DialogueNode] = {}
        self.current_dialogue: Optional[str] = None
        self.current_npc: Optional[NPC] = None
        self.current_player: Optional[Player] = None
        
        # 初始化默认对话
        self._init_default_dialogues()
        logger.info("NPC 对话系统已初始化")
    
    def _init_default_dialogues(self):
        """初始化默认对话树"""
        
        # 友好问候
        friendly_greeting = DialogueNode(
            "friendly_greeting",
            "你好！很高兴见到你。",
            [
                DialogueOption(
                    "你好，我想和你交易。",
                    DialogueResponseType.TRADE,
                    effect=self._start_trade
                ),
                DialogueOption(
                    "有什么任务需要帮助吗？",
                    DialogueResponseType.MISSION,
                    effect=self._show_missions
                ),
                DialogueOption(
                    "能告诉我一些信息吗？",
                    DialogueResponseType.INFO,
                    effect=self._show_info
                ),
                DialogueOption(
                    "跟着我。",
                    DialogueResponseType.FOLLOW,
                    condition=lambda npc, player: npc.is_friendly(),
                    effect=self._start_follow
                ),
                DialogueOption(
                    "再见。",
                    DialogueResponseType.LEAVE,
                    effect=self._end_dialogue
                )
            ]
        )
        self.dialogues["friendly_greeting"] = friendly_greeting
        
        # 中立问候
        neutral_greeting = DialogueNode(
            "neutral_greeting",
            "嗯？你想要什么？",
            [
                DialogueOption(
                    "我想交易。",
                    DialogueResponseType.TRADE,
                    effect=self._start_trade
                ),
                DialogueOption(
                    "你有任务吗？",
                    DialogueResponseType.MISSION,
                    effect=self._show_missions
                ),
                DialogueOption(
                    "没什么，再见。",
                    DialogueResponseType.LEAVE,
                    effect=self._end_dialogue
                )
            ]
        )
        self.dialogues["neutral_greeting"] = neutral_greeting
        
        # 敌对问候
        hostile_greeting = DialogueNode(
            "hostile_greeting",
            "滚开！否则我对你不客气！",
            [
                DialogueOption(
                    "我没有恶意，我只是想谈谈。",
                    DialogueResponseType.INFO,
                    effect=self._attempt_calm
                ),
                DialogueOption(
                    "好吧，我走。",
                    DialogueResponseType.LEAVE,
                    effect=self._end_dialogue
                ),
                DialogueOption(
                    "那就来试试！",
                    DialogueResponseType.ATTACK,
                    effect=self._start_combat
                )
            ]
        )
        self.dialogues["hostile_greeting"] = hostile_greeting
    
    def start_dialogue(self, npc: NPC, player: Player) -> Optional[DialogueNode]:
        """
        开始对话
        
        Args:
            npc: NPC实例
            player: 玩家实例
            
        Returns:
            初始对话节点，如果无法对话则返回None
        """
        self.current_npc = npc
        self.current_player = player
        
        # 根据NPC态度选择初始对话
        if npc.is_hostile():
            dialogue_id = "hostile_greeting"
        elif npc.is_friendly():
            dialogue_id = "friendly_greeting"
        else:
            dialogue_id = "neutral_greeting"
        
        self.current_dialogue = dialogue_id
        node = self.dialogues.get(dialogue_id)
        
        if node:
            logger.info(f"与 {npc.name} 开始对话")
        else:
            logger.warning(f"未找到对话节点: {dialogue_id}")
        
        return node
    
    def get_current_node(self) -> Optional[DialogueNode]:
        """
        获取当前对话节点
        
        Returns:
            当前对话节点
        """
        if self.current_dialogue:
            return self.dialogues.get(self.current_dialogue)
        return None
    
    def select_option(self, option_index: int) -> bool:
        """
        选择对话选项
        
        Args:
            option_index: 选项索引
            
        Returns:
            是否成功选择
        """
        if not self.current_npc or not self.current_player:
            return False
        
        node = self.get_current_node()
        if not node:
            return False
        
        available_options = node.get_available_options(
            self.current_npc,
            self.current_player
        )
        
        if 0 <= option_index < len(available_options):
            option = available_options[option_index]
            logger.info(f"选择对话选项: {option.text}")
            return option.execute(self.current_npc, self.current_player)
        
        return False
    
    def end_dialogue(self):
        """结束对话"""
        if self.current_npc:
            logger.info(f"与 {self.current_npc.name} 的对话结束")
        
        self.current_dialogue = None
        self.current_npc = None
        self.current_player = None
    
    def add_dialogue_node(self, node: DialogueNode):
        """
        添加对话节点
        
        Args:
            node: 对话节点
        """
        self.dialogues[node.node_id] = node
        logger.debug(f"添加对话节点: {node.node_id}")
    
    # 对话选项效果函数
    
    def _start_trade(self, npc: NPC, player: Player) -> bool:
        """
        开始交易
        
        Args:
            npc: NPC实例
            player: 玩家实例
            
        Returns:
            是否成功
        """
        logger.info(f"与 {npc.name} 开始交易")
        # 实际交易逻辑需要交易系统支持
        return True
    
    def _show_missions(self, npc: NPC, player: Player) -> bool:
        """
        显示任务
        
        Args:
            npc: NPC实例
            player: 玩家实例
            
        Returns:
            是否成功
        """
        logger.info(f"{npc.name} 显示可用任务")
        # 实际任务逻辑需要任务系统支持
        if npc.mission:
            logger.info(f"当前任务: {npc.mission}")
        else:
            logger.info("没有可用任务")
        return True
    
    def _show_info(self, npc: NPC, player: Player) -> bool:
        """
        显示信息
        
        Args:
            npc: NPC实例
            player: 玩家实例
            
        Returns:
            是否成功
        """
        logger.info(f"{npc.name} 分享信息")
        # 可以显示关于周围环境、其他NPC等信息
        return True
    
    def _start_follow(self, npc: NPC, player: Player) -> bool:
        """
        开始跟随
        
        Args:
            npc: NPC实例
            player: 玩家实例
            
        Returns:
            是否成功
        """
        if npc.is_friendly():
            npc.follow_player = True
            logger.info(f"{npc.name} 开始跟随玩家")
            return True
        else:
            logger.info(f"{npc.name} 拒绝跟随")
            return False
    
    def _end_dialogue(self, npc: NPC, player: Player) -> bool:
        """
        结束对话
        
        Args:
            npc: NPC实例
            player: 玩家实例
            
        Returns:
            是否成功
        """
        self.end_dialogue()
        return True
    
    def _attempt_calm(self, npc: NPC, player: Player) -> bool:
        """
        尝试安抚NPC
        
        Args:
            npc: NPC实例
            player: 玩家实例
            
        Returns:
            是否成功
        """
        # 根据玩家的speech技能来判断是否成功
        # 这里简单地增加一点态度值
        npc.adjust_attitude(10)
        logger.info(f"尝试安抚 {npc.name}，态度变为 {npc.attitude}")
        
        # 如果态度变为中立，切换到中立对话
        if not npc.is_hostile():
            self.current_dialogue = "neutral_greeting"
            return True
        
        return False
    
    def _start_combat(self, npc: NPC, player: Player) -> bool:
        """
        开始战斗
        
        Args:
            npc: NPC实例
            player: 玩家实例
            
        Returns:
            是否成功
        """
        logger.info(f"与 {npc.name} 开始战斗")
        # 实际战斗逻辑需要战斗系统支持
        self.end_dialogue()
        return True
