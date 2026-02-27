战斗形态：保持半回合/时间轴（移动端省性能）
- 行动点 AP：默认2~3，技能消耗AP；SPD 影响行动先后（可按 SPD 排序/时间轴累积）。
- 伤害公式：Damage = ATK * Ratio - DEF（至少 1），暴击：默认5%，CRIT倍率1.5；RES 可减免部分魔法/状态。
- 技能：读取 skill_config.json；effect 简码示例：
  - bleed:x:turns 流血；def_down:x:turns；stun:p:turns；shield:x 护盾；heal:x 恢复。
- 状态：buff/debuff 有持续回合，回合结束结算。
- 行动顺序：按 SPD 排队，Boss 可有双行动。
- 资源：无MP，使用 AP；后续可加“灵力”作为技能资源。
