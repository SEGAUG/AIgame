任务规则：
- 条件类型：
  - kill(monster_id, count)
  - clear(dungeon_id)
  - reach(dungeon_id)
  - item(item_id, count)
  - trigger(event_id)
- 任务字段：`id, name, desc, conds, rewards, next, dialogue_id(optional)`
  - conds: 数组的 AND；内部可支持 OR 组合（后续扩展）。
  - rewards: exp/gold/item/relic/unlock_chapter/skill。

示例：
```json
{
  "id": "q_ch1_tutorial",
  "name": "新手引导",
  "conds": ["clear:ch1_main"],
  "rewards": {"exp": 50, "gold": 30, "item": [{"id":"healing_potion","count":2}]},
  "next": "q_ch1_boss"
}
```
