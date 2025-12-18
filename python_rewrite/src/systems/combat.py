"""
游戏机制系统 - 战斗系统

处理战斗相关的计算和逻辑
"""

import random
from typing import Optional

from ..utils.logger import logger
from ..utils.math_utils import roll_dice
from ..entities.character import Character
from ..entities.monster import Monster


class CombatSystem:
    """战斗系统"""

    def __init__(self):
        """初始化战斗系统"""
        logger.info("战斗系统已初始化")

    def melee_attack(self, attacker: Character, defender: Character) -> int:
        """
        近战攻击

        Args:
            attacker: 攻击者
            defender: 防御者

        Returns:
            实际造成的伤害值
        """
        # 计算命中率
        hit_chance = self.calculate_hit_chance(attacker, defender)

        # 判定是否命中
        roll = random.random() * 100
        logger.debug(f"命中判定: {roll:.1f} vs {hit_chance:.1f}")

        if roll < hit_chance:
            # 计算伤害
            damage = self.calculate_damage(attacker, defender)

            # 应用伤害
            defender.take_damage(damage)

            logger.info(f"{attacker.name} 攻击 {defender.name}，造成 {damage} 点伤害")
            return damage
        else:
            logger.info(f"{attacker.name} 的攻击未命中 {defender.name}")
            return 0

    def calculate_hit_chance(self, attacker: Character, defender: Character) -> float:
        """
        计算命中率

        Args:
            attacker: 攻击者
            defender: 防御者

        Returns:
            命中率（0-100）
        """
        # 基础命中率
        base_chance = 50.0

        # 攻击者敏捷加成
        base_chance += attacker.dex * 2

        # 防御者闪避（敏捷）
        base_chance -= defender.dex * 1.5

        # 攻击者近战技能加成
        melee_skill = attacker.get_skill_level("melee")
        base_chance += melee_skill * 3

        # 防御者闪避技能
        dodge_skill = defender.get_skill_level("dodge")
        base_chance -= dodge_skill * 2

        # 限制在0-100之间
        return max(0, min(100, base_chance))

    def calculate_damage(self, attacker: Character, defender: Character) -> int:
        """
        计算伤害

        Args:
            attacker: 攻击者
            defender: 防御者

        Returns:
            伤害值
        """
        # 基础伤害（来自武器）
        base_damage = self.get_weapon_damage(attacker)

        # 力量加成
        str_bonus = attacker.str // 2
        base_damage += str_bonus

        # 技能加成
        melee_skill = attacker.get_skill_level("melee")
        skill_bonus = melee_skill
        base_damage += skill_bonus

        # 随机波动（±20%）
        variation = random.uniform(0.8, 1.2)
        base_damage = int(base_damage * variation)

        # 护甲减免
        armor_value = self.get_armor_value(defender)
        final_damage = max(1, base_damage - armor_value)

        logger.debug(f"伤害计算: 基础={base_damage}, 护甲={armor_value}, 最终={final_damage}")

        return final_damage

    def get_weapon_damage(self, character: Character) -> int:
        """
        获取角色的武器伤害

        Args:
            character: 角色

        Returns:
            武器伤害值
        """
        weapon = character.wielded_item
        if weapon:
            weapon_type = weapon.get_type()
            if weapon_type and weapon_type.damage:
                # 返回钝击伤害（如果有）
                return weapon_type.damage.get("bash", 5)

        # 徒手伤害
        return 5

    def get_armor_value(self, character: Character) -> int:
        """
        获取角色的护甲值

        Args:
            character: 角色

        Returns:
            护甲值
        """
        total_armor = 0

        # 计算所有穿戴物品的护甲
        for worn_item in character.worn_items:
            item_type = worn_item.get_type()
            if item_type and item_type.armor:
                # 累加钝击护甲
                total_armor += item_type.armor.get("bash", 0)

        return total_armor

    def ranged_attack(self, attacker: Character, defender: Character, distance: float) -> int:
        """
        远程攻击

        Args:
            attacker: 攻击者
            defender: 防御者
            distance: 距离

        Returns:
            实际造成的伤害值
        """
        # TODO: 实现完整的远程攻击系统
        # 目前仅返回简化版本

        # 计算命中率（远程）
        base_chance = 40.0
        base_chance += attacker.dex * 2
        base_chance += attacker.per * 1.5  # 感知影响远程命中
        base_chance -= distance * 5  # 距离惩罚

        # 远程技能
        ranged_skill = attacker.get_skill_level("ranged")
        base_chance += ranged_skill * 4

        hit_chance = max(0, min(100, base_chance))

        # 判定命中
        if random.random() * 100 < hit_chance:
            # 简化的远程伤害计算
            damage = roll_dice(2, 6) + attacker.per // 2

            defender.take_damage(damage)
            logger.info(f"{attacker.name} 远程攻击 {defender.name}，造成 {damage} 点伤害")
            return damage
        else:
            logger.info(f"{attacker.name} 的远程攻击未命中 {defender.name}")
            return 0

    def apply_status_effect(self, character: Character, effect: str, duration: int):
        """
        应用状态效果

        Args:
            character: 角色
            effect: 效果类型
            duration: 持续时间
        """
        # TODO: 实现状态效果系统
        logger.info(f"{character.name} 受到 {effect} 效果，持续 {duration} 回合")

    def calculate_critical_hit(self, attacker: Character) -> bool:
        """
        判定是否暴击

        Args:
            attacker: 攻击者

        Returns:
            是否暴击
        """
        # 基础暴击率5%
        crit_chance = 5.0

        # 敏捷影响暴击率
        crit_chance += attacker.dex * 0.5

        # 技能影响
        melee_skill = attacker.get_skill_level("melee")
        crit_chance += melee_skill * 0.5

        return random.random() * 100 < crit_chance
