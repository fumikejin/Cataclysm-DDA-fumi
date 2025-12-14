"""
测试 - NPC对话系统
"""

import pytest
from src.ai.npc_talk import (
    NPCTalk, 
    DialogueNode, 
    DialogueOption, 
    DialogueResponseType
)
from src.entities.npc import NPC
from src.entities.player import Player


@pytest.fixture
def npc_talk():
    """创建NPC对话系统"""
    return NPCTalk()


@pytest.fixture
def friendly_npc():
    """创建友好NPC"""
    npc = NPC("FriendlyNPC")
    npc.personality = "friendly"
    npc.attitude = 50
    return npc


@pytest.fixture
def neutral_npc():
    """创建中立NPC"""
    npc = NPC("NeutralNPC")
    npc.personality = "neutral"
    npc.attitude = 0
    return npc


@pytest.fixture
def hostile_npc():
    """创建敌对NPC"""
    npc = NPC("HostileNPC")
    npc.personality = "aggressive"
    npc.attitude = -50
    return npc


@pytest.fixture
def player_char():
    """创建玩家"""
    return Player("TestPlayer")


def test_npc_talk_initialization():
    """测试对话系统初始化"""
    talk = NPCTalk()
    assert len(talk.dialogues) > 0
    assert "friendly_greeting" in talk.dialogues
    assert "neutral_greeting" in talk.dialogues
    assert "hostile_greeting" in talk.dialogues


def test_dialogue_option_creation():
    """测试对话选项创建"""
    option = DialogueOption(
        "测试选项",
        DialogueResponseType.INFO
    )
    
    assert option.text == "测试选项"
    assert option.response_type == DialogueResponseType.INFO


def test_dialogue_option_with_condition():
    """测试带条件的对话选项"""
    condition = lambda npc, player: npc.is_friendly()
    
    option = DialogueOption(
        "友好选项",
        DialogueResponseType.FOLLOW,
        condition=condition
    )
    
    friendly = NPC("Friendly")
    friendly.attitude = 50
    hostile = NPC("Hostile")
    hostile.attitude = -50
    player = Player("Player")
    
    assert option.is_available(friendly, player) is True
    assert option.is_available(hostile, player) is False


def test_dialogue_node_creation():
    """测试对话节点创建"""
    options = [
        DialogueOption("选项1", DialogueResponseType.INFO),
        DialogueOption("选项2", DialogueResponseType.TRADE),
    ]
    
    node = DialogueNode("test_node", "测试对话", options)
    
    assert node.node_id == "test_node"
    assert node.npc_text == "测试对话"
    assert len(node.options) == 2


def test_dialogue_node_available_options():
    """测试对话节点获取可用选项"""
    options = [
        DialogueOption("总是可用", DialogueResponseType.INFO),
        DialogueOption(
            "需要友好",
            DialogueResponseType.FOLLOW,
            condition=lambda npc, player: npc.is_friendly()
        ),
    ]
    
    node = DialogueNode("test", "测试", options)
    
    friendly = NPC("Friendly")
    friendly.attitude = 50
    player = Player("Player")
    
    available = node.get_available_options(friendly, player)
    assert len(available) == 2  # 两个都可用
    
    hostile = NPC("Hostile")
    hostile.attitude = -50
    
    available = node.get_available_options(hostile, player)
    assert len(available) == 1  # 只有一个可用


def test_start_dialogue_with_friendly_npc(npc_talk, friendly_npc, player_char):
    """测试与友好NPC开始对话"""
    node = npc_talk.start_dialogue(friendly_npc, player_char)
    
    assert node is not None
    assert npc_talk.current_npc == friendly_npc
    assert npc_talk.current_player == player_char
    assert npc_talk.current_dialogue == "friendly_greeting"


def test_start_dialogue_with_neutral_npc(npc_talk, neutral_npc, player_char):
    """测试与中立NPC开始对话"""
    node = npc_talk.start_dialogue(neutral_npc, player_char)
    
    assert node is not None
    assert npc_talk.current_dialogue == "neutral_greeting"


def test_start_dialogue_with_hostile_npc(npc_talk, hostile_npc, player_char):
    """测试与敌对NPC开始对话"""
    node = npc_talk.start_dialogue(hostile_npc, player_char)
    
    assert node is not None
    assert npc_talk.current_dialogue == "hostile_greeting"


def test_get_current_node(npc_talk, friendly_npc, player_char):
    """测试获取当前对话节点"""
    npc_talk.start_dialogue(friendly_npc, player_char)
    
    node = npc_talk.get_current_node()
    assert node is not None
    assert node.node_id == "friendly_greeting"


def test_select_valid_option(npc_talk, friendly_npc, player_char):
    """测试选择有效的对话选项"""
    npc_talk.start_dialogue(friendly_npc, player_char)
    
    node = npc_talk.get_current_node()
    available_options = node.get_available_options(friendly_npc, player_char)
    
    if len(available_options) > 0:
        result = npc_talk.select_option(0)
        # 结果取决于选项效果


def test_select_invalid_option(npc_talk, friendly_npc, player_char):
    """测试选择无效的对话选项"""
    npc_talk.start_dialogue(friendly_npc, player_char)
    
    result = npc_talk.select_option(999)
    assert result is False


def test_end_dialogue(npc_talk, friendly_npc, player_char):
    """测试结束对话"""
    npc_talk.start_dialogue(friendly_npc, player_char)
    assert npc_talk.current_npc is not None
    
    npc_talk.end_dialogue()
    assert npc_talk.current_npc is None
    assert npc_talk.current_player is None
    assert npc_talk.current_dialogue is None


def test_add_custom_dialogue_node(npc_talk):
    """测试添加自定义对话节点"""
    custom_node = DialogueNode(
        "custom_node",
        "自定义对话",
        [DialogueOption("选项", DialogueResponseType.INFO)]
    )
    
    npc_talk.add_dialogue_node(custom_node)
    
    assert "custom_node" in npc_talk.dialogues


def test_trade_effect(npc_talk, friendly_npc, player_char):
    """测试交易效果"""
    result = npc_talk._start_trade(friendly_npc, player_char)
    assert result is True


def test_mission_effect(npc_talk, friendly_npc, player_char):
    """测试任务效果"""
    result = npc_talk._show_missions(friendly_npc, player_char)
    assert result is True


def test_info_effect(npc_talk, friendly_npc, player_char):
    """测试信息效果"""
    result = npc_talk._show_info(friendly_npc, player_char)
    assert result is True


def test_follow_effect_friendly(npc_talk, friendly_npc, player_char):
    """测试友好NPC跟随效果"""
    result = npc_talk._start_follow(friendly_npc, player_char)
    assert result is True
    assert friendly_npc.follow_player is True


def test_follow_effect_hostile(npc_talk, hostile_npc, player_char):
    """测试敌对NPC拒绝跟随"""
    result = npc_talk._start_follow(hostile_npc, player_char)
    assert result is False
    assert hostile_npc.follow_player is False


def test_calm_effect(npc_talk, hostile_npc, player_char):
    """测试安抚效果"""
    original_attitude = hostile_npc.attitude
    
    result = npc_talk._attempt_calm(hostile_npc, player_char)
    
    assert hostile_npc.attitude > original_attitude


def test_calm_changes_dialogue(npc_talk, player_char):
    """测试安抚改变对话"""
    npc = NPC("TestNPC")
    npc.attitude = -10  # 轻微敌对
    
    npc_talk.start_dialogue(npc, player_char)
    assert npc_talk.current_dialogue == "hostile_greeting"
    
    # 安抚使其变为中立
    npc_talk._attempt_calm(npc, player_char)
    
    if not npc.is_hostile():
        assert npc_talk.current_dialogue == "neutral_greeting"


def test_combat_effect(npc_talk, hostile_npc, player_char):
    """测试战斗效果"""
    npc_talk.start_dialogue(hostile_npc, player_char)
    
    result = npc_talk._start_combat(hostile_npc, player_char)
    assert result is True
    assert npc_talk.current_dialogue is None  # 对话应该结束


def test_dialogue_option_execution():
    """测试对话选项执行"""
    executed = []
    
    def effect(npc, player):
        executed.append(True)
        return True
    
    option = DialogueOption(
        "测试",
        DialogueResponseType.INFO,
        effect=effect
    )
    
    npc = NPC("Test")
    player = Player("Player")
    
    result = option.execute(npc, player)
    assert result is True
    assert len(executed) == 1


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
