import json
import random
import time
import tkinter as tk
import threading
import urllib.request
import urllib.error
from pathlib import Path
from datetime import date
from tkinter import messagebox, ttk
import re
import subprocess

# Paths
ROOT = Path(__file__).parent
MAZE_FILE_CH1 = ROOT / "data" / "mazes" / "ch1_mine_maze.json"
MAZE_FILE_CH2 = ROOT / "data" / "mazes" / "ch2_bronze_maze.json"
RELIC_FILE = ROOT / "data" / "sanguo" / "zhe.json"
DIALOG_FILE = ROOT / "config" / "dialogue.json"
EQUIP_CATALOG_FILE = ROOT / "config" / "equipment_catalog.json"
TREASURE_CATALOG_FILE = ROOT / "config" / "treasure_catalog.json"
MOUNT_CATALOG_FILE = ROOT / "config" / "mount_catalog.json"
FACTIONS_FILE = ROOT / "config" / "factions.json"
STORY_FILE = ROOT / "config" / "story.json"
MAP_IMAGE = ROOT / "assets" / "maps" / "1_1.png"
SAVE_DIR = ROOT / "data" / "saves"
SAVE_FILE = SAVE_DIR / "save.json"
GRAVEYARD_FILE = SAVE_DIR / "graveyard.json"
NPC_ARCHIVE_FILE = SAVE_DIR / "npc_archive.json"
MODEL_DIR = ROOT / "models"
MODEL_PATH = MODEL_DIR / "Qwen2.5-0.5B-Instruct-Q4_K_M.gguf"
LLAMA_BIN = ROOT / "llama.cpp" / "build" / "bin" / "llama-cli.exe"
LLAMA_SERVER_BIN = ROOT / "llama.cpp" / "build" / "bin" / "llama-server.exe"
LLAMA_SERVER_HOST = "127.0.0.1"
LLAMA_SERVER_PORT = 8088
LLAMA_REQUIRED_DLLS = ["ggml.dll", "llama.dll"]

# Chapter plan：前两章用文件，后两章用程序生成
CHAPTER_PLAN = [
    {"id": "ch1", "name": "矿道·新手", "kind": "file", "path": MAZE_FILE_CH1, "scale": 1.0, "lvl_req": 1, "goal": {"battles": 6}, "faction": "human", "story": "人族开辟矿道，妖影初现。"},
    {"id": "ch2", "name": "青铜秘境", "kind": "file", "path": MAZE_FILE_CH2, "scale": 1.25, "lvl_req": 3, "goal": {"elites": 2}, "faction": "yao", "story": "妖族在古铜秘境设伏。"},
    {"id": "ch3", "name": "荒土试炼", "kind": "proc", "size": 36, "seed": 1337, "scale": 1.55, "lvl_req": 5, "goal": {"battles": 8, "elites": 3}, "faction": "mo", "story": "魔气侵入荒土，试炼开端。"},
    {"id": "ch4", "name": "星路终局", "kind": "proc", "size": 44, "seed": 2026, "scale": 1.9, "lvl_req": 7, "goal": {"boss": 1}, "faction": "xian", "story": "仙族设下星路终局试炼。"},
    {"id": "ch5", "name": "风砂古道", "kind": "proc", "size": 48, "seed": 3033, "scale": 2.2, "lvl_req": 9, "goal": {"mounts": 1}, "faction": "human", "story": "人族旧道重开，争夺灵材。"},
    {"id": "ch6", "name": "寒渊裂隙", "kind": "proc", "size": 52, "seed": 4096, "scale": 2.5, "lvl_req": 11, "goal": {"elites": 4}, "faction": "yao", "story": "妖族寒渊裂隙试探。"},
    {"id": "ch7", "name": "云海幻域", "kind": "proc", "size": 56, "seed": 5129, "scale": 2.8, "lvl_req": 13, "goal": {"battles": 10}, "faction": "mo", "story": "魔族在云海布下幻阵。"},
    {"id": "ch8", "name": "玄火禁庭", "kind": "proc", "size": 60, "seed": 6222, "scale": 3.1, "lvl_req": 15, "goal": {"boss": 1, "elites": 4}, "faction": "xian", "story": "仙族玄火禁庭，强者试炼。"},
    {"id": "ch9", "name": "时隙回廊", "kind": "proc", "size": 64, "seed": 7012, "scale": 3.4, "lvl_req": 17, "goal": {"relics": 2}, "faction": "human", "story": "人族与各族争夺时隙遗宝。"},
    {"id": "ch10", "name": "万界归墟", "kind": "proc", "size": 70, "seed": 8088, "scale": 3.8, "lvl_req": 20, "goal": {"boss": 2}, "faction": "mo", "story": "万界归墟，魔族终局之战。"},
]

# Story NPCs and chapter arcs
DEFAULT_STORY_NPCS = [
    {"id": "npc_tieshuo", "name": "铁烁", "title": "玄铁铺主", "faction": "human",
     "background": "边城铁匠，昔年随军征战，右臂旧伤未愈。",
     "skills": ["断刃回炉", "焚火锻体"], "item": "玄铁火钳"},
    {"id": "npc_lubaichuan", "name": "陆白川", "title": "白川书生", "faction": "human",
     "background": "书院弃徒，研读禁卷被逐，仍以文止兵。",
     "skills": ["文心定魄", "纸雨"], "item": "墨纹书卷"},
    {"id": "npc_fengyin", "name": "风吟", "title": "影河游侠", "faction": "neutral",
     "background": "游侠，寻失散同伴，熟悉各族地界。",
     "skills": ["影步", "短弓连射"], "item": "影河短弓"},
    {"id": "npc_shuangheng", "name": "霜蘅", "title": "寒渊侍女", "faction": "yao",
     "background": "寒渊守护者，守护封印之门。",
     "skills": ["霜结", "冰心"], "item": "寒玉坠"},
    {"id": "npc_yance", "name": "焱策", "title": "炎庭执事", "faction": "xian",
     "background": "玄火禁庭执事，维持试炼秩序。",
     "skills": ["炎戒", "威仪"], "item": "玄火令"},
    {"id": "npc_yanxing", "name": "魇行", "title": "黑雾猎手", "faction": "mo",
     "background": "魔域追猎者，擅长追踪与伏击。",
     "skills": ["黑雾潜袭", "恐惧刃"], "item": "魇影匕"},
    {"id": "npc_muli", "name": "木漓", "title": "林雾药师", "faction": "human",
     "background": "隐居林雾谷，专精药理与灵草。",
     "skills": ["回春", "毒雾"], "item": "青木药囊"},
    {"id": "npc_tingheng", "name": "霆衡", "title": "雷殿巡守", "faction": "xian",
     "background": "雷殿巡守，镇压天雷异常。",
     "skills": ["雷引", "天罡护体"], "item": "雷纹护符"},
    {"id": "npc_moxing", "name": "莫行", "title": "沙原商旅", "faction": "neutral",
     "background": "沙原商队领队，行走四方换物。",
     "skills": ["趁势", "机巧烟幕"], "item": "沙银交易印"},
    {"id": "npc_yuechi", "name": "月迟", "title": "残月剑客", "faction": "human",
     "background": "昔日剑宗弟子，宗门覆灭后独行。",
     "skills": ["残月斩", "剑意"], "item": "残月剑痕"},
    {"id": "npc_yuanji", "name": "渊姬", "title": "幽潭引魂", "faction": "yao",
     "background": "守潭妖灵，擅长操控水魂。",
     "skills": ["泉魂缠身", "逆潮"], "item": "幽潭水镜"},
    {"id": "npc_guiheng", "name": "归衡", "title": "星桥司仪", "faction": "xian",
     "background": "掌管星路试炼的司仪，执秩序之责。",
     "skills": ["星辉裁决", "星桥禁行"], "item": "星桥印"},
    {"id": "npc_shijiang", "name": "石匠", "title": "荒土拾骨", "faction": "human",
     "background": "战场拾骨人，懂墓葬与机关。",
     "skills": ["破障", "祈骨"], "item": "荒骨匠钉"},
    {"id": "npc_yingxi", "name": "影栖", "title": "暗市匿客", "faction": "neutral",
     "background": "暗市交易者，消息灵通。",
     "skills": ["隐息", "漏信"], "item": "暗市徽"},
    {"id": "npc_kongshu", "name": "空疏", "title": "白鹤旅僧", "faction": "xian",
     "background": "游历四方的修行僧，心性平和。",
     "skills": ["清心", "慈悲"], "item": "白鹤念珠"},
    {"id": "npc_lusheng", "name": "炉笙", "title": "赤纹炼器", "faction": "human",
     "background": "炼器师，执着打造最强器胚。",
     "skills": ["熔金", "破炉"], "item": "炉心石"},
    {"id": "npc_rongdong", "name": "绒冬", "title": "雪原驭兽", "faction": "yao",
     "background": "驭兽者，与雪原异兽共生。",
     "skills": ["兽吼", "同心"], "item": "雪原兽铃"},
    {"id": "npc_jiangdi", "name": "江堤", "title": "断桥守卒", "faction": "human",
     "background": "守桥军残部，誓守古桥不退。",
     "skills": ["守势", "反击"], "item": "断桥盾"},
    {"id": "npc_jinyu", "name": "烬语", "title": "幽火术士", "faction": "mo",
     "background": "魔域术士，迷恋幽火的灵魂灼烧。",
     "skills": ["幽火", "心焰"], "item": "幽火灯"},
    {"id": "npc_jianglin", "name": "绛临", "title": "时隙旅者", "faction": "neutral",
     "background": "穿行时隙，记忆断裂者。",
     "skills": ["时停", "残影"], "item": "时砂瓶"},
]

DEFAULT_STORY_CHAPTERS = {
    "ch1": {
        "main": "你在矿道中第一次与妖影交锋，意识到异族活动异常频繁。",
        "side": [
            {"id": "ch1_q1", "name": "矿道清剿", "desc": "击败战斗 3 次", "targets": {"battles": 3}, "reward": {"gold": 20, "exp": 15}},
            {"id": "ch1_q2", "name": "矿脉宝材", "desc": "收集宝材 1 份", "targets": {"treasures": 1}, "reward": {"gold": 15, "exp": 10}},
            {"id": "ch1_q3", "name": "访见工匠", "desc": "与NPC对话 1 次", "targets": {"talk": 1}, "reward": {"gold": 10, "exp": 5}},
        ],
        "npcs": ["npc_tieshuo", "npc_lubaichuan"],
    },
    "ch2": {
        "main": "青铜秘境的祭坛被妖族掌控，你必须夺回阵眼。",
        "side": [
            {"id": "ch2_q1", "name": "秘境精英", "desc": "击败精英 2 次", "targets": {"elites": 2}, "reward": {"gold": 25, "exp": 20}},
            {"id": "ch2_q2", "name": "秘境线索", "desc": "与NPC对话 2 次", "targets": {"talk": 2}, "reward": {"gold": 15, "exp": 10}},
        ],
        "npcs": ["npc_fengyin", "npc_shuangheng"],
    },
    "ch3": {
        "main": "荒土试炼揭露魔族的斥候布局，你被迫迎战。",
        "side": [
            {"id": "ch3_q1", "name": "荒土猎影", "desc": "击败战斗 5 次", "targets": {"battles": 5}, "reward": {"gold": 30, "exp": 25}},
            {"id": "ch3_q2", "name": "暗影刺探", "desc": "与NPC对话 1 次", "targets": {"talk": 1}, "reward": {"gold": 12, "exp": 8}},
        ],
        "npcs": ["npc_yanxing", "npc_muli"],
    },
    "ch4": {
        "main": "星路终局的试炼考验你的心性与战斗节奏。",
        "side": [
            {"id": "ch4_q1", "name": "星路守关", "desc": "击败首领 1 次", "targets": {"boss": 1}, "reward": {"gold": 40, "exp": 35}},
            {"id": "ch4_q2", "name": "星桥低语", "desc": "与NPC对话 2 次", "targets": {"talk": 2}, "reward": {"gold": 18, "exp": 12}},
        ],
        "npcs": ["npc_tingheng", "npc_guiheng"],
    },
    "ch5": {
        "main": "风砂古道重开，各族争夺灵材与补给。",
        "side": [
            {"id": "ch5_q1", "name": "商旅护送", "desc": "击败战斗 4 次", "targets": {"battles": 4}, "reward": {"gold": 35, "exp": 28}},
            {"id": "ch5_q2", "name": "坐骑线索", "desc": "获得坐骑 1 次", "targets": {"mounts": 1}, "reward": {"gold": 20, "exp": 15}},
        ],
        "npcs": ["npc_moxing", "npc_yuechi"],
    },
    "ch6": {
        "main": "寒渊裂隙不断扩张，你必须封闭裂隙核心。",
        "side": [
            {"id": "ch6_q1", "name": "寒渊守望", "desc": "击败精英 2 次", "targets": {"elites": 2}, "reward": {"gold": 35, "exp": 28}},
            {"id": "ch6_q2", "name": "寒渊引魂", "desc": "与NPC对话 2 次", "targets": {"talk": 2}, "reward": {"gold": 18, "exp": 12}},
        ],
        "npcs": ["npc_yuanji", "npc_shijiang"],
    },
    "ch7": {
        "main": "云海幻域的幻阵让真伪难辨，只有破阵才能前进。",
        "side": [
            {"id": "ch7_q1", "name": "幻域清道", "desc": "击败战斗 6 次", "targets": {"battles": 6}, "reward": {"gold": 45, "exp": 35}},
            {"id": "ch7_q2", "name": "暗市交易", "desc": "与NPC对话 1 次", "targets": {"talk": 1}, "reward": {"gold": 20, "exp": 15}},
        ],
        "npcs": ["npc_yingxi", "npc_lusheng"],
    },
    "ch8": {
        "main": "玄火禁庭只允强者踏入，试炼将决定你的去留。",
        "side": [
            {"id": "ch8_q1", "name": "禁庭首领", "desc": "击败首领 1 次", "targets": {"boss": 1}, "reward": {"gold": 55, "exp": 45}},
            {"id": "ch8_q2", "name": "仙庭旧事", "desc": "与NPC对话 2 次", "targets": {"talk": 2}, "reward": {"gold": 22, "exp": 16}},
        ],
        "npcs": ["npc_kongshu", "npc_rongdong"],
    },
    "ch9": {
        "main": "时隙回廊揭示旧世遗民的记忆，你开始怀疑自己的身世。",
        "side": [
            {"id": "ch9_q1", "name": "时隙遗宝", "desc": "获得收藏品 1 次", "targets": {"relics": 1}, "reward": {"gold": 45, "exp": 35}},
            {"id": "ch9_q2", "name": "回廊访谈", "desc": "与NPC对话 2 次", "targets": {"talk": 2}, "reward": {"gold": 20, "exp": 15}},
        ],
        "npcs": ["npc_jiangdi", "npc_jianglin"],
    },
    "ch10": {
        "main": "万界归墟之战拉开帷幕，你的选择将决定四族未来。",
        "side": [
            {"id": "ch10_q1", "name": "终局猎首", "desc": "击败首领 2 次", "targets": {"boss": 2}, "reward": {"gold": 80, "exp": 60}},
            {"id": "ch10_q2", "name": "终局誓言", "desc": "与NPC对话 2 次", "targets": {"talk": 2}, "reward": {"gold": 30, "exp": 20}},
        ],
        "npcs": ["npc_jinyu", "npc_yance"],
    },
}


def load_story_config(path: Path):
    if not path.exists():
        return DEFAULT_STORY_NPCS, DEFAULT_STORY_CHAPTERS
    try:
        data = load_json(path)
        npcs = data.get("npcs") or []
        chapters = data.get("chapters") or {}
        if not npcs or not chapters:
            return DEFAULT_STORY_NPCS, DEFAULT_STORY_CHAPTERS
        return npcs, chapters
    except Exception:
        return DEFAULT_STORY_NPCS, DEFAULT_STORY_CHAPTERS


STORY_NPCS = DEFAULT_STORY_NPCS
STORY_CHAPTERS = DEFAULT_STORY_CHAPTERS
STORY_NPC_BY_ID = {n["id"]: n for n in STORY_NPCS}
# Secret dungeons
SECRET_DUNGEON_POOL = [
    {"id": "sd1", "name": "流沙密窟", "lvl_req": 5, "size": 28, "scale": 1.2},
    {"id": "sd2", "name": "冰封隧道", "lvl_req": 8, "size": 30, "scale": 1.35},
    {"id": "sd3", "name": "藤蔓古林", "lvl_req": 10, "size": 32, "scale": 1.5},
    {"id": "sd4", "name": "熔岩裂谷", "lvl_req": 12, "size": 34, "scale": 1.65},
    {"id": "sd5", "name": "风暴高地", "lvl_req": 14, "size": 36, "scale": 1.8},
    {"id": "sd6", "name": "迷雾湖底", "lvl_req": 16, "size": 30, "scale": 1.4},
    {"id": "sd7", "name": "断塔遗迹", "lvl_req": 18, "size": 38, "scale": 1.95},
    {"id": "sd8", "name": "虚空裂隙", "lvl_req": 20, "size": 40, "scale": 2.1},
]

# Cultivation system
ELEMENTS = ["金", "木", "水", "火", "土", "时间", "空间"]
MUTATION_MAP = {
    "金": "锋",
    "木": "毒",
    "水": "冰",
    "火": "雷",
    "土": "岩",
    "时间": "岁月",
    "空间": "虚空",
}
TIERS = ["黄", "玄", "地", "天", "神"]
METHOD_SUFFIXES = ["诀", "经", "录", "典", "咒", "谱", "法", "图", "印", "章"]
CULTIVATION_STAGES = [
    {"name": "入门", "need": 50},
    {"name": "小成", "need": 120, "skill": True},
    {"name": "中期", "need": 220},
    {"name": "大成", "need": 360, "skill": True},
    {"name": "圆满", "need": 520, "skill": True, "insight_gain": True},
]
ELEMENT_BONUS_WEIGHTS = {
    "金": {"atk": 2, "crit": 1},
    "木": {"max_hp": 8, "res": 1},
    "水": {"def": 2, "res": 1},
    "火": {"atk": 2, "spd": 1},
    "土": {"max_hp": 10, "def": 2},
    "时间": {"spd": 2, "luck": 1},
    "空间": {"crit": 2, "res": 1},
}
STAGE_BONUS_SCALE = {1: 1, 2: 1, 3: 2, 4: 2, 5: 3}
TREASURE_TIERS = ["黄", "玄", "地", "天", "神"]
TREASURE_TIER_WEIGHTS = [("黄", 10), ("玄", 6), ("地", 3), ("天", 1.5), ("神", 0.6)]
TREASURE_BONUS_SCALE = {"黄": 1, "玄": 2, "地": 3, "天": 4, "神": 5}
ALCHEMY_SUCCESS = {"黄": 0.9, "玄": 0.8, "地": 0.65, "天": 0.5, "神": 0.35}
ALCHEMY_CRIT = {"黄": 0.05, "玄": 0.08, "地": 0.12, "天": 0.16, "神": 0.2}
GEAR_TIER_THRESHOLDS = [
    ("黄", 8),
    ("玄", 12),
    ("地", 16),
    ("天", 20),
    ("神", 24),
]
GEAR_REFINE_CAP = {"黄": 2, "玄": 3, "地": 4, "天": 5, "神": 6}
GEAR_KINDS = {
    "weapon": ["剑", "刀", "枪", "弓", "杖"],
    "armor": ["轻甲", "重甲", "法袍", "护甲"],
    "accessory": ["戒", "佩", "链", "符", "坠"],
}
ORE_CATALOG = [
    {"id": "精铁矿", "tier": "黄", "equip": "武器/工具", "desc": "百炼之基，最稳的初阶锻材。"},
    {"id": "赤铁矿", "tier": "黄", "equip": "武器", "desc": "火性炽烈，适合强化攻势。"},
    {"id": "黝铁矿", "tier": "黄", "equip": "护甲", "desc": "质地坚实，偏向防御。"},
    {"id": "青铜矿", "tier": "黄", "equip": "器具", "desc": "韧性佳，适合作为器胚。"},
    {"id": "赤铜矿", "tier": "黄", "equip": "饰品", "desc": "温和易融，适配法器饰件。"},
    {"id": "黑岩矿", "tier": "黄", "equip": "护甲", "desc": "岩脉初凝，可稳固铠甲。"},
    {"id": "砂金矿", "tier": "黄", "equip": "饰品", "desc": "细金成沙，利于细节雕琢。"},
    {"id": "玄铁矿", "tier": "玄", "equip": "武器/护甲", "desc": "玄纹内敛，硬度大幅提升。"},
    {"id": "紫铜矿", "tier": "玄", "equip": "器胚", "desc": "导灵性佳，适合刻阵。"},
    {"id": "青银矿", "tier": "玄", "equip": "饰品", "desc": "银性清凉，利于守心。"},
    {"id": "银矿", "tier": "玄", "equip": "饰品", "desc": "灵性通达，常用于法饰。"},
    {"id": "玄晶矿", "tier": "玄", "equip": "宝石/镶嵌", "desc": "晶体纯净，可容灵纹。"},
    {"id": "冰纹矿", "tier": "玄", "equip": "护甲", "desc": "寒纹凝结，提升抗性。"},
    {"id": "炼心石", "tier": "玄", "equip": "饰品", "desc": "心火淬炼，稳住气机。"},
    {"id": "星铁矿", "tier": "地", "equip": "武器", "desc": "星陨遗铁，锋锐更甚。"},
    {"id": "云纹银", "tier": "地", "equip": "饰品", "desc": "云纹流转，灵息顺畅。"},
    {"id": "金矿", "tier": "地", "equip": "器胚/饰品", "desc": "金性稳定，适配高阶器件。"},
    {"id": "玄金砂", "tier": "地", "equip": "器胚", "desc": "金砂细密，便于重塑。"},
    {"id": "霜晶矿", "tier": "地", "equip": "护甲", "desc": "霜晶厚重，抗性更强。"},
    {"id": "赤焰晶", "tier": "地", "equip": "武器", "desc": "焰晶凝火，强化输出。"},
    {"id": "灵石", "tier": "地", "equip": "通用", "desc": "灵性充足，可充作核心材料。"},
    {"id": "天外陨铁", "tier": "天", "equip": "武器", "desc": "天外陨落，锐不可当。"},
    {"id": "龙纹金", "tier": "天", "equip": "器胚", "desc": "龙纹自生，承载强力符阵。"},
    {"id": "星砂晶", "tier": "天", "equip": "饰品", "desc": "星砂凝晶，灵性外放。"},
    {"id": "玄冰晶", "tier": "天", "equip": "护甲", "desc": "玄冰凝晶，极强抗性。"},
    {"id": "霞光银", "tier": "天", "equip": "饰品", "desc": "霞光环绕，提升灵性。"},
    {"id": "太乙铜", "tier": "天", "equip": "器胚", "desc": "太乙之铜，可作主骨。"},
    {"id": "霜心石", "tier": "天", "equip": "护甲", "desc": "霜心凝结，提升守势。"},
    {"id": "太初神铁", "tier": "神", "equip": "武器/护甲", "desc": "太初遗铁，万器之首。"},
    {"id": "万相灵金", "tier": "神", "equip": "器胚", "desc": "万相随形，适配百般器型。"},
    {"id": "乾坤玄晶", "tier": "神", "equip": "宝石/镶嵌", "desc": "乾坤蕴藏，可承大道。"},
    {"id": "混元灵石", "tier": "神", "equip": "通用", "desc": "混元之源，锻器核心。"},
    {"id": "龙髓晶", "tier": "神", "equip": "武器", "desc": "龙髓凝晶，锋芒毕露。"},
    {"id": "虚空陨晶", "tier": "神", "equip": "饰品", "desc": "虚空遗晶，护持元神。"},
    {"id": "道纹神金", "tier": "神", "equip": "器胚", "desc": "道纹天成，承载神兵。"},
]

def build_ore_maps():
    tier_map = {}
    tier_list = {t: [] for t in TIERS}
    item_set = set()
    for ore in ORE_CATALOG:
        oid = ore["id"]
        tier = ore["tier"]
        tier_map[oid] = tier
        tier_list.setdefault(tier, []).append(oid)
        item_set.add(oid)
    return tier_map, tier_list, item_set


ORE_TIER_MAP, ORE_TIER_LIST, ORE_ITEM_SET = build_ore_maps()
ORE_TIER_WEIGHTS = [("黄", 45), ("玄", 25), ("地", 15), ("天", 10), ("神", 5)]
MATERIAL_ITEM_SET = {"灵巧兽皮", "灵核碎片"}.union(ORE_ITEM_SET)

def pick_ore_by_tier(tier: str) -> str:
    choices = ORE_TIER_LIST.get(tier) or ORE_TIER_LIST.get("黄", [])
    return random.choice(choices) if choices else "精铁矿"


def pick_ore_for_rarity(rarity: str) -> str:
    if rarity == "普通":
        tier = "黄"
    elif rarity == "稀有":
        tier = weighted_choice([("黄", 50), ("玄", 35), ("地", 15)])
    else:
        tier = weighted_choice([("黄", 20), ("玄", 35), ("地", 25), ("天", 15), ("神", 5)])
    return pick_ore_by_tier(tier)


def is_ore_resource(name: str) -> bool:
    if not name:
        return False
    if name in ORE_ITEM_SET:
        return True
    return "矿" in name or "晶" in name or "石" in name


def is_material_item(name: str) -> bool:
    if not name:
        return False
    if name in MATERIAL_ITEM_SET:
        return True
    return name.startswith("treasure_") or "碎片:" in name or "蓝图:" in name or name.startswith("破境灵材·") or name.startswith("破境丹·") or name.startswith("丹方:")


DISCIPLE_PATHS = {
    "战修": {"exp": 3, "atk": 2, "spd": 1},
    "内修": {"exp": 3, "hp": 8, "res": 1},
    "器修": {"exp": 3, "def": 2, "atk": 1},
    "丹修": {"exp": 3, "hp": 6, "res": 1},
    "外修": {"exp": 3, "spd": 2, "crit": 1},
}
DISCIPLE_STAGE_NAMES = ["启蒙", "养元", "凝气", "固体", "通明", "化境"]
NPC_FOLLOW_THRESHOLD = 100
NPC_TRADE_COST = 12
NPC_GIFT_RELATION = 8
NPC_TRADE_RELATION = 2
NPC_ATTACK_RELATION_RESET = 0
NPC_BUFFS = {
    "human": {"hp": 20, "def": 2},
    "yao": {"spd": 2, "crit": 1},
    "mo": {"atk": 3, "crit": 1},
    "xian": {"res": 3, "luck": 1},
    "neutral": {"luck": 2},
}
NPC_TRADE_STOCK = [
    {"id": "回复药", "price": 10},
    {"id": "修理包", "price": 15},
    {"id": "武器图纸", "price": 25},
    {"id": "护甲图纸", "price": 25},
    {"id": "饰品图纸", "price": 25},
    {"id": "灵石", "price": 120},
    {"id": "精铁矿", "price": 12},
    {"id": "灵巧兽皮", "price": 12},
    {"id": "灵核碎片", "price": 20},
]

BREAKTHROUGH_REALMS = ["炼气", "筑基", "金丹", "元婴", "化神", "合体", "大乘", "渡劫", "真仙", "天仙"]
BREAKTHROUGH_RECIPES = {
    "炼气": {"pill": "通脉丹", "materials": ["凝气果", "灵泉露", "青灵草"]},
    "筑基": {"pill": "筑基丹", "materials": ["真元果", "紫玉芝", "玄铁根"]},
    "金丹": {"pill": "结金丹", "materials": ["九叶金莲", "赤炎砂", "玄元果"]},
    "元婴": {"pill": "结婴丹", "materials": ["化婴果", "星月露", "龙血藤", "寒髓晶"]},
    "化神": {"pill": "化神丹", "materials": ["阳烛果", "太清花", "幽冥芝", "灵魄砂"]},
    "合体": {"pill": "合体丹", "materials": ["合体灵髓", "天青玉", "玄雷木", "无相露"]},
    "大乘": {"pill": "大乘丹", "materials": ["玄元果", "苍穹芝", "玉髓晶", "万年灵藤"]},
    "渡劫": {"pill": "渡劫丹", "materials": ["天雷木", "九幽莲", "太虚砂", "紫霄晶"]},
    "真仙": {"pill": "真仙丹", "materials": ["真仙灵芝", "日月露", "星辰砂", "太初玉"]},
    "天仙": {"pill": "天仙丹", "materials": ["天仙寂灭莲", "鸿蒙石", "太古灵髓", "寂灭砂", "九天露"]},
}
BREAKTHROUGH_PILL_BONUS = {
    "炼气": 0.12,
    "筑基": 0.12,
    "金丹": 0.11,
    "元婴": 0.1,
    "化神": 0.09,
    "合体": 0.08,
    "大乘": 0.07,
    "渡劫": 0.06,
    "真仙": 0.05,
    "天仙": 0.04,
}
RECIPE_LEVEL_REQ = {
    "炼气": 1,
    "筑基": 3,
    "金丹": 5,
    "元婴": 7,
    "化神": 10,
    "合体": 13,
    "大乘": 16,
    "渡劫": 20,
    "真仙": 24,
    "天仙": 28,
}
ALCHEMY_SPECS = {
    "成丹": {"success": 0.06, "crit": 0.0},
    "凝丹": {"success": 0.0, "crit": 0.06},
}
REFINE_SPECS = {
    "器纹": {"bonus": 0.06},
    "固器": {"bonus": 0.03},
}
BREAKTHROUGH_BONUS = {
    "炼气": 0.25,
    "筑基": 0.22,
    "金丹": 0.2,
    "元婴": 0.18,
    "化神": 0.16,
    "合体": 0.14,
    "大乘": 0.12,
    "渡劫": 0.1,
    "真仙": 0.08,
    "天仙": 0.06,
}

GEAR_TIER_MATS = {
    "黄": {ORE_TIER_LIST["黄"][0]: 2, "灵巧兽皮": 1},
    "玄": {ORE_TIER_LIST["玄"][0]: 2, ORE_TIER_LIST["黄"][1]: 2, "灵巧兽皮": 2},
    "地": {ORE_TIER_LIST["地"][0]: 2, ORE_TIER_LIST["玄"][1]: 2, "灵巧兽皮": 3},
    "天": {ORE_TIER_LIST["天"][0]: 2, ORE_TIER_LIST["地"][1]: 2, "灵巧兽皮": 4},
    "神": {ORE_TIER_LIST["神"][0]: 2, ORE_TIER_LIST["天"][1]: 2, "灵巧兽皮": 5},
}
FACTION_RELICS = {
    "human": {"id": "fr_human", "name": "人族印", "rarity": "紫", "attrs": [8, 2, 2, 0, 1, 1]},
    "yao": {"id": "fr_yao", "name": "妖灵佩", "rarity": "紫", "attrs": [6, 1, 1, 2, 1, 0]},
    "mo": {"id": "fr_mo", "name": "魔焰戒", "rarity": "紫", "attrs": [4, 3, 0, 1, 2, 0]},
    "xian": {"id": "fr_xian", "name": "仙纹符", "rarity": "紫", "attrs": [6, 1, 1, 0, 0, 3]},
}
ELEMENT_COUNTERS = {
    "金": "木",
    "木": "土",
    "土": "水",
    "水": "火",
    "火": "金",
    "时间": "空间",
    "空间": "时间",
}
ELEMENT_EFFECTS = {
    "金": "stun",
    "木": "poison",
    "水": "slow",
    "火": "burn",
    "土": "shield",
    "时间": "slow",
    "空间": "stun",
}
ELEMENT_COLORS = {
    "金": "#d4af37",
    "木": "#4caf50",
    "水": "#4fc3f7",
    "火": "#ff7043",
    "土": "#a1887f",
    "时间": "#8e24aa",
    "空间": "#5c6bc0",
}
EFFECT_COLORS = {
    "burn": "#ff7043",
    "poison": "#66bb6a",
    "stun": "#fdd835",
    "slow": "#29b6f6",
    "shield": "#bdbdbd",
}
NATION_FACTIONS = [
    {"id": "human", "name": "人族"},
    {"id": "yao", "name": "妖族"},
    {"id": "mo", "name": "魔族"},
    {"id": "xian", "name": "仙族"},
]
FACTION_RELATIONS = {
    ("human", "mo"): -1,
    ("mo", "human"): -1,
    ("xian", "mo"): -1,
    ("mo", "xian"): -1,
    ("human", "yao"): -1,
    ("yao", "human"): -1,
    ("xian", "yao"): 0,
    ("yao", "xian"): 0,
    ("human", "xian"): 1,
    ("xian", "human"): 1,
}
FACTION_BONUS = {
    "human": {"max_hp": 20, "def": 2},
    "yao": {"spd": 2, "crit": 1},
    "mo": {"atk": 3, "crit": 1},
    "xian": {"res": 3, "luck": 1},
}


def build_method_catalog():
    methods = []
    for element in ELEMENTS:
        for i in range(10):
            tier_idx = i // 2
            tier = TIERS[tier_idx]
            suffix = METHOD_SUFFIXES[i]
            mid = f"{element}_{tier_idx}_{i}"
            methods.append(
                {
                    "id": mid,
                    "name": f"{tier}阶·{element}{suffix}",
                    "element": element,
                    "tier": tier,
                    "tier_idx": tier_idx,
                    "mutation": MUTATION_MAP.get(element, "异"),
                }
            )
    return methods


METHOD_CATALOG = build_method_catalog()
METHOD_BY_ID = {m["id"]: m for m in METHOD_CATALOG}


def build_elemental_treasure_catalog():
    catalog = []
    for tier in TREASURE_TIERS:
        for element in ELEMENTS:
            items = []
            for i in range(10):
                tid = f"tre_{element}_{tier}_{i+1:02d}"
                name = f"{tier}品·{element}灵材{i+1}"
                desc = f"蕴含{element}之力的{tier}品天材地宝。"
                items.append({"id": tid, "name": name, "desc": desc, "element": element, "rarity": tier})
            catalog.append({"rarity": tier, "element": element, "items": items})
    return catalog


def build_treasure_index(catalog):
    idx = {}
    for tier in catalog:
        for item in tier.get("items", []):
            idx[item["id"]] = item
    return idx

# Base stats
PLAYER_BASE = {
    "hp": 120,
    "atk": 18,
    "def": 6,
    "spd": 10,
    "crit": 5,
    "res": 5,
    "luck": 0,
    "lvl": 1,
    "exp": 0,
    "exp_next": 30,
    "free_points": 0,
}

# Enemy definitions
ENEMY_POOL = {
    "normal": [
        {"name": "矿区恶徒", "hp": 50, "atk": 10, "def": 3, "spd": 8, "crit": 3, "res": 3, "exp": 10},
        {"name": "石皮虫", "hp": 55, "atk": 12, "def": 2, "spd": 9, "crit": 4, "res": 2, "exp": 10},
    ],
    "elite": [
        {"name": "裂岩巨蜥", "hp": 90, "atk": 16, "def": 5, "spd": 9, "crit": 4, "res": 5, "exp": 20},
        {"name": "燃脉狂徒", "hp": 110, "atk": 18, "def": 6, "spd": 8, "crit": 5, "res": 6, "exp": 25},
    ],
    "boss": [
        {
            "name": "镇矿巨灵",
            "hp": 320,
            "atk": 30,
            "def": 14,
            "spd": 9,
            "crit": 8,
            "res": 10,
            "exp": 90,
            "skills": [
                {"name": "巨锤猛击", "ratio": 1.8, "effect": "stun"},
                {"name": "岩浆横扫", "ratio": 2.2, "effect": "burn"},
                {"name": "石肤护体", "ratio": 0.0, "effect": "shield"},
                {"name": "地脉崩塌", "ratio": 2.6, "effect": "quake"},
            ],
        }
    ],
}

# Loot and drop settings
LOOT_TABLE = [
    "回复药",
    "回复药",
    "basic_sword",
    "basic_armor",
    "修理包",
    "武器图纸",
    "护甲图纸",
    "饰品图纸",
    "精铁矿",
    "灵巧兽皮",
    "灵核碎片",
    "灵巧鞍具",
    "疾风缰绳",
]
LOOT_BONUS = [
    ("灵石", 0.06),
]
PILL_TIERS = ["黄", "玄", "地", "天", "神"]
PILL_BONUS = {"黄": 1, "玄": 2, "地": 3, "天": 4, "神": 5}
PILL_HP_BONUS = {"黄": 3, "玄": 5, "地": 7, "天": 9, "神": 12}
REALM_STAGES = [
    {"name": "炼气", "lvl_cap": 10, "success": 0.9},
    {"name": "筑基", "lvl_cap": 20, "success": 0.85},
    {"name": "金丹", "lvl_cap": 30, "success": 0.8},
    {"name": "元婴", "lvl_cap": 40, "success": 0.75},
    {"name": "化神", "lvl_cap": 50, "success": 0.7},
    {"name": "合体", "lvl_cap": 60, "success": 0.65},
    {"name": "大乘", "lvl_cap": 70, "success": 0.6},
    {"name": "渡劫", "lvl_cap": 80, "success": 0.55},
    {"name": "真仙", "lvl_cap": 90, "success": 0.5},
    {"name": "天仙", "lvl_cap": 100, "success": 0.45},
]
REALM_BONUS = {
    "炼气": {"max_hp": 10, "atk": 1},
    "筑基": {"max_hp": 20, "def": 2},
    "金丹": {"atk": 3, "crit": 2},
    "元婴": {"max_hp": 30, "spd": 2},
    "化神": {"atk": 4, "res": 3},
    "合体": {"max_hp": 40, "def": 3},
    "大乘": {"atk": 5, "crit": 3},
    "渡劫": {"max_hp": 50, "atk": 6, "res": 4},
    "真仙": {"atk": 7, "crit": 4, "spd": 2},
    "天仙": {"max_hp": 60, "def": 5, "res": 5},
}
BRANCHES = ["阳", "阴"]
BRANCH_BONUS = {
    "阳": {"power": 0.12, "effect_boost": 0.2},
    "阴": {"cooldown": -1, "chance": 0.05},
}
REP_TIERS = [
    {"name": "陌生", "rep": -999},
    {"name": "熟悉", "rep": 10},
    {"name": "友好", "rep": 25},
    {"name": "尊敬", "rep": 50},
    {"name": "崇敬", "rep": 80},
]
TALENT_TIERS = ["黄", "玄", "地", "天", "神"]
TALENT_BONUS_SCALE = {"黄": 1, "玄": 2, "地": 3, "天": 4, "神": 5}


def build_talent_pool():
    names = {
        "黄": ["坚韧", "利爪", "灵巧", "沉稳", "迅捷", "灵识", "护体", "胆魄", "专注", "敏锐"],
        "玄": ["铁壁", "破锋", "流影", "凝神", "疾步", "灵心", "护魂", "战意", "洞察", "预感"],
        "地": ["龙息", "裂甲", "风行", "心法", "踏浪", "通明", "魂守", "血勇", "先觉", "天听"],
        "天": ["星护", "破界", "神速", "归元", "踏空", "灵台", "护命", "战魂", "洞天", "天眼"],
        "神": ["不朽", "灭界", "光速", "归一", "踏虚", "悟道", "真身", "战神", "天命", "神觉"],
    }
    bonus_types = ["hp", "atk", "def", "spd", "crit", "res", "luck", "insight"]
    pool = []
    for tier in TALENT_TIERS:
        for i, name in enumerate(names[tier]):
            btype = bonus_types[i % len(bonus_types)]
            scale = TALENT_BONUS_SCALE[tier]
            bonus = {btype: scale}
            pool.append({"id": f"tal_{tier}_{i}", "name": f"{tier}·{name}", "tier": tier, "bonus": bonus})
    return pool


TALENT_POOL = build_talent_pool()
GOLD_DROP_RANGE = (5, 20)
RELIC_DROP_CHANCE = {"battle": 0.02, "battle_elite": 0.04, "boss": 0.08, "chest": 0.10}
UPGRADE_COSTS = [1, 2, 2, 3, 4]

# Rarity bonuses
RELIC_BONUS = {
    "红": {"luck": 5, "hp": 20, "atk": 4, "def": 2, "spd": 2, "crit": 3, "res": 2},
    "金": {"hp": 12, "atk": 3, "def": 1, "spd": 1, "crit": 1, "res": 1},
    "紫": {"hp": 8, "atk": 2, "def": 1, "spd": 1, "crit": 1, "res": 0},
    "蓝": {"hp": 5, "atk": 1, "spd": 1, "crit": 0, "res": 0},
    "绿": {"hp": 3, "atk": 0},
    "白": {"hp": 1},
}

RARITY_WEIGHTS = [("白", 20), ("绿", 10), ("蓝", 5), ("紫", 2), ("金", 1), ("红", 0.1)]

MOVE = {"w": (0, -1), "s": (0, 1), "a": (-1, 0), "d": (1, 0)}
MOUNT_RANKS = ["C", "B", "A", "S", "SS"]
MOUNT_RANK_BONUS = {
    "C": {"hp": 12, "spd": 1},
    "B": {"hp": 22, "atk": 2, "spd": 2},
    "A": {"hp": 36, "atk": 4, "def": 2, "spd": 3, "crit": 1},
    "S": {"hp": 52, "atk": 6, "def": 3, "spd": 4, "crit": 2, "res": 2},
    "SS": {"hp": 80, "atk": 9, "def": 5, "spd": 5, "crit": 3, "res": 3, "luck": 1},
}
MOUNT_ITEM_BONUS = {
    "灵巧鞍具": {"hp": 10, "def": 2, "res": 1},
    "疾风缰绳": {"spd": 3, "crit": 1},
}
SHOP_STOCK = [
    {"id": "回复药", "price": 5, "desc": "恢复40点生命"},
    {"id": "修理包", "price": 8, "desc": "立即修满装备耐久"},
    {"id": "武器图纸", "price": 18, "desc": "用于锻造随机武器"},
    {"id": "护甲图纸", "price": 18, "desc": "用于锻造随机护甲"},
    {"id": "饰品图纸", "price": 18, "desc": "用于锻造随机饰品"},
    {"id": "精铁矿", "price": 6, "desc": "初阶锻造材料"},
    {"id": "赤铁矿", "price": 7, "desc": "偏攻锻材"},
    {"id": "青铜矿", "price": 7, "desc": "器胚锻材"},
    {"id": "灵巧兽皮", "price": 6, "desc": "护甲锻造材料"},
    {"id": "灵核碎片", "price": 10, "desc": "饰品锻造材料"},
    {"id": "basic_sword", "price": 25, "desc": "基础武器箱"},
    {"id": "basic_armor", "price": 25, "desc": "基础护甲箱"},
    {"id": "灵巧鞍具", "price": 28, "desc": "坐骑鞍具，提升坐骑适应性"},
    {"id": "疾风缰绳", "price": 30, "desc": "坐骑缰绳，提升坐骑速度"},
    {"id": "坐骑蛋-灰驴", "price": 30, "desc": "随机获得C级坐骑（灰驴）"},
    {"id": "坐骑蛋-青羽", "price": 40, "desc": "随机获得B级坐骑（青羽鸟）"},
    {"id": "低阶收藏品包", "price": 45, "desc": "开出白/绿/蓝收藏品"},
    {"id": "insight_pill_金_黄", "price": 28, "desc": "提升金之悟性"},
    {"id": "insight_pill_木_黄", "price": 28, "desc": "提升木之悟性"},
    {"id": "insight_pill_水_黄", "price": 28, "desc": "提升水之悟性"},
    {"id": "insight_pill_火_黄", "price": 28, "desc": "提升火之悟性"},
    {"id": "insight_pill_土_黄", "price": 28, "desc": "提升土之悟性"},
    {"id": "insight_pill_时间_黄", "price": 36, "desc": "提升时间悟性"},
    {"id": "insight_pill_空间_黄", "price": 36, "desc": "提升空间悟性"},
]
def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def load_json_safe(path: Path, default):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return default


def apply_story_config():
    global STORY_NPCS, STORY_CHAPTERS, STORY_NPC_BY_ID
    STORY_NPCS, STORY_CHAPTERS = load_story_config(STORY_FILE)
    STORY_NPC_BY_ID = {n["id"]: n for n in STORY_NPCS}


apply_story_config()


def ensure_save_dir():
    SAVE_DIR.mkdir(parents=True, exist_ok=True)


def load_maze(path: Path):
    data = load_json(path)
    blocks = {tuple(b) for b in data["blocks"]}
    events = {tuple(ev["pos"]): ev for ev in data.get("events", [])}
    maze = {
        "name": data.get("name", path.stem),
        "w": data["width"],
        "h": data["height"],
        "start": tuple(data["start"]),
        "exit": tuple(data["exit"]),
        "blocks": blocks,
        "events": events,
    }
    return normalize_maze(maze)


def generate_maze(width: int, height: int, seed=None):
    """程序生成迷宫：外围墙 + 保底通路 + 随机障碍 + 随机事件"""
    rng = random.Random(seed)
    start = (1, height - 2)
    exit_pos = (width - 2, 1)

    blocks = set()
    for x in range(width):
        blocks.add((x, 0))
        blocks.add((x, height - 1))
    for y in range(height):
        blocks.add((0, y))
        blocks.add((width - 1, y))

    spine = set()
    for x in range(1, width - 1):
        spine.add((x, height - 2))
    for y in range(1, height - 1):
        spine.add((width - 2, y))

    density = 0.22
    for x in range(1, width - 1):
        for y in range(1, height - 1):
            if (x, y) in spine or (x, y) in (start, exit_pos):
                continue
            if rng.random() < density:
                blocks.add((x, y))

    blocks.discard(start)
    blocks.discard(exit_pos)

    def pick_free(n):
        free = []
        tries = 0
        while len(free) < n and tries < 2000:
            tries += 1
            x, y = rng.randint(1, width - 2), rng.randint(1, height - 2)
            if (x, y) in blocks or (x, y) == start or (x, y) == exit_pos or (x, y) in free:
                continue
            free.append((x, y))
        return free

    events = []
    chest_n = max(6, width // 5)
    heal_n = max(3, width // 10)
    elite_n = max(3, width // 12)

    for pos in pick_free(chest_n):
        events.append({"id": f"chest_{pos}", "pos": list(pos), "type": "loot"})
    for pos in pick_free(heal_n):
        events.append({"id": f"heal_{pos}", "pos": list(pos), "type": "heal"})
    for pos in pick_free(elite_n):
        events.append({"id": f"elite_{pos}", "pos": list(pos), "type": "battle"})

    boss_pos = (exit_pos[0] - 1, exit_pos[1] + 2)
    free_one = pick_free(1)
    if boss_pos in blocks or not free_one:
        boss_pos = free_one[0] if free_one else exit_pos
    events.append({"id": "boss_proc", "pos": list(boss_pos), "type": "boss"})

    events_dict = {tuple(ev["pos"]): ev for ev in events}
    maze = {
        "name": "procedural_maze",
        "w": width,
        "h": height,
        "start": start,
        "exit": exit_pos,
        "blocks": blocks,
        "events": events_dict,
    }
    return normalize_maze(maze)


def normalize_maze(maze: dict):
    if not maze:
        return maze
    w, h = maze["w"], maze["h"]
    start = maze["start"]
    blocks = set(maze.get("blocks", set()))
    events = dict(maze.get("events", {}))

    def in_bounds(p):
        return 0 <= p[0] < w and 0 <= p[1] < h

    reachable = set()
    stack = [start]
    while stack:
        x, y = stack.pop()
        if (x, y) in reachable or (x, y) in blocks or not in_bounds((x, y)):
            continue
        reachable.add((x, y))
        stack.extend([(x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)])

    for x in range(w):
        for y in range(h):
            if (x, y) in blocks:
                continue
            if (x, y) not in reachable:
                blocks.add((x, y))
                if (x, y) in events:
                    events.pop((x, y), None)

    free_cells = [
        (x, y)
        for x in range(w)
        for y in range(h)
        if (x, y) not in blocks and (x, y) != maze["start"] and (x, y) != maze["exit"]
    ]
    if free_cells:
        for pos, ev in list(events.items()):
            if pos in blocks:
                new_pos = random.choice(free_cells)
                events.pop(pos, None)
                events[new_pos] = ev

    maze["blocks"] = blocks
    maze["events"] = events
    return maze


def load_relic_db(path: Path):
    data = load_json(path)
    relics_by_rarity = {}
    for tier in data.get("tiers", []):
        color = tier["rarity_color"]
        relics_by_rarity[color] = tier.get("items", [])
    return relics_by_rarity


def load_dialogues(path: Path):
    try:
        data = load_json(path)
        return {dlg["id"]: dlg for dlg in data.get("dialogs", [])}
    except Exception:
        return {}


def load_catalog(path: Path, key: str):
    try:
        data = load_json(path)
        return data.get(key, [])
    except Exception:
        return []


def weighted_choice(weight_pairs):
    total = sum(w for _, w in weight_pairs)
    r = random.uniform(0, total)
    upto = 0
    for item, weight in weight_pairs:
        upto += weight
        if r <= upto:
            return item
    return weight_pairs[-1][0]

def build_chapter_enemies(chap_idx: int, scale: float):
    rng = random.Random(2026 + chap_idx * 13)
    tier_labels = ["杂兵", "游侠", "斥候", "祭司", "守卫", "执法者"]
    counts = [6, 5, 4, 3, 1, 1]  # total 20
    enemies = []
    base_hp = 85 + chap_idx * 48
    base_atk = 16 + chap_idx * 9
    base_def = 5 + chap_idx * 4
    for tier_idx, cnt in enumerate(counts):
        for i in range(cnt):
            hp = int(base_hp * (1 + 0.2 * tier_idx))
            atk = int(base_atk * (1 + 0.15 * tier_idx))
            de = int(base_def * (1 + 0.12 * tier_idx))
            enemy = {
                "name": f"第{chap_idx+1}章·{tier_labels[tier_idx]}·{i+1}",
                "hp": int(hp * scale),
                "atk": int(atk * scale),
                "def": max(1, int(de * scale)),
                "spd": 8 + tier_idx,
                "crit": 3 + tier_idx,
                "res": 3 + tier_idx,
                "exp": 28 + chap_idx * 12 + tier_idx * 10,
                "rarity": str(tier_idx),
            }
            enemies.append(enemy)
    enemies.sort(key=lambda e: int(e["rarity"]))
    elite = [e for e in enemies if int(e["rarity"]) >= 2]
    boss = {
        "name": f"第{chap_idx+1}章·守关者",
        "hp": int((base_hp * 8.2) * scale),
        "atk": int((base_atk * 4.0) * scale),
        "def": int((base_def * 4.2) * scale),
        "spd": 12 + chap_idx,
        "crit": 10 + chap_idx,
        "res": 12 + chap_idx,
        "exp": 220 + chap_idx * 70,
        "rarity": "boss",
        "skills": [
            {"name": "重击", "ratio": 2.0, "effect": "stun"},
            {"name": "灼烧挥砍", "ratio": 2.4, "effect": "burn"},
            {"name": "护盾", "ratio": 0.0, "effect": "shield"},
        ],
    }
    return {"normal": enemies, "elite": elite, "boss": boss}

def scale_enemy(enemy: dict, factor: float):
    e = dict(enemy)
    e["hp"] = int(e["hp"] * factor)
    e["atk"] = int(e["atk"] * factor)
    e["def"] = int(e["def"] * factor)
    e["res"] = int(e.get("res", 0) * factor)
    e["exp"] = int(e["exp"] * (0.8 + factor * 0.4))
    return e


def display_name(item_id: str) -> str:
    mapping = {
        "healing_potion": "回复药",
        "repair_kit": "修理包",
        "basic_sword": "基础武器箱",
        "basic_armor": "基础护甲箱",
        "武器图纸": "武器图纸",
        "护甲图纸": "护甲图纸",
        "饰品图纸": "饰品图纸",
        "精铁矿": "精铁矿",
        "灵巧兽皮": "灵巧兽皮",
        "灵核碎片": "灵核碎片",
        "灵巧鞍具": "灵巧鞍具",
        "疾风缰绳": "疾风缰绳",
        "回复药": "回复药",
        "修理包": "修理包",
    }
    if item_id.startswith("破境灵材·"):
        return item_id
    if item_id.startswith("破境丹·"):
        return item_id
    if item_id.startswith("丹方:"):
        return item_id
    if item_id.startswith("insight_pill_"):
        parts = item_id.replace("insight_pill_", "").split("_")
        if len(parts) == 2:
            element, tier = parts[0], parts[1]
            return f"悟性丹·{element}·{tier}"
        if len(parts) == 1:
            return f"悟性丹·{parts[0]}"
    return mapping.get(item_id, item_id)


def format_bonus(bonus: dict) -> str:
    parts = []
    if bonus.get("hp"):
        parts.append(f"生命+{bonus['hp']}")
    if bonus.get("atk"):
        parts.append(f"攻+{bonus['atk']}")
    if bonus.get("def"):
        parts.append(f"防+{bonus['def']}")
    if bonus.get("spd"):
        parts.append(f"速+{bonus['spd']}")
    if bonus.get("crit"):
        parts.append(f"暴+{bonus['crit']}")
    if bonus.get("res"):
        parts.append(f"抗+{bonus['res']}")
    if bonus.get("luck"):
        parts.append(f"幸运+{bonus['luck']}")
    return " ".join(parts) if parts else "无"


def format_attrs(attrs: list) -> str:
    labels = ["生命", "攻", "防", "速", "暴", "抗"]
    parts = []
    for i, label in enumerate(labels):
        if i < len(attrs) and attrs[i]:
            parts.append(f"{label}+{attrs[i]}")
    return " ".join(parts) if parts else "无"


def relic_total_bonus(relic: dict) -> dict:
    rarity = relic.get("rarity_color", relic.get("rarity", "白"))
    base = RELIC_BONUS.get(rarity, {})
    attrs = relic.get("属性") or relic.get("attrs") or [0, 0, 0, 0, 0, 0]
    bonus = {
        "hp": base.get("hp", 0) + (attrs[0] if len(attrs) > 0 else 0),
        "atk": base.get("atk", 0) + (attrs[1] if len(attrs) > 1 else 0),
        "def": base.get("def", 0) + (attrs[2] if len(attrs) > 2 else 0),
        "spd": base.get("spd", 0) + (attrs[3] if len(attrs) > 3 else 0),
        "crit": base.get("crit", 0) + (attrs[4] if len(attrs) > 4 else 0),
        "res": base.get("res", 0) + (attrs[5] if len(attrs) > 5 else 0),
        "luck": base.get("luck", 0),
    }
    return bonus
class GameUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Immortal Demo")
        self.relic_db = load_relic_db(RELIC_FILE)
        self.dialogues = load_dialogues(DIALOG_FILE)
        self.equip_catalog = load_catalog(EQUIP_CATALOG_FILE, "items")
        self.treasure_catalog = load_catalog(TREASURE_CATALOG_FILE, "rarities")
        self.treasure_catalog += build_elemental_treasure_catalog()
        self.treasure_index = build_treasure_index(self.treasure_catalog)
        self.mount_catalog = load_catalog(MOUNT_CATALOG_FILE, "rarities")
        self.factions = self.load_factions(FACTIONS_FILE)
        self.chapters = CHAPTER_PLAN
        self.chapter_idx = 0
        self.current_chapter = None
        self.enemy_pool = ENEMY_POOL
        self.enemy_pool_generated = False
        self.secret_dungeons = []
        self.run_mode = "chapter"  # chapter / secret
        self.chapter_before_secret = 0
        self.secret_unlocked = False
        self.loot_multiplier = 1.0
        self.active_faction = None
        self.sect = None  # 自创宗门
        self.secret_refresh_date = None
        self.life_id = None
        self.life_stats = {}
        self.npc_archive = []
        self.alive = True
        self.faction_task = None
        self.chapter_progress = {"battles": 0, "elites": 0, "boss": 0, "treasures": 0, "mounts": 0, "relics": 0}
        self.llm_server_process = None
        self.last_llm_error = ""
        self.active_quests = []
        self.completed_quests = []
        self.current_story = {}
        self.minimap_visible_span = 4

        self.player = self.build_new_player()

        self.maze = None
        self.pos = (0, 0)
        self.msgs = []

        # UI layout
        self.canvas = tk.Canvas(root, width=960, height=720, bg="black")
        self.canvas.grid(row=0, column=0, columnspan=4, sticky="nsew")
        try:
            self.bg_img = tk.PhotoImage(file=str(MAP_IMAGE))
            self.canvas.create_image(0, 0, anchor="nw", image=self.bg_img)
        except Exception as e:
            self.bg_img = None
            self.log(f"背景图加载失败: {e}")

        self.player_marker = self.canvas.create_oval(0, 0, 0, 0, fill="#00ff88", outline="")
        self.info = tk.StringVar()
        tk.Label(root, textvariable=self.info, anchor="w").grid(row=1, column=0, columnspan=4, sticky="we")

        self.move_frame = ttk.LabelFrame(root, text="移动")
        self.move_frame.grid(row=2, column=0, rowspan=2, sticky="nsew", padx=4, pady=2)
        self.action_frame = ttk.LabelFrame(root, text="快捷")
        self.action_frame.grid(row=2, column=3, rowspan=2, sticky="nsew", padx=4, pady=2)
        self.system_frame = ttk.LabelFrame(root, text="系统/剧情")
        self.system_frame.grid(row=5, column=0, columnspan=4, sticky="we", padx=4, pady=2)

        self.btn_up = tk.Button(self.move_frame, text="上", width=5, command=lambda: self.on_move("w"))
        self.btn_left = tk.Button(self.move_frame, text="左", width=5, command=lambda: self.on_move("a"))
        self.btn_down = tk.Button(self.move_frame, text="下", width=5, command=lambda: self.on_move("s"))
        self.btn_right = tk.Button(self.move_frame, text="右", width=5, command=lambda: self.on_move("d"))
        self.btn_up.grid(row=0, column=1, padx=2, pady=2)
        self.btn_left.grid(row=1, column=0, padx=2, pady=2)
        self.btn_down.grid(row=1, column=1, padx=2, pady=2)
        self.btn_right.grid(row=1, column=2, padx=2, pady=2)
        tk.Label(self.move_frame, text="小地图").grid(row=2, column=0, columnspan=3, sticky="w", padx=2)
        self.minimap = tk.Canvas(self.move_frame, width=180, height=180, bg="#111")
        self.minimap.grid(row=3, column=0, columnspan=3, padx=2, pady=4)

        self.btn_use = tk.Button(self.action_frame, text="药水(U)", command=self.use_potion)
        self.btn_bag = tk.Button(self.action_frame, text="背包(I)", command=self.show_bag)
        self.btn_train = tk.Button(self.action_frame, text="养成/锻造/商店", command=self.show_training)
        self.btn_secret = tk.Button(self.action_frame, text="秘境", state="disabled", command=self.show_secret_ui)
        self.btn_sect = tk.Button(self.action_frame, text="宗门", state="disabled", command=self.show_sect_ui)
        self.btn_use.grid(row=0, column=0, sticky="we", padx=2, pady=2)
        self.btn_bag.grid(row=1, column=0, sticky="we", padx=2, pady=2)
        self.btn_train.grid(row=2, column=0, sticky="we", padx=2, pady=2)
        self.btn_secret.grid(row=3, column=0, sticky="we", padx=2, pady=2)
        self.btn_sect.grid(row=4, column=0, sticky="we", padx=2, pady=2)

        self.btn_story = tk.Button(self.system_frame, text="剧情/任务", command=self.show_story_ui)
        self.btn_chapter = tk.Button(self.system_frame, text="章节目录", command=self.show_chapter_ui)
        self.btn_save = tk.Button(self.system_frame, text="存档", command=self.manual_save)
        self.btn_load = tk.Button(self.system_frame, text="读档", command=self.manual_load)
        self.btn_restart = tk.Button(self.system_frame, text="新生", command=self.restart_after_death, state="disabled")
        self.btn_restart_any = tk.Button(self.system_frame, text="重开", command=self.restart_anytime)
        self.btn_quit = tk.Button(self.system_frame, text="退出", command=self.on_quit)
        self.btn_npc_test = tk.Button(self.system_frame, text="测试NPC", command=self.show_test_npc_dialog)
        self.btn_story.grid(row=0, column=0, sticky="we", padx=2, pady=2)
        self.btn_chapter.grid(row=0, column=1, sticky="we", padx=2, pady=2)
        self.btn_npc_test.grid(row=0, column=2, sticky="we", padx=2, pady=2)
        self.btn_save.grid(row=1, column=0, sticky="we", padx=2, pady=2)
        self.btn_load.grid(row=1, column=1, sticky="we", padx=2, pady=2)
        self.btn_restart.grid(row=2, column=0, sticky="we", padx=2, pady=2)
        self.btn_restart_any.grid(row=2, column=1, sticky="we", padx=2, pady=2)
        self.btn_quit.grid(row=3, column=1, sticky="we", padx=2, pady=2)

        self.log_box = tk.Text(root, height=12, state="disabled")
        self.log_box.grid(row=4, column=1, columnspan=2, sticky="nsew", padx=4, pady=2)
        for elem, color in ELEMENT_COLORS.items():
            self.log_box.tag_configure(f"elem_{elem}", foreground=color)
        for eff, color in EFFECT_COLORS.items():
            self.log_box.tag_configure(f"eff_{eff}", foreground=color)
        self.log_box.tag_configure("skill", foreground="#ffee58")
        self.log_box.tag_configure("system", foreground="#90a4ae")

        self.manual_battle = False
        self.battle_frame = ttk.LabelFrame(root, text="战斗状态")
        self.battle_frame.grid(row=6, column=0, columnspan=4, sticky="we", padx=4, pady=4)
        self.battle_player_var = tk.StringVar(value="你: -")
        self.battle_enemy_var = tk.StringVar(value="敌: -")
        self.battle_status_var = tk.StringVar(value="状态: -")
        self.battle_player_status_var = tk.StringVar(value="状态: 无")
        self.battle_enemy_status_var = tk.StringVar(value="状态: 无")
        self.battle_player_bar = ttk.Progressbar(self.battle_frame, length=260, mode="determinate")
        self.battle_enemy_bar = ttk.Progressbar(self.battle_frame, length=260, mode="determinate")
        self.exp_var = tk.StringVar(value="经验: 0/0")
        self.exp_bar = ttk.Progressbar(self.battle_frame, length=260, mode="determinate")
        tk.Label(self.battle_frame, textvariable=self.battle_player_var, anchor="w").grid(row=0, column=0, sticky="w")
        self.battle_player_bar.grid(row=0, column=1, sticky="we", padx=4)
        tk.Label(self.battle_frame, textvariable=self.battle_enemy_var, anchor="w").grid(row=1, column=0, sticky="w")
        self.battle_enemy_bar.grid(row=1, column=1, sticky="we", padx=4)
        tk.Label(self.battle_frame, textvariable=self.battle_player_status_var, anchor="w").grid(row=2, column=0, columnspan=2, sticky="w")
        tk.Label(self.battle_frame, textvariable=self.battle_enemy_status_var, anchor="w").grid(row=3, column=0, columnspan=2, sticky="w")
        tk.Label(self.battle_frame, textvariable=self.exp_var, anchor="w").grid(row=4, column=0, sticky="w")
        self.exp_bar.grid(row=4, column=1, sticky="we", padx=4)
        self.battle_skill_box = tk.Listbox(self.battle_frame, height=3, width=60)
        self.battle_skill_box.grid(row=5, column=0, columnspan=2, sticky="we", padx=4, pady=2)
        self.battle_skill_btn_frame = tk.Frame(self.battle_frame)
        self.battle_skill_btn_frame.grid(row=6, column=0, columnspan=2, sticky="we", padx=4, pady=2)
        self.battle_action_box = tk.Listbox(self.battle_frame, height=3, width=60)
        self.battle_action_box.grid(row=7, column=0, columnspan=2, sticky="we", padx=4, pady=2)
        self.battle_action_var = tk.StringVar(value="")
        self.battle_action_btn = tk.Button(self.battle_frame, text="执行动作", command=self.commit_battle_action)
        self.battle_action_btn.grid(row=8, column=1, sticky="e", padx=4, pady=2)
        self.battle_strategy_var = tk.StringVar(value="均衡")
        tk.Label(self.battle_frame, text="策略").grid(row=8, column=0, sticky="w", padx=4)
        self.battle_strategy_menu = ttk.Combobox(
            self.battle_frame,
            textvariable=self.battle_strategy_var,
            values=["均衡", "爆发", "控制", "保守"],
            width=8,
            state="readonly",
        )
        self.battle_strategy_menu.grid(row=8, column=0, sticky="e", padx=70)
        self.battle_strategy_menu.bind("<<ComboboxSelected>>", lambda _e: self.set_battle_strategy())
        self.battle_loadout_btn = tk.Button(self.battle_frame, text="技能池", command=self.show_skill_loadout)
        self.battle_loadout_btn.grid(row=8, column=1, sticky="w", padx=4)
        self.battle_hint_var = tk.StringVar(value="")
        tk.Label(self.battle_frame, textvariable=self.battle_hint_var, anchor="w").grid(row=9, column=0, columnspan=2, sticky="we", padx=4)
        self.battle_frame.grid_columnconfigure(1, weight=1)

        root.grid_rowconfigure(0, weight=1)
        root.grid_columnconfigure(0, weight=1)
        root.grid_columnconfigure(1, weight=1)
        root.grid_columnconfigure(2, weight=1)
        root.grid_columnconfigure(3, weight=1)
        root.protocol("WM_DELETE_WINDOW", self.on_quit)

        ensure_save_dir()
        self.npc_archive = self.load_npc_archive()
        if not self.load_game():
            self.start_new_life()
        self.refresh_secret_pool()
    # ---------- utilities ----------
    def log(self, text: str, tag: str = None):
        self.msgs.append(text)
        self.log_box.configure(state="normal")
        if tag:
            self.log_box.insert("end", text + "\n", tag)
        else:
            self.log_box.insert("end", text + "\n")
        self.log_box.configure(state="disabled")
        self.log_box.see("end")

    def opening_story_lines(self):
        name = self.player.get("name", "无名")
        life_id = self.life_id if self.life_id is not None else "?"
        main_elem = self.player_main_element()
        elem_desc = {
            "金": "锋锐开路，攻伐见长",
            "木": "生机绵长，恢复稳健",
            "水": "以柔克刚，善守反击",
            "火": "爆发迅疾，先手压制",
            "土": "厚重不移，护体强横",
            "时间": "迟速由心，掌控节奏",
            "空间": "虚实变换，穿插突进",
        }
        talents = [t.get("name", "") for t in self.player.get("talents", []) if t.get("name")]
        talent_text = "、".join(talents) if talents else "凡骨未显"
        return [
            "【序章】灵潮复苏，四族并立，万界归墟将启。",
            f"【身世】你名为{name}，第{life_id}世入道者，天赋：{talent_text}。",
            f"【命途】主修{main_elem}，{elem_desc.get(main_elem, '以道心破局')}。",
            "【目标】活下去，破境成名，最终踏入归墟终局。",
        ]

    def show_opening_story(self, force=False):
        if not force and self.player.get("opening_story_shown"):
            return False
        for line in self.opening_story_lines():
            self.log(line, "system")
        self.player["opening_story_shown"] = True
        return True

    def play_dialogue(self, dlg_id: str):
        dlg = self.dialogues.get(dlg_id)
        if not dlg:
            return
        for line in dlg.get("lines", []):
            speaker = line.get("name", "")
            txt = line.get("text", "")
            self.log(f"{speaker}: {txt}" if speaker else txt)

    def ensure_npc_state(self, npc: dict):
        if not npc:
            return
        npc.setdefault("name", "无名者")
        npc.setdefault("faction", "中立")
        npc.setdefault("background", npc.get("story", "无"))
        npc.setdefault("goal", "无")
        npc.setdefault("mood", "平静")
        npc.setdefault("relation", 0)
        npc.setdefault("memory", [])
        npc.setdefault("dialogue_history", [])
        npc.setdefault("hostile", False)
        npc.setdefault("follow", False)
        npc.setdefault("buff_applied", False)

    def build_npc_prompt(self, npc: dict, player_text: str):
        mood = npc.get("mood", "平静")
        relation = npc.get("relation", 0)
        background = npc.get("background", "无")
        goal = npc.get("goal", "无")
        faction = npc.get("faction", "中立")
        memory = npc.get("memory", [])
        memory_text = "；".join(memory[-5:]) if memory else "无"
        history = npc.get("dialogue_history", [])
        recent = history[-4:] if history else []
        history_lines = []
        for item in recent:
            p = item.get("player", "").strip()
            n = item.get("npc", "").strip()
            if p:
                history_lines.append(f"玩家:{p}")
            if n:
                history_lines.append(f"NPC:{n}")
        history_text = " | ".join(history_lines) if history_lines else "无"
        prompt = (
            f"你是NPC：{npc.get('name','无名')}\n"
            f"阵营：{faction}\n"
            f"背景：{background}\n"
            f"目标：{goal}\n"
            f"心情：{mood}\n"
            f"与玩家关系：{relation}（-100敌对~100亲近）\n"
            f"近期记忆：{memory_text}\n"
            f"对话历史：{history_text}\n"
            f"玩家说：{player_text}\n"
            "请只用中文回应（避免英文），必须直接回答玩家问题/请求，不要复读固定句。"
            "不要重复自我介绍，除非玩家问你是谁。"
            "不要重复上一次NPC回复。"
            "用一句话回答，并在末尾附加JSON状态更新。JSON必须包含reply字段，例如："
            "{\"reply\":\"此处多险，小心前行。\",\"mood\":\"警惕\",\"relation\":-3,\"hint\":\"不引导\"}"
        )
        return prompt

    def llm_available(self):
        if not MODEL_PATH.exists():
            return False
        if not LLAMA_SERVER_BIN.exists():
            return False
        for dll in LLAMA_REQUIRED_DLLS:
            if not (LLAMA_BIN.parent / dll).exists():
                return False
        return True

    def llm_missing_reason(self):
        if not MODEL_PATH.exists():
            return f"模型缺失: {MODEL_PATH}"
        if not LLAMA_SERVER_BIN.exists():
            return f"llama-server 缺失: {LLAMA_SERVER_BIN}"
        missing = [dll for dll in LLAMA_REQUIRED_DLLS if not (LLAMA_BIN.parent / dll).exists()]
        if missing:
            return "缺少依赖: " + ", ".join(missing)
        return "未知原因"

    def llama_server_url(self, path: str):
        return f"http://{LLAMA_SERVER_HOST}:{LLAMA_SERVER_PORT}{path}"

    def llama_server_running(self):
        try:
            with urllib.request.urlopen(self.llama_server_url("/health"), timeout=1) as resp:
                return resp.status == 200
        except Exception:
            return False

    def ensure_llama_server(self):
        if self.llama_server_running():
            return True
        if not LLAMA_SERVER_BIN.exists():
            return False
        try:
            cmd = [
                str(LLAMA_SERVER_BIN),
                "-m",
                str(MODEL_PATH),
                "--port",
                str(LLAMA_SERVER_PORT),
            ]
            self.llm_server_process = subprocess.Popen(
                cmd,
                cwd=str(LLAMA_BIN.parent),
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                creationflags=subprocess.CREATE_NO_WINDOW,
            )
        except Exception:
            return False
        # wait for server up
        for _ in range(40):
            if self.llama_server_running():
                return True
            time.sleep(0.25)
        return False

    def llm_generate_via_server(self, prompt: str):
        def post_json(path: str, payload: dict):
            data = json.dumps(payload).encode("utf-8")
            req = urllib.request.Request(
                self.llama_server_url(path),
                data=data,
                headers={"Content-Type": "application/json"},
                method="POST",
            )
            with urllib.request.urlopen(req, timeout=120) as resp:
                raw = resp.read().decode("utf-8", errors="ignore")
            return json.loads(raw)

        # chat completions first
        payload = {
            "model": "local",
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.7,
            "top_p": 0.9,
            "max_tokens": 80,
            "stream": False,
        }
        result = post_json("/v1/chat/completions", payload)
        if "choices" in result and result["choices"]:
            choice = result["choices"][0]
            msg = choice.get("message", {})
            if isinstance(msg, dict) and msg.get("content"):
                return msg["content"]
            if choice.get("text"):
                return choice["text"]

        # fallback to /completion
        payload = {
            "prompt": prompt,
            "temperature": 0.7,
            "top_p": 0.9,
            "n_predict": 80,
        }
        result = post_json("/completion", payload)
        if "content" in result and result["content"]:
            return result["content"]
        if "choices" in result and result["choices"]:
            choice = result["choices"][0]
            if choice.get("text"):
                return choice["text"]
        return ""

    def llm_generate(self, prompt: str):
        if not self.llm_available():
            return ""
        try:
            if not self.ensure_llama_server():
                self.last_llm_error = "llama-server 启动失败"
                return ""
            self.last_llm_error = ""
            text = self.llm_generate_via_server(prompt)
            if not text:
                self.last_llm_error = "llama-server 空响应"
            return text
        except Exception as e:
            self.last_llm_error = f"LLM异常: {e}"
            return ""

    def parse_npc_update(self, text: str):
        match = re.search(r"{.*}$", text.strip())
        if not match:
            return text.strip(), {}
        json_part = match.group(0)
        try:
            update = json.loads(json_part)
        except Exception:
            return text.strip(), {}
        reply = text.replace(json_part, "").strip()
        if not reply:
            for key in ("reply", "text", "say"):
                val = update.get(key)
                if isinstance(val, str) and val.strip():
                    reply = val.strip()
                    break
        # normalize mood/relation
        if "relation" in update:
            try:
                update["relation"] = max(-100, min(100, int(update["relation"])))
            except Exception:
                update.pop("relation", None)
        if "mood" in update and not isinstance(update["mood"], str):
            try:
                update["mood"] = str(update["mood"])
            except Exception:
                update.pop("mood", None)
        return reply, update

    def is_repetitive_reply(self, npc: dict, reply: str):
        if not reply:
            return False
        history = npc.get("dialogue_history", [])
        if not history:
            return False
        last = history[-1].get("npc", "")
        if not last:
            return False
        if reply.strip() == last.strip():
            return True
        short = reply.strip()[:10]
        return short and short in last

    def is_unhelpful_reply(self, reply: str, player_text: str):
        if not reply:
            return True
        bad = {"不引导", "不知道", "无", "沉默"}
        if reply.strip() in bad:
            return True
        if len(reply.strip()) <= 4:
            return True
        # basic keyword coverage
        keywords = [k for k in re.findall(r"[\u4e00-\u9fa5]{2,4}", player_text) if len(k) >= 2]
        if keywords:
            hit = any(k in reply for k in keywords[:3])
            return not hit
        return False

    def fallback_context_reply(self, npc: dict, player_text: str):
        text = player_text.strip()
        if any(k in text for k in ("你是谁", "名字", "来历")):
            return f"我叫{npc.get('name','无名')},行走江湖的小游侠。"
        if any(k in text for k in ("技能", "本领", "绝招", "招式")):
            faction = npc.get("faction", "中立")
            return f"我擅长身法与游侠近战技巧，常在{faction}地界行走。"
        if any(k in text for k in ("你好", "嗨", "在吗")):
            return "你好，路上小心，我愿与你交流。"
        return "此地险恶，但若你愿意，我可以给些建议。"

    def npc_tactical_hint(self):
        hints = []
        pending = [q for q in self.active_quests if not q.get("completed")] if self.active_quests else []
        if pending:
            q = pending[0]
            targets = q.get("targets", {})
            parts = []
            mapping = {
                "battles": "战斗",
                "elites": "精英",
                "boss": "首领",
                "treasures": "宝材",
                "mounts": "坐骑",
                "relics": "收藏品",
                "talk": "对话",
            }
            for k, v in targets.items():
                prog = q.get("progress", {}).get(k, 0)
                parts.append(f"{mapping.get(k,k)} {prog}/{v}")
            hints.append(f"支线提示：{q.get('name')}（{' '.join(parts)}）")
            types = []
            if "treasures" in targets:
                types.append("treasure")
            if "mounts" in targets:
                types.append("mount")
            if "talk" in targets:
                types.append("npc")
            if types:
                event_hint = self.nearest_event_hint(types)
                if event_hint:
                    hints.append(f"位置线索：{event_hint}")
        if self.current_chapter and self.current_chapter.get("faction"):
            f_name = next((f["name"] for f in NATION_FACTIONS if f["id"] == self.current_chapter.get("faction")), "势力")
            hints.append(f"本章势力：{f_name}，建议根据敌人元素调整策略。")
        main_elem = self.player_main_element()
        if main_elem:
            countered_by = {v: k for k, v in ELEMENT_COUNTERS.items()}
            if countered_by.get(main_elem):
                hints.append(f"你主修{main_elem}，遇到{countered_by.get(main_elem)}系敌人需谨慎。")
        if self.maze and self.maze.get("exit"):
            hints.append(f"出口方向：{self.direction_hint(self.pos, self.maze['exit'])}")
        if not hints:
            hints.append("建议查看剧情/任务面板，优先推进当前章节目标。")
        return " | ".join(hints)

    def direction_hint(self, pos_a, pos_b):
        if not pos_a or not pos_b:
            return "未知"
        dx = pos_b[0] - pos_a[0]
        dy = pos_b[1] - pos_a[1]
        if abs(dx) + abs(dy) <= 2:
            return "就在附近"
        parts = []
        if dy < 0:
            parts.append("向上")
        elif dy > 0:
            parts.append("向下")
        if dx < 0:
            parts.append("向左")
        elif dx > 0:
            parts.append("向右")
        return " ".join(parts) if parts else "原地"

    def nearest_event_hint(self, types):
        if not self.maze or not self.maze.get("events"):
            return ""
        best = None
        for pos, ev in self.maze["events"].items():
            if ev.get("type") in types:
                dist = abs(pos[0] - self.pos[0]) + abs(pos[1] - self.pos[1])
                if best is None or dist < best[0]:
                    best = (dist, pos, ev.get("type"))
        if not best:
            return ""
        _, pos, etype = best
        label = {"treasure": "宝材", "mount": "坐骑", "npc": "NPC"}.get(etype, etype)
        return f"{label} {self.direction_hint(self.pos, pos)}"

    def npc_generate_reply(self, npc: dict, player_text: str):
        quick = self.npc_quick_reply(npc, player_text)
        if quick:
            reply, update = quick
            return reply, update, {"used_llm": False, "raw": ""}
        prompt = self.build_npc_prompt(npc, player_text)
        debug = {"used_llm": False, "raw": ""}
        if self.llm_available():
            raw = self.llm_generate(prompt)
            debug["used_llm"] = True
            debug["raw"] = raw or ""
            reply, update = self.parse_npc_update(raw if raw else "")
            if reply:
                if self.is_repetitive_reply(npc, reply) or self.is_unhelpful_reply(reply, player_text):
                    reply = self.fallback_context_reply(npc, player_text)
                return reply, update, debug
        # Fallback deterministic reply
        relation = npc.get("relation", 0)
        if relation >= 30:
            reply = "你曾助我一臂之力，我愿指引你前路。"
            update = {"mood": "友好", "relation": 2, "hint": "引导"}
        elif relation <= -20:
            reply = "你的气息让我不安，最好保持距离。"
            update = {"mood": "警惕", "relation": -2, "hint": "不引导"}
        else:
            reply = "此处多险，小心前行。"
            update = {"mood": "平静", "relation": 0, "hint": "中立"}
        return reply, update, debug

    def npc_quick_reply(self, npc: dict, player_text: str):
        text = player_text.strip()
        if not text:
            return None
        if any(k in text for k in ("金币", "钱", "给点", "施舍")):
            return "可以交易或赠礼，我会以礼相待。", {"mood": "平静", "relation": 0, "hint": "交易"}
        if any(k in text for k in ("赠礼", "送你", "礼物")):
            return "你可赠礼，我会记在心里。", {"mood": "友好", "relation": 1, "hint": "赠礼"}
        if any(k in text for k in ("交易", "买", "卖")):
            return "可用金币交易，我会回赠物资。", {"mood": "平静", "relation": 1, "hint": "交易"}
        if any(k in text for k in ("跟随", "随行", "加入")):
            return "好感足够时我会随行，赠礼或交易可提升好感。", {"mood": "平静", "relation": 0, "hint": "随行"}
        return None

    def apply_npc_update(self, npc: dict, update: dict):
        if not update:
            return
        if "mood" in update:
            npc["mood"] = update["mood"]
        if "relation" in update:
            npc["relation"] = npc.get("relation", 0) + int(update["relation"])
        if "hint" in update:
            npc["hint"] = update["hint"]
        if npc.get("relation", 0) >= NPC_FOLLOW_THRESHOLD:
            self.npc_follow(npc)

    def npc_faction_id(self, npc: dict):
        faction = npc.get("faction", "中立")
        if faction in ("human", "yao", "mo", "xian"):
            return faction
        mapping = {"人族": "human", "妖族": "yao", "魔族": "mo", "仙族": "xian", "中立": "neutral"}
        return mapping.get(faction, "neutral")

    def adjust_faction_rep(self, npc: dict, delta: int):
        fid = self.npc_faction_id(npc)
        if fid in ("human", "yao", "mo", "xian"):
            self.player["reputation"][fid] = self.player["reputation"].get(fid, 0) + delta

    def npc_follow(self, npc: dict):
        if npc.get("follow"):
            return
        npc["follow"] = True
        fid = self.npc_faction_id(npc)
        bonus = NPC_BUFFS.get(fid, NPC_BUFFS["neutral"])
        if not self.player.get("followers"):
            self.player["followers"] = []
        if npc.get("name") in self.player["followers"]:
            return
        self.player["followers"].append(npc.get("name"))
        self.player["max_hp"] += bonus.get("hp", 0)
        self.player["atk"] += bonus.get("atk", 0)
        self.player["def"] += bonus.get("def", 0)
        self.player["spd"] += bonus.get("spd", 0)
        self.player["crit"] += bonus.get("crit", 0)
        self.player["res"] += bonus.get("res", 0)
        self.player["luck"] += bonus.get("luck", 0)
        self.player["hp"] = min(self.player["hp"], self.player["max_hp"])
        self.log(f"{npc.get('name','NPC')} 决定随行，获得随行增益。", "system")

    def set_npc_hostile(self, npc: dict):
        npc["relation"] = NPC_ATTACK_RELATION_RESET
        npc["mood"] = "仇恨"
        npc["hostile"] = True
        npc["follow"] = False
        self.adjust_faction_rep(npc, -3)

    def build_npc_enemy(self, npc: dict):
        lvl = self.player.get("lvl", 1)
        hp = max(40, int(self.player.get("max_hp", 100) * 0.7))
        atk = max(8, int(self.player.get("atk", 10) * 0.85))
        de = max(3, int(self.player.get("def", 5) * 0.7))
        spd = max(6, int(self.player.get("spd", 8) * 0.9))
        enemy = {
            "name": f"{npc.get('name','仇敌')}·仇恨",
            "hp": hp,
            "atk": atk,
            "def": de,
            "spd": spd,
            "crit": 4 + lvl // 4,
            "res": 4 + lvl // 4,
            "exp": 8 + lvl * 2,
            "rarity": "elite",
        }
        fid = self.npc_faction_id(npc)
        if fid in ("human", "yao", "mo", "xian"):
            enemy["faction"] = fid
        return enemy

    def hostile_npc_attack(self, npc: dict):
        self.log(f"{npc.get('name','仇敌')}对你发动攻击！无法逃跑。", "system")
        dmg = max(1, int(self.player.get("max_hp", 100) / 3))
        self.player["hp"] = max(1, self.player["hp"] - dmg)
        self.log(f"遭受重创，生命 -{dmg}", "system")
        enemy = self.build_npc_enemy(npc)
        self.battle(enemy, is_boss=False, is_elite=True)
        self.respawn_npc_event(npc)

    def respawn_npc_event(self, npc: dict):
        if not self.maze:
            return
        free = [
            (x, y)
            for x in range(self.maze["w"])
            for y in range(self.maze["h"])
            if self.can_walk(x, y)
            and (x, y) != self.maze["start"]
            and (x, y) != self.maze["exit"]
            and (x, y) not in self.maze["events"]
        ]
        if not free:
            return
        pos = random.choice(free)
        self.maze["events"][pos] = {"type": "npc", "pos": pos, "npc": dict(npc)}

    def show_npc_dialog(self, npc: dict, title: str = "NPC对话"):
        if not npc:
            return
        self.ensure_npc_state(npc)
        win = tk.Toplevel(self.root)
        win.title(title)
        win.geometry("560x520")

        header = tk.Frame(win)
        header.pack(fill="x", padx=8, pady=6)
        name = npc.get("name", "无名者")
        faction = npc.get("faction", "中立")
        mood = npc.get("mood", "平静")
        relation = npc.get("relation", 0)
        header_var = tk.StringVar(value=f"{name}  阵营:{faction}  心情:{mood}  关系:{relation}")
        tk.Label(header, textvariable=header_var).pack(anchor="w")
        if not self.llm_available():
            reason = self.llm_missing_reason()
            tk.Label(header, text=f"提示：本地模型未就绪，将使用简易对话。{reason}", fg="#888").pack(anchor="w")

        log_box = tk.Text(win, height=12, wrap="word", state="disabled")
        log_box.pack(fill="both", expand=True, padx=8, pady=6)

        gift_frame = ttk.LabelFrame(win, text="赠礼/互动")
        gift_frame.pack(fill="x", padx=8, pady=4)
        gift_box = tk.Listbox(gift_frame, height=4)
        gift_box.pack(fill="x", padx=6, pady=4)
        gift_items = [k for k, v in self.player.get("bag", {}).items() if v > 0]
        for k in gift_items:
            gift_box.insert("end", f"{k} x{self.player['bag'][k]}")

        btn_row = tk.Frame(gift_frame)
        btn_row.pack(fill="x", padx=6, pady=4)

        input_row = tk.Frame(win)
        input_row.pack(fill="x", padx=8, pady=6)
        entry = tk.Entry(input_row)
        entry.pack(side="left", fill="x", expand=True, padx=(0, 6))
        send_btn = tk.Button(input_row, text="发送")
        close_btn = tk.Button(input_row, text="关闭")

        def append_dialog(speaker: str, text: str):
            log_box.configure(state="normal")
            log_box.insert("end", f"{speaker}: {text}\n")
            log_box.configure(state="disabled")
            log_box.see("end")

        hint_shown = {"value": False}

        def refresh_header():
            header_var.set(
                f"{npc.get('name','无名者')}  阵营:{npc.get('faction','中立')}  心情:{npc.get('mood','平静')}  关系:{npc.get('relation',0)}"
            )

        def trade_with_npc():
            trade_win = tk.Toplevel(win)
            trade_win.title("NPC交易")
            trade_win.geometry("360x320")
            tk.Label(trade_win, text=f"金币：{self.player.get('gold',0)}").pack(anchor="w", padx=6, pady=4)
            listbox = tk.Listbox(trade_win, height=10, width=40)
            listbox.pack(fill="both", expand=True, padx=6, pady=4)
            for itm in NPC_TRADE_STOCK:
                listbox.insert("end", f"{display_name(itm['id'])} | 价格{itm['price']}")

            def buy():
                sel = listbox.curselection()
                if not sel:
                    return
                itm = NPC_TRADE_STOCK[sel[0]]
                if self.player.get("gold", 0) < itm["price"]:
                    self.log("金币不足，无法购买。", "system")
                    return
                self.player["gold"] -= itm["price"]
                self.player["bag"][itm["id"]] = self.player["bag"].get(itm["id"], 0) + 1
                npc["relation"] = min(100, npc.get("relation", 0) + NPC_TRADE_RELATION)
                self.adjust_faction_rep(npc, 1)
                append_dialog("系统", f"购买 {display_name(itm['id'])} 成功。")
                if npc.get("relation", 0) >= NPC_FOLLOW_THRESHOLD:
                    self.npc_follow(npc)
                refresh_header()
                trade_win.destroy()

            tk.Button(trade_win, text="购买", command=buy).pack(side="left", padx=6, pady=6)
            tk.Button(trade_win, text="关闭", command=trade_win.destroy).pack(side="left", padx=6, pady=6)

        def gift_to_npc():
            sel = gift_box.curselection()
            if not sel:
                return
            item = gift_items[sel[0]]
            if self.player["bag"].get(item, 0) <= 0:
                return
            self.player["bag"][item] -= 1
            npc["relation"] = min(100, npc.get("relation", 0) + NPC_GIFT_RELATION)
            self.adjust_faction_rep(npc, 1)
            append_dialog("系统", f"赠礼：{display_name(item)}，好感提升。")
            if npc.get("relation", 0) >= NPC_FOLLOW_THRESHOLD:
                self.npc_follow(npc)
            refresh_header()
            win.destroy()

        def attack_npc():
            self.set_npc_hostile(npc)
            win.destroy()
            self.hostile_npc_attack(npc)

        for item in npc.get("dialogue_history", []):
            player_text = item.get("player", "")
            npc_text = item.get("npc", "")
            if player_text:
                append_dialog("玩家", player_text)
            if npc_text:
                append_dialog(name, npc_text)

        def set_input_state(enabled: bool):
            state = "normal" if enabled else "disabled"
            entry.configure(state=state)
            send_btn.configure(state=state)
            close_btn.configure(state=state)

        def send():
            player_text = entry.get().strip()
            if not player_text:
                return
            entry.delete(0, "end")
            append_dialog("玩家", player_text)
            npc.get("memory", []).append(f"玩家:{player_text}")
            set_input_state(False)

            def worker():
                reply, update, debug = self.npc_generate_reply(npc, player_text)

                def finish():
                    if debug.get("used_llm"):
                        mode_text = "模型回复"
                    else:
                        mode_text = "简易回复"
                    err = self.last_llm_error
                    raw = debug.get("raw", "")
                    if raw:
                        append_dialog("DEBUG", f"{mode_text} | raw: {raw[:180]}")
                    elif err:
                        append_dialog("DEBUG", f"{mode_text} | error: {err}")
                    else:
                        append_dialog("DEBUG", f"{mode_text}")
                    if reply:
                        append_dialog(name, reply)
                        npc.get("memory", []).append(f"{name}:{reply}")
                        npc.setdefault("dialogue_history", []).append({"player": player_text, "npc": reply})
                        npc["memory"] = npc.get("memory", [])[-8:]
                        npc["dialogue_history"] = npc.get("dialogue_history", [])[-10:]
                    self.apply_npc_update(npc, update)
                    if not hint_shown["value"]:
                        hint = self.npc_tactical_hint()
                        if hint:
                            append_dialog("提示", hint)
                        hint_shown["value"] = True
                    refresh_header()
                    set_input_state(True)

                win.after(0, finish)

            threading.Thread(target=worker, daemon=True).start()

        def close():
            win.destroy()

        send_btn.configure(command=send)
        close_btn.configure(command=close)
        send_btn.pack(side="left")
        close_btn.pack(side="left", padx=6)
        entry.bind("<Return>", lambda _e: send())
        entry.focus_set()
        tk.Button(btn_row, text="交易", command=trade_with_npc).pack(side="left", padx=4)
        tk.Button(btn_row, text="赠礼", command=gift_to_npc).pack(side="left", padx=4)
        tk.Button(btn_row, text="攻击", command=attack_npc).pack(side="left", padx=4)

    def show_test_npc_dialog(self):
        npc = {
            "name": "风吟",
            "faction": "中立",
            "background": "行走江湖的游侠，见多识广。",
            "goal": "寻找失散的同伴。",
            "mood": "平静",
            "relation": 5,
            "memory": [],
            "dialogue_history": [],
        }
        self.show_npc_dialog(npc, title="测试NPC")

    def generate_random_base_bonus(self):
        return {
            "hp": random.randint(0, 20),
            "atk": random.randint(0, 4),
            "def": random.randint(0, 3),
            "spd": random.randint(0, 3),
            "crit": random.randint(0, 3),
            "res": random.randint(0, 3),
            "luck": random.randint(0, 2),
        }

    def roll_talents(self):
        cnt = random.randint(1, 3)
        return random.sample(TALENT_POOL, cnt)

    def apply_base_bonus(self, bonus):
        self.player["max_hp"] += bonus.get("hp", 0)
        self.player["hp"] = min(self.player["hp"] + bonus.get("hp", 0), self.player["max_hp"])
        self.player["atk"] += bonus.get("atk", 0)
        self.player["def"] += bonus.get("def", 0)
        self.player["spd"] += bonus.get("spd", 0)
        self.player["crit"] += bonus.get("crit", 0)
        self.player["res"] += bonus.get("res", 0)
        self.player["luck"] += bonus.get("luck", 0)

    def apply_talent_bonuses(self, talents):
        for t in talents:
            bonus = t.get("bonus", {})
            if "hp" in bonus:
                self.player["max_hp"] += bonus["hp"]
                self.player["hp"] = min(self.player["hp"] + bonus["hp"], self.player["max_hp"])
            if "atk" in bonus:
                self.player["atk"] += bonus["atk"]
            if "def" in bonus:
                self.player["def"] += bonus["def"]
            if "spd" in bonus:
                self.player["spd"] += bonus["spd"]
            if "crit" in bonus:
                self.player["crit"] += bonus["crit"]
            if "res" in bonus:
                self.player["res"] += bonus["res"]
            if "luck" in bonus:
                self.player["luck"] += bonus["luck"]
            if "insight" in bonus:
                elem = self.player_main_element()
                self.player["insight"][elem] = self.player["insight"].get(elem, 0) + bonus["insight"]

    def show_character_creation(self):
        win = tk.Toplevel(self.root)
        win.title("角色创建")
        base_var = tk.StringVar()
        talent_var = tk.StringVar()
        name_var = tk.StringVar(value=self.player.get("name", "无名"))
        tip = tk.StringVar(value="随机生成属性与天赋，可重新随机。")

        def refresh():
            bonus = self.generate_random_base_bonus()
            talents = self.roll_talents()
            self.player["base_bonus"] = bonus
            self.player["talents"] = talents
            base_var.set(
                f"属性加成：生命+{bonus['hp']} 攻+{bonus['atk']} 防+{bonus['def']} 速+{bonus['spd']} "
                f"暴+{bonus['crit']} 抗+{bonus['res']} 幸运+{bonus['luck']}"
            )
            tnames = "，".join([t["name"] for t in talents]) or "无"
            talent_var.set(f"天赋：{tnames}")

        def confirm():
            name = name_var.get().strip() or "无名"
            self.player["name"] = name
            if not self.player.get("creation_applied"):
                self.apply_base_bonus(self.player["base_bonus"])
                self.apply_talent_bonuses(self.player["talents"])
                self.player["creation_applied"] = True
            win.destroy()

        tk.Label(win, textvariable=tip, anchor="w").grid(row=0, column=0, columnspan=2, sticky="w", padx=4, pady=4)
        tk.Label(win, text="姓名：").grid(row=1, column=0, sticky="w", padx=4)
        tk.Entry(win, textvariable=name_var).grid(row=1, column=1, sticky="we", padx=4)
        tk.Label(win, textvariable=base_var, anchor="w").grid(row=2, column=0, columnspan=2, sticky="w", padx=4, pady=4)
        tk.Label(win, textvariable=talent_var, anchor="w").grid(row=3, column=0, columnspan=2, sticky="w", padx=4, pady=4)
        tk.Button(win, text="重新随机", command=refresh).grid(row=4, column=0, sticky="we", padx=4, pady=4)
        tk.Button(win, text="确认", command=confirm).grid(row=4, column=1, sticky="we", padx=4, pady=4)
        refresh()
        win.grab_set()
        self.root.wait_window(win)

    def build_new_player(self):
        return {
            "name": "无名",
            "hp": PLAYER_BASE["hp"],
            "max_hp": PLAYER_BASE["hp"],
            "atk": PLAYER_BASE["atk"],
            "def": PLAYER_BASE["def"],
            "spd": PLAYER_BASE["spd"],
            "crit": PLAYER_BASE["crit"],
            "res": PLAYER_BASE["res"],
            "luck": PLAYER_BASE["luck"],
            "lvl": PLAYER_BASE["lvl"],
            "exp": PLAYER_BASE["exp"],
            "exp_next": PLAYER_BASE["exp_next"],
            "free_points": PLAYER_BASE["free_points"],
            "gold": 0,
            "bag": {},
            "equip": {"weapon": None, "armor": None, "accessory": None},
            "relics": {},
            "equipped_relics": [],
            "mounts": [
                {"id": "mount_01", "name": "青羽兽", "rank": "C", "breed_count": 0},
                {"id": "mount_02", "name": "赤兔驹", "rank": "C", "breed_count": 0},
            ],
            "mount_equip": {"saddle": None, "rein": None},
            "active_mount": None,
            "active_mount_id": None,
            "affinity": self.generate_affinity(),
            "insight": {e: 0 for e in ELEMENTS},
            "skills": [],
            "cultivation": {"methods": {}, "active": None, "primary": None, "secondary": []},
            "injury": {"turns": 0, "atk": 0, "def": 0, "spd": 0},
            "stagnation": 0,
            "faction": None,
            "reputation": {f["id"]: 0 for f in NATION_FACTIONS},
            "faction_bonus_applied": False,
            "faction_task_tier": 1,
            "realm_idx": 0,
            "legacy_points": 0,
            "branch": {e: random.choice(BRANCHES) for e in ELEMENTS},
            "talents": [],
            "base_bonus": {"hp": 0, "atk": 0, "def": 0, "spd": 0, "crit": 0, "res": 0, "luck": 0},
            "creation_applied": False,
            "npc_buffs": {"ally_follow": 0, "patrol_alert": 0},
            "followers": [],
            "recipes": [],
            "alchemy_level": 1,
            "alchemy_exp": 0,
            "refine_level": 1,
            "refine_exp": 0,
            "alchemy_spec": None,
            "refine_spec": None,
            "battle_strategy": "均衡",
            "skill_loadout": [],
            "special_items": [],
            "time_tick": 0,
            "age_months": 0,
            "lifespan_months": 0,
            "opening_story_shown": False,
        }

    def generate_affinity(self):
        return {e: random.randint(5, 10) for e in ELEMENTS}

    def ensure_player_fields(self):
        defaults = self.build_new_player()
        for key, val in defaults.items():
            if key not in self.player:
                self.player[key] = val
        if "affinity" not in self.player:
            self.player["affinity"] = self.generate_affinity()
        if "name" not in self.player:
            self.player["name"] = "无名"
        for e in ELEMENTS:
            self.player["affinity"].setdefault(e, 5)
        if "insight" not in self.player:
            self.player["insight"] = {e: 0 for e in ELEMENTS}
        for e in ELEMENTS:
            self.player["insight"].setdefault(e, 0)
        if "skills" not in self.player:
            self.player["skills"] = []
        for sk in self.player.get("skills", []):
            sk.setdefault("rank", 1)
            sk.setdefault("mastery", 0)
            sk.setdefault("power", 1.2)
            sk.setdefault("cooldown", 3)
            sk.setdefault("chance", 0.3)
            sk.setdefault("effect", ELEMENT_EFFECTS.get(sk.get("element"), "burn"))
        for g in self.player.get("equip", {}).values():
            if g:
                self.ensure_gear_meta(g)
        if "injury" not in self.player:
            self.player["injury"] = {"turns": 0, "atk": 0, "def": 0, "spd": 0}
        if "stagnation" not in self.player:
            self.player["stagnation"] = 0
        if "faction" not in self.player:
            self.player["faction"] = None
        if "reputation" not in self.player:
            self.player["reputation"] = {f["id"]: 0 for f in NATION_FACTIONS}
        if "battle_strategy" not in self.player:
            self.player["battle_strategy"] = "均衡"
        if "alchemy_level" not in self.player:
            self.player["alchemy_level"] = 1
        if "alchemy_exp" not in self.player:
            self.player["alchemy_exp"] = 0
        if "refine_level" not in self.player:
            self.player["refine_level"] = 1
        if "refine_exp" not in self.player:
            self.player["refine_exp"] = 0
        if "alchemy_spec" not in self.player:
            self.player["alchemy_spec"] = None
        if "refine_spec" not in self.player:
            self.player["refine_spec"] = None
        if "skill_loadout" not in self.player:
            self.player["skill_loadout"] = []
        if "special_items" not in self.player:
            self.player["special_items"] = []
        if "time_tick" not in self.player:
            self.player["time_tick"] = 0
        if "age_months" not in self.player:
            self.player["age_months"] = 0
        if "lifespan_months" not in self.player:
            self.player["lifespan_months"] = self.compute_lifespan_months()
        else:
            self.player["lifespan_months"] = max(self.player["lifespan_months"], self.compute_lifespan_months())
        if "opening_story_shown" not in self.player:
            self.player["opening_story_shown"] = False
        for f in NATION_FACTIONS:
            self.player["reputation"].setdefault(f["id"], 0)
        if "faction_bonus_applied" not in self.player:
            self.player["faction_bonus_applied"] = False
        if "faction_task_tier" not in self.player:
            self.player["faction_task_tier"] = 1
        if "realm_idx" not in self.player:
            self.player["realm_idx"] = 0
        if "legacy_points" not in self.player:
            self.player["legacy_points"] = 0
        if "branch" not in self.player:
            self.player["branch"] = {e: random.choice(BRANCHES) for e in ELEMENTS}
        for e in ELEMENTS:
            self.player["branch"].setdefault(e, random.choice(BRANCHES))
        if "talents" not in self.player:
            self.player["talents"] = []
        if "base_bonus" not in self.player:
            self.player["base_bonus"] = {"hp": 0, "atk": 0, "def": 0, "spd": 0, "crit": 0, "res": 0, "luck": 0}
        if "creation_applied" not in self.player:
            self.player["creation_applied"] = True
        if "npc_buffs" not in self.player:
            self.player["npc_buffs"] = {"ally_follow": 0, "patrol_alert": 0}
        if "followers" not in self.player:
            self.player["followers"] = []
        if "recipes" not in self.player:
            self.player["recipes"] = []
        if "cultivation" not in self.player:
            self.player["cultivation"] = {"methods": {}, "active": None, "primary": None, "secondary": []}
        self.player["cultivation"].setdefault("methods", {})
        self.player["cultivation"].setdefault("active", None)
        self.player["cultivation"].setdefault("primary", None)
        self.player["cultivation"].setdefault("secondary", [])

    def default_life_stats(self, life_id: int):
        return {
            "life_id": life_id,
            "born_at": date.today().isoformat(),
            "steps": 0,
            "battles": 0,
            "elites": 0,
            "bosses": 0,
            "treasures": 0,
            "mounts": 0,
            "relics": 0,
            "gold_earned": 0,
            "max_level": 1,
            "chapters_cleared": 0,
        }

    def serialize_maze(self, maze):
        if not maze:
            return None
        events = []
        for pos, ev in maze.get("events", {}).items():
            e = dict(ev)
            e["pos"] = list(pos)
            events.append(e)
        return {
            "name": maze.get("name"),
            "w": maze.get("w"),
            "h": maze.get("h"),
            "start": list(maze.get("start")),
            "exit": list(maze.get("exit")),
            "blocks": [list(p) for p in maze.get("blocks", [])],
            "events": events,
            "scale": maze.get("scale", 1.0),
        }

    def deserialize_maze(self, data):
        if not data:
            return None
        blocks = {tuple(b) for b in data.get("blocks", [])}
        events = {tuple(ev["pos"]): ev for ev in data.get("events", [])}
        return {
            "name": data.get("name", "maze"),
            "w": data.get("w"),
            "h": data.get("h"),
            "start": tuple(data.get("start", (1, 1))),
            "exit": tuple(data.get("exit", (1, 1))),
            "blocks": blocks,
            "events": events,
            "scale": data.get("scale", 1.0),
        }

    def load_graveyard(self):
        return load_json_safe(GRAVEYARD_FILE, {"next_id": 1, "used_ids": [], "dead_lives": []})

    def save_graveyard(self, data):
        GRAVEYARD_FILE.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

    def allocate_life_id(self):
        data = self.load_graveyard()
        life_id = data.get("next_id", 1)
        data["used_ids"] = data.get("used_ids", [])
        data["used_ids"].append(life_id)
        data["next_id"] = life_id + 1
        self.save_graveyard(data)
        return life_id

    def load_npc_archive(self):
        return load_json_safe(NPC_ARCHIVE_FILE, [])

    def save_npc_archive(self):
        NPC_ARCHIVE_FILE.write_text(json.dumps(self.npc_archive, ensure_ascii=False, indent=2), encoding="utf-8")

    def save_game(self, manual=False):
        ensure_save_dir()
        payload = {
            "version": 1,
            "alive": True,
            "life_id": self.life_id,
            "life_stats": self.life_stats,
            "player": self.player,
            "faction_task": self.faction_task,
            "chapter_progress": self.chapter_progress,
            "active_quests": self.active_quests,
            "completed_quests": self.completed_quests,
            "maze": self.serialize_maze(self.maze),
            "pos": list(self.pos),
            "chapter_idx": self.chapter_idx,
            "current_chapter_id": self.current_chapter.get("id") if self.current_chapter else None,
            "enemy_pool": self.enemy_pool,
            "enemy_pool_generated": self.enemy_pool_generated,
            "run_mode": self.run_mode,
            "chapter_before_secret": self.chapter_before_secret,
            "secret_unlocked": self.secret_unlocked,
            "secret_dungeons": self.secret_dungeons,
            "secret_refresh_date": self.secret_refresh_date,
            "loot_multiplier": self.loot_multiplier,
            "active_faction": self.active_faction,
            "sect": self.sect,
        }
        SAVE_FILE.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
        if manual:
            messagebox.showinfo("存档", "存档完成。")

    def load_game(self):
        if not SAVE_FILE.exists():
            return False
        data = load_json_safe(SAVE_FILE, None)
        if not data or not data.get("alive", False):
            return False
        self.life_id = data.get("life_id")
        if not self.life_id:
            self.life_id = self.allocate_life_id()
        self.life_stats = data.get("life_stats", self.default_life_stats(self.life_id))
        self.player = data.get("player", self.build_new_player())
        self.ensure_player_fields()
        for key in list(self.player.get("bag", {}).keys()):
            if key.startswith("丹方:"):
                self.learn_recipe(key)
        self.apply_faction_bonus()
        self.faction_task = data.get("faction_task")
        self.chapter_progress = data.get("chapter_progress", {"battles": 0, "elites": 0, "boss": 0, "treasures": 0, "mounts": 0, "relics": 0})
        self.active_quests = data.get("active_quests", [])
        self.completed_quests = data.get("completed_quests", [])
        self.maze = self.deserialize_maze(data.get("maze"))
        pos = data.get("pos", [0, 0])
        self.pos = (pos[0], pos[1])
        self.chapter_idx = data.get("chapter_idx", 0)
        cid = data.get("current_chapter_id")
        self.current_chapter = next((c for c in self.chapters if c["id"] == cid), self.chapters[self.chapter_idx])
        self.current_story = STORY_CHAPTERS.get(self.current_chapter.get("id"), {})
        if not self.active_quests:
            self.active_quests = self.build_chapter_quests(self.current_chapter.get("id"))
        self.enemy_pool = data.get("enemy_pool") or build_chapter_enemies(self.chapter_idx, self.current_chapter.get("scale", 1.0))
        self.enemy_pool_generated = data.get("enemy_pool_generated", False)
        self.run_mode = data.get("run_mode", "chapter")
        self.chapter_before_secret = data.get("chapter_before_secret", 0)
        self.secret_unlocked = data.get("secret_unlocked", False)
        self.secret_dungeons = data.get("secret_dungeons", [])
        self.secret_refresh_date = data.get("secret_refresh_date")
        self.loot_multiplier = data.get("loot_multiplier", 1.0)
        self.active_faction = data.get("active_faction")
        self.sect = data.get("sect")
        if self.secret_unlocked:
            self.btn_secret.config(state="normal")
            self.btn_sect.config(state="normal")
        if self.maze:
            self.describe()
        self.log("已加载存档，继续旅程。")
        if self.show_opening_story(force=False):
            self.save_game()
        return True

    def manual_save(self):
        self.save_game(manual=True)

    def manual_load(self):
        if not SAVE_FILE.exists():
            messagebox.showinfo("读档", "没有可用存档。")
            return
        if messagebox.askyesno("读档", "读档会覆盖当前进度，是否继续？"):
            self.load_game()

    def restart_after_death(self):
        if self.alive:
            return
        self.alive = True
        self.btn_restart.config(state="disabled")
        self.start_new_life()

    def restart_anytime(self):
        self.alive = True
        self.btn_restart.config(state="disabled")
        self.start_new_life()

    def delete_save(self):
        try:
            if SAVE_FILE.exists():
                SAVE_FILE.unlink()
        except Exception:
            pass

    def start_new_life(self):
        self.alive = True
        self.player = self.build_new_player()
        self.life_id = self.allocate_life_id()
        self.life_stats = self.default_life_stats(self.life_id)
        self.faction_task = None
        self.chapter_progress = {"battles": 0, "elites": 0, "boss": 0, "treasures": 0, "mounts": 0, "relics": 0}
        self.run_mode = "chapter"
        self.chapter_before_secret = 0
        self.secret_unlocked = False
        self.btn_secret.config(state="disabled")
        self.btn_sect.config(state="disabled")
        self.show_character_creation()
        self.load_chapter(0)
        self.show_opening_story(force=True)
        self.log(f"新生旅者 ID #{self.life_id} 已启程。")
        self.save_game()

    def generate_npc_from_life(self, life_record: dict):
        life_id = life_record.get("life_id", 0)
        stats = life_record.get("stats", {})
        rng = random.Random(1000 + life_id)
        surnames = ["沈", "林", "叶", "司徒", "顾", "白", "萧", "楚", "夏", "姜", "洛", "唐", "墨", "云", "陆", "韩", "苏"]
        given = ["寒星", "折月", "青岚", "行舟", "晚照", "孤鸿", "赤霄", "霜影", "墨澜", "清衡", "北斗", "若水"]
        name = rng.choice(surnames) + rng.choice(given)
        title_pool = ["遗世旅者", "断境行者", "苍痕旧影", "迷途誓者", "秘境访客", "遗火守望"]
        if stats.get("bosses", 0) > 0:
            title_pool.append("破关者")
        if stats.get("max_level", 1) >= 8:
            title_pool.append("踏风者")
        if stats.get("relics", 0) >= 2:
            title_pool.append("收藏者")
        title = rng.choice(title_pool)
        chapter = life_record.get("chapter", "未知之地")
        cause = life_record.get("cause", "不详")
        tone = rng.choice(["沉静", "冷冽", "温和", "寡言", "执拗"])
        story = (
            f"第{life_id}号旅者，止步于{chapter}。"
            f"他在生前{tone}而坚定，留下的足迹与战痕至今未散。"
            f"传闻其死因与“{cause}”有关，因此化作游魂般的指引者。"
        )
        dialogue = rng.choice(
            [
                "若你愿意聆听，我可以讲述一段未竟之路。",
                "别回头，风中有我留下的叹息。",
                "我失去的，并非生命，而是下一次选择。",
                "前方不是终点，只是你新的名字。",
            ]
        )
        affinity = {e: rng.randint(4, 9) for e in ELEMENTS}
        main_element = self.main_element_from_affinity(affinity)
        return {
            "npc_id": f"npc_{life_id}",
            "name": name,
            "title": title,
            "story": story,
            "dialogue": dialogue,
            "source_life_id": life_id,
            "affinity": affinity,
            "main_element": main_element,
        }

    def record_death(self, cause: str):
        life_record = {
            "life_id": self.life_id,
            "died_at": date.today().isoformat(),
            "cause": cause,
            "chapter": self.current_chapter.get("name") if self.current_chapter else "未知",
            "stats": self.life_stats,
            "snapshot": {
                "lvl": self.player.get("lvl"),
                "gold": self.player.get("gold"),
                "equip": self.player.get("equip"),
                "relics": list(self.player.get("relics", {}).keys()),
            },
        }
        data = self.load_graveyard()
        data["dead_lives"] = data.get("dead_lives", [])
        data["dead_lives"].append(life_record)
        self.save_graveyard(data)
        npc = self.generate_npc_from_life(life_record)
        self.npc_archive.append(npc)
        self.save_npc_archive()
        return npc, life_record

    def build_death_autobiography(self, life_record: dict):
        stats = life_record.get("stats", {})
        chapter = life_record.get("chapter", "未知之地")
        cause = life_record.get("cause", "未知")
        lvl = life_record.get("snapshot", {}).get("lvl", 1)
        battles = stats.get("battles", 0)
        elites = stats.get("elites", 0)
        bosses = stats.get("bosses", 0)
        relics = stats.get("relics", 0)
        tone = "谨慎" if battles < 6 else ("果断" if elites >= 2 else "执拗")
        return (
            f"自传：我走到{chapter}便止步了。"
            f"一生{tone}，共战{battles}场，精英{elites}，首领{bosses}。"
            f"曾得收藏品{relics}件，却仍死于“{cause}”。"
        )

    def build_death_route_advice(self, life_record: dict):
        stats = life_record.get("stats", {})
        battles = stats.get("battles", 0)
        elites = stats.get("elites", 0)
        bosses = stats.get("bosses", 0)
        treasures = stats.get("treasures", 0)
        mounts = stats.get("mounts", 0)
        relics = stats.get("relics", 0)
        tips = []
        if battles < 5:
            tips.append("建议先刷几场普通战斗稳固属性。")
        if elites == 0:
            tips.append("优先击败精英获取更好掉落。")
        if treasures == 0:
            tips.append("优先搜集宝材，炼化提升属性。")
        if mounts == 0:
            tips.append("寻找坐骑提高速度与收益。")
        if relics == 0:
            tips.append("争取收藏品，提升长线强度。")
        if bosses == 0:
            tips.append("首领战前建议切换保守或控制策略。")
        if not tips:
            tips.append("整体路线已稳，注意元素克制与技能冷却。")
        return "死亡路线复盘：" + " ".join(tips)

    def maybe_spawn_npc_event(self):
        if not self.npc_archive:
            return
        if random.random() > 0.35:
            return
        free_cells = [
            (x, y)
            for x in range(self.maze["w"])
            for y in range(self.maze["h"])
            if self.can_walk(x, y)
            and (x, y) != self.maze["start"]
            and (x, y) != self.maze["exit"]
            and (x, y) not in self.maze["events"]
        ]
        if not free_cells:
            return
        pos = random.choice(free_cells)
        npc = random.choice(self.npc_archive)
        self.maze["events"][pos] = {"type": "npc", "pos": pos, "npc": npc}

    def spawn_faction_npcs(self, count=2):
        if not self.current_chapter:
            return
        free_cells = [
            (x, y)
            for x in range(self.maze["w"])
            for y in range(self.maze["h"])
            if self.can_walk(x, y)
            and (x, y) != self.maze["start"]
            and (x, y) != self.maze["exit"]
            and (x, y) not in self.maze["events"]
        ]
        random.shuffle(free_cells)
        picks = free_cells[:count]
        chap_faction = self.current_chapter.get("faction")
        for pos in picks:
            fid = chap_faction or random.choice([f["id"] for f in NATION_FACTIONS])
            self.maze["events"][pos] = {
                "type": "faction_npc",
                "pos": pos,
                "faction": fid,
                "name": f"{next((f['name'] for f in NATION_FACTIONS if f['id']==fid), fid)}使者",
                "background": "巡游各地，传递阵营消息。",
                "goal": "观察局势，寻找可合作的修行者。",
                "mood": random.choice(["平静", "警惕", "友好"]),
                "relation": 0,
                "memory": [],
            }

    def on_quit(self):
        self.save_game()
        if self.llm_server_process and self.llm_server_process.poll() is None:
            try:
                self.llm_server_process.terminate()
            except Exception:
                pass
        self.root.destroy()

    def generate_entity_affinity(self, base_min=4, base_max=9):
        return {e: random.randint(base_min, base_max) for e in ELEMENTS}

    def main_element_from_affinity(self, affinity: dict):
        if not affinity:
            return random.choice(ELEMENTS)
        return max(affinity.keys(), key=lambda k: affinity.get(k, 0))

    def ensure_enemy_affinity(self, enemy: dict):
        if "affinity" not in enemy:
            enemy["affinity"] = self.generate_entity_affinity()
        if "main_element" not in enemy:
            enemy["main_element"] = self.main_element_from_affinity(enemy["affinity"])
        enemy.setdefault("max_hp", enemy.get("hp", 1))
        return enemy

    def ensure_enemy_faction(self, enemy: dict):
        if "faction" not in enemy:
            enemy["faction"] = random.choice([f["id"] for f in NATION_FACTIONS])
        return enemy

    def faction_relation(self, fa: str, fb: str):
        if not fa or not fb or fa == fb:
            return 1
        return FACTION_RELATIONS.get((fa, fb), 0)

    def apply_faction_bonus(self):
        if self.player.get("faction_bonus_applied"):
            return
        fid = self.player.get("faction")
        if not fid:
            return
        bonus = FACTION_BONUS.get(fid, {})
        for stat, val in bonus.items():
            if stat == "max_hp":
                self.player["max_hp"] += val
                self.player["hp"] = min(self.player["hp"] + val, self.player["max_hp"])
            else:
                self.player[stat] += val
        self.player["faction_bonus_applied"] = True

    def current_realm(self):
        idx = min(self.player.get("realm_idx", 0), len(REALM_STAGES) - 1)
        return REALM_STAGES[idx]

    def breakthrough_item_name(self, realm_name: str):
        mats = BREAKTHROUGH_RECIPES.get(realm_name, {}).get("materials", [])
        item = mats[0] if mats else realm_name
        return f"破境灵材·{item}"

    def breakthrough_pill_name(self, realm_name: str):
        pill = BREAKTHROUGH_RECIPES.get(realm_name, {}).get("pill", realm_name)
        return f"破境丹·{pill}"

    def recipe_unlock_item(self, realm_name: str):
        pill = BREAKTHROUGH_RECIPES.get(realm_name, {}).get("pill", realm_name)
        return f"丹方:{pill}"

    def recipe_pill_id(self, realm_name: str):
        return self.breakthrough_pill_name(realm_name)

    def recipe_materials(self, realm_name: str):
        return BREAKTHROUGH_RECIPES.get(realm_name, {}).get("materials", [])

    def learn_recipe(self, item_id: str):
        if not item_id or not item_id.startswith("丹方:"):
            return
        pill_name = item_id.replace("丹方:", "").strip()
        if not pill_name:
            return
        learned = set(self.player.get("recipes", []))
        if pill_name in learned:
            self.log(f"已学会丹方：{pill_name}", "system")
            return
        learned.add(pill_name)
        self.player["recipes"] = list(learned)
        self.log(f"学会丹方：{pill_name}", "system")

    def has_fire_affinity(self):
        return self.player.get("affinity", {}).get("火", 0) >= 5

    def has_fire_disciple(self):
        if not self.sect:
            return False
        for d in self.sect.get("disciples", []):
            if d.get("element") == "火":
                return True
        return False

    def gain_alchemy_exp(self, amount: int):
        self.player["alchemy_exp"] += amount
        need = 30 + self.player["alchemy_level"] * 20
        while self.player["alchemy_exp"] >= need:
            self.player["alchemy_exp"] -= need
            self.player["alchemy_level"] += 1
            need = 30 + self.player["alchemy_level"] * 20
            self.log(f"炼丹师等级提升至 {self.player['alchemy_level']}", "system")

    def gain_refine_exp(self, amount: int):
        self.player["refine_exp"] += amount
        need = 30 + self.player["refine_level"] * 20
        while self.player["refine_exp"] >= need:
            self.player["refine_exp"] -= need
            self.player["refine_level"] += 1
            need = 30 + self.player["refine_level"] * 20
            self.log(f"炼器师等级提升至 {self.player['refine_level']}", "system")

    def alchemy_spec_bonus(self):
        spec = self.player.get("alchemy_spec")
        return ALCHEMY_SPECS.get(spec, {"success": 0.0, "crit": 0.0})

    def refine_spec_bonus(self):
        spec = self.player.get("refine_spec")
        return REFINE_SPECS.get(spec, {"bonus": 0.0})

    def pick_breakthrough_item(self, realm_idx: int):
        realm_idx = max(0, min(realm_idx, len(BREAKTHROUGH_REALMS) - 1))
        realm_name = BREAKTHROUGH_REALMS[realm_idx]
        mats = self.recipe_materials(realm_name)
        if not mats:
            return self.breakthrough_item_name(realm_name)
        return f"破境灵材·{random.choice(mats)}"

    def can_breakthrough(self):
        stage = self.current_realm()
        return self.player["lvl"] >= stage["lvl_cap"] and self.player.get("realm_idx", 0) < len(REALM_STAGES) - 1

    def attempt_breakthrough(self):
        if not self.can_breakthrough():
            self.log("境界未达突破条件。", "system")
            return
        stage = self.current_realm()
        chance = stage["success"]
        realm_name = stage["name"]
        item = self.breakthrough_item_name(realm_name)
        if self.player["bag"].get(item, 0) > 0:
            bonus = BREAKTHROUGH_BONUS.get(realm_name, 0.1)
            chance = min(0.98, chance + bonus)
            self.player["bag"][item] -= 1
            self.log(f"使用{item}，突破概率提升至 {int(chance*100)}%。", "system")
        pill = self.breakthrough_pill_name(realm_name)
        if self.player["bag"].get(pill, 0) > 0:
            bonus = BREAKTHROUGH_PILL_BONUS.get(realm_name, 0.06)
            chance = min(0.98, chance + bonus)
            self.player["bag"][pill] -= 1
            self.log(f"服用{pill}，突破概率提升至 {int(chance*100)}%。", "system")
        if random.random() <= chance:
            self.player["realm_idx"] += 1
            next_name = self.current_realm()["name"]
            bonus = REALM_BONUS.get(next_name, {})
            for stat, val in bonus.items():
                if stat == "max_hp":
                    self.player["max_hp"] += val
                    self.player["hp"] = min(self.player["hp"] + val, self.player["max_hp"])
                else:
                    self.player[stat] += val
            self.log(f"突破成功，境界提升至 {next_name}。", "system")
        else:
            npc, life_record = self.record_death("突破失败")
            self.delete_save()
            self.alive = False
            self.log("突破失败，身死道消。", "system")
            self.log(f"遗世旅者诞生：{npc.get('name','未知')}·{npc.get('title','')}", "system")
            self.log(self.build_death_autobiography(life_record), "system")
            self.log(self.build_death_route_advice(life_record), "system")
            self.log("点击“新生”开始新的旅程。", "system")
            self.btn_restart.config(state="normal")

    def player_main_element(self):
        primary = self.player["cultivation"].get("primary")
        if primary:
            return primary
        return self.main_element_from_affinity(self.player.get("affinity", {}))

    def element_advantage(self, atk_element: str, def_affinity: dict):
        if not atk_element or not def_affinity:
            return 1.0
        def_main = self.main_element_from_affinity(def_affinity)
        if ELEMENT_COUNTERS.get(atk_element) == def_main:
            return 1.15
        if ELEMENT_COUNTERS.get(def_main) == atk_element:
            return 0.9
        return 1.0

    def init_status(self):
        return {"burn": None, "poison": None, "stun": 0, "slow": 0, "shield": 0}

    def apply_status(self, status, effect: str, potency: int):
        if effect in ("burn", "poison"):
            status[effect] = {"turns": 3, "dmg": potency}
        elif effect == "stun":
            status["stun"] = max(status.get("stun", 0), 1)
        elif effect == "slow":
            status["slow"] = max(status.get("slow", 0), 2)
        elif effect == "shield":
            status["shield"] = max(status.get("shield", 0), 2)

    def format_status(self, status):
        parts = []
        if status.get("burn"):
            parts.append(f"灼烧{status['burn'].get('turns',0)}")
        if status.get("poison"):
            parts.append(f"中毒{status['poison'].get('turns',0)}")
        if status.get("stun", 0) > 0:
            parts.append(f"眩晕{status.get('stun',0)}")
        if status.get("slow", 0) > 0:
            parts.append(f"迟缓{status.get('slow',0)}")
        if status.get("shield", 0) > 0:
            parts.append(f"护盾{status.get('shield',0)}")
        return " ".join(parts) if parts else "无"

    def log_battle_status(self, enemy, player_status, enemy_status):
        ps = self.format_status(player_status)
        es = self.format_status(enemy_status)
        self.log(f"[状态] 你: {self.player['hp']}/{self.player['max_hp']} | {ps}", "system")
        self.log(f"[状态] {enemy['name']}: {enemy['hp']}/{enemy.get('max_hp', enemy['hp'])} | {es}", "system")
        self.battle_player_var.set(f"你: {self.player['hp']}/{self.player['max_hp']}")
        self.battle_enemy_var.set(f"{enemy['name']}: {enemy['hp']}/{enemy.get('max_hp', enemy['hp'])}")
        self.battle_player_status_var.set(f"你状态: {ps}")
        self.battle_enemy_status_var.set(f"敌状态: {es}")
        self.battle_player_bar["maximum"] = max(1, self.player["max_hp"])
        self.battle_player_bar["value"] = max(0, self.player["hp"])
        self.battle_enemy_bar["maximum"] = max(1, enemy.get("max_hp", enemy["hp"]))
        self.battle_enemy_bar["value"] = max(0, enemy["hp"])
        self.battle_skill_box.delete(0, "end")
        for s in self.get_active_skills():
            self.battle_skill_box.insert(
                "end",
                f"{s.get('name')} | 阶{s.get('rank',1)} | CD {s.get('cd_left',0)} | {s.get('effect','')}",
            )
        active = self.get_active_skills()
        total = len(self.player.get("skills", []))
        self.battle_hint_var.set(f"技能池：{len(active)}/{total}  |  策略：{self.player.get('battle_strategy','均衡')}")
        self.refresh_action_box()
        self.root.update_idletasks()

    def refresh_action_box(self):
        self.battle_action_box.delete(0, "end")
        self.battle_action_box.insert("end", "普攻")
        self.battle_action_box.insert("end", "等待")
        for s in self.get_active_skills():
            self.battle_action_box.insert("end", f"技能: {s.get('name')}")
        for w in self.battle_skill_btn_frame.winfo_children():
            w.destroy()
        for s in self.get_active_skills():
            cd = s.get("cd_left", 0)
            label = f"{s.get('name')} (CD {cd})"
            btn = tk.Button(
                self.battle_skill_btn_frame,
                text=label,
                state="disabled" if cd > 0 else "normal",
                command=lambda n=s.get("name"): [self.battle_action_var.set(f"技能: {n}"), self.commit_battle_action()],
            )
            btn.pack(side="left", padx=2)

    def set_battle_strategy(self):
        if self.player:
            self.player["battle_strategy"] = self.battle_strategy_var.get()

    def get_active_skills(self):
        skills = self.player.get("skills", [])
        loadout = self.player.get("skill_loadout", [])
        if not loadout:
            return skills
        picked = [s for s in skills if s.get("name") in loadout]
        return picked if picked else skills

    def choose_auto_action(self, enemy, player_status, enemy_status, elem_adv, faction_mult, injury):
        strategy = self.player.get("battle_strategy", "均衡")
        hp_ratio = self.player["hp"] / max(1, self.player["max_hp"])
        skills = [s for s in self.get_active_skills() if s.get("cd_left", 0) <= 0]
        if strategy == "保守" and hp_ratio < 0.45:
            return "等待", None
        if strategy == "控制":
            ctl = [s for s in skills if s.get("effect") in ("stun", "slow", "poison", "burn", "shield")]
            if ctl:
                return "技能", max(ctl, key=lambda s: s.get("chance", 0.3))
        if strategy == "爆发":
            if skills:
                return "技能", max(skills, key=lambda s: s.get("power", 1.2))
        if strategy == "均衡":
            for sk in sorted(skills, key=lambda s: s.get("cooldown", 5)):
                if random.random() <= sk.get("chance", 0.3):
                    return "技能", sk
        if skills and random.random() < 0.4:
            return "技能", random.choice(skills)
        return "普攻", None

    def commit_battle_action(self):
        sel = self.battle_action_box.curselection()
        if not sel:
            return
        text = self.battle_action_box.get(sel[0])
        self.battle_action_var.set(text)

    def wait_for_action(self):
        self.battle_action_var.set("")
        self.root.wait_variable(self.battle_action_var)
        return self.battle_action_var.get()

    def tick_cooldowns(self):
        for sk in self.player.get("skills", []):
            if sk.get("cd_left", 0) > 0:
                sk["cd_left"] -= 1

    def tick_status_start(self, status, target_name: str, is_player: bool):
        total_dot = 0
        for key in ("burn", "poison"):
            dot = status.get(key)
            if dot and dot.get("turns", 0) > 0:
                total_dot += dot.get("dmg", 0)
                dot["turns"] -= 1
                if dot["turns"] <= 0:
                    status[key] = None
        if total_dot > 0:
            if is_player:
                self.player["hp"] -= total_dot
            else:
                self.current_enemy["hp"] -= total_dot
            eff_tag = "eff_burn" if status.get("burn") else "eff_poison"
            self.log(f"{target_name} 受到持续伤害 {total_dot}", eff_tag)

    def compute_damage(self, base_dmg: int, defender_status):
        dmg = base_dmg
        reduced = False
        reduced_by = 0
        if defender_status.get("shield", 0) > 0:
            reduced_by = int(dmg * 0.3)
            dmg = int(dmg * 0.7)
            defender_status["shield"] -= 1
            reduced = True
        return max(0, dmg), reduced, reduced_by

    def roll_crit(self, crit_value: int):
        chance = min(0.5, max(0.0, crit_value / 100.0))
        return random.random() < chance

    def update_quests(self, key: str, amount: int = 1):
        if not self.active_quests:
            return
        for q in self.active_quests:
            if q.get("completed"):
                continue
            targets = q.get("targets", {})
            if key not in targets:
                continue
            prog = q.setdefault("progress", {})
            prog[key] = min(targets[key], prog.get(key, 0) + amount)
            if all(prog.get(k, 0) >= v for k, v in targets.items()):
                q["completed"] = True
                reward = q.get("reward", {})
                gold, exp, items = self.apply_quest_reward(reward)
                self.completed_quests.append(q["id"])
                extra = f" 物品:{'、'.join(items)}" if items else ""
                self.log(f"支线完成：{q.get('name')}，奖励 金币{gold} 经验{exp}{extra}", "system")

    def add_special_item(self, npc: dict):
        item = npc.get("item")
        if not item:
            return
        owned = self.player.get("special_items", [])
        if item in owned:
            return
        owned.append(item)
        self.player["special_items"] = owned
        self.player["bag"][item] = self.player["bag"].get(item, 0) + 1
        self.log(f"获得专属物品：{item}", "system")

    def apply_quest_reward(self, reward: dict):
        gold = reward.get("gold", 0)
        exp = reward.get("exp", 0)
        items = []
        if gold:
            self.player["gold"] += gold
        if exp:
            self.add_exp(exp)
        for key, prefix in [
            ("items", ""),
            ("blueprints", "蓝图:"),
            ("method_frags", "功法碎片:"),
            ("skill_pages", "技能残页:"),
        ]:
            for entry in reward.get(key, []):
                if isinstance(entry, dict):
                    name = entry.get("id") or entry.get("name")
                    count = int(entry.get("count", 1))
                else:
                    name = str(entry)
                    count = 1
                if not name:
                    continue
                item_name = f"{prefix}:{name}" if prefix else name
                self.player["bag"][item_name] = self.player["bag"].get(item_name, 0) + count
                items.append(f"{item_name}x{count}")
        return gold, exp, items

    def get_injury_penalty(self):
        inj = self.player.get("injury", {"turns": 0})
        if inj.get("turns", 0) > 0:
            return inj
        return {"turns": 0, "atk": 0, "def": 0, "spd": 0}

    def decay_injury(self):
        inj = self.player.get("injury", {"turns": 0})
        if inj.get("turns", 0) > 0:
            inj["turns"] -= 1
            if inj["turns"] <= 0:
                self.player["injury"] = {"turns": 0, "atk": 0, "def": 0, "spd": 0}

    def compute_lifespan_months(self):
        realm_idx = self.player.get("realm_idx", 0)
        lvl = self.player.get("lvl", 1)
        base = 240  # 20 years
        return base + realm_idx * 120 + lvl * 6

    def compute_disciple_lifespan(self, d: dict):
        realm_idx = d.get("realm_idx", 0)
        lvl = d.get("lvl", 1)
        base = 180  # 15 years
        return base + realm_idx * 90 + lvl * 4

    def current_month(self):
        return self.player.get("time_tick", 0) // 3

    def advance_time(self, ticks: int = 1):
        self.player["time_tick"] += ticks
        self.player["age_months"] = self.current_month()
        self.player["lifespan_months"] = max(self.player["lifespan_months"], self.compute_lifespan_months())
        # sect monthly attack check
        if ticks > 0:
            if self.player["time_tick"] % 3 == 0 and self.sect:
                self.auto_run_sect_monthly()
                if random.random() < 0.25:
                    self.sect_under_attack()
        if self.player["age_months"] >= self.player["lifespan_months"]:
            npc, life_record = self.record_death("寿元耗尽")
            self.delete_save()
            self.alive = False
            self.log(f"寿元耗尽：遗世旅者已诞生：{npc.get('name','未知')}·{npc.get('title','')}", "system")
            self.log(self.build_death_autobiography(life_record), "system")
            self.log(self.build_death_route_advice(life_record), "system")
            self.log("点击“新生”开始新的旅程。", "system")
            self.btn_restart.config(state="normal")

    def attack_multiplier_from_status(self, attacker_status):
        mult = 1.0
        if attacker_status.get("slow", 0) > 0:
            mult *= 0.8
            attacker_status["slow"] -= 1
        return mult

    def compute_action_count(self, spd_a: int, spd_b: int):
        if spd_a >= spd_b + 8 or spd_a >= int(spd_b * 1.5):
            return 2
        return 1

    def total_insight(self):
        return sum(self.player.get("insight", {}).values())

    def cultivation_speed(self, element: str):
        affinity = self.player.get("affinity", {}).get(element, 5)
        insight_elem = self.player.get("insight", {}).get(element, 0)
        base = 5
        speed = base + affinity * 0.6 + insight_elem * 1.2 + self.total_insight() * 0.2
        primary = self.player["cultivation"].get("primary")
        secondary = self.player["cultivation"].get("secondary", [])
        if primary == element:
            speed *= 1.2
        elif element in secondary:
            speed *= 1.1
        if primary and ELEMENT_COUNTERS.get(primary) == element:
            speed *= 0.7
        if primary and ELEMENT_COUNTERS.get(element) == primary:
            speed *= 0.8
        if self.player.get("stagnation", 0) > 0:
            speed *= 0.7
        return int(speed + random.randint(0, 3))

    def recommend_cultivation(self):
        affinity = self.player.get("affinity", {})
        if not affinity:
            return "暂无数据"
        best_elem = max(affinity.keys(), key=lambda k: affinity.get(k, 0))
        insight = self.player.get("insight", {}).get(best_elem, 0)
        candidates = [m for m in METHOD_CATALOG if m["element"] == best_elem]
        method_name = candidates[0]["name"] if candidates else "无"
        return f"优先修炼 {best_elem}（亲和{affinity.get(best_elem,0)}，悟性{insight}），可先练 {method_name}"

    def recommend_materials(self):
        affinity = self.player.get("affinity", {})
        if not affinity:
            return "暂无"
        best_elem = max(affinity.keys(), key=lambda k: affinity.get(k, 0))
        frag_need = []
        for key, label in [("技能残页", "技能残页"), ("功法碎片", "功法碎片"), ("装备蓝图", "装备蓝图")]:
            need = 0
            for item, cnt in self.player.get("bag", {}).items():
                if item.startswith(f"{label}:"):
                    need += cnt
            if need == 0:
                frag_need.append(label)
        hint = f"建议刷 {best_elem} 系宝材"
        elem_map = {"human": "金", "yao": "木", "mo": "火", "xian": "水"}
        chapters = [c["name"] for c in CHAPTER_PLAN if elem_map.get(c.get("faction")) == best_elem]
        if chapters:
            hint += f"，推荐章节：{'、'.join(chapters[:2])}"
        if frag_need:
            hint += f"，同时收集 {('、'.join(frag_need))}"
        return hint

    def apply_element_bonus(self, element: str, stage_idx: int):
        weights = ELEMENT_BONUS_WEIGHTS.get(element, {})
        scale = STAGE_BONUS_SCALE.get(stage_idx + 1, 1)
        for stat, base in weights.items():
            inc = base * scale
            if stat == "max_hp":
                self.player["max_hp"] += inc
                self.player["hp"] = min(self.player["hp"] + inc, self.player["max_hp"])
            else:
                self.player[stat] += inc

    def grant_skill(self, element: str, stage_idx: int, method: dict):
        stage_name = CULTIVATION_STAGES[stage_idx]["name"]
        skill_rank = {1: "初式", 3: "真诀", 4: "奥义"}.get(stage_idx, "术")
        mutation = method.get("mutation", "异")
        if stage_idx >= len(CULTIVATION_STAGES) - 1:
            skill_name = f"{mutation}·{element}{skill_rank}"
        else:
            skill_name = f"{element}·{skill_rank}"
        key = f"{method['id']}_{stage_idx}"
        for s in self.player.get("skills", []):
            if s.get("key") == key:
                return
        power = 1.2 + 0.25 * stage_idx
        cooldown = max(2, 6 - stage_idx)
        effect = ELEMENT_EFFECTS.get(element, "burn")
        chance = 0.35 + 0.08 * stage_idx
        branch = self.player["branch"].get(element, "阳")
        if branch == "阳":
            power += BRANCH_BONUS["阳"]["power"]
            chance += BRANCH_BONUS["阳"]["effect_boost"]
        else:
            cooldown = max(1, cooldown + BRANCH_BONUS["阴"]["cooldown"])
            chance += BRANCH_BONUS["阴"]["chance"]
        self.player.setdefault("skills", []).append(
            {
                "key": key,
                "name": skill_name,
                "element": element,
                "stage": stage_name,
                "method_id": method["id"],
                "desc": f"源自 {method['name']} 的{stage_name}之技。",
                "power": power,
                "cooldown": cooldown,
                "effect": effect,
                "chance": chance,
                "rank": 1,
                "mastery": 0,
            }
        )
        self.log(f"领悟技能：{skill_name}（{stage_name}）", "skill")

    def train_method_once(self, method_id: str):
        method = METHOD_BY_ID.get(method_id)
        if not method:
            return
        stone_cost = {"黄": 1, "玄": 2, "地": 3, "天": 4, "神": 5}.get(method.get("tier", "黄"), 1)
        if self.player["bag"].get("灵石", 0) < stone_cost:
            self.log(f"灵石不足，修炼需要 灵石x{stone_cost}。", "system")
            return
        self.player["bag"]["灵石"] -= stone_cost
        if self.player.get("stagnation", 0) > 0:
            self.player["stagnation"] -= 1
            self.log("经脉凝滞，修炼效率降低。", "system")
        self.player["cultivation"]["active"] = method_id
        if not self.player["cultivation"].get("primary"):
            self.player["cultivation"]["primary"] = method["element"]
        else:
            sec = self.player["cultivation"].get("secondary", [])
            if method["element"] != self.player["cultivation"]["primary"] and method["element"] not in sec:
                if len(sec) < 2:
                    sec.append(method["element"])
                    self.player["cultivation"]["secondary"] = sec
        primary = self.player["cultivation"].get("primary")
        if primary and ELEMENT_COUNTERS.get(primary) == method["element"]:
            if random.random() < 0.25:
                backlash = max(5, int(self.player["max_hp"] * 0.08))
                self.player["hp"] = max(1, self.player["hp"] - backlash)
                self.player["injury"] = {"turns": 3, "atk": 2, "def": 1, "spd": 1}
                self.log(f"功法冲突走火入魔，生命 -{backlash}", "eff_burn")
                self.save_game()
                return
        if primary and ELEMENT_COUNTERS.get(method["element"]) == primary:
            if random.random() < 0.15:
                self.log("功法被主修抑制，修炼失败。", "system")
                self.player["stagnation"] = max(self.player.get("stagnation", 0), 2)
                self.save_game()
                return
        records = self.player["cultivation"]["methods"]
        rec = records.get(method_id, {"stage": 0, "progress": 0, "completed": False})
        stage_idx = rec["stage"]
        if stage_idx >= len(CULTIVATION_STAGES) - 1:
            self.log(f"{method['name']} 已圆满。")
            return
        gain = self.cultivation_speed(method["element"])
        rec["progress"] += gain
        advanced = False
        while stage_idx < len(CULTIVATION_STAGES) - 1:
            need = CULTIVATION_STAGES[stage_idx]["need"]
            if rec["progress"] < need:
                break
            rec["progress"] -= need
            stage_idx += 1
            rec["stage"] = stage_idx
            advanced = True
            self.apply_element_bonus(method["element"], stage_idx)
            if CULTIVATION_STAGES[stage_idx].get("skill"):
                self.grant_skill(method["element"], stage_idx, method)
            self.log(f"{method['name']} 突破至 {CULTIVATION_STAGES[stage_idx]['name']}")
            if stage_idx >= len(CULTIVATION_STAGES) - 1 and not rec.get("completed"):
                gain_insight = 1 + method.get("tier_idx", 0)
                self.player["insight"][method["element"]] += gain_insight
                rec["completed"] = True
                self.log(f"{method['name']} 圆满，{method['element']}悟性 +{gain_insight}")
        records[method_id] = rec
        if not advanced:
            self.log(f"{method['name']} 修炼进度 +{gain}（{rec['progress']}/{CULTIVATION_STAGES[stage_idx]['need']}）")
        self.save_game()


    # ---------- chapter / map ----------
    def load_chapter(self, idx: int, force: bool = False):
        if idx >= len(self.chapters):
            messagebox.showinfo("提示", "所有章节已通关！")
            return
        self.chapter_idx = idx
        chap = self.chapters[idx]
        if not force and self.player["lvl"] < chap.get("lvl_req", 1):
            messagebox.showinfo("提示", f"等级不足，需 {chap.get('lvl_req',1)} 级进入该章节。")
            return
        self.current_chapter = chap
        self.chapter_progress = {"battles": 0, "elites": 0, "boss": 0, "treasures": 0, "mounts": 0, "relics": 0}
        self.chapter_context = {"faction": chap.get("faction"), "story": chap.get("story")}
        self.current_story = STORY_CHAPTERS.get(chap.get("id"), {})
        self.active_quests = self.build_chapter_quests(chap.get("id"))
        level_gap = (idx + 1) - self.player.get("lvl", 1)
        gap_scale = 1.0 + max(-0.3, min(0.3, level_gap * 0.06))
        chapter_scale = 1.0 + idx * 0.18
        effective_scale = chap.get("scale", 1.0) * gap_scale * chapter_scale
        self.enemy_pool = build_chapter_enemies(idx, effective_scale)
        self.enemy_pool_generated = True
        self.run_mode = "chapter"
        self.loot_multiplier = 1.0
        self.active_faction = None
        if chap["kind"] == "file":
            self.maze = load_maze(chap["path"])
        else:
            size = chap.get("size", 30)
            self.maze = generate_maze(size, size, seed=chap.get("seed"))
        self.current_chapter["idx"] = idx
        self.maze["name"] = chap["name"]
        self.maze["scale"] = chap.get("scale", 1.0)
        self.pos = self.maze["start"]
        self.player["hp"] = self.player["max_hp"]
        self.spawn_special_events(count=4 if max(self.maze["w"], self.maze["h"]) >= 30 else 2)
        self.maybe_spawn_npc_event()
        self.spawn_faction_npcs(count=2)
        self.spawn_story_npcs()
        self.spawn_story_events()
        self.log(f"进入章节：{chap['name']} （{self.maze['w']}x{self.maze['h']}）")
        if chap.get("story"):
            self.log(f"章节剧情：{chap['story']}", "system")
        if chap.get("faction"):
            f_name = next((f["name"] for f in NATION_FACTIONS if f["id"] == chap["faction"]), chap["faction"])
            self.log(f"本章势力：{f_name}", "system")
        if idx == 0:
            self.play_dialogue("ch1_intro")
        self.describe()

    def advance_chapter(self):
        if self.chapter_idx + 1 < len(self.chapters):
            if self.chapter_idx == 0:
                self.unlock_secret_content()
            self.life_stats["chapters_cleared"] = self.life_stats.get("chapters_cleared", 0) + 1
            if self.sect:
                self.player["legacy_points"] = self.player.get("legacy_points", 0) + 1
            self.load_chapter(self.chapter_idx + 1)
        else:
            messagebox.showinfo("通关", "恭喜，已完成所有章节！")
            self.root.destroy()

    def goal_text(self):
        if not self.current_chapter:
            return ""
        goal = self.current_chapter.get("goal", {})
        if not goal:
            return ""
        parts = []
        mapping = {
            "battles": "战斗",
            "elites": "精英",
            "boss": "首领",
            "treasures": "宝材",
            "mounts": "坐骑",
            "relics": "收藏品",
        }
        for k, v in goal.items():
            cur = self.chapter_progress.get(k, 0)
            parts.append(f"{mapping.get(k,k)} {cur}/{v}")
        return " | 目标: " + " ".join(parts)

    def quest_summary_text(self):
        if not self.active_quests:
            return ""
        pending = [q for q in self.active_quests if not q.get("completed")]
        if not pending:
            return " | 支线:已完成"
        q = pending[0]
        targets = q.get("targets", {})
        prog = q.get("progress", {})
        prog_text = " ".join([f"{k} {prog.get(k,0)}/{v}" for k, v in targets.items()])
        return f" | 支线:{q.get('name')} {prog_text}"

    def goal_completed(self):
        if not self.current_chapter:
            return True
        goal = self.current_chapter.get("goal", {})
        for k, v in goal.items():
            if self.chapter_progress.get(k, 0) < v:
                return False
        return True

    # ---------- map / movement ----------
    def describe(self):
        x, y = self.pos
        can = {k: self.can_walk(x + dx, y + dy) for k, (dx, dy) in MOVE.items()}
        status = "出口" if self.pos == self.maze["exit"] else "前进中"
        ok = lambda flag: "√" if flag else "×"
        age = self.player.get("age_months", 0)
        life = self.player.get("lifespan_months", 0)
        month = self.current_month()
        visible_cells = self.minimap_visible_cells(self.pos)
        boss_pos = self.find_boss_pos()
        boss_hint = f" | 首领方向:{self.direction_hint(self.pos, boss_pos)}" if boss_pos and boss_pos in visible_cells else ""
        mount_pos = self.find_event_pos("mount")
        treasure_pos = self.find_event_pos("treasure")
        mount_hint = f" | 坐骑方向:{self.direction_hint(self.pos, mount_pos)}" if mount_pos and mount_pos in visible_cells else ""
        treasure_hint = f" | 宝材方向:{self.direction_hint(self.pos, treasure_pos)}" if treasure_pos and treasure_pos in visible_cells else ""
        info = (
            f"{self.maze['name']} | 坐标 ({x}, {y}) | {status} | "
            f"可通行: W({ok(can['w'])}) S({ok(can['s'])}) A({ok(can['a'])}) D({ok(can['d'])}) | "
            f"月{month} 寿命{age}/{life}"
        )
        self.info.set(info + boss_hint + mount_hint + treasure_hint + self.goal_text() + self.quest_summary_text())
        cell = 24
        self.canvas.coords(
            self.player_marker,
            x * cell + 4,
            y * cell + 4,
            x * cell + cell - 4,
            y * cell + cell - 4,
        )
        self.draw_minimap()
        self.update_exp_ui()

    def update_exp_ui(self):
        if not getattr(self, "exp_bar", None):
            return
        cur = self.player.get("exp", 0)
        need = max(1, self.player.get("exp_next", 1))
        self.exp_bar["maximum"] = need
        self.exp_bar["value"] = min(cur, need)
        self.exp_var.set(f"经验: {cur}/{need}")

    def find_boss_pos(self):
        if not self.maze or not self.maze.get("events"):
            return None
        for pos, ev in self.maze["events"].items():
            if ev.get("type") == "boss":
                return pos
        return None

    def find_event_pos(self, etype: str):
        if not self.maze or not self.maze.get("events"):
            return None
        for pos, ev in self.maze["events"].items():
            if ev.get("type") == etype:
                return pos
        return None

    def minimap_visible_cells(self, center=None):
        if not self.maze:
            return set()
        if center is None:
            center = self.pos
        span = max(1, int(getattr(self, "minimap_visible_span", 4)))
        half_left = (span - 1) // 2
        half_right = span // 2
        cx, cy = center
        visible = set()
        for x in range(cx - half_left, cx + half_right + 1):
            for y in range(cy - half_left, cy + half_right + 1):
                if 0 <= x < self.maze["w"] and 0 <= y < self.maze["h"]:
                    visible.add((x, y))
        return visible

    def draw_minimap(self):
        if not self.maze or not getattr(self, "minimap", None):
            return
        w, h = self.maze["w"], self.maze["h"]
        if w <= 0 or h <= 0:
            return
        canvas_w = int(self.minimap["width"])
        canvas_h = int(self.minimap["height"])
        size = min(canvas_w, canvas_h) - 6
        cell = max(2, min(6, size // max(w, h)))
        map_w = cell * w
        map_h = cell * h
        ox = (canvas_w - map_w) // 2
        oy = (canvas_h - map_h) // 2

        self.minimap.delete("all")
        visible = self.minimap_visible_cells(self.pos)
        for vx, vy in visible:
            x1 = ox + vx * cell
            y1 = oy + vy * cell
            self.minimap.create_rectangle(x1, y1, x1 + cell, y1 + cell, fill="#252b35", outline="")
        self.minimap.create_rectangle(ox, oy, ox + map_w, oy + map_h, outline="#2a2d34")
        # blocks
        for bx, by in self.maze.get("blocks", []):
            if (bx, by) not in visible:
                continue
            x1 = ox + bx * cell
            y1 = oy + by * cell
            self.minimap.create_rectangle(x1, y1, x1 + cell, y1 + cell, fill="#333", outline="")
        # exit
        ex, ey = self.maze["exit"]
        if (ex, ey) in visible:
            ex1 = ox + ex * cell
            ey1 = oy + ey * cell
            self.minimap.create_rectangle(ex1, ey1, ex1 + cell, ey1 + cell, fill="#ffd54f", outline="")
        # boss
        boss_pos = self.find_boss_pos()
        if boss_pos and boss_pos in visible:
            bx, by = boss_pos
            bx1 = ox + bx * cell
            by1 = oy + by * cell
            self.minimap.create_rectangle(bx1, by1, bx1 + cell, by1 + cell, fill="#ff5252", outline="")
        # mount/treasure
        mount_pos = self.find_event_pos("mount")
        if mount_pos and mount_pos in visible:
            mx, my = mount_pos
            mx1 = ox + mx * cell
            my1 = oy + my * cell
            self.minimap.create_rectangle(mx1, my1, mx1 + cell, my1 + cell, fill="#00e5ff", outline="")
        treasure_pos = self.find_event_pos("treasure")
        if treasure_pos and treasure_pos in visible:
            tx, ty = treasure_pos
            tx1 = ox + tx * cell
            ty1 = oy + ty * cell
            self.minimap.create_rectangle(tx1, ty1, tx1 + cell, ty1 + cell, fill="#ff9800", outline="")
        # player
        px, py = self.pos
        px1 = ox + px * cell
        py1 = oy + py * cell
        self.minimap.create_oval(px1 + 1, py1 + 1, px1 + cell - 1, py1 + cell - 1, fill="#00ff88", outline="")

    def can_walk(self, x, y):
        if x < 0 or y < 0 or x >= self.maze["w"] or y >= self.maze["h"]:
            return False
        return (x, y) not in self.maze["blocks"]

    def on_move(self, key):
        if not self.alive:
            self.log("你已陨落，请点击“新生”重新开始。", "system")
            return
        if key not in MOVE:
            return
        dx, dy = MOVE[key]
        nx, ny = self.pos[0] + dx, self.pos[1] + dy
        if not self.can_walk(nx, ny):
            self.log("前方受阻，无法通行")
            return
        self.pos = (nx, ny)
        self.describe()
        self.check_event()
        self.advance_time(1)
        # NPC patrol increases encounter chance temporarily
        if self.player.get("npc_buffs", {}).get("patrol_alert", 0) > 0:
            self.player["npc_buffs"]["patrol_alert"] -= 1
            if random.random() < 0.18:
                self.maybe_encounter()
        else:
            self.maybe_encounter()
        self.life_stats["steps"] = self.life_stats.get("steps", 0) + 1
        self.save_game()

    def check_event(self):
        pos = self.pos
        events = self.maze["events"]
        if pos in events:
            ev = events.pop(pos)
            etype = ev.get("type")
            if etype == "loot":
                self.log("你找到宝箱，获得随机掉落。")
                self.reward_loot("chest")
            elif etype == "heal":
                self.player["hp"] = self.player["max_hp"]
                self.log("休整完毕，生命全满。")
            elif etype == "battle":
                self.log("遭遇精英守卫！")
                pool = self.enemy_pool.get("elite", ENEMY_POOL["elite"])
                picked = dict(random.choice(pool))
                enemy = picked if self.enemy_pool_generated else scale_enemy(picked, self.current_chapter.get("scale", 1.0))
                self.battle(enemy, is_boss=False)
            elif etype == "boss":
                self.log("首领出现！")
                picked = dict(self.enemy_pool.get("boss", ENEMY_POOL["boss"][0]))
                enemy = picked if self.enemy_pool_generated else scale_enemy(picked, self.current_chapter.get("scale", 1.0))
                self.battle(enemy, is_boss=True)
            elif etype == "treasure":
                item = ev.get("item")
                if item:
                    self.collect_treasure(item)
            elif etype == "mount":
                item = ev.get("item")
                if item:
                    self.collect_mount(item)
            elif etype == "story_event":
                ev_data = ev.get("event", {})
                title = ev_data.get("title", "剧情事件")
                text = ev_data.get("text", "")
                reward = ev_data.get("reward", {})
                if text:
                    messagebox.showinfo(title, text)
                    self.log(f"剧情事件：{title} - {text}", "system")
                if reward:
                    gold, exp, items = self.apply_quest_reward(reward)
                    extra = f" 物品:{'、'.join(items)}" if items else ""
                    self.log(f"事件奖励：金币{gold} 经验{exp}{extra}", "system")
            elif etype == "break_item":
                item = ev.get("item")
                if item:
                    self.player["bag"][item] = self.player["bag"].get(item, 0) + 1
                    self.log(f"发现天材地宝：{item}", "system")
            elif etype == "break_recipe":
                item = ev.get("item")
                if item:
                    self.player["bag"][item] = self.player["bag"].get(item, 0) + 1
                    self.learn_recipe(item)
            elif etype == "faction_event":
                fid = ev.get("faction")
                fname = next((f["name"] for f in NATION_FACTIONS if f["id"] == fid), fid)
                if ev.get("ambush"):
                    msg = f"阵营伏击：{fname}埋伏在此！"
                    self.log(msg, "system")
                    pool = self.enemy_pool.get("elite", ENEMY_POOL["elite"])
                    picked = dict(random.choice(pool))
                    picked["faction"] = fid
                    picked["name"] = f"{picked['name']}·伏击"
                    self.battle(picked, is_boss=False, is_elite=True)
                    return
                msg = f"阵营事件：{fname}使者出现，给予修行指引。"
                self.log(msg, "system")
                if fid == "human":
                    self.player["gold"] += 10
                    self.log("人族援助，金币 +10", "system")
                elif fid == "yao":
                    self.player["spd"] += 1
                    self.log("妖族契约，速度 +1", "system")
                elif fid == "mo":
                    self.player["atk"] += 1
                    self.log("魔族试炼，攻击 +1", "system")
                elif fid == "xian":
                    self.player["res"] += 1
                    self.log("仙族赐福，抗性 +1", "system")
            elif etype == "npc":
                npc = ev.get("npc", {})
                title = npc.get("title", "遗世之人")
                name = npc.get("name", "无名者")
                story = npc.get("story", "")
                bio = npc.get("bio", "")
                skills = npc.get("skills", [])
                item = npc.get("item")
                dialogue = npc.get("dialogue", "")
                self.ensure_npc_state(npc)
                if npc.get("hostile"):
                    self.hostile_npc_attack(npc)
                    return
                self.log(f"你遇见了 {name}·{title}")
                npc_elem = npc.get("main_element")
                if npc_elem:
                    self.log(f"{name} 的本源亲和：{npc_elem}", f"elem_{npc_elem}")
                if story:
                    self.log(story)
                if bio:
                    self.log(f"自传：{bio}")
                if skills:
                    self.log(f"{name} 的擅长：{ '、'.join(skills) }")
                if item:
                    self.log(f"{name} 的专属物品：{item}")
                self.log(f"线索：{self.npc_tactical_hint()}")
                if dialogue:
                    self.log(f"{name}: {dialogue}")
                player_elem = self.player_main_element()
                if npc_elem and player_elem:
                    if npc_elem == player_elem:
                        self.player["insight"][player_elem] = self.player["insight"].get(player_elem, 0) + 1
                        self.log(f"同源共鸣，{player_elem}悟性 +1", f"elem_{player_elem}")
                    elif ELEMENT_COUNTERS.get(player_elem) == npc_elem:
                        self.player["gold"] += 5
                        self.log("克制相生，获得金币 +5")
                    elif ELEMENT_COUNTERS.get(npc_elem) == player_elem:
                        self.player["res"] += 1
                        self.log("受其指点，抗性 +1")
                npc["title"] = title
                if story:
                    npc.setdefault("background", story)
                if dialogue:
                    npc.setdefault("dialogue_history", []).append({"player": "", "npc": dialogue})
                self.show_npc_dialog(npc, title="遗世旅者")
                self.update_quests("talk", 1)
                self.add_special_item(npc)
            elif etype == "faction_npc":
                fid = ev.get("faction")
                npc_name = ev.get("name", "使者")
                pf = self.player.get("faction")
                relation = self.faction_relation(pf, fid)
                fname = next((f["name"] for f in NATION_FACTIONS if f["id"] == fid), fid)
                self.ensure_npc_state(ev)
                if ev.get("hostile"):
                    self.hostile_npc_attack(ev)
                    return
                if not ev.get("dialogue_history"):
                    reply, update, _debug = self.npc_generate_reply(ev, "你好")
                    self.apply_npc_update(ev, update)
                    if reply:
                        ev.setdefault("dialogue_history", []).append({"player": "你好", "npc": reply})
                        self.log(f"{npc_name}: {reply}")
                if relation == 1:
                    self.log(f"{npc_name}（{fname}）向你致意。", "system")
                    roll = random.random()
                    if roll < 0.4:
                        self.player["gold"] += 8
                        self.player["insight"][self.player_main_element()] = self.player["insight"].get(self.player_main_element(), 0) + 1
                        self.log("盟友赠礼：金币+8，悟性+1", "system")
                    elif roll < 0.7:
                        self.player["npc_buffs"]["ally_follow"] = 5
                        self.log("盟友随行：接下来5场战斗伤害略增。", "system")
                    else:
                        self.player["npc_buffs"]["patrol_alert"] = 4
                        self.log("盟友驻扎：巡逻加强，遭遇战概率提高。", "system")
                elif relation == -1:
                    if random.random() < 0.6:
                        self.log(f"{npc_name}（{fname}）敌意显现，发动伏击！", "system")
                        pool = self.enemy_pool.get("elite", ENEMY_POOL["elite"])
                        picked = dict(random.choice(pool))
                        picked["faction"] = fid
                        picked["name"] = f"{picked['name']}·伏击"
                        self.battle(picked, is_boss=False, is_elite=True)
                    else:
                        self.log(f"{npc_name}（{fname}）在附近巡逻。", "system")
                        self.player["npc_buffs"]["patrol_alert"] = 4
                else:
                    self.log(f"{npc_name}（{fname}）与你保持距离。", "system")
                    if random.random() < 0.6:
                        self.show_neutral_shop()
                self.show_npc_dialog(ev, title=f"{npc_name}·{fname}")
                self.update_quests("talk", 1)
                self.add_special_item(ev)
        if pos == self.maze["exit"]:
            self.log("你到达出口。")
            if self.run_mode == "chapter":
                if not self.goal_completed():
                    messagebox.showinfo("提示", "章节目标未完成，无法通关。")
                    return
                self.play_dialogue("ch1_outro")
                self.advance_chapter()
            else:
                self.log("秘境已通关，返回章节。")
                # ?红???
                self.run_mode = "chapter"
                self.load_chapter(self.chapter_idx)

    def spawn_special_events(self, count=2):
        free_cells = [
            (x, y)
            for x in range(self.maze["w"])
            for y in range(self.maze["h"])
            if self.can_walk(x, y)
            and (x, y) != self.maze["start"]
            and (x, y) != self.maze["exit"]
            and (x, y) not in self.maze["events"]
        ]
        random.shuffle(free_cells)
        picks = free_cells[:count]
        for pos in picks:
            if random.random() < 0.5:
                item = self.pick_from_catalog(self.treasure_catalog)
                if item:
                    self.maze["events"][pos] = {"type": "treasure", "pos": pos, "item": item}
            else:
                item = self.pick_from_catalog(self.mount_catalog)
                if item:
                    self.maze["events"][pos] = {"type": "mount", "pos": pos, "item": item}
        # breakthrough material spawn
        extra_cells = [
            (x, y)
            for x in range(self.maze["w"])
            for y in range(self.maze["h"])
            if self.can_walk(x, y)
            and (x, y) != self.maze["start"]
            and (x, y) != self.maze["exit"]
            and (x, y) not in self.maze["events"]
        ]
        if extra_cells and random.random() < 0.4:
            pos = random.choice(extra_cells)
            realm_idx = min(self.player.get("realm_idx", 0), len(BREAKTHROUGH_REALMS) - 1)
            if self.current_chapter:
                realm_idx = min(self.current_chapter.get("idx", self.chapter_idx), len(BREAKTHROUGH_REALMS) - 1)
            low = max(0, realm_idx - random.randint(0, 2))
            item_id = self.pick_breakthrough_item(low)
            self.maze["events"][pos] = {"type": "break_item", "pos": pos, "item": item_id}
        if extra_cells and random.random() < 0.2:
            pos = random.choice(extra_cells)
            realm_idx = min(self.player.get("realm_idx", 0), len(BREAKTHROUGH_REALMS) - 1)
            if self.current_chapter:
                realm_idx = min(self.current_chapter.get("idx", self.chapter_idx), len(BREAKTHROUGH_REALMS) - 1)
            low = max(0, realm_idx - random.randint(0, 1))
            realm_name = BREAKTHROUGH_REALMS[low]
            recipe_item = self.recipe_unlock_item(realm_name)
            self.maze["events"][pos] = {"type": "break_recipe", "pos": pos, "item": recipe_item}
        # chapter faction event
        if self.current_chapter and self.current_chapter.get("faction"):
            free_cells = [
                (x, y)
                for x in range(self.maze["w"])
                for y in range(self.maze["h"])
                if self.can_walk(x, y)
                and (x, y) != self.maze["start"]
                and (x, y) != self.maze["exit"]
                and (x, y) not in self.maze["events"]
            ]
            if free_cells:
                pos = random.choice(free_cells)
                ambush = random.random() < 0.25
                self.maze["events"][pos] = {
                    "type": "faction_event",
                    "pos": pos,
                    "faction": self.current_chapter.get("faction"),
                    "ambush": ambush,
                }

    def spawn_story_npcs(self):
        if not self.current_chapter or not self.maze:
            return
        story = STORY_CHAPTERS.get(self.current_chapter.get("id"), {})
        npc_ids = story.get("npcs", [])
        if not npc_ids:
            return
        free_cells = [
            (x, y)
            for x in range(self.maze["w"])
            for y in range(self.maze["h"])
            if self.can_walk(x, y)
            and (x, y) != self.maze["start"]
            and (x, y) != self.maze["exit"]
            and (x, y) not in self.maze["events"]
        ]
        random.shuffle(free_cells)
        for npc_id, pos in zip(npc_ids, free_cells):
            npc = STORY_NPC_BY_ID.get(npc_id)
            if not npc:
                continue
            self.maze["events"][pos] = {"type": "npc", "pos": pos, "npc": dict(npc)}

    def spawn_story_events(self):
        if not self.current_chapter or not self.maze:
            return
        story = STORY_CHAPTERS.get(self.current_chapter.get("id"), {})
        events = story.get("events", [])
        if not events:
            return
        free_cells = [
            (x, y)
            for x in range(self.maze["w"])
            for y in range(self.maze["h"])
            if self.can_walk(x, y)
            and (x, y) != self.maze["start"]
            and (x, y) != self.maze["exit"]
            and (x, y) not in self.maze["events"]
        ]
        random.shuffle(free_cells)
        for ev, pos in zip(events, free_cells):
            self.maze["events"][pos] = {"type": "story_event", "pos": pos, "event": ev}

    def pick_from_catalog(self, catalog):
        if not catalog:
            return None
        weights = []
        for r in catalog:
            if any(r2 == r["rarity"] for r2, _ in TREASURE_TIER_WEIGHTS):
                w = next((w for r2, w in TREASURE_TIER_WEIGHTS if r2 == r["rarity"]), 1)
            else:
                w = next((w for r2, w in RARITY_WEIGHTS if r2 == r["rarity"]), 1)
            weights.append((r["rarity"], w))
        rarity = weighted_choice(weights)
        candidates = [r for r in catalog if r["rarity"] == rarity]
        tier = random.choice(candidates) if candidates else None
        if not tier:
            return None
        items = tier.get("items") or tier.get("mounts")
        if not items:
            return None
        return random.choice(items)

    # ---------- encounters ----------
    def maybe_encounter(self):
        roll = random.random()
        if roll < 0.15:
            pool = self.enemy_pool.get("normal", ENEMY_POOL["normal"])
            picked = dict(random.choice(pool))
            enemy = picked if self.enemy_pool_generated else scale_enemy(picked, self.current_chapter.get("scale", 1.0))
            self.log(f"遭遇小怪：{enemy['name']}")
            self.battle(enemy, is_boss=False)
        elif roll < 0.23:
            pool = self.enemy_pool.get("elite", ENEMY_POOL["elite"])
            picked = dict(random.choice(pool))
            enemy = picked if self.enemy_pool_generated else scale_enemy(picked, self.current_chapter.get("scale", 1.0))
            if self.current_chapter and self.current_chapter.get("faction"):
                enemy["faction"] = self.current_chapter.get("faction")
                enemy["name"] = f"{enemy['name']}·阵营精英"
                enemy = scale_enemy(enemy, 1.1)
            self.log(f"遭遇精英：{enemy['name']}")
            self.battle(enemy, is_boss=False, is_elite=True)
    def battle(self, enemy, is_boss=False, is_elite=False):
        skill_idx = 0
        enemy = self.ensure_enemy_affinity(enemy)
        enemy = self.ensure_enemy_faction(enemy)
        self.current_enemy = enemy
        player_status = self.init_status()
        enemy_status = self.init_status()
        boss_stage = 1
        if self.player.get("battle_strategy"):
            self.battle_strategy_var.set(self.player.get("battle_strategy"))
        player_element = self.player_main_element()
        elem_adv = self.element_advantage(player_element, enemy.get("affinity", {}))
        enemy_adv = self.element_advantage(enemy.get("main_element"), self.player.get("affinity", {}))
        for sk in self.player.get("skills", []):
            sk["cd_left"] = 0
        injury = self.get_injury_penalty()
        pf = self.player.get("faction")
        ef = enemy.get("faction")
        relation = self.faction_relation(pf, ef)
        faction_mult = 1.0
        if relation == 1:
            faction_mult = 1.05
        elif relation == -1:
            faction_mult = 0.92
        if player_element:
            self.log(f"你的主元素：{player_element}", f"elem_{player_element}")
        if enemy.get("main_element"):
            self.log(f"{enemy['name']} 主元素：{enemy.get('main_element')}", f"elem_{enemy.get('main_element')}")
        if ef:
            ef_name = next((f["name"] for f in NATION_FACTIONS if f["id"] == ef), ef)
            self.log(f"{enemy['name']} 阵营：{ef_name}")
        if relation == 1:
            self.log("阵营同盟：战斗更顺利", "system")
        elif relation == -1:
            self.log("阵营敌对：战斗更艰难", "system")
        if elem_adv > 1.0:
            self.log("元素克制优势：你的伤害提升、掉落提升", "system")
        elif elem_adv < 1.0:
            self.log("元素克制劣势：你的伤害降低、掉落降低", "system")
        self.log(f"当前战斗策略：{self.player.get('battle_strategy','均衡')}", "system")
        if is_boss:
            skills = enemy.get("skills") or []
            if skills:
                skill_names = "、".join([s.get("name", "技能") for s in skills])
                self.log(f"首领技能预告：{skill_names}", "system")
        while enemy["hp"] > 0 and self.player["hp"] > 0:
            if is_boss and enemy.get("max_hp"):
                hp_ratio = enemy["hp"] / max(1, enemy.get("max_hp", enemy["hp"]))
                if boss_stage == 1 and hp_ratio <= 0.6:
                    boss_stage = 2
                    self.log(f"{enemy['name']} 进入第二阶段，攻击提升！", "system")
                    enemy["atk"] = int(enemy["atk"] * 1.15)
                elif boss_stage == 2 and hp_ratio <= 0.3:
                    boss_stage = 3
                    self.log(f"{enemy['name']} 进入第三阶段，速度提升！", "system")
                    enemy["spd"] = int(enemy.get("spd", 8) * 1.2)
            self.tick_status_start(player_status, "你", True)
            self.tick_status_start(enemy_status, enemy["name"], False)
            if self.player["hp"] <= 0 or enemy["hp"] <= 0:
                break
            self.log_battle_status(enemy, player_status, enemy_status)
            p_spd = max(1, self.player["spd"] - injury.get("spd", 0))
            e_spd = enemy.get("spd", 8)
            p_actions = self.compute_action_count(p_spd, e_spd)
            e_actions = self.compute_action_count(e_spd, p_spd)
            if p_actions > 1:
                self.log("你速度占优，可连动两次。", "system")
            if e_actions > 1:
                self.log(f"{enemy['name']} 速度占优，可能连动两次。", "system")

            for _ in range(p_actions):
                if enemy["hp"] <= 0 or self.player["hp"] <= 0:
                    break
                if player_status.get("stun", 0) > 0:
                    player_status["stun"] -= 1
                    self.log("你被眩晕，无法行动。", "eff_stun")
                    continue
                self.tick_cooldowns()
                skill_used = False
                action = ""
                if self.manual_battle:
                    action = self.wait_for_action()
                if action.startswith("技能: "):
                    sk_name = action.replace("技能: ", "").strip()
                    sk = next((s for s in self.player.get("skills", []) if s.get("name") == sk_name), None)
                    if sk and sk.get("cd_left", 0) <= 0:
                        base_atk = max(1, self.player["atk"] - injury.get("atk", 0))
                        base = int(base_atk * sk.get("power", 1.2))
                        base = int(base * self.attack_multiplier_from_status(player_status) * elem_adv * faction_mult)
                        dmg, reduced, reduced_by = self.compute_damage(max(1, base - enemy["def"] // 2), enemy_status)
                        if self.roll_crit(self.player.get("crit", 0)):
                            dmg = int(dmg * 1.5)
                            self.log("暴击！", "system")
                        enemy["hp"] -= dmg
                        self.log(f"你施放 {sk['name']}，造成 {dmg} 伤害 (剩余 {max(enemy['hp'],0)})", "skill")
                        if reduced:
                            self.log(f"{enemy['name']} 护盾减伤 -{reduced_by}", "eff_shield")
                        elem_tag = f"elem_{sk.get('element')}"
                        if sk.get("element") in ELEMENT_COLORS:
                            self.log(f"元素共鸣：{sk.get('element')}", elem_tag)
                        effect = sk.get("effect")
                        if effect:
                            chance = sk.get("chance", 0.3)
                            if random.random() <= chance:
                                potency = max(2, int(self.player["atk"] * 0.2))
                                self.apply_status(enemy_status, effect, potency)
                                self.log(f"{enemy['name']} 受到 {effect} 影响（命中率 {int(chance*100)}%）", f"eff_{effect}")
                            else:
                                self.log(f"{enemy['name']} 抵抗了 {effect}（命中率 {int(chance*100)}%）", "system")
                        sk["cd_left"] = sk.get("cooldown", 3)
                        sk["mastery"] = sk.get("mastery", 0) + 1
                        rank = sk.get("rank", 1)
                        need = 5 * rank
                        if sk["mastery"] >= need and rank < 5:
                            sk["mastery"] = 0
                            sk["rank"] = rank + 1
                            sk["power"] = round(sk.get("power", 1.2) + 0.1, 2)
                            sk["chance"] = min(0.9, round(sk.get("chance", 0.3) + 0.02, 2))
                            sk["cooldown"] = max(1, sk.get("cooldown", 3) - 1)
                            self.log(f"{sk['name']} 熟练度提升，升至 {sk['rank']} 阶", "skill")
                        skill_used = True
                    else:
                        self.log("技能冷却中，改为普攻。", "system")
                elif action == "等待":
                    self.apply_status(player_status, "shield", 1)
                    self.player["hp"] = min(self.player["max_hp"], self.player["hp"] + 2)
                    self.log("你选择等待一回合，获得护盾并回复少量生命。", "system")
                    skill_used = True
                else:
                    if not self.manual_battle:
                        auto_action, auto_skill = self.choose_auto_action(
                            enemy, player_status, enemy_status, elem_adv, faction_mult, injury
                        )
                        if auto_action == "等待":
                            self.apply_status(player_status, "shield", 1)
                            self.player["hp"] = min(self.player["max_hp"], self.player["hp"] + 2)
                            self.log("你选择等待一回合，获得护盾并回复少量生命。", "system")
                            skill_used = True
                        elif auto_action == "技能" and auto_skill:
                            sk = auto_skill
                            base_atk = max(1, self.player["atk"] - injury.get("atk", 0))
                            base = int(base_atk * sk.get("power", 1.2))
                            base = int(base * self.attack_multiplier_from_status(player_status) * elem_adv * faction_mult)
                            dmg, reduced, reduced_by = self.compute_damage(max(1, base - enemy["def"] // 2), enemy_status)
                            enemy["hp"] -= dmg
                            self.log(f"你施放 {sk['name']}，造成 {dmg} 伤害 (剩余 {max(enemy['hp'],0)})", "skill")
                            if reduced:
                                self.log(f"{enemy['name']} 护盾减伤 -{reduced_by}", "eff_shield")
                            elem_tag = f"elem_{sk.get('element')}"
                            if sk.get("element") in ELEMENT_COLORS:
                                self.log(f"元素共鸣：{sk.get('element')}", elem_tag)
                            effect = sk.get("effect")
                            if effect:
                                chance = sk.get("chance", 0.3)
                                if random.random() <= chance:
                                    potency = max(2, int(self.player["atk"] * 0.2))
                                    self.apply_status(enemy_status, effect, potency)
                                    self.log(f"{enemy['name']} 受到 {effect} 影响（命中率 {int(chance*100)}%）", f"eff_{effect}")
                                else:
                                    self.log(f"{enemy['name']} 抵抗了 {effect}（命中率 {int(chance*100)}%）", "system")
                            sk["cd_left"] = sk.get("cooldown", 3)
                            sk["mastery"] = sk.get("mastery", 0) + 1
                            rank = sk.get("rank", 1)
                            need = 5 * rank
                            if sk["mastery"] >= need and rank < 5:
                                sk["mastery"] = 0
                                sk["rank"] = rank + 1
                                sk["power"] = round(sk.get("power", 1.2) + 0.1, 2)
                                sk["chance"] = min(0.9, round(sk.get("chance", 0.3) + 0.02, 2))
                                sk["cooldown"] = max(1, sk.get("cooldown", 3) - 1)
                                self.log(f"{sk['name']} 熟练度提升，升至 {sk['rank']} 阶", "skill")
                            skill_used = True
                    if not skill_used:
                        base_atk = max(1, self.player["atk"] - injury.get("atk", 0))
                        base = max(1, base_atk - enemy["def"] // 2)
                        base = int(base * self.attack_multiplier_from_status(player_status) * elem_adv * faction_mult)
                        if self.player.get("npc_buffs", {}).get("ally_follow", 0) > 0:
                            base = int(base * 1.08)
                        dmg, reduced, reduced_by = self.compute_damage(base, enemy_status)
                        if self.roll_crit(self.player.get("crit", 0)):
                            dmg = int(dmg * 1.5)
                            self.log("暴击！", "system")
                        enemy["hp"] -= dmg
                        self.log(f"你对 {enemy['name']} 造成 {dmg} 伤害 (剩余 {max(enemy['hp'],0)})")
                        if reduced:
                            self.log(f"{enemy['name']} 护盾减伤 -{reduced_by}", "eff_shield")

            for _ in range(e_actions):
                if enemy["hp"] <= 0 or self.player["hp"] <= 0:
                    break
                if enemy_status.get("stun", 0) > 0:
                    enemy_status["stun"] -= 1
                    self.log(f"{enemy['name']} 被眩晕，无法行动。", "eff_stun")
                    continue
                if is_boss and enemy.get("skills"):
                    skill = enemy["skills"][skill_idx % len(enemy["skills"])]
                    skill_idx += 1
                    base_def = max(1, self.player["def"] - injury.get("def", 0))
                    base = max(0, int(enemy["atk"] * skill["ratio"]) - base_def // 2) if skill["ratio"] > 0 else 0
                    base = int(base * self.attack_multiplier_from_status(enemy_status) * enemy_adv)
                    edmg, reduced, reduced_by = self.compute_damage(base, player_status)
                    if self.roll_crit(enemy.get("crit", 0)):
                        edmg = int(edmg * 1.5)
                        self.log("敌方暴击！", "system")
                    self.player["hp"] -= edmg
                    self.log(f"{enemy['name']} 施放 {skill['name']}，对你造成 {edmg} 伤害")
                    if skill.get("effect"):
                        chance = skill.get("chance", 0.25)
                        if random.random() <= chance:
                            potency = max(2, int(enemy["atk"] * 0.15))
                            self.apply_status(player_status, skill["effect"], potency)
                            self.log(f"你受到 {skill['effect']} 影响（命中率 {int(chance*100)}%）", f"eff_{skill['effect']}")
                        else:
                            self.log(f"你抵抗了 {skill['effect']}（命中率 {int(chance*100)}%）", "system")
                    if reduced:
                        self.log(f"护盾减伤 -{reduced_by}", "eff_shield")
                else:
                    base_def = max(1, self.player["def"] - injury.get("def", 0))
                    base = max(1, enemy["atk"] - base_def // 2)
                    base = int(base * self.attack_multiplier_from_status(enemy_status) * enemy_adv)
                    edmg, reduced, reduced_by = self.compute_damage(base, player_status)
                    if self.roll_crit(enemy.get("crit", 0)):
                        edmg = int(edmg * 1.5)
                        self.log("敌方暴击！", "system")
                    self.player["hp"] -= edmg
                    if reduced:
                        self.log(f"护盾减伤 -{reduced_by}", "eff_shield")
                self.log(f"{enemy['name']} 对你造成 {edmg} 伤害 (剩余 {max(self.player['hp'],0)})")
            self.decay_injury()
            if self.player.get("npc_buffs", {}).get("ally_follow", 0) > 0:
                self.player["npc_buffs"]["ally_follow"] -= 1
            if not self.manual_battle and self.root.winfo_exists():
                self.root.update_idletasks()
                self.root.update()
                time.sleep(0.05)
        if self.player["hp"] <= 0:
            npc, life_record = self.record_death(enemy.get("name", "未知敌人"))
            self.delete_save()
            self.alive = False
            self.log(f"战斗失败：你被击败。遗世旅者已诞生：{npc.get('name','未知')}·{npc.get('title','')}", "system")
            self.log(self.build_death_autobiography(life_record), "system")
            self.log(self.build_death_route_advice(life_record), "system")
            self.log("点击“新生”开始新的旅程。", "system")
            self.btn_restart.config(state="normal")
            return
        # Reputation and faction effects
        if pf and ef:
            if relation == -1:
                self.player["reputation"][pf] = self.player["reputation"].get(pf, 0) + 2
                self.player["reputation"][ef] = self.player["reputation"].get(ef, 0) - 2
                self.log("击败敌对阵营，声望提升。", "system")
            elif relation == 1:
                self.player["reputation"][pf] = self.player["reputation"].get(pf, 0) - 1
                self.log("误伤同盟，声望下降。", "system")
        if self.faction_task and ef == self.faction_task.get("target"):
            self.faction_task["progress"] += 1
            if self.faction_task["progress"] >= self.faction_task["need"]:
                self.player["gold"] += self.faction_task["reward_gold"]
                if pf:
                    self.player["reputation"][pf] = self.player["reputation"].get(pf, 0) + self.faction_task["reward_rep"]
                self.log("阵营任务完成，获得奖励。", "system")
                self.player["faction_task_tier"] = min(self.player.get("faction_task_tier", 1) + 1, 5)
                self.faction_task = None
        self.life_stats["battles"] = self.life_stats.get("battles", 0) + 1
        self.chapter_progress["battles"] = self.chapter_progress.get("battles", 0) + 1
        self.update_quests("battles", 1)
        if is_elite:
            self.life_stats["elites"] = self.life_stats.get("elites", 0) + 1
            self.chapter_progress["elites"] = self.chapter_progress.get("elites", 0) + 1
            self.update_quests("elites", 1)
        if is_boss:
            self.life_stats["bosses"] = self.life_stats.get("bosses", 0) + 1
            self.chapter_progress["boss"] = self.chapter_progress.get("boss", 0) + 1
            self.update_quests("boss", 1)
        self.log(f"击败 {enemy['name']}，获得经验 {enemy['exp']}")
        level_before = self.player.get("lvl", 1)
        self.add_exp(enemy["exp"])
        source = "battle"
        if is_boss:
            source = "boss"
        elif is_elite:
            source = "battle_elite"
        rarity_boost = 10 if is_boss or enemy.get("rarity") == "红" else 1
        drop_mult = 1.1 if elem_adv > 1.0 else (0.9 if elem_adv < 1.0 else 1.0)
        if relation == -1:
            drop_mult *= 1.08
        elif relation == 1:
            drop_mult *= 0.95
        loot_summary = self.reward_loot(source, rarity_boost=rarity_boost, extra_mult=drop_mult)
        if is_boss and self.current_chapter and self.current_chapter.get("faction"):
            fid = self.current_chapter.get("faction")
            elem_map = {"human": "金", "yao": "木", "mo": "火", "xian": "水"}
            elem = elem_map.get(fid, self.player_main_element())
            tier = random.choice(["玄", "地"]) if is_boss else "黄"
            pill_id = f"insight_pill_{elem}_{tier}"
            self.player["bag"][pill_id] = self.player["bag"].get(pill_id, 0) + 1
            self.log(f"阵营Boss掉落：{display_name(pill_id)}")
            relic = FACTION_RELICS.get(fid)
            if relic:
                relic_item = dict(relic)
                relic_item["rarity_color"] = relic_item.get("rarity", "紫")
                self.add_or_upgrade_relic(relic_item)
                self.log(f"获得阵营收藏品：{relic_item['name']}")
        self.degrade_equipment()
        self.describe()
        self.show_battle_result(enemy["name"], enemy["exp"], loot_summary, level_before)
        self.battle_player_var.set("你: -")
        self.battle_enemy_var.set("敌: -")
        self.battle_player_status_var.set("状态: -")
        self.battle_enemy_status_var.set("状态: -")
        self.battle_skill_box.delete(0, "end")
        self.battle_action_box.delete(0, "end")
        for w in self.battle_skill_btn_frame.winfo_children():
            w.destroy()

    # ---------- rewards / growth ----------
    def add_exp(self, amount):
        self.player["exp"] += amount
        while self.player["exp"] >= self.player["exp_next"]:
            stage = self.current_realm()
            if self.player["lvl"] >= stage["lvl_cap"]:
                self.player["exp"] = min(self.player["exp"], self.player["exp_next"] - 1)
                self.log(f"境界受限（{stage['name']}），请突破后继续升级。", "system")
                break
            self.player["exp"] -= self.player["exp_next"]
            self.player["lvl"] += 1
            self.player["exp_next"] = int(self.player["exp_next"] * 1.22 + 18)
            self.player["max_hp"] += 10
            self.player["atk"] += 2
            self.player["def"] += 1
            self.player["spd"] += 1
            self.player["hp"] = self.player["max_hp"]
            self.player["free_points"] += 3
            self.log(f"等级提升至 {self.player['lvl']}！ 获得 3 自由点。")
            self.life_stats["max_level"] = max(self.life_stats.get("max_level", 1), self.player["lvl"])
        self.update_exp_ui()

    def reward_loot(self, source, rarity_boost: float = 1.0, extra_mult: float = 1.0):
        summary = {"items": [], "gold": 0, "relic": None}
        item = random.choice(LOOT_TABLE)
        self.player["bag"][item] = self.player["bag"].get(item, 0) + 1
        self.log(f"获得物品：{display_name(item)}")
        summary["items"].append(display_name(item))
        for itm, prob in LOOT_BONUS:
            if random.random() < prob:
                self.player["bag"][itm] = self.player["bag"].get(itm, 0) + 1
                self.log(f"额外掉落：{display_name(itm)}")
                summary["items"].append(display_name(itm))
        # breakthrough material & recipe drops (lower realms more common)
        base = 0.06
        if self.run_mode == "secret":
            base += 0.04
        if source == "boss":
            base += 0.08
        elif source == "battle_elite":
            base += 0.04
        if random.random() < base:
            realm_idx = min(self.player.get("realm_idx", 0), len(BREAKTHROUGH_REALMS) - 1)
            if self.current_chapter:
                realm_idx = min(self.current_chapter.get("idx", self.chapter_idx), len(BREAKTHROUGH_REALMS) - 1)
            low = max(0, realm_idx - random.randint(0, 2))
            item_id = self.pick_breakthrough_item(low)
            self.player["bag"][item_id] = self.player["bag"].get(item_id, 0) + 1
            self.log(f"获得天材地宝：{item_id}")
            summary["items"].append(item_id)
        recipe_base = 0.02
        if self.run_mode == "secret":
            recipe_base += 0.03
        if source == "boss":
            recipe_base += 0.05
        if random.random() < recipe_base:
            realm_idx = min(self.player.get("realm_idx", 0), len(BREAKTHROUGH_REALMS) - 1)
            if self.current_chapter:
                realm_idx = min(self.current_chapter.get("idx", self.chapter_idx), len(BREAKTHROUGH_REALMS) - 1)
            low = max(0, realm_idx - random.randint(0, 1))
            realm_name = BREAKTHROUGH_REALMS[low]
            recipe_item = self.recipe_unlock_item(realm_name)
            self.player["bag"][recipe_item] = self.player["bag"].get(recipe_item, 0) + 1
            self.log(f"获得丹方：{recipe_item}")
            summary["items"].append(recipe_item)
            self.learn_recipe(recipe_item)
        loot_mult = self.get_loot_multiplier()
        loot_mult *= extra_mult
        gold_gain = int(random.randint(*GOLD_DROP_RANGE) * loot_mult)
        self.player["gold"] += gold_gain
        self.life_stats["gold_earned"] = self.life_stats.get("gold_earned", 0) + gold_gain
        self.log(f"获得金币：{gold_gain}，当前金币 {self.player['gold']}")
        summary["gold"] = gold_gain
        if random.random() < 0.05:
            elem = self.player_main_element()
            pill_id = f"insight_pill_{elem}_黄"
            self.player["bag"][pill_id] = self.player["bag"].get(pill_id, 0) + 1
            self.log(f"获得 {display_name(pill_id)}")
            summary["items"].append(display_name(pill_id))
        luck_bonus = min(self.player.get("luck", 0), 10) * 0.01
        relic_chance = RELIC_DROP_CHANCE.get(source, 0) * (1 + luck_bonus) * loot_mult
        if source in RELIC_DROP_CHANCE and random.random() < relic_chance:
            relic = self.pick_relic_new(rarity_boost=rarity_boost * loot_mult)
            if relic:
                self.add_or_upgrade_relic(relic)
                summary["relic"] = relic.get("name")
        if self.player["equip"]["weapon"] is None and "basic_sword" == item:
            self.equip_gear({"id": "basic_sword", "name": "破旧短剑", "slot": "weapon", "attrs": [0, 3, 0, 0, 0, 0], "dur": 50, "max_dur": 50})
        if self.player["equip"]["armor"] is None and "basic_armor" == item:
            self.equip_gear({"id": "basic_armor", "name": "破旧皮甲", "slot": "armor", "attrs": [8, 0, 2, 0, 0, 0], "dur": 50, "max_dur": 50})
        return summary

    def pick_relic(self):
        rarity = weighted_choice(RARITY_WEIGHTS)
        if rarity == "红":
            owned_red = any(r["item"]["rarity_color"] == "红" for r in self.player["relics"].values())
            if owned_red:
                rarity = "金"
        candidates = self.relic_db.get(rarity, [])
        if not candidates:
            return None
        relic = dict(random.choice(candidates))
        relic["rarity_color"] = rarity
        return relic

    def pick_relic_new(self, rarity_boost: float = 1.0):
        """带红/金加成的收藏品抽取，红色唯一。"""
        weights = []
        for color, w in RARITY_WEIGHTS:
            if color in ("金", "红"):
                w *= rarity_boost
            weights.append((color, w))
        rarity = weighted_choice(weights)
        if rarity == "红":
            owned_red = any(r["item"].get("rarity_color") == "红" for r in self.player["relics"].values())
            if owned_red:
                rarity = "金"
        candidates = self.relic_db.get(rarity, [])
        if not candidates:
            return None
        relic = dict(random.choice(candidates))
        relic["rarity_color"] = rarity
        relic["rarity"] = rarity
        return relic

    def show_battle_result(self, enemy_name: str, exp_gain: int, loot_summary: dict, level_before: int):
        lines = [f"[战斗结算] 击败 {enemy_name} | 经验 +{exp_gain}"]
        if self.player["lvl"] > level_before:
            lines.append(f"[战斗结算] 升级！当前等级 {self.player['lvl']}")
        if loot_summary:
            items = loot_summary.get("items") or []
            if items:
                lines.append("[战斗结算] 物品：" + "、".join(items))
            gold = loot_summary.get("gold", 0)
            lines.append(f"[战斗结算] 金币：+{gold}")
            if loot_summary.get("relic"):
                lines.append(f"[战斗结算] 收藏品：{loot_summary['relic']}")
        for line in lines:
            self.log(line, "system")

    def add_or_upgrade_relic(self, relic):
        rid = relic["id"]
        entry = self.player["relics"].get(rid)
        if entry:
            entry["count"] += 1
        else:
            entry = {"item": relic, "count": 1, "star": 1, "equipped": False}
            self.player["relics"][rid] = entry
            self.life_stats["relics"] = self.life_stats.get("relics", 0) + 1
            self.chapter_progress["relics"] = self.chapter_progress.get("relics", 0) + 1
            self.update_quests("relics", 1)
        for need in UPGRADE_COSTS:
            if entry["star"] >= 5:
                break
            if entry["count"] > need:
                entry["count"] -= need
                entry["star"] += 1
                self.log(f"收藏品 {relic['name']} 升至 {entry['star']} 星")
            else:
                break
        if len(self.player["equipped_relics"]) < 2 and rid not in self.player["equipped_relics"]:
            self.player["equipped_relics"].append(rid)
            self.apply_relic_bonus(relic)
            self.log(f"装备收藏品：{relic['name']}")

    def apply_relic_bonus(self, relic):
        rarity = relic.get("rarity_color", "白")
        bonus = RELIC_BONUS.get(rarity, {})
        attrs = relic.get("属性") or relic.get("attrs") or [0, 0, 0, 0, 0, 0]
        self.player["max_hp"] += bonus.get("hp", 0) + (attrs[0] if len(attrs) > 0 else 0)
        self.player["atk"] += bonus.get("atk", 0) + (attrs[1] if len(attrs) > 1 else 0)
        self.player["def"] += bonus.get("def", 0) + (attrs[2] if len(attrs) > 2 else 0)
        self.player["spd"] += bonus.get("spd", 0) + (attrs[3] if len(attrs) > 3 else 0)
        self.player["crit"] += bonus.get("crit", 0) + (attrs[4] if len(attrs) > 4 else 0)
        self.player["res"] += bonus.get("res", 0) + (attrs[5] if len(attrs) > 5 else 0)
        self.player["luck"] += bonus.get("luck", 0)
        self.player["hp"] = min(self.player["hp"], self.player["max_hp"])

    # ---------- treasures / mounts ----------
    def collect_treasure(self, item):
        tid = item.get("id", "treasure")
        name = item.get("name", "奇物")
        rarity = item.get("rarity", "?")
        key = f"treasure_{tid}"
        self.player["bag"][key] = self.player["bag"].get(key, 0) + 1
        self.life_stats["treasures"] = self.life_stats.get("treasures", 0) + 1
        self.chapter_progress["treasures"] = self.chapter_progress.get("treasures", 0) + 1
        self.update_quests("treasures", 1)
        self.log(f"获得天材地宝：{name}（{rarity}）")

    def treasure_meta_from_bag_key(self, key: str):
        if not key.startswith("treasure_"):
            return None
        tid = key.replace("treasure_", "")
        return self.treasure_index.get(tid)

    def apply_treasure_bonus(self, item):
        element = item.get("element") or self.player_main_element()
        tier = item.get("rarity", "黄")
        scale = TREASURE_BONUS_SCALE.get(tier, 1)
        weights = ELEMENT_BONUS_WEIGHTS.get(element, {})
        for stat, base in weights.items():
            inc = base * scale
            if stat == "max_hp":
                self.player["max_hp"] += inc
                self.player["hp"] = min(self.player["hp"] + inc, self.player["max_hp"])
            else:
                self.player[stat] += inc
        if tier in ("地", "天", "神"):
            self.player["insight"][element] = self.player["insight"].get(element, 0) + 1
            self.log(f"{element}悟性 +1", f"elem_{element}")
        self.log(f"炼化 {item.get('name','灵材')}，属性提升。")

    def collect_mount(self, item):
        name = item.get("name", "坐骑")
        rank = item.get("rarity", item.get("rank", "C"))
        mid = f"m{len(self.player['mounts'])+1}"
        mount = {"id": mid, "name": name, "rank": rank, "breed_count": 0}
        self.player["mounts"].append(mount)
        self.life_stats["mounts"] = self.life_stats.get("mounts", 0) + 1
        self.chapter_progress["mounts"] = self.chapter_progress.get("mounts", 0) + 1
        self.update_quests("mounts", 1)
        self.log(f"获得坐骑：{name} Rank {rank}")

    # ---------- factions / secret dungeons ----------
    def load_factions(self, path: Path):
        try:
            data = load_json(path)
            return data.get("factions", [])
        except Exception:
            return []

    def refresh_secret_pool(self, force=False):
        today = date.today().isoformat()
        if not force and self.secret_refresh_date == today:
            return
        rng = random.Random()
        refreshed = []
        for base in SECRET_DUNGEON_POOL:
            dungeon = dict(base)
            dungeon["drop_mult"] = round(rng.uniform(1.05, 1.6), 2)
            fac = rng.choice(self.factions) if self.factions else None
            if fac:
                dungeon["faction"] = fac
                dungeon["drop_mult"] = round(dungeon["drop_mult"] * (1 + fac.get("drop_bonus", 0)), 2)
            refreshed.append(dungeon)
        refreshed.sort(key=lambda d: d.get("lvl_req", 0))
        self.secret_dungeons = refreshed
        self.secret_refresh_date = today
        self.log("秘境已刷新（每日一次），按等级需求排序。")

    def unlock_secret_content(self):
        if self.secret_unlocked:
            return
        self.secret_unlocked = True
        self.btn_secret.config(state="normal")
        self.btn_sect.config(state="normal")
        self.log("秘境探索已开放，可在章节间进入。")

    def show_secret_ui(self):
        if not self.secret_unlocked:
            messagebox.showinfo("提示", "通关第一章后解锁秘境。")
            return
        self.refresh_secret_pool()
        win = tk.Toplevel(self.root)
        win.title("秘境列表")
        tk.Label(win, text=f"当前等级 {self.player['lvl']} | 今日刷新 {self.secret_refresh_date or '-'}").grid(row=0, column=0, sticky="w")
        tk.Label(win, text=f"自创宗门：{self.sect['name'] if self.sect else '未创建'}").grid(row=0, column=1, sticky="w")
        listbox = tk.Listbox(win, height=8, width=60)
        listbox.grid(row=1, column=0, columnspan=4, sticky="nsew", padx=4, pady=4)
        for dg in self.secret_dungeons:
            fac_name = dg.get("faction", {}).get("name", "无阵营")
            listbox.insert(
                "end",
                f"{dg['name']} | 需求Lv{dg['lvl_req']} | 规模{dg['size']} | 掉落x{dg['drop_mult']} | 阵营 {fac_name}",
            )

        def enter_selected():
            sel = listbox.curselection()
            if not sel:
                return
            dungeon = self.secret_dungeons[sel[0]]
            self.start_secret_run(dungeon)
            win.destroy()

        tk.Button(win, text="进入", command=enter_selected).grid(row=2, column=0, sticky="we", padx=4, pady=4)
        tk.Button(win, text="刷新", command=lambda: [self.refresh_secret_pool(force=True), win.destroy(), self.show_secret_ui()]).grid(
            row=2, column=1, sticky="we", padx=4, pady=4
        )
        tk.Button(win, text="自创宗门", command=lambda: [win.destroy(), self.show_sect_ui()]).grid(
            row=2, column=2, sticky="we", padx=4, pady=4
        )
        tk.Button(win, text="关闭", command=win.destroy).grid(row=2, column=3, sticky="we", padx=4, pady=4)

    def start_secret_run(self, dungeon):
        if self.player["lvl"] < dungeon.get("lvl_req", 0):
            self.log(f"等级不足，需 {dungeon['lvl_req']} 级才能进入。")
            return
        self.run_mode = "secret"
        self.chapter_before_secret = self.chapter_idx
        self.enemy_pool = build_chapter_enemies(self.chapter_idx, dungeon.get("scale", 1.0))
        self.enemy_pool_generated = True
        size = dungeon.get("size", 30)
        self.maze = generate_maze(size, size, seed=random.randint(1, 999999))
        self.maze["name"] = dungeon["name"]
        self.maze["scale"] = dungeon.get("scale", 1.0)
        self.pos = self.maze["start"]
        self.player["hp"] = self.player["max_hp"]
        self.spawn_special_events(count=3)
        self.chapter_progress = {"battles": 0, "elites": 0, "boss": 0, "treasures": 0, "mounts": 0, "relics": 0}
        self.maybe_spawn_npc_event()
        self.spawn_faction_npcs(count=1)
        self.loot_multiplier = dungeon.get("drop_mult", 1.0)
        self.active_faction = dungeon.get("faction")
        fac_msg = ""
        if self.active_faction:
            fac_msg = f"，阵营 {self.active_faction.get('name','')} 提供掉落加成"
        sect_msg = ""
        if self.sect:
            sect_msg = f"，宗门 {self.sect.get('name','')} 加成"
        self.log(f"进入秘境：{dungeon['name']} (掉落x{self.loot_multiplier}){fac_msg}{sect_msg}")
        self.describe()

    def get_loot_multiplier(self):
        mult = self.loot_multiplier
        if self.active_faction:
            mult *= 1 + self.active_faction.get("drop_bonus", 0)
        if self.sect and self.run_mode == "secret":
            mult *= 1 + self.sect.get("drop_bonus", 0)
        return max(1.0, round(mult, 2))

    def show_sect_ui(self):
        win = tk.Toplevel(self.root)
        win.title("自创宗门")
        self.ensure_sect_data()
        tk.Label(win, text="宗门名称").grid(row=0, column=0, sticky="w", padx=4, pady=4)
        name_var = tk.StringVar(value=self.sect["name"] if self.sect else "")
        entry = tk.Entry(win, textvariable=name_var, width=18)
        entry.grid(row=0, column=1, padx=4, pady=4)
        tk.Label(win, text="加成类型").grid(row=1, column=0, sticky="w", padx=4, pady=4)
        bonus_var = tk.StringVar(value=self.sect.get("bonus_type") if self.sect else "drop")
        rb1 = tk.Radiobutton(win, text="掉落+8%", variable=bonus_var, value="drop")
        rb2 = tk.Radiobutton(win, text="幸运+3（影响收藏品）", variable=bonus_var, value="luck")
        rb1.grid(row=1, column=1, sticky="w")
        rb2.grid(row=2, column=1, sticky="w")

        def save_sect():
            name = name_var.get().strip() or "无名宗门"
            bonus_type = bonus_var.get()
            # 先移除旧的幸运加成，避免多次叠加
            if self.sect and self.sect.get("luck_bonus", 0):
                self.player["luck"] = max(0, self.player["luck"] - self.sect["luck_bonus"])
            sect = {
                "name": name,
                "bonus_type": bonus_type,
                "drop_bonus": 0.08 if bonus_type == "drop" else 0.0,
                "luck_bonus": 3 if bonus_type == "luck" else 0,
                "created": True,
            }
            self.sect = sect
            if sect["luck_bonus"]:
                self.player["luck"] += sect["luck_bonus"]
            self.log(f"创建/更新宗门：{name}，加成类型 {bonus_type}")
            win.destroy()

        def legacy_teach():
            if self.player.get("legacy_points", 0) <= 0:
                self.log("传承点不足。", "system")
                return
            element = self.player_main_element()
            self.player["insight"][element] = self.player["insight"].get(element, 0) + 1
            self.player["legacy_points"] -= 1
            self.log(f"宗门传功，{element}悟性 +1", f"elem_{element}")

        tabs = ttk.Notebook(win)
        tabs.grid(row=3, column=0, columnspan=2, padx=4, pady=4, sticky="nsew")
        tab_base = ttk.Frame(tabs)
        tab_manage = ttk.Frame(tabs)
        tabs.add(tab_base, text="宗门管理")
        tabs.add(tab_manage, text="内务/生产")

        # Base actions
        tk.Button(tab_base, text="保存", command=save_sect).grid(row=0, column=0, sticky="we", padx=4, pady=4)
        tk.Button(tab_base, text="宗门传功", command=legacy_teach).grid(row=0, column=1, sticky="we", padx=4, pady=4)
        tk.Button(tab_base, text="招收弟子", command=self.recruit_disciple).grid(row=1, column=0, sticky="we", padx=4, pady=4)
        tk.Button(tab_base, text="占领地盘", command=self.occupy_territory).grid(row=1, column=1, sticky="we", padx=4, pady=4)

        disciple_box = tk.Listbox(tab_base, height=6, width=36)
        disciple_box.grid(row=2, column=0, columnspan=2, sticky="we", padx=4, pady=4)
        for d in self.sect.get("disciples", []):
            realm = REALM_STAGES[min(d.get("realm_idx", 0), len(REALM_STAGES) - 1)]["name"]
            disciple_box.insert("end", f"{d['name']} | 资质{d['apt']} | {realm}{d.get('lvl',1)}级 | 擅长{d['element']}")

        land_box = tk.Listbox(tab_base, height=5, width=36)
        land_box.grid(row=3, column=0, columnspan=2, sticky="we", padx=4, pady=4)
        for t in self.sect.get("territories", []):
            land_box.insert("end", f"{t['name']} | {t['rarity']} | 规模{t['size']} | 资源{t.get('resource','灵田')}")

        # Inner management
        tk.Button(tab_manage, text="种植灵田", command=self.sect_plant).grid(row=0, column=0, sticky="we", padx=4, pady=4)
        tk.Button(tab_manage, text="炼丹", command=self.sect_alchemy).grid(row=0, column=1, sticky="we", padx=4, pady=4)
        tk.Button(tab_manage, text="炼器", command=self.sect_refine).grid(row=1, column=0, sticky="we", padx=4, pady=4)
        tk.Button(tab_manage, text="练功", command=self.sect_training).grid(row=1, column=1, sticky="we", padx=4, pady=4)
        tk.Button(tab_manage, text="历练", command=self.sect_expedition).grid(row=2, column=0, sticky="we", padx=4, pady=4)

        tk.Button(tab_manage, text="税赋", command=self.sect_collect_tax).grid(row=2, column=1, sticky="we", padx=4, pady=4)
        tk.Button(tab_manage, text="矿脉开采", command=self.sect_mine).grid(row=3, column=0, sticky="we", padx=4, pady=4)
        tk.Button(tab_manage, text="经阁研习", command=self.sect_library).grid(row=3, column=1, sticky="we", padx=4, pady=4)
        tk.Button(tab_manage, text="宗门戒备", command=self.sect_defense).grid(row=4, column=0, sticky="we", padx=4, pady=4)
        tk.Button(tab_manage, text="弟子训练", command=self.sect_train_disciple).grid(row=4, column=1, sticky="we", padx=4, pady=4)
        tk.Button(tab_manage, text="派遣任务", command=self.sect_mission).grid(row=5, column=0, sticky="we", padx=4, pady=4)
        tk.Button(tab_manage, text="灵田扩建", command=self.sect_expand_farm).grid(row=5, column=1, sticky="we", padx=4, pady=4)
        tk.Button(tab_manage, text="宗门仓库", command=self.sect_open_vault).grid(row=6, column=0, sticky="we", padx=4, pady=4)
        tk.Button(tab_manage, text="唯一宝物", command=self.sect_unique_relic).grid(row=6, column=1, sticky="we", padx=4, pady=4)

        res = self.sect.get("resources", {})
        bld = self.sect.get("buildings", {})
        ores = res.get("ores", {})
        ore_text = " ".join([f"{k}{v}" for k, v in ores.items()]) if ores else "无"
        res_label = tk.Label(
            tab_manage,
            text=(
                f"资源：灵力{res.get('spirit',0)} 草药{res.get('herbs',0)} 矿产[{ore_text}] | "
                f"建筑：灵田{bld.get('farm',1)} 矿脉{bld.get('mine',1)} 经阁{bld.get('library',1)} | "
                f"戒备{self.sect.get('security',0)} 名望{self.sect.get('fame',0)}"
            ),
        )
        res_label.grid(row=7, column=0, columnspan=2, sticky="w", padx=4, pady=4)

        tk.Button(win, text="返回秘境列表", command=lambda: [win.destroy(), self.show_secret_ui()]).grid(row=4, column=1, sticky="we", padx=4, pady=6)
        win.grid_columnconfigure(1, weight=1)
        win.grid_rowconfigure(3, weight=1)

    # ---------- items / gear ----------
    def use_potion(self):
        for pid in ("回复药", "healing_potion"):
            if self.player["bag"].get(pid, 0) > 0:
                self.use_item(pid)
                return
        self.log("没有可用的药品。")

    # ---------- sect management ----------
    def ensure_sect_data(self):
        if not self.sect:
            self.sect = {
                "name": "无名宗门",
                "bonus_type": "drop",
                "drop_bonus": 0.08,
                "luck_bonus": 0,
                "created": False,
            }
        self.sect.setdefault("disciples", [])
        self.sect.setdefault("territories", [])
        self.sect.setdefault("resources", {"spirit": 0, "herbs": 0, "ores": {}})
        self.sect.setdefault("last_actions", {})
        self.sect.setdefault("buildings", {"farm": 1, "mine": 1, "library": 1, "hall": 1})
        self.sect.setdefault("security", 0)
        self.sect.setdefault("fame", 0)
        self.sect.setdefault("vault", {})
        self.sect.setdefault("unique_relics", ["护宗灵印"])
        self.sect.setdefault("protected_disciple", None)
        self.sect.setdefault("created", False)
        # normalize resources for older saves
        if isinstance(self.sect["resources"].get("ores"), int):
            val = self.sect["resources"]["ores"]
            self.sect["resources"]["ores"] = {}
            if val > 0:
                self.sect["resources"]["ores"][ORE_TIER_LIST["黄"][0]] = val
        for d in self.sect["disciples"]:
            self.ensure_disciple(d)

    def ensure_disciple(self, d: dict):
        d.setdefault("lvl", 1)
        d.setdefault("realm_idx", 0)
        d.setdefault("exp", 0)
        d.setdefault("exp_next", 20)
        d.setdefault("stats", {"hp": 60, "atk": 6, "def": 3, "spd": 6, "crit": 1, "res": 1})
        d.setdefault("age_months", 0)
        d.setdefault("lifespan_months", self.compute_disciple_lifespan(d))
        d.setdefault("skills", [])
        d.setdefault("status", "修行")
        if not d.get("path"):
            element = d.get("element", "")
            if element in ("火", "金"):
                d["path"] = "战修"
            elif element in ("水", "土"):
                d["path"] = "内修"
            elif element in ("木",):
                d["path"] = "丹修"
            else:
                d["path"] = random.choice(list(DISCIPLE_PATHS.keys()))
        if not d.get("stage_idx"):
            d["stage_idx"] = 0
        d["lifespan_months"] = max(d.get("lifespan_months", 0), self.compute_disciple_lifespan(d))

    def disciple_gain_exp(self, d: dict, amount: int):
        d["exp"] += amount
        while d["exp"] >= d["exp_next"]:
            stage = REALM_STAGES[min(d.get("realm_idx", 0), len(REALM_STAGES) - 1)]
            if d["lvl"] >= stage["lvl_cap"]:
                d["exp"] = min(d["exp"], d["exp_next"] - 1)
                break
            d["exp"] -= d["exp_next"]
            d["lvl"] += 1
            d["exp_next"] = int(d["exp_next"] * 1.2 + 6)
            d["stats"]["hp"] += 6
            d["stats"]["atk"] += 1
            d["stats"]["def"] += 1
            d["stats"]["spd"] += 1
        d["stage_idx"] = min(d.get("stage_idx", 0), len(DISCIPLE_STAGE_NAMES) - 1)

    def disciple_try_breakthrough(self, d: dict):
        stage = REALM_STAGES[min(d.get("realm_idx", 0), len(REALM_STAGES) - 1)]
        if d.get("lvl", 1) < stage["lvl_cap"]:
            return False
        apt = d.get("apt", 1)
        chance = min(0.9, 0.25 + apt * 0.05)
        if random.random() > chance:
            return False
        if d.get("realm_idx", 0) < len(REALM_STAGES) - 1:
            d["realm_idx"] += 1
            d["exp_next"] = int(d["exp_next"] * 1.25 + 10)
            d["stats"]["hp"] += 10
            d["stats"]["atk"] += 2
            d["stats"]["def"] += 2
            d["stats"]["spd"] += 1
            d["stage_idx"] = min(d.get("stage_idx", 0) + 1, len(DISCIPLE_STAGE_NAMES) - 1)
            d["lifespan_months"] = max(d.get("lifespan_months", 0), self.compute_disciple_lifespan(d))
            return True
        return False

    def disciple_monthly_progress(self, d: dict):
        self.ensure_disciple(d)
        path = d.get("path", "内修")
        bonus = DISCIPLE_PATHS.get(path, {"exp": 2})
        base_exp = 2 + d.get("apt", 1) // 3 + bonus.get("exp", 0)
        self.disciple_gain_exp(d, base_exp)
        stats = d.get("stats", {})
        for key in ("hp", "atk", "def", "spd", "crit", "res"):
            if bonus.get(key):
                stats[key] = stats.get(key, 0) + bonus[key]
        d["stats"] = stats
        d["age_months"] = d.get("age_months", 0) + 1
        d["lifespan_months"] = max(d.get("lifespan_months", 0), self.compute_disciple_lifespan(d))
        if d["age_months"] >= d["lifespan_months"]:
            return "寿终"
        if self.disciple_try_breakthrough(d):
            return "突破"
        return "修行"

    def sect_action_ready(self, key: str):
        self.ensure_sect_data()
        last = self.sect["last_actions"].get(key)
        month = self.current_month()
        if last == month:
            self.log("本月已执行该内务，下月再试。", "system")
            return False
        self.sect["last_actions"][key] = month
        return True

    def recruit_disciple(self):
        self.ensure_sect_data()
        if not self.sect.get("territories"):
            self.log("没有地盘，无法招收弟子。", "system")
            return
        if not self.sect_action_ready("recruit"):
            return
        best_rarity = max((t["rarity"] for t in self.sect["territories"]), default="普通")
        base = {"普通": 0.6, "稀有": 0.85, "极品": 1.0}.get(best_rarity, 0.6)
        apt = random.randint(1, 6)
        if random.random() < base:
            apt += random.randint(2, 6)
        name = random.choice(["林", "叶", "顾", "白", "洛", "唐", "苏"]) + random.choice(["青", "玄", "尘", "渊", "离", "澜"])
        element = random.choice(ELEMENTS)
        d = {"name": name, "apt": apt, "element": element}
        self.ensure_disciple(d)
        self.sect["disciples"].append(d)
        self.log(f"招收弟子：{name}（资质{apt}，擅长{element}）", "system")

    def occupy_territory(self):
        self.ensure_sect_data()
        if not self.sect_action_ready("territory"):
            return
        cost = 80 + 20 * len(self.sect["territories"])
        if self.player["gold"] < cost:
            self.log(f"金币不足，需要 {cost}。", "system")
            return
        self.player["gold"] -= cost
        rarity = weighted_choice([("普通", 70), ("稀有", 25), ("极品", 5)])
        size = random.randint(1, 3) + (1 if rarity == "稀有" else 2 if rarity == "极品" else 0)
        name = random.choice(["临川", "青岭", "栖霞", "落星", "寒山", "玉泉"]) + "城"
        if rarity == "普通":
            res_type = "灵田" if random.random() < 0.7 else pick_ore_for_rarity("普通")
        elif rarity == "稀有":
            res_type = "灵田" if random.random() < 0.2 else pick_ore_for_rarity("稀有")
        else:
            res_type = "灵田" if random.random() < 0.1 else pick_ore_for_rarity("极品")
        self.sect["territories"].append({"name": name, "rarity": rarity, "size": size, "resource": res_type})
        self.log(f"占领地盘：{name}（{rarity}，规模{size}，资源{res_type}）", "system")

    def sect_plant(self):
        self.ensure_sect_data()
        if not self.sect_action_ready("plant"):
            return
        land = sum(t.get("size", 1) for t in self.sect.get("territories", []) if t.get("resource") == "灵田")
        gain = max(1, land) * random.randint(1, 3)
        self.sect["resources"]["herbs"] += gain
        self.log(f"灵田收成：草药 +{gain}", "system")

    def sect_alchemy(self):
        self.ensure_sect_data()
        if not self.sect_action_ready("alchemy"):
            return
        if not self.has_fire_disciple():
            self.log("宗门缺少火属性弟子，无法炼丹。", "system")
            return
        if self.sect["resources"]["herbs"] < 3:
            self.log("草药不足，无法炼丹。", "system")
            return
        self.sect["resources"]["herbs"] -= 3
        pill = random.choice(["悟性丹·黄", "回春丹", "破境丹(小)"])
        self.player["bag"][pill] = self.player["bag"].get(pill, 0) + 1
        fire_cnt = sum(1 for d in self.sect.get("disciples", []) if d.get("element") == "火")
        extra_chance = min(0.4, fire_cnt * 0.05)
        if random.random() < extra_chance:
            self.player["bag"][pill] = self.player["bag"].get(pill, 0) + 1
            self.log(f"炼丹成功：{pill}（火系协力+1）", "system")
        else:
            self.log(f"炼丹成功：{pill}", "system")

    def sect_refine(self):
        self.ensure_sect_data()
        if not self.sect_action_ready("refine"):
            return
        if not self.has_fire_disciple():
            self.log("宗门缺少火属性弟子，无法炼器。", "system")
            return
        ores = self.sect["resources"]["ores"]
        if not ores:
            self.log("矿石不足，无法炼器。", "system")
            return
        ore = next(iter(ores.keys()))
        ores[ore] -= 2
        if ores[ore] <= 0:
            del ores[ore]
        gear = random.choice(["玄铁护符", "精铁短刃", "灵木护甲"])
        self.player["bag"][gear] = self.player["bag"].get(gear, 0) + 1
        fire_cnt = sum(1 for d in self.sect.get("disciples", []) if d.get("element") == "火")
        extra_chance = min(0.3, fire_cnt * 0.04)
        if random.random() < extra_chance:
            self.player["bag"][gear] = self.player["bag"].get(gear, 0) + 1
            self.log(f"炼器成功：{gear}（火系协力+1）", "system")
        else:
            self.log(f"炼器成功：{gear}（消耗{ore}）", "system")

    def sect_training(self):
        self.ensure_sect_data()
        if not self.sect_action_ready("training"):
            return
        spirit = self.sect["resources"]["spirit"]
        if spirit < 2:
            self.log("灵力不足，无法练功。", "system")
            return
        self.sect["resources"]["spirit"] -= 2
        if self.sect["disciples"]:
            d = random.choice(self.sect["disciples"])
            gain = 2 + d.get("apt", 1) // 3
            self.disciple_gain_exp(d, gain)
            self.log(f"弟子{d['name']}修行进展，经验 +{gain}", "system")
        else:
            self.add_exp(6)
            self.log("无人可训，宗门资源转化为自身修为。", "system")

    def sect_expedition(self):
        self.ensure_sect_data()
        if not self.sect_action_ready("expedition"):
            return
        if not self.sect["disciples"]:
            self.log("无弟子可历练。", "system")
            return
        d = random.choice(self.sect["disciples"])
        gain_gold = random.randint(15, 35) + d.get("apt", 1)
        self.player["gold"] += gain_gold
        self.log(f"弟子{d['name']}历练归来，带回金币 +{gain_gold}", "system")
        self.disciple_gain_exp(d, 2 + d.get("apt", 1) // 2)
        if random.random() < 0.25:
            ore = pick_ore_by_tier("黄")
            self.sect["resources"]["ores"][ore] = self.sect["resources"]["ores"].get(ore, 0) + 1
            self.log(f"历练带回矿石 {ore} +1", "system")
        if random.random() < 0.25:
            self.sect["resources"]["spirit"] += 1
            self.log("历练带回灵力 +1", "system")
        if random.random() < 0.2:
            realm_idx = min(d.get("realm_idx", 0), len(BREAKTHROUGH_REALMS) - 1)
            low = max(0, realm_idx - random.randint(0, 2))
            item_id = self.pick_breakthrough_item(low)
            self.player["bag"][item_id] = self.player["bag"].get(item_id, 0) + 1
            self.log(f"历练带回天材地宝：{item_id}", "system")
        if random.random() < 0.08:
            realm_idx = min(d.get("realm_idx", 0), len(BREAKTHROUGH_REALMS) - 1)
            low = max(0, realm_idx - random.randint(0, 1))
            realm_name = BREAKTHROUGH_REALMS[low]
            recipe_item = self.recipe_unlock_item(realm_name)
            self.player["bag"][recipe_item] = self.player["bag"].get(recipe_item, 0) + 1
            self.learn_recipe(recipe_item)

    def sect_collect_tax(self):
        self.ensure_sect_data()
        if not self.sect_action_ready("tax"):
            return
        territories = self.sect.get("territories", [])
        if not territories:
            self.log("暂无地盘可征收。", "system")
            return
        base = sum(t.get("size", 1) for t in territories) * 8
        bonus = self.sect.get("fame", 0)
        gold = base + bonus
        self.player["gold"] += gold
        self.log(f"征收税赋：金币 +{gold}", "system")

    def sect_expand_farm(self):
        self.ensure_sect_data()
        if not self.sect_action_ready("farm"):
            return
        cost = 20 + self.sect["buildings"]["farm"] * 10
        if self.player["gold"] < cost:
            self.log(f"金币不足，需要 {cost}。", "system")
            return
        self.player["gold"] -= cost
        self.sect["buildings"]["farm"] += 1
        self.log(f"灵田扩建成功，等级 {self.sect['buildings']['farm']}", "system")

    def sect_mine(self):
        self.ensure_sect_data()
        if not self.sect_action_ready("mine"):
            return
        level = self.sect["buildings"]["mine"]
        mines = [t for t in self.sect.get("territories", []) if is_ore_resource(t.get("resource", ""))]
        if not mines:
            self.log("暂无矿产地盘。", "system")
            return
        t = random.choice(mines)
        res = t.get("resource", "")
        ore_map = {"铁矿": "精铁矿", "铜矿": "铜矿", "金矿": "金矿", "灵石矿": "灵石"}
        if res in ORE_ITEM_SET:
            ore = res
        else:
            ore = ore_map.get(res, "精铁矿")
        gain = random.randint(1, 1 + level)
        self.sect["resources"]["ores"][ore] = self.sect["resources"]["ores"].get(ore, 0) + gain
        self.log(f"矿脉开采：{ore} +{gain}", "system")

    def sect_library(self):
        self.ensure_sect_data()
        if not self.sect_action_ready("library"):
            return
        level = self.sect["buildings"]["library"]
        self.player["insight"][self.player_main_element()] += max(1, level // 2)
        self.log("经阁研习，悟性有所提升。", "system")

    def sect_defense(self):
        self.ensure_sect_data()
        if not self.sect_action_ready("defense"):
            return
        self.sect["security"] += 1
        self.log(f"宗门戒备提升，当前戒备 {self.sect['security']}", "system")

    def sect_train_disciple(self):
        self.ensure_sect_data()
        if not self.sect_action_ready("disciple"):
            return
        if not self.sect["disciples"]:
            self.log("暂无弟子可训练。", "system")
            return
        d = random.choice(self.sect["disciples"])
        d["apt"] += 1
        self.disciple_gain_exp(d, 3)
        self.log(f"弟子{d['name']}资质提升至 {d['apt']}", "system")

    def sect_mission(self):
        self.ensure_sect_data()
        if not self.sect_action_ready("mission"):
            return
        if not self.sect["disciples"]:
            self.log("暂无弟子可派遣。", "system")
            return
        d = random.choice(self.sect["disciples"])
        gold = random.randint(20, 50)
        self.player["gold"] += gold
        if random.random() < 0.2:
            self.sect["fame"] += 1
        self.log(f"弟子{d['name']}执行任务归来，金币 +{gold}", "system")
        self.disciple_gain_exp(d, 3 + d.get("apt", 1) // 2)

    def sect_open_vault(self):
        self.ensure_sect_data()
        win = tk.Toplevel(self.root)
        win.title("宗门仓库")
        tk.Label(win, text="把背包物品存入仓库，或分配给弟子。").pack(anchor="w", padx=6, pady=4)

        bag_box = tk.Listbox(win, height=6, width=40)
        bag_box.pack(fill="x", padx=6, pady=4)
        bag_items = [k for k, v in self.player["bag"].items() if v > 0]
        for k in bag_items:
            bag_box.insert("end", f"{k} x{self.player['bag'][k]}")

        tk.Label(win, text="选择分配弟子：").pack(anchor="w", padx=6)
        disciple_box = tk.Listbox(win, height=5, width=40)
        disciple_box.pack(fill="x", padx=6, pady=4)
        disciple_ids = []
        for d in self.sect.get("disciples", []):
            realm = REALM_STAGES[min(d.get("realm_idx", 0), len(REALM_STAGES) - 1)]["name"]
            stage = DISCIPLE_STAGE_NAMES[min(d.get("stage_idx", 0), len(DISCIPLE_STAGE_NAMES) - 1)]
            disciple_box.insert("end", f"{d['name']} | {realm}{d.get('lvl',1)}级 | {stage}·{d.get('path','修行')}")
            disciple_ids.append(d["name"])

        vault_box = tk.Listbox(win, height=6, width=40)
        vault_box.pack(fill="x", padx=6, pady=4)
        vault_items = list(self.sect["vault"].keys())
        for k in vault_items:
            vault_box.insert("end", f"{k} x{self.sect['vault'][k]}")

        def move_to_vault():
            sel = bag_box.curselection()
            if not sel:
                return
            item = bag_items[sel[0]]
            if self.player["bag"].get(item, 0) <= 0:
                return
            self.player["bag"][item] -= 1
            self.sect["vault"][item] = self.sect["vault"].get(item, 0) + 1
            win.destroy()
            self.sect_open_vault()

        def assign_disciple():
            if not self.sect["disciples"]:
                self.log("暂无弟子可装备。", "system")
                return
            sel = vault_box.curselection()
            if not sel:
                return
            if sel[0] >= len(vault_items):
                return
            item = vault_items[sel[0]]
            dsel = disciple_box.curselection()
            if not dsel or dsel[0] >= len(self.sect["disciples"]):
                self.log("请先选择要分配的弟子。", "system")
                return
            d = self.sect["disciples"][dsel[0]]
            d.setdefault("gear", [])
            d["gear"].append(item)
            self.sect["vault"][item] -= 1
            if self.sect["vault"][item] <= 0:
                del self.sect["vault"][item]
            self.log(f"给弟子{d['name']}装备 {item}", "system")
            win.destroy()

        tk.Button(win, text="存入仓库", command=move_to_vault).pack(side="left", padx=6, pady=6)
        tk.Button(win, text="分配给弟子", command=assign_disciple).pack(side="left", padx=6, pady=6)
        tk.Button(win, text="关闭", command=win.destroy).pack(side="left", padx=6, pady=6)

    def sect_unique_relic(self):
        self.ensure_sect_data()
        if not self.sect["disciples"]:
            self.log("暂无弟子可保护。", "system")
            return
        if not self.sect.get("unique_relics"):
            self.log("没有可用的唯一宝物。", "system")
            return
        d = random.choice(self.sect["disciples"])
        self.sect["protected_disciple"] = d["name"]
        relic = self.sect["unique_relics"][0]
        self.log(f"唯一宝物【{relic}】护佑弟子 {d['name']}，本月不牺牲。", "system")

    def sect_under_attack(self):
        self.ensure_sect_data()
        if not self.sect["disciples"]:
            return
        threat = weighted_choice([("兽潮", 60), ("敌袭", 40)])
        base_loss = max(1, len(self.sect["disciples"]) // 3)
        loss = max(0, base_loss - self.sect.get("security", 0))
        protected = self.sect.get("protected_disciple")
        casualties = []
        if loss > 0:
            candidates = [d for d in self.sect["disciples"] if d["name"] != protected]
            random.shuffle(candidates)
            casualties = candidates[:loss]
            self.sect["disciples"] = [d for d in self.sect["disciples"] if d not in casualties]
        if casualties:
            names = "、".join([d["name"] for d in casualties])
            self.log(f"宗门遭遇{threat}，弟子牺牲：{names}", "system")
        else:
            self.log(f"宗门遭遇{threat}，无弟子牺牲。", "system")

    def auto_run_sect_monthly(self):
        if not self.sect or not self.sect.get("created"):
            return
        self.ensure_sect_data()
        month = self.current_month()
        if self.sect.get("last_auto_month") == month:
            return
        self.sect["last_auto_month"] = month

        log_lines = []
        # auto resources
        land = sum(t.get("size", 1) for t in self.sect.get("territories", []) if t.get("resource") == "灵田")
        if land > 0:
            gain = max(1, land // 2)
            self.sect["resources"]["herbs"] += gain
            log_lines.append(f"灵田+{gain}")

        mines = [t for t in self.sect.get("territories", []) if is_ore_resource(t.get("resource", ""))]
        if mines:
            t = random.choice(mines)
            res = t.get("resource", "")
            ore_map = {"铁矿": "精铁矿", "铜矿": "铜矿", "金矿": "金矿", "灵石矿": "灵石"}
            ore = res if res in ORE_ITEM_SET else ore_map.get(res, "精铁矿")
            gain = random.randint(1, 2)
            self.sect["resources"]["ores"][ore] = self.sect["resources"]["ores"].get(ore, 0) + gain
            log_lines.append(f"{ore}+{gain}")

        # disciple progression
        breakthroughs = []
        deaths = []
        for d in list(self.sect.get("disciples", [])):
            result = self.disciple_monthly_progress(d)
            if result == "突破":
                breakthroughs.append(d["name"])
            elif result == "寿终":
                deaths.append(d["name"])
                self.sect["disciples"] = [x for x in self.sect["disciples"] if x is not d]

        if breakthroughs:
            log_lines.append(f"突破:{'、'.join(breakthroughs)}")
        if deaths:
            log_lines.append(f"寿终:{'、'.join(deaths)}")

        # passive income
        if self.sect.get("territories"):
            gold = sum(t.get("size", 1) for t in self.sect["territories"]) * 2
            self.player["gold"] += gold
            log_lines.append(f"税赋+{gold}")

        if log_lines:
            self.log(f"[宗门自动] " + " | ".join(log_lines), "system")
    def use_item(self, item_id):
        cnt = self.player["bag"].get(item_id, 0)
        if cnt <= 0:
            self.log("没有可用的药品。")
            return
        if item_id in ("healing_potion", "回复药"):
            heal = 40
            self.player["hp"] = min(self.player["hp"] + heal, self.player["max_hp"])
            self.player["bag"][item_id] -= 1
            self.log(f"使用回复药，恢复 {heal} 点生命。")
        elif item_id in ("repair_kit", "修理包"):
            self.repair_equipment()
            self.player["bag"][item_id] -= 1
        elif item_id.startswith("insight_pill_"):
            parts = item_id.replace("insight_pill_", "").split("_")
            if len(parts) == 2:
                element, tier = parts
            else:
                element, tier = parts[0], "黄"
            bonus = PILL_BONUS.get(tier, 1)
            hp_bonus = PILL_HP_BONUS.get(tier, 3)
            self.player["insight"][element] = self.player["insight"].get(element, 0) + bonus
            self.player["max_hp"] += hp_bonus
            self.player["hp"] = min(self.player["hp"] + hp_bonus, self.player["max_hp"])
            self.player["bag"][item_id] -= 1
            self.log(f"服用悟性丹·{element}·{tier}，{element}悟性 +{bonus}，生命上限 +{hp_bonus}。")

    def show_forge_ui(self):
        win = tk.Toplevel(self.root)
        win.title("选择锻造类型")
        tk.Button(win, text="武器", width=12, command=lambda: [self.forge_slot("weapon"), win.destroy(), self.describe()]).grid(row=0, column=0, padx=6, pady=6)
        tk.Button(win, text="护甲", width=12, command=lambda: [self.forge_slot("armor"), win.destroy(), self.describe()]).grid(row=0, column=1, padx=6, pady=6)
        tk.Button(win, text="饰品", width=12, command=lambda: [self.forge_slot("accessory"), win.destroy(), self.describe()]).grid(row=0, column=2, padx=6, pady=6)
        tk.Button(win, text="取消", command=win.destroy).grid(row=1, column=2, padx=6, pady=6, sticky="e")

    def forge_slot(self, slot: str):
        if not self.equip_catalog:
            self.log("未找到装备图纸。")
            return
        choices = [g for g in self.equip_catalog if g.get("slot") == slot]
        if not choices:
            self.log(f"没有该槽位的装备：{slot}")
            return
        gear = dict(random.choice(choices))
        bp_map = {
            "weapon": "武器图纸",
            "armor": "护甲图纸",
            "accessory": "饰品图纸",
        }
        tier = gear.get("tier", "黄")
        mat_need = {
            "weapon": {"精铁矿": 3},
            "armor": {"灵巧兽皮": 2},
            "accessory": {"灵核碎片": 1},
        }
        for k, v in GEAR_TIER_MATS.get(tier, {}).items():
            mat_need.setdefault(slot, {})
            mat_need[slot][k] = mat_need[slot].get(k, 0) + v
        bp_key = bp_map.get(slot, "武器图纸")
        if self.player["bag"].get(bp_key, 0) <= 0:
            self.log(f"缺少{bp_key}，无法锻造。")
            return
        need = mat_need.get(slot, {})
        for k, v in need.items():
            if self.player["bag"].get(k, 0) < v:
                self.log(f"材料不足：需要 {k} x{v}")
                return
        self.player["bag"][bp_key] -= 1
        for k, v in need.items():
            self.player["bag"][k] -= v
        gear.setdefault("dur", 100)
        gear.setdefault("max_dur", gear["dur"])
        self.equip_gear(gear)
        need_txt = "，".join([f"{k}x{v}" for k, v in need.items()]) if need else "无"
        self.log(f"消耗 {bp_key} x1，材料({need_txt})，锻造并装备：{gear.get('name', gear['id'])}")

    def equip_gear(self, gear):
        slot = gear.get("slot", "weapon")
        if slot not in self.player["equip"]:
            self.log(f"未知装备槽位 {slot}")
            return
        self.ensure_gear_meta(gear)
        old = self.player["equip"].get(slot)
        if old:
            self.remove_gear_bonus(old)
        self.player["equip"][slot] = gear
        self.apply_gear_bonus(gear)

    def apply_gear_bonus(self, gear):
        attrs = gear.get("attrs", [0, 0, 0, 0, 0, 0])
        self.player["max_hp"] += attrs[0]
        self.player["atk"] += attrs[1]
        self.player["def"] += attrs[2]
        self.player["spd"] += attrs[3]
        self.player["crit"] += attrs[4]
        self.player["res"] += attrs[5]
        self.player["hp"] = min(self.player["hp"], self.player["max_hp"])

    def remove_gear_bonus(self, gear):
        attrs = gear.get("attrs", [0, 0, 0, 0, 0, 0])
        self.player["max_hp"] -= attrs[0]
        self.player["atk"] -= attrs[1]
        self.player["def"] -= attrs[2]
        self.player["spd"] -= attrs[3]
        self.player["crit"] -= attrs[4]
        self.player["res"] -= attrs[5]
        self.player["hp"] = min(self.player["hp"], self.player["max_hp"])

    def ensure_gear_meta(self, gear):
        if "kind" not in gear:
            kinds = GEAR_KINDS.get(gear.get("slot", "weapon"), ["装备"])
            idx = 0
            try:
                raw = "".join(ch for ch in gear.get("id", "") if ch.isdigit())
                idx = int(raw) if raw else 0
            except Exception:
                idx = 0
            gear["kind"] = kinds[idx % len(kinds)]
        if "tier" not in gear:
            score = sum(v for v in gear.get("attrs", []) if v > 0)
            tier = "黄"
            for t, th in GEAR_TIER_THRESHOLDS:
                if score >= th:
                    tier = t
            gear["tier"] = tier
        gear.setdefault("refine", 0)

    def refine_gear(self, gear, treasure):
        element = treasure.get("element") or self.player_main_element()
        tier = treasure.get("rarity", "黄")
        scale = TREASURE_BONUS_SCALE.get(tier, 1)
        self.ensure_gear_meta(gear)
        cap = GEAR_REFINE_CAP.get(gear.get("tier", "黄"), 2)
        if gear.get("refine", 0) >= cap:
            self.log(f"{gear.get('name')} 炼器已达上限（{gear.get('tier')}品 {cap}次）", "system")
            return
        attrs = gear.get("attrs", [0, 0, 0, 0, 0, 0])
        weights = ELEMENT_BONUS_WEIGHTS.get(element, {})
        level_mult = 1.0 + 0.03 * max(0, self.player.get("refine_level", 1) - 1)
        level_mult += self.refine_spec_bonus().get("bonus", 0.0)
        inc = [0, 0, 0, 0, 0, 0]
        inc[0] = int(weights.get("max_hp", 0) * scale * level_mult)
        inc[1] = int(weights.get("atk", 0) * scale * level_mult)
        inc[2] = int(weights.get("def", 0) * scale * level_mult)
        inc[3] = int(weights.get("spd", 0) * scale * level_mult)
        inc[4] = int(weights.get("crit", 0) * scale * level_mult)
        inc[5] = int(weights.get("res", 0) * scale * level_mult)
        self.remove_gear_bonus(gear)
        for i in range(6):
            attrs[i] += inc[i]
        gear["attrs"] = attrs
        gear["elem"] = element
        gear["refine"] = gear.get("refine", 0) + 1
        self.apply_gear_bonus(gear)
        self.log(f"炼器成功：{gear.get('name')} 获得 {element} 加成（{tier}品）", f"elem_{element}")

    def degrade_equipment(self):
        for gear in self.player["equip"].values():
            if gear:
                loss = random.randint(3, 8)
                gear["dur"] = max(0, gear.get("dur", 100) - loss)
                if gear["dur"] <= 0:
                    self.log(f"{gear.get('name','装备')} 耐久耗尽，请维修。")

    def repair_equipment(self):
        cost = 10
        if self.player["gold"] < cost:
            self.log(f"金币不足，维修需要 {cost} 金币。")
            return
        self.player["gold"] -= cost
        for gear in self.player["equip"].values():
            if gear:
                gear["dur"] = gear.get("max_dur", 100)
        self.log(f"装备耐久已全部恢复，消耗金币 {cost}。")

    # ---------- mount equipment ----------
    def apply_mount_bonus(self, item_id):
        bonus = MOUNT_ITEM_BONUS.get(item_id, {})
        self.player["max_hp"] += bonus.get("hp", 0)
        self.player["atk"] += bonus.get("atk", 0)
        self.player["def"] += bonus.get("def", 0)
        self.player["spd"] += bonus.get("spd", 0)
        self.player["crit"] += bonus.get("crit", 0)
        self.player["res"] += bonus.get("res", 0)
        self.player["hp"] = min(self.player["hp"], self.player["max_hp"])

    def remove_mount_bonus(self, item_id):
        bonus = MOUNT_ITEM_BONUS.get(item_id, {})
        self.player["max_hp"] -= bonus.get("hp", 0)
        self.player["atk"] -= bonus.get("atk", 0)
        self.player["def"] -= bonus.get("def", 0)
        self.player["spd"] -= bonus.get("spd", 0)
        self.player["crit"] -= bonus.get("crit", 0)
        self.player["res"] -= bonus.get("res", 0)

    def apply_active_mount_bonus(self, mount):
        if not mount:
            return
        bonus = MOUNT_RANK_BONUS.get(mount.get("rank", "C"), {})
        self.player["max_hp"] += bonus.get("hp", 0)
        self.player["atk"] += bonus.get("atk", 0)
        self.player["def"] += bonus.get("def", 0)
        self.player["spd"] += bonus.get("spd", 0)
        self.player["crit"] += bonus.get("crit", 0)
        self.player["res"] += bonus.get("res", 0)
        self.player["luck"] += bonus.get("luck", 0)
        self.player["hp"] = min(self.player["hp"], self.player["max_hp"])

    def remove_active_mount_bonus(self, mount):
        if not mount:
            return
        bonus = MOUNT_RANK_BONUS.get(mount.get("rank", "C"), {})
        self.player["max_hp"] -= bonus.get("hp", 0)
        self.player["atk"] -= bonus.get("atk", 0)
        self.player["def"] -= bonus.get("def", 0)
        self.player["spd"] -= bonus.get("spd", 0)
        self.player["crit"] -= bonus.get("crit", 0)
        self.player["res"] -= bonus.get("res", 0)
        self.player["luck"] -= bonus.get("luck", 0)
        self.player["hp"] = min(self.player["hp"], self.player["max_hp"])

    def equip_mount_item(self, slot: str, item_id: str):
        if self.player["bag"].get(item_id, 0) <= 0:
            self.log(f"缺少{display_name(item_id)}，无法装备。")
            return
        old = self.player.get("mount_equip", {}).get(slot)
        if old:
            self.remove_mount_bonus(old)
        self.player["bag"][item_id] -= 1
        self.player["mount_equip"][slot] = item_id
        self.apply_mount_bonus(item_id)
        self.log(f"装备坐骑部件：{display_name(item_id)}（槽位 {slot}）")

    def equip_mount_from_list(self, listbox, mount_ids, parent_win=None):
        sel = listbox.curselection()
        if not sel:
            self.log("请选择一只坐骑。")
            return
        idx = sel[0]
        if idx >= len(mount_ids):
            return
        mid = mount_ids[idx]
        mount = next((m for m in self.player["mounts"] if m["id"] == mid), None)
        if not mount:
            self.log("坐骑不存在。")
            return
        if self.player.get("active_mount_id"):
            old = next((m for m in self.player["mounts"] if m["id"] == self.player["active_mount_id"]), None)
            self.remove_active_mount_bonus(old)
        self.player["active_mount"] = mount["name"]
        self.player["active_mount_id"] = mount["id"]
        self.apply_active_mount_bonus(mount)
        self.log(f"已装备坐骑：{mount['name']} Rank {mount['rank']}")
        if parent_win:
            parent_win.destroy()
            self.show_bag()

    # ---------- mount breeding ----------
    def show_breed_ui(self):
        mounts = self.player.get("mounts", [])
        if len(mounts) < 2:
            self.log("坐骑不足，无法繁育。")
            return
        win = tk.Toplevel(self.root)
        win.title("选择父母进行繁育")
        tk.Label(win, text="父母A").grid(row=0, column=0)
        tk.Label(win, text="父母B").grid(row=0, column=1)
        list_a = tk.Listbox(win, height=6)
        list_b = tk.Listbox(win, height=6)
        list_a.grid(row=1, column=0, padx=4, pady=4)
        list_b.grid(row=1, column=1, padx=4, pady=4)
        for m in mounts:
            list_a.insert("end", f"{m['name']} Rank {m['rank']} 繁育:{m['breed_count']}/4")
            list_b.insert("end", f"{m['name']} Rank {m['rank']} 繁育:{m['breed_count']}/4")

        def do_breed():
            sel_a, sel_b = list_a.curselection(), list_b.curselection()
            if not sel_a or not sel_b:
                return
            idx_a, idx_b = sel_a[0], sel_b[0]
            if idx_a == idx_b:
                self.log("不能选择同一只坐骑。")
                return
            parent1, parent2 = mounts[idx_a], mounts[idx_b]
            if parent1["breed_count"] >= 4 or parent2["breed_count"] >= 4:
                self.log("父母繁育次数已达上限。")
                return
            p = random.random()
            rank = parent1["rank"] if p < 0.495 else parent2["rank"]
            if p >= 0.99:
                rank = self.upgrade_rank(rank)
            parent1["breed_count"] += 1
            parent2["breed_count"] += 1
            child_id = f"m{len(mounts)+1}"
            child = {"id": child_id, "name": f"幼崽{child_id}", "rank": rank, "breed_count": 0}
            mounts.append(child)
            self.log(f"繁育成功，获得坐骑 {child['name']} Rank {rank}")
            win.destroy()
            self.describe()

        tk.Button(win, text="繁育", command=do_breed).grid(row=2, column=0, columnspan=2, pady=6)

    def upgrade_rank(self, rank):
        if rank not in MOUNT_RANKS:
            return rank
        idx = MOUNT_RANKS.index(rank)
        if idx + 1 < len(MOUNT_RANKS):
            return MOUNT_RANKS[idx + 1]
        return rank
    # ---------- UI windows ----------
    def show_bag(self):
        win = tk.Toplevel(self.root)
        win.title("背包")
        win.geometry("520x560")

        tabs = ttk.Notebook(win)
        tabs.pack(fill="both", expand=True, padx=6, pady=6)

        tab_attr = ttk.Frame(tabs)
        tab_relic = ttk.Frame(tabs)
        tab_mount = ttk.Frame(tabs)
        tab_material = ttk.Frame(tabs)
        tabs.add(tab_attr, text="属性/装备")
        tabs.add(tab_relic, text="收藏品")
        tabs.add(tab_mount, text="坐骑")
        tabs.add(tab_material, text="材料/碎片")

        attr_frame = ttk.LabelFrame(tab_attr, text="属性")
        attr_frame.pack(fill="x", padx=6, pady=4)
        lines = [
            f"等级 {self.player['lvl']}  经验 {self.player['exp']}/{self.player['exp_next']}",
            f"境界 {self.current_realm()['name']}  传承点 {self.player.get('legacy_points',0)}",
            f"生命 {self.player['hp']}/{self.player['max_hp']}",
            f"攻击 {self.player['atk']}",
            f"防御 {self.player['def']}",
            f"速度 {self.player['spd']}",
            f"暴击 {self.player['crit']}",
            f"抗性 {self.player['res']}",
            f"幸运 {self.player['luck']}",
            f"悟性 {self.total_insight()}",
            f"未分配点数 {self.player['free_points']}",
            f"金币 {self.player.get('gold',0)}",
            f"当前坐骑 {self.player.get('active_mount','(未装备)')}",
        ]
        for i, t in enumerate(lines):
            tk.Label(attr_frame, text=t, anchor="w").grid(row=i, column=0, sticky="w")

        equip_frame = ttk.LabelFrame(tab_attr, text="装备")
        equip_frame.pack(fill="x", padx=6, pady=4)
        slot_names = {"weapon": "武器", "armor": "护甲", "accessory": "饰品"}
        for idx, slot in enumerate(["weapon", "armor", "accessory"]):
            gear = self.player["equip"].get(slot)
            if gear:
                attrs = gear.get("attrs", [0, 0, 0, 0, 0, 0])
                stat_txt = format_attrs(attrs)
                dur = f"耐久 {gear['dur']}/{gear['max_dur']}"
                tier = gear.get("tier", "?")
                kind = gear.get("kind", "")
                kind_txt = f"{kind}·" if kind else ""
                text = f"{slot_names.get(slot, slot)}: {kind_txt}{gear['name']} {tier}品 {dur} | {stat_txt}"
            else:
                text = f"{slot_names.get(slot, slot)}: (无)"
            tk.Label(equip_frame, text=text, anchor="w").grid(row=idx, column=0, sticky="w")

        relic_frame = ttk.LabelFrame(tab_relic, text="收藏品 (可装备2件)")
        relic_frame.pack(fill="both", expand=True, padx=6, pady=4)
        relic_box = tk.Listbox(relic_frame, height=8, selectmode="browse")
        relic_box.pack(fill="both", expand=True)
        relic_ids = list(self.player["relics"].keys())
        for rid in relic_ids:
            data = self.player["relics"][rid]
            item = data["item"]
            flag = "★" * data["star"]
            eq = " (已装备)" if rid in self.player["equipped_relics"] else ""
            bonus_txt = format_bonus(relic_total_bonus(item))
            relic_box.insert("end", f"{flag} {item['name']} x{data['count']}{eq} | 加成: {bonus_txt}")

        def equip_selected():
            sel = relic_box.curselection()
            if not sel:
                return
            rid = relic_ids[sel[0]]
            if rid in self.player["equipped_relics"]:
                self.log("该收藏品已装备")
                return
            if len(self.player["equipped_relics"]) >= 2:
                self.log("最多装备2件收藏品")
                return
            self.player["equipped_relics"].append(rid)
            self.apply_relic_bonus(self.player["relics"][rid]["item"])
            self.log(f"装备收藏品 {self.player['relics'][rid]['item']['name']}")
            win.destroy()
            self.show_bag()

        def unequip_selected():
            sel = relic_box.curselection()
            if not sel:
                return
            rid = relic_ids[sel[0]]
            if rid in self.player["equipped_relics"]:
                self.player["equipped_relics"].remove(rid)
                self.log(f"卸下收藏品 {self.player['relics'][rid]['item']['name']}")
                win.destroy()
                self.show_bag()
            else:
                self.log("该收藏品未装备")

        btn_frame = tk.Frame(relic_frame)
        btn_frame.pack(fill="x")
        tk.Button(btn_frame, text="装备", command=equip_selected).pack(side="left", padx=2, pady=2)
        tk.Button(btn_frame, text="卸下", command=unequip_selected).pack(side="left", padx=2, pady=2)

        mount_eq_frame = ttk.LabelFrame(tab_mount, text="马具")
        mount_eq_frame.pack(fill="x", padx=6, pady=4)
        saddle = self.player.get("mount_equip", {}).get("saddle")
        rein = self.player.get("mount_equip", {}).get("rein")
        saddle_bonus = format_bonus(MOUNT_ITEM_BONUS.get(saddle, {})) if saddle else "无"
        rein_bonus = format_bonus(MOUNT_ITEM_BONUS.get(rein, {})) if rein else "无"
        tk.Label(
            mount_eq_frame,
            text=f"鞍具: {display_name(saddle) if saddle else '(无)'} | 加成: {saddle_bonus}",
            anchor="w",
        ).grid(row=0, column=0, sticky="w")
        tk.Label(
            mount_eq_frame,
            text=f"缰绳: {display_name(rein) if rein else '(无)'} | 加成: {rein_bonus}",
            anchor="w",
        ).grid(row=1, column=0, sticky="w")

        mount_frame = ttk.LabelFrame(tab_mount, text="坐骑")
        mount_frame.pack(fill="x", padx=6, pady=4)
        mount_list = tk.Listbox(mount_frame, height=6)
        mount_list.pack(fill="x")
        mount_ids = []
        for m in self.player["mounts"]:
            mount_list.insert("end", f"{m['name']} Rank {m['rank']} 繁育:{m['breed_count']}/4")
            mount_ids.append(m["id"])

        def equip_saddle():
            if self.player["bag"].get("灵巧鞍具", 0) <= 0:
                self.log("缺少灵巧鞍具。")
                return
            self.equip_mount_item("saddle", "灵巧鞍具")
            win.destroy()
            self.show_bag()

        def equip_rein():
            if self.player["bag"].get("疾风缰绳", 0) <= 0:
                self.log("缺少疾风缰绳。")
                return
            self.equip_mount_item("rein", "疾风缰绳")
            win.destroy()
            self.show_bag()

        btn_mount = tk.Frame(mount_frame)
        btn_mount.pack(fill="x")
        tk.Button(btn_mount, text="佩戴鞍具", command=equip_saddle).pack(side="left", padx=2, pady=2)
        tk.Button(btn_mount, text="佩戴缰绳", command=equip_rein).pack(side="left", padx=2, pady=2)
        tk.Button(btn_mount, text="切换坐骑", command=lambda: self.equip_mount_from_list(mount_list, mount_ids, win)).pack(side="left", padx=2, pady=2)

        mat_frame = ttk.LabelFrame(tab_material, text="材料/碎片")
        mat_frame.pack(fill="both", expand=True, padx=6, pady=4)
        mat_box = tk.Listbox(mat_frame, height=12)
        mat_box.pack(fill="both", expand=True)
        mats = [(k, v) for k, v in self.player["bag"].items() if is_material_item(k)]
        mats.sort(key=lambda x: x[0])
        for k, v in mats:
            mat_box.insert("end", f"{k} x{v}")

        tk.Button(win, text="关闭", command=win.destroy).pack(pady=6)

    def show_training(self):
        win = tk.Toplevel(self.root)
        win.title("养成与锻造")
        stats = (
            f"等级{self.player['lvl']} 生命 {self.player['hp']}/{self.player['max_hp']} "
            f"攻 {self.player['atk']} 防 {self.player['def']} 速 {self.player['spd']} "
            f"暴击 {self.player['crit']} 抗性 {self.player['res']} 幸运 {self.player['luck']} "
            f"自由点 {self.player['free_points']} 金币 {self.player.get('gold',0)} "
            f"悟性 {self.total_insight()} 境界 {self.current_realm()['name']} "
            f"炼丹Lv{self.player.get('alchemy_level',1)} 炼器Lv{self.player.get('refine_level',1)} "
            f"丹专精{self.player.get('alchemy_spec') or '无'} 器专精{self.player.get('refine_spec') or '无'}"
        )
        tk.Label(win, text=stats, anchor="w").grid(row=0, column=0, columnspan=3, sticky="we")

        def choose_spec():
            w = tk.Toplevel(win)
            w.title("选择专精")
            al_var = tk.StringVar(value=self.player.get("alchemy_spec") or "成丹")
            rf_var = tk.StringVar(value=self.player.get("refine_spec") or "器纹")
            tk.Label(w, text="炼丹专精").grid(row=0, column=0, sticky="w", padx=4, pady=4)
            for i, name in enumerate(ALCHEMY_SPECS.keys()):
                tk.Radiobutton(w, text=name, variable=al_var, value=name).grid(row=1, column=i, padx=4, pady=4)
            tk.Label(w, text="炼器专精").grid(row=2, column=0, sticky="w", padx=4, pady=4)
            for i, name in enumerate(REFINE_SPECS.keys()):
                tk.Radiobutton(w, text=name, variable=rf_var, value=name).grid(row=3, column=i, padx=4, pady=4)

            def apply():
                self.player["alchemy_spec"] = al_var.get()
                self.player["refine_spec"] = rf_var.get()
                w.destroy()
                win.destroy()
                self.show_training()

            tk.Button(w, text="确定", command=apply).grid(row=4, column=1, padx=4, pady=6)

        def exchange_lingshi():
            if self.player.get("gold", 0) < 100:
                self.log("金币不足，兑换灵石需要 100 金币。", "system")
                return
            self.player["gold"] -= 100
            self.player["bag"]["灵石"] = self.player["bag"].get("灵石", 0) + 1
            self.log("兑换成功：灵石 +1（消耗金币100）", "system")
            win.destroy()
            self.show_training()
        tk.Button(win, text="修理装备", command=lambda: [self.use_item("修理包"), self.describe()]).grid(row=1, column=0, sticky="we")
        tk.Button(win, text="锻造选择", command=self.show_forge_ui).grid(row=1, column=1, sticky="we")
        tk.Button(win, text="坐骑繁育", command=self.show_breed_ui).grid(row=1, column=2, sticky="we")
        tk.Button(win, text="打开商店", command=self.show_shop).grid(row=2, column=0, sticky="we")
        tk.Button(win, text="分配自由点", command=lambda: [self.allocate_points(), self.describe()]).grid(row=2, column=1, sticky="we")
        tk.Button(win, text="功法修炼", command=self.show_cultivation_ui).grid(row=2, column=2, sticky="we")
        alchemy_btn = tk.Button(win, text="炼丹/炼化", command=self.show_alchemy_ui)
        refine_btn = tk.Button(win, text="炼器", command=self.show_refine_ui)
        alchemy_btn.grid(row=3, column=0, sticky="we")
        refine_btn.grid(row=3, column=1, sticky="we")
        if not self.has_fire_affinity():
            alchemy_btn.configure(state="disabled")
            refine_btn.configure(state="disabled")
            tk.Label(win, text="缺少火属性亲和，炼丹/炼器已关闭（可通过宗门火系弟子进行内务）。", fg="#666").grid(
                row=3, column=2, sticky="w"
            )
        tk.Button(win, text="阵营/声望", command=self.show_faction_ui).grid(row=3, column=2, sticky="we")
        tk.Button(win, text="境界突破", command=self.attempt_breakthrough).grid(row=4, column=0, sticky="we")
        tk.Button(win, text="技能池", command=self.show_skill_loadout).grid(row=4, column=1, sticky="we")
        tk.Button(win, text="金币换灵石(100)", command=exchange_lingshi).grid(row=4, column=2, sticky="we")
        tk.Button(win, text="选择专精", command=choose_spec).grid(row=5, column=0, sticky="we")
        tk.Button(win, text="碎片/蓝图合成", command=self.show_fragment_ui).grid(row=6, column=0, sticky="we")
        tk.Label(win, text=f"成长建议：{self.recommend_materials()}").grid(row=6, column=1, columnspan=2, sticky="w")
        tk.Button(win, text="关闭", command=win.destroy).grid(row=6, column=2, sticky="we")

    def build_chapter_quests(self, chapter_id: str):
        story = STORY_CHAPTERS.get(chapter_id, {})
        quests = []
        for q in story.get("side", []):
            entry = dict(q)
            entry["progress"] = {k: 0 for k in q.get("targets", {})}
            entry["completed"] = False
            quests.append(entry)
        return quests

    def show_story_ui(self):
        win = tk.Toplevel(self.root)
        win.title("剧情与任务")
        chap_id = self.current_chapter.get("id") if self.current_chapter else None
        story = STORY_CHAPTERS.get(chap_id, {}) if chap_id else {}
        main = story.get("main", "暂无章节剧情。")
        tk.Label(win, text=f"主线剧情：{main}", anchor="w", justify="left", wraplength=520).pack(fill="x", padx=6, pady=4)
        tk.Label(win, text=f"成长建议：{self.recommend_materials()}", anchor="w").pack(fill="x", padx=6, pady=2)

        quest_frame = ttk.LabelFrame(win, text="支线任务")
        quest_frame.pack(fill="both", expand=True, padx=6, pady=4)
        quest_box = tk.Listbox(quest_frame, height=8, width=70)
        quest_box.pack(fill="both", expand=True)
        for q in self.active_quests:
            targets = q.get("targets", {})
            prog = q.get("progress", {})
            prog_text = " ".join([f"{k} {prog.get(k,0)}/{v}" for k, v in targets.items()])
            reward = q.get("reward", {})
            items = []
            for key, prefix in [
                ("items", ""),
                ("blueprints", "蓝图:"),
                ("method_frags", "功法碎片:"),
                ("skill_pages", "技能残页:"),
            ]:
                for entry in reward.get(key, []):
                    name = entry.get("id") if isinstance(entry, dict) else str(entry)
                    if name:
                        items.append(f"{prefix}:{name}" if prefix else name)
            item_txt = f" 物品:{'、'.join(items)}" if items else ""
            reward_text = f"奖: 金币{reward.get('gold',0)} 经验{reward.get('exp',0)}{item_txt}"
            flag = "✓" if q.get("completed") else "·"
            quest_box.insert("end", f"{flag} {q.get('name')} | {q.get('desc')} | {prog_text} | {reward_text}")

        npc_frame = ttk.LabelFrame(win, text="本章NPC")
        npc_frame.pack(fill="both", expand=True, padx=6, pady=4)
        npc_box = tk.Listbox(npc_frame, height=6, width=70)
        npc_box.pack(fill="both", expand=True)
        for npc_id in story.get("npcs", []):
            npc = STORY_NPC_BY_ID.get(npc_id, {})
            if not npc:
                continue
            skills = "、".join(npc.get("skills", []))
            npc_box.insert("end", f"{npc.get('name')}·{npc.get('title')} | {npc.get('background')} | 技能: {skills} | 物品: {npc.get('item')}")

        evt_frame = ttk.LabelFrame(win, text="剧情事件")
        evt_frame.pack(fill="both", expand=True, padx=6, pady=4)
        evt_box = tk.Listbox(evt_frame, height=5, width=70)
        evt_box.pack(fill="both", expand=True)
        for ev in story.get("events", []):
            evt_box.insert("end", ev.get("title", "未命名事件"))

        tk.Button(win, text="关闭", command=win.destroy).pack(pady=6)

    def show_skill_loadout(self):
        win = tk.Toplevel(self.root)
        win.title("技能池配置")
        skills = self.player.get("skills", [])
        loadout = set(self.player.get("skill_loadout", []))
        tk.Label(win, text="选择上阵技能（最多4个），未选择则默认全部技能。").pack(anchor="w", padx=6, pady=4)
        frame = tk.Frame(win)
        frame.pack(fill="both", expand=True, padx=6, pady=4)
        vars_by_name = {}

        for s in skills:
            name = s.get("name")
            if not name:
                continue
            var = tk.IntVar(value=1 if name in loadout else 0)
            vars_by_name[name] = var
            text = f"{name} | CD {s.get('cd_left',0)} | {s.get('effect','')}"
            tk.Checkbutton(frame, text=text, variable=var).pack(anchor="w")

        def save():
            picked = [name for name, var in vars_by_name.items() if var.get() == 1]
            if len(picked) > 4:
                messagebox.showinfo("提示", "最多选择4个技能。")
                return
            self.player["skill_loadout"] = picked
            if self.battle_hint_var:
                active = self.get_active_skills()
                total = len(self.player.get("skills", []))
                self.battle_hint_var.set(f"技能池：{len(active)}/{total}  |  策略：{self.player.get('battle_strategy','均衡')}")
            win.destroy()

        tk.Button(win, text="保存", command=save).pack(side="left", padx=6, pady=6)
        tk.Button(win, text="取消", command=win.destroy).pack(side="left", padx=6, pady=6)

    def show_fragment_ui(self):
        win = tk.Toplevel(self.root)
        win.title("碎片/蓝图合成")

        craft_defs = [
            {"name": "基础剑式", "type": "skill_pages", "need": 3, "reward": {"kind": "skill", "name": "基础剑式"}},
            {"name": "驭兽术", "type": "skill_pages", "need": 3, "reward": {"kind": "skill", "name": "驭兽术"}},
            {"name": "归墟终式", "type": "skill_pages", "need": 4, "reward": {"kind": "skill", "name": "归墟终式"}},
            {"name": "青铜秘境诀", "type": "method_frags", "need": 3, "reward": {"kind": "method", "element": "金", "tier_idx": 1}},
            {"name": "时隙回廊经", "type": "method_frags", "need": 3, "reward": {"kind": "method", "element": "时间", "tier_idx": 2}},
            {"name": "星桥护符", "type": "blueprints", "need": 2, "reward": {"kind": "gear", "id": "bp_star_charm", "name": "星桥护符", "slot": "accessory", "attrs": [6, 0, 0, 0, 1, 1]}},
            {"name": "玄火护甲", "type": "blueprints", "need": 2, "reward": {"kind": "gear", "id": "bp_fire_armor", "name": "玄火护甲", "slot": "armor", "attrs": [14, 0, 3, 0, 0, 0]}},
        ]

        listbox = tk.Listbox(win, height=10, width=70)
        listbox.pack(fill="both", expand=True, padx=6, pady=6)
        meta = []

        for c in craft_defs:
            prefix = {"skill_pages": "技能残页", "method_frags": "功法碎片", "blueprints": "装备蓝图"}[c["type"]]
            key = f"{prefix}:{c['name']}"
            owned = self.player["bag"].get(key, 0)
            missing = max(0, c["need"] - owned)
            listbox.insert("end", f"{c['name']} | 需要 {c['need']} | 拥有 {owned} | 缺 {missing}")
            meta.append(c)

        def craft():
            sel = listbox.curselection()
            if not sel:
                return
            c = meta[sel[0]]
            prefix = {"skill_pages": "技能残页", "method_frags": "功法碎片", "blueprints": "装备蓝图"}[c["type"]]
            key = f"{prefix}:{c['name']}"
            owned = self.player["bag"].get(key, 0)
            if owned < c["need"]:
                messagebox.showinfo("提示", "碎片数量不足。")
                return
            self.player["bag"][key] = owned - c["need"]
            reward = c["reward"]
            if reward["kind"] == "skill":
                self.player.setdefault("skills", []).append(
                    {"key": f"frag_{reward['name']}", "name": reward["name"], "element": self.player_main_element(), "rank": 1, "power": 1.2, "cooldown": 3, "chance": 0.3, "effect": "burn"}
                )
                self.log(f"合成技能：{reward['name']}", "system")
            elif reward["kind"] == "method":
                tier_idx = reward["tier_idx"]
                element = reward["element"]
                method = next((m for m in METHOD_CATALOG if m["element"] == element and m["tier_idx"] == tier_idx), None)
                if method:
                    self.player["cultivation"]["methods"].setdefault(method["id"], {"stage": 0, "progress": 0})
                    self.log(f"获得功法：{method['name']}", "system")
            elif reward["kind"] == "gear":
                gear = dict(reward)
                gear.pop("kind", None)
                gear.setdefault("dur", 60)
                gear.setdefault("max_dur", 60)
                self.player["bag"][gear["name"]] = self.player["bag"].get(gear["name"], 0) + 1
                self.log(f"获得装备：{gear['name']}", "system")
            win.destroy()

        tk.Button(win, text="合成", command=craft).pack(side="left", padx=6, pady=6)
        tk.Button(win, text="关闭", command=win.destroy).pack(side="left", padx=6, pady=6)

    def allocate_points(self):
        if self.player["free_points"] <= 0:
            messagebox.showinfo("提示", "没有可分配的自由点。")
            return
        win = tk.Toplevel(self.root)
        win.title(f"自由点分配（剩余 {self.player['free_points']}）")

        def add_stat(stat, amount_hp=0, amount_other=0):
            if self.player["free_points"] <= 0:
                return
            self.player["free_points"] -= 1
            if stat == "hp":
                self.player["max_hp"] += amount_hp
                self.player["hp"] += amount_hp
            else:
                self.player[stat] += amount_other
            label_points.config(text=f"剩余自由点：{self.player['free_points']}")
            label_stats.config(
                text=(
                    f"生命 {self.player['hp']}/{self.player['max_hp']}  "
                    f"攻 {self.player['atk']}  防 {self.player['def']}  "
                    f"速 {self.player['spd']}  暴击 {self.player['crit']}  抗性 {self.player['res']}  "
                    f"幸运 {self.player['luck']}"
                )
            )

        label_points = tk.Label(win, text=f"剩余自由点：{self.player['free_points']}")
        label_points.grid(row=0, column=0, columnspan=2, sticky="w")
        label_stats = tk.Label(
            win,
            text=(
                f"生命 {self.player['hp']}/{self.player['max_hp']}  "
                f"攻 {self.player['atk']}  防 {self.player['def']}  "
                f"速 {self.player['spd']}  暴击 {self.player['crit']}  抗性 {self.player['res']}  "
                f"幸运 {self.player['luck']}"
            ),
            anchor="w",
            justify="left",
        )
        label_stats.grid(row=1, column=0, columnspan=2, sticky="w")

        tk.Button(win, text="生命+5", command=lambda: add_stat("hp", amount_hp=5)).grid(row=2, column=0, sticky="we")
        tk.Button(win, text="攻击+1", command=lambda: add_stat("atk", amount_other=1)).grid(row=2, column=1, sticky="we")
        tk.Button(win, text="防御+1", command=lambda: add_stat("def", amount_other=1)).grid(row=3, column=0, sticky="we")
        tk.Button(win, text="速度+1", command=lambda: add_stat("spd", amount_other=1)).grid(row=3, column=1, sticky="we")
        tk.Button(win, text="暴击+1", command=lambda: add_stat("crit", amount_other=1)).grid(row=4, column=0, sticky="we")
        tk.Button(win, text="抗性+1", command=lambda: add_stat("res", amount_other=1)).grid(row=4, column=1, sticky="we")
        tk.Label(win, text="幸运不可用自由点提升，需靠装备/收藏品。", fg="#666").grid(row=5, column=0, columnspan=2, sticky="w")
        tk.Button(win, text="关闭", command=lambda: [win.destroy(), self.describe()]).grid(row=6, column=1, sticky="e")

    def show_cultivation_ui(self):
        win = tk.Toplevel(self.root)
        win.title("功法修炼")

        affinity_line = " ".join([f"{e}{self.player['affinity'].get(e,0)}" for e in ELEMENTS])
        insight_line = " ".join([f"{e}{self.player['insight'].get(e,0)}" for e in ELEMENTS])
        primary = self.player["cultivation"].get("primary") or "未定"
        secondary = ",".join(self.player["cultivation"].get("secondary", [])) or "无"
        tk.Label(win, text=f"亲和度: {affinity_line}").grid(row=0, column=0, columnspan=3, sticky="w")
        tk.Label(win, text=f"悟性: {insight_line} | 总悟性 {self.total_insight()}").grid(row=1, column=0, columnspan=3, sticky="w")
        suppress = f"{ELEMENT_COUNTERS.get(primary,'无')}" if primary != "未定" else "无"
        tk.Label(win, text=f"主修: {primary} | 辅修: {secondary} | 抑制: {suppress}").grid(row=2, column=0, columnspan=3, sticky="w")
        tk.Label(win, text=f"推荐：{self.recommend_cultivation()}").grid(row=3, column=0, columnspan=3, sticky="w")
        tk.Label(win, text=f"灵石: {self.player['bag'].get('灵石',0)}").grid(row=3, column=2, sticky="e")

        listbox = tk.Listbox(win, height=12, width=40)
        listbox.grid(row=4, column=0, rowspan=5, padx=4, pady=4, sticky="nsew")

        detail_var = tk.StringVar(value="请选择功法查看详情。")
        tk.Label(win, textvariable=detail_var, justify="left", anchor="nw").grid(row=4, column=1, columnspan=2, sticky="nsew")

        method_ids = []

        def stage_text(mid):
            rec = self.player["cultivation"]["methods"].get(mid, {"stage": 0, "progress": 0})
            stage_idx = rec.get("stage", 0)
            stage_name = CULTIVATION_STAGES[stage_idx]["name"]
            if stage_idx >= len(CULTIVATION_STAGES) - 1:
                return f"{stage_name} (圆满)"
            need = CULTIVATION_STAGES[stage_idx]["need"]
            return f"{stage_name} {rec.get('progress',0)}/{need}"

        def refresh_list():
            listbox.delete(0, "end")
            method_ids.clear()
            for m in METHOD_CATALOG:
                line = f"{m['name']} | {m['element']} | {m['tier']} | {stage_text(m['id'])}"
                listbox.insert("end", line)
                method_ids.append(m["id"])

        def refresh_detail():
            sel = listbox.curselection()
            if not sel:
                detail_var.set("请选择功法查看详情。")
                return
            mid = method_ids[sel[0]]
            m = METHOD_BY_ID.get(mid)
            rec = self.player["cultivation"]["methods"].get(mid, {"stage": 0, "progress": 0})
            stage_idx = rec.get("stage", 0)
            stage_name = CULTIVATION_STAGES[stage_idx]["name"]
            need = CULTIVATION_STAGES[stage_idx]["need"] if stage_idx < len(CULTIVATION_STAGES) else 0
            speed = self.cultivation_speed(m["element"])
            primary = self.player["cultivation"].get("primary")
            conflict = ""
            if primary and ELEMENT_COUNTERS.get(primary) == m["element"]:
                conflict = "冲突(高失败)"
            elif primary and ELEMENT_COUNTERS.get(m["element"]) == primary:
                conflict = "抑制(低成功)"
            branch = self.player["branch"].get(m["element"], "阳")
            stone_cost = {"黄": 1, "玄": 2, "地": 3, "天": 4, "神": 5}.get(m.get("tier", "黄"), 1)
            detail_var.set(
                "功法: {name}\n元素: {el} | 变异: {mut}\n分支: {branch}\n品阶: {tier}\n阶段: {stage}\n进度: {prog}/{need}\n修炼速度: {speed}/次\n灵石消耗: {cost}/次\n冲突: {conf}\n".format(
                    name=m["name"],
                    el=m["element"],
                    mut=m.get("mutation", "异"),
                    branch=branch,
                    tier=m["tier"],
                    stage=stage_name,
                    prog=rec.get("progress", 0),
                    need=need,
                    speed=speed,
                    cost=stone_cost,
                    conf=conflict or "无",
                )
            )

        def train_selected():
            sel = listbox.curselection()
            if not sel:
                return
            mid = method_ids[sel[0]]
            self.train_method_once(mid)
            refresh_list()
            listbox.selection_set(sel[0])
            refresh_detail()

        def set_primary():
            sel = listbox.curselection()
            if not sel:
                return
            mid = method_ids[sel[0]]
            element = METHOD_BY_ID[mid]["element"]
            self.player["cultivation"]["primary"] = element
            if element in self.player["cultivation"].get("secondary", []):
                self.player["cultivation"]["secondary"].remove(element)
            win.destroy()
            self.show_cultivation_ui()

        def toggle_secondary():
            sel = listbox.curselection()
            if not sel:
                return
            mid = method_ids[sel[0]]
            element = METHOD_BY_ID[mid]["element"]
            if element == self.player["cultivation"].get("primary"):
                return
            sec = self.player["cultivation"].get("secondary", [])
            if element in sec:
                sec.remove(element)
            else:
                if len(sec) >= 2:
                    return
                sec.append(element)
            self.player["cultivation"]["secondary"] = sec
            win.destroy()
            self.show_cultivation_ui()

        def toggle_branch():
            sel = listbox.curselection()
            if not sel:
                return
            mid = method_ids[sel[0]]
            element = METHOD_BY_ID[mid]["element"]
            cur = self.player["branch"].get(element, "阳")
            self.player["branch"][element] = "阴" if cur == "阳" else "阳"
            refresh_detail()

        listbox.bind("<<ListboxSelect>>", lambda _e: refresh_detail())

        tk.Button(win, text="修炼一次", command=train_selected).grid(row=4, column=1, sticky="we", padx=4, pady=4)
        tk.Button(win, text="设为主修", command=set_primary).grid(row=5, column=1, sticky="we", padx=4, pady=4)
        tk.Button(win, text="切换辅修", command=toggle_secondary).grid(row=6, column=1, sticky="we", padx=4, pady=4)
        tk.Button(win, text="切换分支", command=toggle_branch).grid(row=7, column=1, sticky="we", padx=4, pady=4)
        tk.Button(win, text="关闭", command=win.destroy).grid(row=7, column=2, sticky="we", padx=4, pady=4)

        win.grid_columnconfigure(1, weight=1)
        win.grid_columnconfigure(2, weight=1)
        win.grid_rowconfigure(3, weight=1)
        refresh_list()

    def show_faction_ui(self):
        win = tk.Toplevel(self.root)
        win.title("阵营与声望")
        cur = self.player.get("faction")
        cur_name = next((f["name"] for f in NATION_FACTIONS if f["id"] == cur), "未加入")
        tk.Label(win, text=f"当前阵营: {cur_name}").grid(row=0, column=0, columnspan=2, sticky="w")
        listbox = tk.Listbox(win, height=5, width=24)
        listbox.grid(row=1, column=0, padx=4, pady=4, sticky="nsew")
        faction_ids = []
        for f in NATION_FACTIONS:
            listbox.insert("end", f"{f['name']} ({f['id']})")
            faction_ids.append(f["id"])

        rep_box = tk.Listbox(win, height=5, width=30)
        rep_box.grid(row=1, column=1, padx=4, pady=4, sticky="nsew")
        for f in NATION_FACTIONS:
            rep = self.player["reputation"].get(f["id"], 0)
            rep_box.insert("end", f"{f['name']}: {rep}")

        task_var = tk.StringVar(value=self.describe_faction_task())
        tk.Label(win, textvariable=task_var, anchor="w", justify="left").grid(row=2, column=0, columnspan=2, sticky="w", padx=4)

        def join():
            if self.player.get("faction"):
                self.log("已加入阵营，无法更改。", "system")
                return
            sel = listbox.curselection()
            if not sel:
                return
            fid = faction_ids[sel[0]]
            self.player["faction"] = fid
            self.apply_faction_bonus()
            self.log(f"加入阵营：{next(f['name'] for f in NATION_FACTIONS if f['id']==fid)}")
            win.destroy()

        def accept_task():
            if not self.player.get("faction"):
                self.log("未加入阵营，无法接取任务。", "system")
                return
            self.faction_task = self.generate_faction_task()
            task_var.set(self.describe_faction_task())

        def open_shop():
            if not self.player.get("faction"):
                self.log("未加入阵营，无法访问商店。", "system")
                return
            self.show_faction_shop()

        tk.Button(win, text="加入", command=join).grid(row=3, column=0, sticky="we", padx=4, pady=4)
        tk.Button(win, text="接取/刷新任务", command=accept_task).grid(row=3, column=1, sticky="we", padx=4, pady=4)
        tk.Button(win, text="阵营商店", command=open_shop).grid(row=4, column=0, sticky="we", padx=4, pady=4)
        tk.Button(win, text="关闭", command=win.destroy).grid(row=4, column=1, sticky="we", padx=4, pady=4)

    def show_alchemy_ui(self):
        if not self.has_fire_affinity():
            self.log("缺少火属性亲和，无法炼丹（可通过宗门火系弟子进行内务）。", "system")
            return
        win = tk.Toplevel(self.root)
        win.title("炼丹与炼化")
        for key in list(self.player.get("bag", {}).keys()):
            if key.startswith("丹方:"):
                self.learn_recipe(key)
        listbox = tk.Listbox(win, height=10, width=46)
        listbox.grid(row=0, column=0, columnspan=3, padx=4, pady=4, sticky="nsew")
        bag_keys = []

        def refresh_list():
            listbox.delete(0, "end")
            bag_keys.clear()
            for key, cnt in self.player["bag"].items():
                if not key.startswith("treasure_") or cnt <= 0:
                    continue
                meta = self.treasure_meta_from_bag_key(key)
                if not meta:
                    continue
                line = f"{meta.get('name')} | {meta.get('element')} | {meta.get('rarity')} | x{cnt}"
                listbox.insert("end", line)
                bag_keys.append(key)

        def refine_one():
            sel = listbox.curselection()
            if not sel:
                return
            key = bag_keys[sel[0]]
            meta = self.treasure_meta_from_bag_key(key)
            if not meta:
                return
            self.player["bag"][key] -= 1
            if self.player["bag"][key] <= 0:
                del self.player["bag"][key]
            self.apply_treasure_bonus(meta)
            refresh_list()
            self.describe()

        def craft_pill():
            sel = listbox.curselection()
            if not sel:
                return
            key = bag_keys[sel[0]]
            meta = self.treasure_meta_from_bag_key(key)
            if not meta:
                return
            element = meta.get("element")
            same_keys = [k for k in self.player["bag"].keys() if k.startswith("treasure_")]
            total = 0
            max_tier = "黄"
            for k in same_keys:
                m = self.treasure_meta_from_bag_key(k)
                if m and m.get("element") == element:
                    total += self.player["bag"].get(k, 0)
                    if TREASURE_TIERS.index(m.get("rarity", "黄")) > TREASURE_TIERS.index(max_tier):
                        max_tier = m.get("rarity", "黄")
            if total < 3:
                self.log("同属性天材地宝不足3件，无法炼丹。", "system")
                return
            need = 3
            consumed = []
            for k in list(same_keys):
                m = self.treasure_meta_from_bag_key(k)
                if not m or m.get("element") != element:
                    continue
                take = min(self.player["bag"][k], need)
                if take > 0:
                    for _ in range(take):
                        consumed.append(m)
                self.player["bag"][k] -= take
                need -= take
                if self.player["bag"][k] <= 0:
                    del self.player["bag"][k]
                if need <= 0:
                    break
            pill_id = f"insight_pill_{element}_{max_tier}"
            success_rate = ALCHEMY_SUCCESS.get(max_tier, 0.8)
            success_rate = min(0.95, success_rate + 0.02 * (self.player.get("alchemy_level", 1) - 1))
            spec_bonus = self.alchemy_spec_bonus()
            success_rate = min(0.98, success_rate + spec_bonus.get("success", 0))
            crit_rate = ALCHEMY_CRIT.get(max_tier, 0.1) + spec_bonus.get("crit", 0)
            roll = random.random()
            if roll <= success_rate:
                count = 2 if random.random() < crit_rate else 1
                self.player["bag"][pill_id] = self.player["bag"].get(pill_id, 0) + count
                suffix = "（暴击+1）" if count == 2 else ""
                self.log(f"炼成 {display_name(pill_id)} x{count} {suffix}")
                self.gain_alchemy_exp(5)
            else:
                if consumed:
                    back = random.choice(consumed)
                    back_key = f"treasure_{back['id']}"
                    self.player["bag"][back_key] = self.player["bag"].get(back_key, 0) + 1
                self.log("炼丹失败，材料损耗。", "system")
            refresh_list()
            self.describe()

        recipe_box = tk.Listbox(win, height=8, width=46)
        recipe_box.grid(row=2, column=0, columnspan=3, padx=4, pady=4, sticky="nsew")
        recipe_keys = []

        def refresh_recipes():
            recipe_box.delete(0, "end")
            recipe_keys.clear()
            learned = set(self.player.get("recipes", []))
            for realm in BREAKTHROUGH_REALMS:
                pill = self.breakthrough_pill_name(realm).replace("破境丹·", "")
                if pill not in learned:
                    continue
                mats = [f"破境灵材·{m}" for m in self.recipe_materials(realm)]
                lvl_req = RECIPE_LEVEL_REQ.get(realm, 1)
                recipe_box.insert("end", f"破境丹·{pill} | 需求: " + "，".join(mats) + f" | 炼丹Lv{lvl_req}")
                recipe_keys.append(realm)

        def craft_break_pill():
            sel = recipe_box.curselection()
            if not sel:
                return
            realm = recipe_keys[sel[0]]
            need_level = RECIPE_LEVEL_REQ.get(realm, 1)
            if self.player.get("alchemy_level", 1) < need_level:
                self.log(f"炼丹师等级不足，需求 Lv{need_level}。", "system")
                return
            pill = self.breakthrough_pill_name(realm)
            mats = self.recipe_materials(realm)
            if not mats:
                self.log("丹方异常，缺少材料配置。", "system")
                return
            for m in mats:
                key = f"破境灵材·{m}"
                if self.player["bag"].get(key, 0) <= 0:
                    self.log("材料不足，无法炼制。", "system")
                    return
            for m in mats:
                key = f"破境灵材·{m}"
                self.player["bag"][key] -= 1
            success = 0.8 if realm in ("炼气", "筑基") else 0.65 if realm in ("金丹", "元婴") else 0.55
            success = min(0.95, success + 0.02 * (self.player.get("alchemy_level", 1) - 1))
            spec_bonus = self.alchemy_spec_bonus()
            success = min(0.98, success + spec_bonus.get("success", 0))
            crit = 0.2 if realm in ("炼气", "筑基") else 0.15 if realm in ("金丹", "元婴") else 0.1
            crit = max(0.0, crit + spec_bonus.get("crit", 0))
            if random.random() <= success:
                count = 2 if random.random() < crit else 1
                self.player["bag"][pill] = self.player["bag"].get(pill, 0) + count
                suffix = "（暴击+1）" if count == 2 else ""
                self.log(f"炼成 {pill} x{count} {suffix}", "system")
                self.gain_alchemy_exp(8)
            else:
                self.log("炼丹失败，材料损耗。", "system")
            refresh_recipes()
            self.describe()

        tk.Button(win, text="炼化(吸收)", command=refine_one).grid(row=1, column=0, sticky="we", padx=4, pady=4)
        tk.Button(win, text="炼丹(3合1)", command=craft_pill).grid(row=1, column=1, sticky="we", padx=4, pady=4)
        tk.Button(win, text="关闭", command=win.destroy).grid(row=1, column=2, sticky="we", padx=4, pady=4)
        tk.Button(win, text="炼制破境丹", command=craft_break_pill).grid(row=3, column=1, sticky="we", padx=4, pady=4)
        refresh_list()
        refresh_recipes()

    def generate_faction_task(self):
        own = self.player.get("faction")
        targets = [f["id"] for f in NATION_FACTIONS if f["id"] != own]
        target = random.choice(targets) if targets else "mo"
        tier = self.player.get("faction_task_tier", 1)
        need = random.randint(2 + tier, 4 + tier)
        reward_gold = 20 + need * 6 + tier * 8
        reward_rep = 5 + need + tier * 2
        return {"target": target, "need": need, "progress": 0, "reward_gold": reward_gold, "reward_rep": reward_rep}

    def describe_faction_task(self):
        if not self.faction_task:
            return "当前任务：无"
        t = self.faction_task
        tname = next((f["name"] for f in NATION_FACTIONS if f["id"] == t["target"]), t["target"])
        return f"当前任务：讨伐 {tname} x{t['need']}（{t['progress']}/{t['need']}）"

    def show_chapter_ui(self):
        win = tk.Toplevel(self.root)
        win.title("章节目录")
        listbox = tk.Listbox(win, height=10, width=56)
        listbox.grid(row=0, column=0, columnspan=3, padx=4, pady=4, sticky="nsew")
        for idx, chap in enumerate(self.chapters):
            status = "已通关" if idx < self.chapter_idx else ("当前" if idx == self.chapter_idx else "未解锁")
            req = chap.get("lvl_req", 1)
            realm_idx = min(idx, len(BREAKTHROUGH_REALMS) - 1)
            realm = BREAKTHROUGH_REALMS[realm_idx]
            mats = self.recipe_materials(realm)
            pill = self.breakthrough_pill_name(realm)
            mat_txt = "、".join(mats[:2]) + ("…" if len(mats) > 2 else "")
            listbox.insert("end", f"{idx+1}. {chap['name']} | 需求Lv{req} | {status} | 丹材:{mat_txt} | 丹方:{pill}")

        def enter_selected():
            sel = listbox.curselection()
            if not sel:
                return
            idx = sel[0]
            if idx > self.chapter_idx:
                self.log("该章节未解锁。", "system")
                return
            self.load_chapter(idx, force=True)
            win.destroy()

        tk.Button(win, text="进入/重玩", command=enter_selected).grid(row=1, column=0, sticky="we", padx=4, pady=4)
        tk.Button(win, text="关闭", command=win.destroy).grid(row=1, column=2, sticky="we", padx=4, pady=4)

    def show_neutral_shop(self):
        win = tk.Toplevel(self.root)
        win.title("中立商人")
        items = [
            {"id": "回复药", "price": 6, "desc": "回复40点生命"},
            {"id": "修理包", "price": 10, "desc": "修满装备耐久"},
            {"id": "武器图纸", "price": 22, "desc": "随机武器"},
            {"id": "护甲图纸", "price": 22, "desc": "随机护甲"},
            {"id": "饰品图纸", "price": 22, "desc": "随机饰品"},
            {"id": "insight_pill_金_黄", "price": 30, "desc": "金之悟性丹"},
            {"id": "insight_pill_木_黄", "price": 30, "desc": "木之悟性丹"},
            {"id": "insight_pill_水_黄", "price": 30, "desc": "水之悟性丹"},
            {"id": "insight_pill_火_黄", "price": 30, "desc": "火之悟性丹"},
            {"id": "insight_pill_土_黄", "price": 30, "desc": "土之悟性丹"},
        ]
        listbox = tk.Listbox(win, height=8, width=48)
        listbox.grid(row=0, column=0, columnspan=2, padx=4, pady=4, sticky="nsew")
        for itm in items:
            listbox.insert("end", f"{display_name(itm['id'])} | {itm['price']} 金币 | {itm['desc']}")

        def buy():
            sel = listbox.curselection()
            if not sel:
                return
            itm = items[sel[0]]
            if self.player["gold"] < itm["price"]:
                self.log("金币不足，无法购买。", "system")
                return
            self.player["gold"] -= itm["price"]
            iid = itm["id"]
            self.player["bag"][iid] = self.player["bag"].get(iid, 0) + 1
            self.log(f"购买 {display_name(iid)} x1")

        tk.Button(win, text="购买", command=buy).grid(row=1, column=0, sticky="we", padx=4, pady=4)
        tk.Button(win, text="关闭", command=win.destroy).grid(row=1, column=1, sticky="we", padx=4, pady=4)

    def show_faction_shop(self):
        win = tk.Toplevel(self.root)
        win.title("阵营商店")
        fid = self.player.get("faction")
        rep = self.player["reputation"].get(fid, 0) if fid else 0
        rep_name = next((t["name"] for t in reversed(REP_TIERS) if rep >= t["rep"]), "陌生")
        tk.Label(win, text=f"阵营声望：{rep}（{rep_name}）").grid(row=0, column=0, sticky="w")
        listbox = tk.Listbox(win, height=8, width=48)
        listbox.grid(row=1, column=0, columnspan=2, padx=4, pady=4, sticky="nsew")

        items = []
        if fid:
            items = [
                {"id": f"insight_pill_{self.player_main_element()}_玄", "price": 40, "rep_req": 10},
                {"id": f"insight_pill_{self.player_main_element()}_地", "price": 70, "rep_req": 25},
                {"id": "武器图纸", "price": 25, "rep_req": 10},
                {"id": "护甲图纸", "price": 25, "rep_req": 10},
                {"id": "饰品图纸", "price": 25, "rep_req": 10},
            ]
        for itm in items:
            listbox.insert("end", f"{display_name(itm['id'])} | 价格{itm['price']} | 需求声望{itm['rep_req']}")

        def buy():
            sel = listbox.curselection()
            if not sel:
                return
            itm = items[sel[0]]
            if rep < itm["rep_req"]:
                self.log("声望不足，无法购买。", "system")
                return
            if self.player["gold"] < itm["price"]:
                self.log("金币不足，无法购买。", "system")
                return
            self.player["gold"] -= itm["price"]
            iid = itm["id"]
            self.player["bag"][iid] = self.player["bag"].get(iid, 0) + 1
            self.log(f"购买 {display_name(iid)} x1")

        tk.Button(win, text="购买", command=buy).grid(row=2, column=0, sticky="we", padx=4, pady=4)
        tk.Button(win, text="关闭", command=win.destroy).grid(row=2, column=1, sticky="we", padx=4, pady=4)

    def show_refine_ui(self):
        if not self.has_fire_affinity():
            self.log("缺少火属性亲和，无法炼器（可通过宗门火系弟子进行内务）。", "system")
            return
        win = tk.Toplevel(self.root)
        win.title("炼器")
        tk.Label(win, text="选择装备").grid(row=0, column=0, sticky="w")
        tk.Label(win, text=f"炼器师等级: {self.player.get('refine_level',1)}").grid(row=0, column=1, sticky="e")
        gear_box = tk.Listbox(win, height=6, width=34)
        gear_box.grid(row=1, column=0, padx=4, pady=4, sticky="nsew")
        gear_slots = []
        for slot, gear in self.player["equip"].items():
            if not gear:
                continue
            name = gear.get("name", slot)
            elem = gear.get("elem", "")
            elem_txt = f"·{elem}" if elem else ""
            tier = gear.get("tier", "?")
            kind = gear.get("kind", "")
            kind_txt = f"[{kind}]" if kind else ""
            gear_box.insert("end", f"{slot}: {name}{elem_txt} {kind_txt} {tier}品")
            gear_slots.append(slot)

        tk.Label(win, text="选择灵材").grid(row=0, column=1, sticky="w")
        tre_box = tk.Listbox(win, height=6, width=34)
        tre_box.grid(row=1, column=1, padx=4, pady=4, sticky="nsew")
        tre_keys = []
        for key, cnt in self.player["bag"].items():
            if not key.startswith("treasure_") or cnt <= 0:
                continue
            meta = self.treasure_meta_from_bag_key(key)
            if not meta:
                continue
            tre_box.insert("end", f"{meta.get('name')} | {meta.get('element')} | {meta.get('rarity')} | x{cnt}")
            tre_keys.append(key)

        def refine():
            sel_g = gear_box.curselection()
            sel_t = tre_box.curselection()
            if not sel_g or not sel_t:
                return
            slot = gear_slots[sel_g[0]]
            key = tre_keys[sel_t[0]]
            meta = self.treasure_meta_from_bag_key(key)
            if not meta:
                return
            gear = self.player["equip"].get(slot)
            if not gear:
                return
            self.player["bag"][key] -= 1
            if self.player["bag"][key] <= 0:
                del self.player["bag"][key]
            self.refine_gear(gear, meta)
            self.gain_refine_exp(6)
            win.destroy()
            self.show_refine_ui()

        tk.Button(win, text="炼器", command=refine).grid(row=2, column=0, sticky="we", padx=4, pady=4)
        tk.Button(win, text="关闭", command=win.destroy).grid(row=2, column=1, sticky="we", padx=4, pady=4)

    # ---------- shop ----------
    def show_shop(self):
        win = tk.Toplevel(self.root)
        title_var = tk.StringVar(value=f"商店（金币 {self.player.get('gold',0)}）")
        win.title(title_var.get())
        tk.Label(win, text="选择商品购买：").grid(row=0, column=0, sticky="w")
        listbox = tk.Listbox(win, height=10, width=42)
        listbox.grid(row=1, column=0, columnspan=2, sticky="nsew")
        for itm in SHOP_STOCK:
            listbox.insert("end", f"{display_name(itm['id'])} - {itm['price']} 金币 | {itm.get('desc','')}")

        def refresh_title():
            title_var.set(f"商店（金币 {self.player.get('gold',0)}）")
            win.title(title_var.get())

        def buy():
            sel = listbox.curselection()
            if not sel:
                return
            itm = SHOP_STOCK[sel[0]]
            price = itm["price"]
            if self.player["gold"] < price:
                self.log(f"金币不足，购买需要 {price} 金币。")
                return
            self.player["gold"] -= price
            iid = itm["id"]
            if iid.startswith("坐骑蛋"):
                name = iid.split("坐骑蛋-")[-1]
                rank = "C" if "灰驴" in iid else "B"
                mid = f"m{len(self.player['mounts'])+1}"
                mount = {"id": mid, "name": name, "rank": rank, "breed_count": 0}
                self.player["mounts"].append(mount)
                self.log(f"购买获得坐骑：{name} Rank {rank}，花费 {price} 金币")
            elif iid == "低阶收藏品包":
                rarity = weighted_choice([("白", 60), ("绿", 30), ("蓝", 10)])
                cand = self.relic_db.get(rarity, [])
                if cand:
                    relic = dict(random.choice(cand))
                    relic["rarity_color"] = rarity
                    self.add_or_upgrade_relic(relic)
                    self.log(f"开启收藏品包，获得 {rarity} 收藏品：{relic['name']}，花费 {price} 金币")
                else:
                    self.log("收藏品库为空，未获得物品。")
            else:
                self.player["bag"][iid] = self.player["bag"].get(iid, 0) + 1
                self.log(f"购买 {display_name(iid)} x1，花费 {price} 金币，剩余 {self.player['gold']}")
            refresh_title()

        tk.Button(win, text="购买", command=lambda: [buy(), self.describe()]).grid(row=2, column=0, sticky="we")
        tk.Button(win, text="关闭", command=win.destroy).grid(row=2, column=1, sticky="we")


def main():
    root = tk.Tk()
    root.rowconfigure(0, weight=1)
    root.columnconfigure(0, weight=1)
    GameUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()











