package com.jinhui.immortaldemo.core

data class Pos(val x: Int, val y: Int)

data class Enemy(
    val name: String,
    var hp: Int,
    val maxHp: Int,
    val atk: Int,
    val def: Int,
    val spd: Int,
    val exp: Int,
    val gold: Int,
)

data class SkillState(
    val id: String,
    val name: String,
    val ratio: Double,
    val cdMax: Int,
    var cdNow: Int = 0,
    val effect: String = "",
)

data class ShopItem(
    val id: String,
    val price: Int,
    val desc: String = "",
    val rarity: String = "白",
    val minChapter: Int = 0,
)

data class TalentState(
    val id: String,
    val name: String,
    val tier: Int,
    val hp: Int = 0,
    val atk: Int = 0,
    val def: Int = 0,
    val spd: Int = 0,
    val luck: Int = 0,
)

data class MethodState(
    val id: String,
    val name: String,
    val element: String,
    var stage: Int = 0,
    var progress: Int = 0,
    var need: Int = 12,
)

data class NpcState(
    val id: String,
    var name: String,
    var faction: String,
    var background: String = "",
    var goal: String = "",
    var relation: Int = 0,
    var mood: String = "平静",
    var hint: String = "不引导",
    var hostile: Boolean = false,
    var follow: Boolean = false,
    var alive: Boolean = true,
    var isLegacyEcho: Boolean = false,
    var lifeIdRef: Int = 0,
    var noRespawn: Boolean = false,
    var combatPower: Int = 24,
    var lootItem: String = "",
    var lastReply: String = "",
    val memory: MutableList<String> = mutableListOf(),
)

data class CollectibleState(
    val id: String,
    val name: String,
    val rarity: String,
    var level: Int = 1,
    val hp: Int = 0,
    val atk: Int = 0,
    val def: Int = 0,
    val spd: Int = 0,
)

data class CollectibleAtlasEntry(
    val id: String,
    val name: String,
    val rarity: String,
    val ownedLevel: Int = 0,
)

data class EquipmentState(
    val id: String,
    val name: String,
    val slot: String,
    val tier: Int,
    val atk: Int = 0,
    val def: Int = 0,
    val spd: Int = 0,
    var durability: Int = 80,
    var maxDurability: Int = 80,
)

data class BlueprintState(
    val id: String,
    val name: String,
    val slot: String,
    val tier: Int,
    val atk: Int = 0,
    val def: Int = 0,
    val spd: Int = 0,
    val materials: Map<String, Int> = emptyMap(),
)

data class DiscipleState(
    var name: String,
    var level: Int,
    var apt: Int,
    var alive: Boolean = true,
    var atkBonus: Int = 0,
    var defBonus: Int = 0,
    var spdBonus: Int = 0,
    var equippedTag: String = "",
    var lifeGuardRelic: String = "",
    var relicCharges: Int = 0,
)

data class SectState(
    var created: Boolean = false,
    var name: String = "",
    var month: Int = 0,
    var spiritField: Int = 1,
    var mine: Int = 0,
    var library: Int = 0,
    var defense: Int = 0,
    var lastAutoMonth: Int = -1,
    var lingshi: Int = 0,
    var herb: Int = 0,
    var ore: Int = 0,
    val vault: MutableMap<String, Int> = mutableMapOf(),
    val uniqueRelics: MutableMap<String, Int> = mutableMapOf(),
    val disciples: MutableList<DiscipleState> = mutableListOf(),
)

data class PlayerState(
    var name: String = "旅者",
    var lifeId: Int = 1,
    var level: Int = 1,
    var exp: Int = 0,
    var expNext: Int = 30,
    var hp: Int = 120,
    var maxHp: Int = 120,
    var atk: Int = 14,
    var def: Int = 6,
    var spd: Int = 8,
    var gold: Int = 50,
    var lingshi: Int = 0,
    var freePoints: Int = 0,
    var timeTick: Int = 0,
    var ageMonths: Int = 0,
    var lifespanMonths: Int = 246,
    var realmIdx: Int = 0,
    var isDead: Boolean = false,
    var deathCount: Int = 0,
    var factionRepHuman: Int = 0,
    var factionRepYao: Int = 0,
    var factionRepMo: Int = 0,
    var factionRepXian: Int = 0,
    var gearLevel: Int = 0,
    var legacyForgeAtkBonus: Int = 0,
    var legacyForgeDefBonus: Int = 0,
    var gearAtkBonus: Int = 0,
    var gearDefBonus: Int = 0,
    var mountName: String = "",
    var mountSpdBonus: Int = 0,
    var luck: Int = 0,
    var collectibleName: String = "",
    var collectibleHpBonus: Int = 0,
    var collectibleAtkBonus: Int = 0,
    var collectibleDefBonus: Int = 0,
    var collectibleSpdBonus: Int = 0,
    val bag: MutableMap<String, Int> = mutableMapOf(),
    val methods: MutableList<MethodState> = mutableListOf(),
    val skills: MutableList<SkillState> = mutableListOf(),
    val talents: MutableList<TalentState> = mutableListOf(),
    val collectibles: MutableList<CollectibleState> = mutableListOf(),
    val equipments: MutableMap<String, EquipmentState> = mutableMapOf(),
    val knownBlueprints: MutableSet<String> = mutableSetOf(),
    var kills: Int = 0,
)

data class Maze(
    val width: Int,
    val height: Int,
    val start: Pos,
    val exit: Pos,
    val blocks: Set<Pos>,
)

data class MiniMapSnapshot(
    val width: Int,
    val height: Int,
    val player: Pos,
    val exit: Pos,
    val blocks: List<Pos>,
    val explored: List<Pos> = emptyList(),
    val visible: List<Pos> = emptyList(),
    val boss: Pos? = null,
    val mount: Pos? = null,
    val treasure: Pos? = null,
)

data class ChapterState(
    var idx: Int = 0,
    var battles: Int = 0,
    var battleTarget: Int = 6,
    var questTalk: Int = 0,
    var questTalkTarget: Int = 1,
)

data class ChapterDef(
    val id: String,
    val name: String,
    val width: Int,
    val height: Int,
    val battleTarget: Int,
    val enemyScale: Double,
)

data class GameState(
    var maze: Maze,
    var pos: Pos,
    val player: PlayerState,
    val chapter: ChapterState = ChapterState(),
    val sect: SectState = SectState(),
    val log: ArrayDeque<String> = ArrayDeque(),
)
