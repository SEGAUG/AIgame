# config_schema.md

约定（可按需扩展）：

- 资源引用：路径相对于项目根或 CDN；图片/音频异步加载。
- ID 唯一且全局稳定，后续迁移用 ID。
- 数值维度：`hp, atk, def, spd, crit, res, luck`（luck 仅部分系统用）。

## main_story_flow.json
```json
{
  "chapters": [
    {
      "id": "ch1",
      "name": "九龙拉棺·新手段",
      "unlock_cond": null,
      "entry_dungeon": "ch1_main",
      "dialogue_id": "dlg_ch1_intro",
      "quests": ["q_ch1_tutorial"]
    }
  ]
}
```
字段：`id` 章节ID；`entry_dungeon` 入口副本；`dialogue_id` 开场对话；`quests` 任务链。

## dungeons.json
```json
{
  "dungeons": [
    {
      "id": "ch1_main",
      "name": "矿洞·新手",
      "type": "story",
      "map": "assets/maps/1_1.png",
      "monsters": ["mob_slime", "mob_thief"],
      "elite": ["elite_guard"],
      "boss": "boss_keeper",
      "dropset": "drop_ch1",
      "next": "ch1_boss"
    }
  ]
}
```
字段：`type` story/side/secret；`map` 背景；`monsters/elite/boss` 列表；`dropset` 掉落表ID；`next` 下一关ID。

## skill_config.json
```json
{
  "skills": [
    {"id":"basic_atk","name":"普攻","type":"phys","cost_ap":1,"ratio":1.0,"cd":0},
    {"id":"skill_1","name":"裂石斩","type":"phys","cost_ap":1,"ratio":1.4,"cd":2,"effect":"bleed:0.05:2"},
    {"id":"skill_2","name":"源力冲击","type":"mag","cost_ap":2,"ratio":1.8,"cd":3,"effect":""},
    {"id":"skill_3","name":"碎甲","type":"phys","cost_ap":1,"ratio":1.1,"cd":2,"effect":"def_down:0.2:2"},
    {"id":"ult","name":"星河一击","type":"phys","cost_ap":3,"ratio":2.5,"cd":5,"effect":"stun:0.3:1"}
  ]
}
```
字段：`type` phys/mag/support；`ratio` 伤害系数；`effect` 状态简码。

## drop_table.json
```json
{
  "dropsets": {
    "drop_ch1": {"gold":[5,20],"exp":[8,15],"loot":["healing_potion","basic_sword"],"relic_drop":"default"}
  },
  "relic_drop_rules": {
    "default": {"rarity_weights":{"白":20,"绿":10,"蓝":5,"紫":2,"金":1,"红":0.1}}
  }
}
```

## collectibles.json
从 `data/sanguo/zhe.json` 读取，字段：`id,name,rarity,attrs:[hp,atk,def,spd,crit,res],unique`（红为 unique）。

## dialogue.json
```json
{
  "dialogs":[
    {"id":"dlg_ch1_intro","lines":[
      {"actor":"主角","avatar":"ui/actor/player.png","text":"这里是哪里？"},
      {"actor":"向导","avatar":"ui/actor/guide.png","text":"前方有异动，小心！","options":[
        {"text":"准备战斗","goto":"line3"}
      ]}
    ]}
  ]
}
```

## quest_rules.md
- 条件：kill(monster_id,count) / reach(dungeon_id) / item(item_id,count) / clear(dungeon_id)
- 任务字段：`id,name,desc,conds,rewards,next`；`rewards` 支持 exp/gold/item/relic/unlock_chapter。

## save_format.json
```json
{
  "version": 1,
  "player": {"lvl":1,"exp":0,"hp":120,"atk":18,"def":6,"spd":10,"crit":5,"res":5,"luck":0},
  "inventory": {"items":{},"relics":{},"equip":{"weapon":null,"armor":null}},
  "progress": {"chapter":"ch1","dungeon":"ch1_main","quests":{"q_ch1_tutorial":"in_progress"}},
  "settings": {"quality":"medium","controls":"touch"},
  "checksum": ""
}
```

## save_migration.md
- 含 `version` 字段；加载时：校验 checksum → 不匹配则回滚备份。
- 迁移：旧版本缺失字段填默认，新字段加默认值。
- 自动存档：关键节点（战斗结束/任务完成）；手动存档多槽位（建议 3）。

## quality_levels.md
- high: 全贴图/粒子阴影/特效LOD高/分辨率100%
- medium: 贴图中/粒子减半/LOD中/分辨率75%
- low: 贴图低/关闭阴影/LOD低/分辨率50%

## asset_budget.csv
列：`category,max_count,notes`。示例：`texture,200MB,贴图总预算`。

## ui_layout_rules.md
- 触控热区≥48dp；安全区留边；UI可缩放（0.8–1.2）。
- 移动端优先右下技能区、左下摇杆；对话弹窗底部/中部。  
