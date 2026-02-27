package com.jinhui.immortaldemo.core

import org.json.JSONArray
import org.json.JSONObject
import kotlin.math.max
import kotlin.math.min
import kotlin.random.Random

class GameCore(seed: Int = 2026) {
    private data class CollectibleTemplate(
        val id: String,
        val name: String,
        val rarity: String,
        val hp: Int,
        val atk: Int,
        val def: Int,
        val spd: Int,
    )

    private val rng = Random(seed)
    private val realms = listOf("练气", "筑基", "金丹", "元婴", "化神", "合体", "渡劫", "大乘", "真仙", "天仙")

    private val chapters = listOf(
        ChapterDef("ch1", "矿道新手", 30, 30, 6, 1.0),
        ChapterDef("ch2", "青铜秘境", 32, 32, 8, 1.15),
        ChapterDef("ch3", "荒土猎影", 34, 34, 10, 1.3),
        ChapterDef("ch4", "星桥守关", 36, 36, 12, 1.45),
        ChapterDef("ch5", "风砂古道", 38, 38, 14, 1.6),
        ChapterDef("ch6", "寒渊回廊", 40, 40, 16, 1.8),
        ChapterDef("ch7", "暗域裂谷", 42, 42, 18, 2.0),
        ChapterDef("ch8", "禁庭废都", 44, 44, 20, 2.2),
        ChapterDef("ch9", "时隙回廊", 46, 46, 22, 2.4),
        ChapterDef("ch10", "星骸终局", 48, 48, 24, 2.7),
    )

    private val npcs = mutableListOf(
        NpcState("npc_fengyin", "风吟", "中立", background = "行走江湖的游侠，见多识广。", goal = "寻找失散同伴。", relation = 5),
        NpcState("npc_tieshuo", "铁烁", "人族", background = "矿区守备，寡言但守信。", goal = "守住矿脉与工匠村。"),
        NpcState("npc_shuangheng", "霜蘅", "妖族", background = "寒渊狐妖，擅幻术与追踪。", goal = "夺回被封印的祖器。"),
        NpcState("npc_yance", "焱策", "仙族", background = "仙门外放执事，重视秩序。", goal = "筛选可入门的修士。"),
        NpcState("npc_yanxing", "魇行", "魔族", background = "暗域斥候，善于探查弱点。", goal = "收集各宗门情报。"),
    )
    private val discipleSurnames = listOf(
        "赵", "钱", "孙", "李", "周", "吴", "郑", "王", "冯", "陈", "褚", "卫", "蒋", "沈", "韩", "杨",
        "朱", "秦", "尤", "许", "何", "吕", "施", "张", "孔", "曹", "严", "华", "金", "魏", "陶", "姜",
        "戚", "谢", "邹", "喻", "柏", "水", "窦", "章", "云", "苏", "潘", "葛", "奚", "范", "彭", "郎",
        "鲁", "韦", "昌", "马", "苗", "凤", "花", "方", "俞", "任", "袁", "柳", "酆", "鲍", "史", "唐",
        "费", "廉", "岑", "薛", "雷", "贺", "倪", "汤", "滕", "殷", "罗", "毕", "郝", "邬", "安", "常",
        "乐", "于", "时", "傅", "皮", "卞", "齐", "康", "伍", "余", "元", "卜", "顾", "孟", "平", "黄",
        "和", "穆", "萧", "尹", "姚", "邵", "湛", "汪", "祁", "毛", "禹", "狄", "米", "贝", "明", "臧",
        "欧阳", "司马", "上官", "诸葛", "东方", "独孤", "夏侯", "慕容", "公孙", "司徒"
    )
    private val discipleGivenChars = listOf(
        "子", "一", "云", "天", "玄", "青", "白", "赤", "寒", "星", "月", "风", "雨", "雷", "霜", "雪",
        "川", "海", "山", "河", "松", "竹", "兰", "若", "安", "宁", "和", "清", "灵", "渊", "衡", "然",
        "尘", "璃", "瑶", "岚", "歌", "羽", "辰", "景", "川", "峥", "岳", "衡", "芷", "瑾", "瑜", "珩"
    )
    private val talentPool = buildTalentPool()
    private val shopStock = listOf(
        ShopItem("回复药", 5, "恢复40点生命", rarity = "白"),
        ShopItem("修理包", 8, "立即修满装备耐久", rarity = "绿"),
        ShopItem("武器图纸", 18, "用于锻造随机武器", rarity = "绿"),
        ShopItem("护甲图纸", 18, "用于锻造随机护甲", rarity = "绿"),
        ShopItem("饰品图纸", 18, "用于锻造随机饰品", rarity = "绿"),
        ShopItem("精铁矿", 6, "初阶锻造材料", rarity = "白"),
        ShopItem("赤铁矿", 7, "偏攻锻材", rarity = "绿"),
        ShopItem("青铜矿", 7, "器胚锻材", rarity = "绿"),
        ShopItem("灵巧兽皮", 6, "护甲锻造材料", rarity = "白"),
        ShopItem("灵核碎片", 10, "饰品锻造材料", rarity = "蓝"),
        ShopItem("basic_sword", 25, "基础武器箱", rarity = "绿"),
        ShopItem("basic_armor", 25, "基础护甲箱", rarity = "绿"),
        ShopItem("灵巧鞍具", 28, "坐骑鞍具", rarity = "蓝"),
        ShopItem("疾风缰绳", 30, "坐骑缰绳", rarity = "蓝"),
        ShopItem("坐骑蛋-灰驴", 30, "随机获得C级坐骑（灰驴）", rarity = "绿"),
        ShopItem("坐骑蛋-青羽", 40, "随机获得B级坐骑（青羽鸟）", rarity = "蓝"),
        ShopItem("低阶收藏品包", 45, "开出白/绿/蓝收藏品", rarity = "紫"),
        ShopItem("insight_pill_金_黄", 28, "提升金之悟性", rarity = "金"),
        ShopItem("insight_pill_木_黄", 28, "提升木之悟性", rarity = "金"),
        ShopItem("insight_pill_水_黄", 28, "提升水之悟性", rarity = "金"),
        ShopItem("insight_pill_火_黄", 28, "提升火之悟性", rarity = "金"),
        ShopItem("insight_pill_土_黄", 28, "提升土之悟性", rarity = "金"),
        ShopItem("insight_pill_时间_黄", 36, "提升时间悟性", rarity = "金"),
        ShopItem("insight_pill_空间_黄", 36, "提升空间悟性", rarity = "金"),
        ShopItem("灵石", 120, "基础修炼资源", rarity = "蓝"),
        ShopItem("基础锻造箱", 160, "可研习蓝图", rarity = "紫"),
    )
    private val equipmentSlots = listOf("weapon", "head", "body", "boots", "accessory")
    private val slotName = mapOf(
        "weapon" to "武器",
        "head" to "头冠",
        "body" to "护甲",
        "boots" to "身法",
        "accessory" to "饰品",
    )
    private val blueprintCatalog = buildBlueprintCatalog()

    val state: GameState = GameState(
        maze = generateMaze(chapters[0].width, chapters[0].height),
        pos = Pos(1, chapters[0].height - 2),
        player = PlayerState(),
    )

    private var moveTick = 0
    private var secretMode = false
    private var npcInferenceProvider: NpcInferenceProvider? = null
    private var npcLastRaw = ""
    private var npcLastError = ""
    private var lastBattleSummary = "暂无战斗"
    private val collectibleTemplatesByRarity = mutableMapOf<String, MutableList<CollectibleTemplate>>()
    private val usedLifeIds = mutableSetOf<Int>()
    private val deadLifeIds = mutableSetOf<Int>()
    private var nextLifeId = 2
    private var bossMarkerPos: Pos? = null
    private var mountMarkerPos: Pos? = null
    private var treasureMarkerPos: Pos? = null
    private val exploredCells = mutableSetOf<Pos>()
    private val miniMapSpan = 4

    init {
        ensurePlayerSystems()
        initDefaultCollectibleCatalog()
        initTalentsForNewLife()
        initStarterBlueprints()
        usedLifeIds.add(state.player.lifeId)
        nextLifeId = state.player.lifeId + 1
        loadChapter(0)
        appendOpeningStory("start")
    }

    fun infoText(): String {
        val p = state.pos
        val pl = state.player
        val chap = chapters[state.chapter.idx]
        val realm = realms[pl.realmIdx.coerceIn(0, realms.size - 1)]
        val sectTag = if (state.sect.created) "| 宗门:${state.sect.name} 月${state.sect.month}" else "| 未建宗门"
        val deadTag = if (pl.isDead) "| 已死亡" else ""
        val mountTag = if (pl.mountName.isBlank()) "无坐骑" else pl.mountName
        val modeTag = if (secretMode) "秘境" else "章节"
        val equippedCount = pl.equipments.values.count { it.durability > 0 }
        return "${pl.name}#${pl.lifeId} 坐标(${p.x},${p.y}) | Lv${pl.level} ${realm} | 经验 ${pl.exp}/${pl.expNext} | 生命 ${pl.hp}/${pl.maxHp} | 金币 ${pl.gold} | 灵石 ${pl.lingshi} | 自由点 ${pl.freePoints} | 月${currentMonth()} 寿命${pl.ageMonths}/${pl.lifespanMonths} | ${chap.name} ${state.chapter.battles}/${state.chapter.battleTarget} | 对话 ${state.chapter.questTalk}/${state.chapter.questTalkTarget} | 装备+${pl.gearAtkBonus}/${pl.gearDefBonus} | 装备槽${equippedCount}/${equipmentSlots.size} 蓝图${pl.knownBlueprints.size}/${blueprintCatalog.size} | 坐骑:${mountTag} | 天赋${pl.talents.size} 收藏${pl.collectibles.size} | 模式:${modeTag} ${sectTag} ${deadTag}"
    }

    fun battleHudText(): String {
        val pl = state.player
        val chapter = state.chapter
        return "你 HP ${pl.hp}/${pl.maxHp} | 攻${pl.atk + pl.gearAtkBonus} 防${pl.def + pl.gearDefBonus} 速${pl.spd + gearSpdBonus() + pl.mountSpdBonus}\n最近战斗: $lastBattleSummary\n章节战斗进度: ${chapter.battles}/${chapter.battleTarget}"
    }

    fun mapHintText(): String {
        val visible = visibleCellsAt(state.pos)
        val hints = mutableListOf<String>()
        hints.add("出口方向:${directionHint(state.pos, state.maze.exit)}")
        bossMarkerPos?.takeIf { visible.contains(it) }?.let { hints.add("首领方向:${directionHint(state.pos, it)}") }
        mountMarkerPos?.takeIf { visible.contains(it) }?.let { hints.add("坐骑方向:${directionHint(state.pos, it)}") }
        treasureMarkerPos?.takeIf { visible.contains(it) }?.let { hints.add("宝材方向:${directionHint(state.pos, it)}") }
        return hints.joinToString(" | ")
    }

    fun miniMapSnapshot(): MiniMapSnapshot {
        val visible = visibleCellsAt(state.pos)
        return MiniMapSnapshot(
            width = state.maze.width,
            height = state.maze.height,
            player = state.pos,
            exit = state.maze.exit,
            blocks = state.maze.blocks.toList(),
            explored = emptyList(),
            visible = visible.toList(),
            boss = bossMarkerPos,
            mount = mountMarkerPos,
            treasure = treasureMarkerPos,
        )
    }

    fun move(dx: Int, dy: Int) {
        if (!ensureAlive()) return
        val nx = state.pos.x + dx
        val ny = state.pos.y + dy
        val next = Pos(nx, ny)
        if (!canWalk(next)) {
            log("前方受阻，无法通行")
            return
        }
        state.pos = next
        revealAroundCurrentPos()
        moveTick += 1
        log("移动到 (${nx}, ${ny})")
        if (moveTick % 2 == 0) {
            applyDurabilityLoss("boots", 1)
        }
        advanceTime(1)
        if (state.player.isDead) return

        val markerTriggered = triggerMapMarkersIfNeeded()
        if (!markerTriggered) {
            val battleRate = if (secretMode) 0.52 else 0.32
            if (rng.nextDouble() < battleRate) {
                battle(randomEnemy())
            } else if (rng.nextDouble() < 0.08) {
                triggerNpcEncounter()
            }
        }

        if (state.pos == state.maze.exit) {
            log("到达出口。完成目标后可前往下一章")
        }
    }

    fun chapterList(): List<String> {
        return chapters.mapIndexed { i, c ->
            val status = when {
                i < state.chapter.idx -> "已通关"
                i == state.chapter.idx -> "当前"
                else -> "未解锁"
            }
            val talkNeed = 1 + (i / 3)
            "第${i + 1}章 ${c.name} | 目标${c.battleTarget}战+对话${talkNeed}次 | ${status}"
        }
    }

    fun questStatus(): String {
        val c = state.chapter
        val battleDone = c.battles >= c.battleTarget
        val talkDone = c.questTalk >= c.questTalkTarget
        return "任务进度: 战斗 ${c.battles}/${c.battleTarget} ${if (battleDone) "已完成" else "未完成"} | 对话 ${c.questTalk}/${c.questTalkTarget} ${if (talkDone) "已完成" else "未完成"}"
    }

    fun canAdvanceChapter(): Boolean {
        val c = state.chapter
        return c.battles >= c.battleTarget && c.questTalk >= c.questTalkTarget && state.pos == state.maze.exit
    }

    fun advanceChapter(): Boolean {
        if (!ensureAlive()) return false
        val next = state.chapter.idx + 1
        if (next >= chapters.size) {
            log("已到终章")
            return false
        }
        if (!canAdvanceChapter()) {
            log("需要完成本章战斗/对话目标并抵达出口")
            return false
        }
        loadChapter(next)
        return true
    }

    fun bagItems(): List<Pair<String, Int>> {
        return state.player.bag.entries.sortedBy { it.key }.map { it.key to it.value }
    }

    fun useItem(itemId: String): Boolean {
        if (!ensureAlive()) return false
        val bag = state.player.bag
        val have = bag[itemId] ?: 0
        if (have <= 0) {
            log("物品不足: ${displayItemName(itemId)}")
            return false
        }
        val pl = state.player
        val used = when (itemId) {
            "回复药", "回春药" -> {
                pl.hp = min(pl.maxHp, pl.hp + 40)
                log("使用${itemId}，恢复40生命")
                true
            }
            "修理包" -> {
                repairAllEquipment()
            }
            "灵巧鞍具" -> {
                pl.maxHp += 10
                pl.hp = min(pl.maxHp, pl.hp + 10)
                pl.def += 2
                log("使用灵巧鞍具，生命+10 防御+2")
                true
            }
            "疾风缰绳" -> {
                pl.spd += 3
                log("使用疾风缰绳，速度+3")
                true
            }
            "基础锻造箱" -> {
                learnBlueprintFromBox()
            }
            "低阶收藏品包" -> {
                openLowCollectiblePack()
            }
            "武器图纸", "护甲图纸", "饰品图纸", "basic_sword", "basic_armor" -> {
                addItem("基础锻造箱", 1)
                log("图纸已折算为基础锻造箱 x1")
                true
            }
            "灵石" -> {
                log("灵石用于修炼/突破/炼丹")
                false
            }
            else -> {
                if (itemId.startsWith("insight_pill_")) {
                    useInsightPill(itemId)
                } else {
                    log("当前不可使用: ${displayItemName(itemId)}")
                    false
                }
            }
        }
        if (used) {
            if (have == 1) bag.remove(itemId) else bag[itemId] = have - 1
        }
        return used
    }

    fun cultivate(): Boolean {
        if (!ensureAlive()) return false
        val pl = state.player
        if (pl.lingshi <= 0) {
            log("灵石不足，无法修炼")
            return false
        }
        pl.lingshi -= 1
        val gain = 5 + pl.realmIdx * 2
        addExp(gain)
        log("修炼完成，经验 +$gain")
        return true
    }

    fun pointSummary(): String {
        val pl = state.player
        return "剩余自由点 ${pl.freePoints}\n生命 ${pl.maxHp}\n攻击 ${pl.atk}\n防御 ${pl.def}\n速度 ${pl.spd}\n幸运 ${pl.luck}"
    }

    fun allocatePlayerPoint(stat: String): Boolean {
        if (!ensureAlive()) return false
        val pl = state.player
        if (pl.freePoints <= 0) {
            log("没有可分配自由点")
            return false
        }
        when (stat) {
            "hp" -> {
                pl.maxHp += 12
                pl.hp += 12
            }
            "atk" -> pl.atk += 1
            "def" -> pl.def += 1
            "spd" -> pl.spd += 1
            "luck" -> pl.luck += 1
            else -> return false
        }
        pl.freePoints -= 1
        log("分配自由点：$stat（剩余 ${pl.freePoints}）")
        return true
    }

    fun exchangeLingshi(): Boolean {
        if (!ensureAlive()) return false
        val pl = state.player
        if (pl.gold < 100) {
            log("金币不足，无法兑换")
            return false
        }
        pl.gold -= 100
        pl.lingshi += 1
        log("金币兑换灵石 x1")
        return true
    }

    fun shopCatalog(): List<Pair<String, Int>> {
        return shopCatalogDetailed().map { it.id to it.price }
    }

    fun shopCatalogDetailed(): List<ShopItem> {
        val chap = state.chapter.idx
        return shopStock.filter { chap >= it.minChapter }
    }

    fun displayItemName(itemId: String): String {
        val fixed = mapOf(
            "basic_sword" to "基础武器箱",
            "basic_armor" to "基础护甲箱",
        )
        fixed[itemId]?.let { return it }
        if (itemId.startsWith("insight_pill_")) {
            val parts = itemId.split("_")
            if (parts.size >= 4) {
                val element = parts[2]
                val tier = parts[3]
                return "${element}悟性丹·${tier}"
            }
        }
        if (itemId.startsWith("坐骑:")) {
            return "坐骑契约·${itemId.removePrefix("坐骑:")}"
        }
        if (itemId.startsWith("treasure_")) {
            return "天材地宝·${itemId.removePrefix("treasure_").replace('_', '·')}"
        }
        return itemId
    }

    fun rarityOfItem(itemId: String): String {
        shopStock.firstOrNull { it.id == itemId }?.let { return it.rarity }
        return when {
            itemId.startsWith("坐骑:") -> "蓝"
            itemId.startsWith("insight_pill_") -> "金"
            itemId.startsWith("treasure_") -> "紫"
            itemId == "护宗灵印" -> "红"
            itemId == "星骸粉" -> "红"
            itemId == "时纹石" -> "金"
            itemId == "天火砂" || itemId == "幽晶" -> "紫"
            itemId == "星砂" || itemId == "冰魄" || itemId == "玄铁" -> "蓝"
            itemId == "赤砂" || itemId == "寒露" -> "绿"
            itemId == "灵草" || itemId == "精铁矿" || itemId == "灵巧兽皮" -> "白"
            itemId.contains("图纸") || itemId.contains("蓝图") -> "绿"
            itemId.contains("收藏品") || itemId.contains("残卷") -> "紫"
            itemId.contains("灵核") -> "蓝"
            itemId.contains("破境") -> "金"
            else -> "白"
        }
    }

    fun rarityBadge(itemId: String): String {
        val rarity = rarityOfItem(itemId)
        return rarityBadgeByRarity(rarity)
    }

    fun rarityBadgeByRarity(rarity: String): String {
        val icon = when (rarity) {
            "白" -> "⬜"
            "绿" -> "🟩"
            "蓝" -> "🟦"
            "紫" -> "🟪"
            "金" -> "🟨"
            "红" -> "🟥"
            else -> "⬛"
        }
        return "$icon[$rarity]"
    }

    fun buyFromShop(itemId: String, price: Int): Boolean {
        if (!ensureAlive()) return false
        val pl = state.player
        if (pl.gold < price) {
            log("金币不足，购买失败")
            return false
        }
        val stockItem = shopCatalogDetailed().find { it.id == itemId }
        val realPrice = stockItem?.price ?: price
        if (pl.gold < realPrice) {
            log("金币不足，购买失败")
            return false
        }
        pl.gold -= realPrice
        when {
            itemId.startsWith("坐骑蛋-") -> {
                val name = itemId.removePrefix("坐骑蛋-")
                addItem("坐骑:$name", 1)
                log("商店购买成功: ${displayItemName(itemId)} (-$realPrice 金币)")
            }
            itemId == "低阶收藏品包" -> {
                openLowCollectiblePack()
                log("商店购买成功: ${displayItemName(itemId)} (-$realPrice 金币)")
            }
            else -> {
                addItem(itemId, 1)
                log("商店购买成功: ${displayItemName(itemId)} (-$realPrice 金币)")
            }
        }
        return true
    }

    fun equipmentSummaryLines(): List<String> {
        val pl = state.player
        return equipmentSlots.map { slot ->
            val eq = pl.equipments[slot]
            if (eq == null) {
                "${slotLabel(slot)}: 空"
            } else {
                val tier = tierName(eq.tier)
                val status = if (eq.durability > 0) "可用" else "损坏"
                "${slotLabel(slot)}: ${eq.name} [$tier] 攻+${eq.atk} 防+${eq.def} 速+${eq.spd} 耐久${eq.durability}/${eq.maxDurability} $status"
            }
        }
    }

    fun blueprintStatusLines(learnedOnly: Boolean = false): List<String> {
        val known = state.player.knownBlueprints
        val list = if (learnedOnly) {
            blueprintCatalog.filter { known.contains(it.id) }
        } else {
            blueprintCatalog
        }
        return list.map { bp ->
            val stateText = if (known.contains(bp.id)) "已掌握" else "未掌握"
            val mats = bp.materials.entries.joinToString(" ") { "${it.key}x${it.value}" }
            "${bp.name} | ${slotLabel(bp.slot)} ${tierName(bp.tier)} | 攻+${bp.atk} 防+${bp.def} 速+${bp.spd} | $mats | $stateText"
        }
    }

    fun knownBlueprintIds(): List<String> {
        return blueprintCatalog.filter { state.player.knownBlueprints.contains(it.id) }.map { it.id }
    }

    fun blueprintLabel(blueprintId: String): String {
        val bp = blueprintCatalog.find { it.id == blueprintId } ?: return blueprintId
        val mats = bp.materials.entries.joinToString(" ") { "${it.key}x${it.value}" }
        return "${bp.name} | ${slotLabel(bp.slot)} ${tierName(bp.tier)} | $mats"
    }

    fun learnBlueprintFromBox(): Boolean {
        if (!ensureAlive()) return false
        val bag = state.player.bag
        val have = bag["基础锻造箱"] ?: 0
        if (have <= 0) {
            log("缺少基础锻造箱，无法研习蓝图")
            return false
        }
        val maxTier = min(4, state.chapter.idx / 2 + 1)
        val known = state.player.knownBlueprints
        val candidates = blueprintCatalog.filter { bp ->
            if (known.contains(bp.id) || bp.tier > maxTier) return@filter false
            if (bp.tier == 0) return@filter true
            val prev = blueprintCatalog.find { it.slot == bp.slot && it.tier == bp.tier - 1 } ?: return@filter false
            known.contains(prev.id)
        }
        if (candidates.isEmpty()) {
            log("当前章节暂无可研习新蓝图")
            return false
        }
        val picked = candidates.random(rng)
        if (have == 1) bag.remove("基础锻造箱") else bag["基础锻造箱"] = have - 1
        known.add(picked.id)
        log("研习成功：掌握蓝图 ${picked.name}")
        return true
    }

    fun craftFromBlueprint(blueprintId: String): Boolean {
        if (!ensureAlive()) return false
        val bp = blueprintCatalog.find { it.id == blueprintId }
        if (bp == null) {
            log("蓝图不存在")
            return false
        }
        val pl = state.player
        if (!pl.knownBlueprints.contains(bp.id)) {
            log("未掌握该蓝图")
            return false
        }
        if (bp.tier > 0) {
            val equipped = pl.equipments[bp.slot]
            if (equipped == null || equipped.tier < bp.tier - 1) {
                log("打造 ${bp.name} 需要先装备同部位上一阶器胚")
                return false
            }
        }
        val missing = bp.materials.entries.firstOrNull { (k, v) -> (pl.bag[k] ?: 0) < v }
        if (missing != null) {
            log("材料不足：${missing.key} 需要 ${missing.value}")
            return false
        }
        val lingshiCost = 1 + bp.tier
        if (pl.lingshi < lingshiCost) {
            log("灵石不足，打造需要 $lingshiCost")
            return false
        }
        bp.materials.forEach { (k, v) ->
            val left = (pl.bag[k] ?: 0) - v
            if (left <= 0) pl.bag.remove(k) else pl.bag[k] = left
        }
        pl.lingshi -= lingshiCost
        val maxDura = 70 + bp.tier * 30
        pl.equipments[bp.slot] = EquipmentState(
            id = "eq_${bp.id}_${pl.level}_${rng.nextInt(1000, 9999)}",
            name = bp.name,
            slot = bp.slot,
            tier = bp.tier,
            atk = bp.atk,
            def = bp.def,
            spd = bp.spd,
            durability = maxDura,
            maxDurability = maxDura,
        )
        refreshGearBonuses()
        log("打造完成：${bp.name}（${slotLabel(bp.slot)} ${tierName(bp.tier)}）")
        return true
    }

    fun repairAllEquipment(): Boolean {
        if (!ensureAlive()) return false
        val slots = equipmentSlots.filter { state.player.equipments[it] != null }
        if (slots.isEmpty()) {
            log("当前没有可修理装备")
            return false
        }
        var repaired = 0
        slots.forEach {
            if (repairEquipment(it, silent = true)) repaired += 1
        }
        if (repaired <= 0) {
            log("修理失败：材料或金币不足")
            return false
        }
        refreshGearBonuses()
        log("完成修理：$repaired 件装备恢复耐久")
        return true
    }

    fun repairEquipment(slot: String): Boolean {
        return repairEquipment(slot, silent = false)
    }

    fun forgeOnce(): Boolean {
        if (!ensureAlive()) return false
        val pl = state.player
        val bag = pl.bag
        val hasMat = listOf("玄铁", "星砂", "天火砂", "时纹石").any { (bag[it] ?: 0) > 0 }
        if (!hasMat) {
            log("缺少矿材，无法淬炼")
            return false
        }
        when {
            (bag["时纹石"] ?: 0) > 0 -> bag["时纹石"] = (bag["时纹石"] ?: 1) - 1
            (bag["天火砂"] ?: 0) > 0 -> bag["天火砂"] = (bag["天火砂"] ?: 1) - 1
            (bag["星砂"] ?: 0) > 0 -> bag["星砂"] = (bag["星砂"] ?: 1) - 1
            else -> bag["玄铁"] = (bag["玄铁"] ?: 1) - 1
        }
        bag.entries.removeIf { it.value <= 0 }
        pl.gearLevel += 1
        pl.legacyForgeAtkBonus += 1 + pl.gearLevel / 3
        pl.legacyForgeDefBonus += 1 + pl.gearLevel / 4
        refreshGearBonuses()
        log("淬炼成功：基础强化提升（攻+${pl.legacyForgeAtkBonus} 防+${pl.legacyForgeDefBonus}）")
        return true
    }

    fun mountCatalog(): List<Pair<String, Int>> {
        return listOf(
            "青羽马" to 120,
            "踏云鹿" to 220,
            "玄甲犀" to 320,
            "赤焰驹" to 420,
        )
    }

    fun buyMount(name: String, price: Int): Boolean {
        if (!ensureAlive()) return false
        val pl = state.player
        if (pl.gold < price) {
            log("金币不足，无法购买坐骑")
            return false
        }
        pl.gold -= price
        addItem("坐骑:$name", 1)
        log("获得坐骑契约：$name")
        return true
    }

    fun equipMount(name: String): Boolean {
        if (!ensureAlive()) return false
        val key = "坐骑:$name"
        val have = state.player.bag[key] ?: 0
        if (have <= 0) {
            log("没有该坐骑契约")
            return false
        }
        val pl = state.player
        if (pl.mountName.isNotBlank()) {
            pl.spd -= pl.mountSpdBonus
        }
        pl.mountName = name
        pl.mountSpdBonus = when (name) {
            "青羽马" -> 2
            "踏云鹿" -> 4
            "玄甲犀" -> 3
            "赤焰驹" -> 6
            else -> 1
        }
        pl.spd += pl.mountSpdBonus
        log("坐骑上阵：$name（速度 +${pl.mountSpdBonus}）")
        return true
    }

    fun enterSecret(): Boolean {
        if (!ensureAlive()) return false
        if (secretMode) {
            log("已在秘境中")
            return false
        }
        secretMode = true
        state.maze = generateMaze(28 + rng.nextInt(0, 6), 28 + rng.nextInt(0, 6))
        state.pos = state.maze.start
        exploredCells.clear()
        revealAroundCurrentPos()
        rollChapterMarkers()
        log("进入秘境：掉落与遭遇概率提升")
        return true
    }

    fun leaveSecret(): Boolean {
        if (!secretMode) return false
        secretMode = false
        loadChapter(state.chapter.idx)
        log("离开秘境，返回章节地图")
        return true
    }

    fun attemptBreakthrough(): Boolean {
        if (!ensureAlive()) return false
        val pl = state.player
        if (pl.realmIdx >= realms.lastIndex) {
            log("已达最高境界")
            return false
        }
        val levelReq = (pl.realmIdx + 1) * 10
        if (pl.level < levelReq) {
            log("突破需求等级: Lv$levelReq")
            return false
        }
        var chance = 0.55
        val pill = pl.bag["破境丹"] ?: 0
        if (pill > 0) {
            pl.bag["破境丹"] = pill - 1
            if (pill - 1 <= 0) pl.bag.remove("破境丹")
            chance += 0.2
            log("服用破境丹，突破概率提升")
        }
        if (rng.nextDouble() <= min(0.9, chance)) {
            pl.realmIdx += 1
            pl.maxHp += 24
            pl.hp = pl.maxHp
            pl.atk += 4
            pl.def += 2
            syncLifespanCap()
            log("突破成功，当前境界 ${realms[pl.realmIdx]}")
            return true
        }
        pl.hp = max(1, pl.hp / 2)
        log("突破失败，气血重创")
        return false
    }

    fun craftBreakthroughPill(): Boolean {
        if (!ensureAlive()) return false
        val bag = state.player.bag
        val herb = bag["灵草"] ?: 0
        val dew = bag["寒露"] ?: 0
        val sand = bag["赤砂"] ?: 0
        if (herb < 1 || dew < 1 || sand < 1) {
            log("炼制破境丹需要 灵草+寒露+赤砂")
            return false
        }
        bag["灵草"] = herb - 1
        bag["寒露"] = dew - 1
        bag["赤砂"] = sand - 1
        if (bag["灵草"] == 0) bag.remove("灵草")
        if (bag["寒露"] == 0) bag.remove("寒露")
        if (bag["赤砂"] == 0) bag.remove("赤砂")
        addItem("破境丹", 1)
        log("炼成破境丹 x1")
        return true
    }

    fun methodList(): List<MethodState> = state.player.methods

    fun talentList(): List<TalentState> = state.player.talents

    fun collectibleList(): List<CollectibleState> = state.player.collectibles

    fun importCollectibleCatalogJson(raw: String): Boolean {
        return try {
            val root = JSONObject(raw)
            val tiers = root.optJSONArray("tiers") ?: return false
            val parsed = mutableMapOf<String, MutableList<CollectibleTemplate>>()
            for (i in 0 until tiers.length()) {
                val tier = tiers.optJSONObject(i) ?: continue
                val rarity = tier.optString("rarity_color", "").trim()
                if (rarity.isBlank()) continue
                val items = tier.optJSONArray("items") ?: continue
                val list = parsed.getOrPut(rarity) { mutableListOf() }
                for (j in 0 until items.length()) {
                    val item = items.optJSONObject(j) ?: continue
                    val id = item.optString("id", "").ifBlank { "col_${rarity}_$j" }
                    val name = item.optString("name", "").ifBlank { "未知收藏$j" }
                    val attrs = item.optJSONArray("属性") ?: item.optJSONArray("attrs")
                    val a0 = attrs?.optInt(0, 0) ?: 0
                    val a1 = attrs?.optInt(1, 0) ?: 0
                    val a2 = attrs?.optInt(2, 0) ?: 0
                    val a4 = attrs?.optInt(4, 0) ?: 0
                    val base = when (rarity) {
                        "红" -> 6
                        "金" -> 4
                        "紫" -> 3
                        "蓝" -> 2
                        "绿" -> 1
                        else -> 1
                    }
                    list.add(
                        CollectibleTemplate(
                            id = id,
                            name = name,
                            rarity = rarity,
                            hp = max(4, base * 6 + a2 / 2),
                            atk = max(1, base + a0 / 6),
                            def = max(1, base + a1 / 6),
                            spd = max(0, (if (rarity == "红" || rarity == "金") 1 else 0) + a4 / 8),
                        )
                    )
                }
            }
            if (parsed.isEmpty()) return false
            collectibleTemplatesByRarity.clear()
            parsed.forEach { (rarity, list) ->
                collectibleTemplatesByRarity[rarity] = list.sortedBy { it.name }.toMutableList()
            }
            true
        } catch (_: Exception) {
            false
        }
    }

    fun collectibleAtlas(): List<CollectibleAtlasEntry> {
        val rarityOrder = listOf("白", "绿", "蓝", "紫", "金", "红")
        val ownedById = state.player.collectibles.associateBy { it.id }
        val ownedByNameRarity = state.player.collectibles.associateBy { "${it.name}|${it.rarity}" }
        val entries = mutableListOf<CollectibleAtlasEntry>()
        for (rarity in rarityOrder) {
            val list = collectibleTemplatesByRarity[rarity].orEmpty()
            for (template in list) {
                val got = ownedById[template.id] ?: ownedByNameRarity["${template.name}|${template.rarity}"]
                entries.add(
                    CollectibleAtlasEntry(
                        id = template.id,
                        name = template.name,
                        rarity = template.rarity,
                        ownedLevel = got?.level ?: 0,
                    )
                )
            }
        }
        state.player.collectibles.forEach { owned ->
            if (entries.none { it.id == owned.id }) {
                entries.add(
                    CollectibleAtlasEntry(
                        id = owned.id,
                        name = owned.name,
                        rarity = owned.rarity,
                        ownedLevel = owned.level,
                    )
                )
            }
        }
        return entries
    }

    fun equipCollectible(index: Int): Boolean {
        if (!ensureAlive()) return false
        val pl = state.player
        if (index !in pl.collectibles.indices) return false
        if (pl.collectibleName.isNotBlank()) {
            pl.maxHp -= pl.collectibleHpBonus
            pl.hp = min(pl.hp, pl.maxHp)
            pl.atk -= pl.collectibleAtkBonus
            pl.def -= pl.collectibleDefBonus
            pl.spd -= pl.collectibleSpdBonus
        }
        val c = pl.collectibles[index]
        pl.collectibleName = c.name
        pl.collectibleHpBonus = c.hp * c.level
        pl.collectibleAtkBonus = c.atk * c.level
        pl.collectibleDefBonus = c.def * c.level
        pl.collectibleSpdBonus = c.spd * c.level
        pl.maxHp += pl.collectibleHpBonus
        pl.hp = min(pl.maxHp, pl.hp + pl.collectibleHpBonus)
        pl.atk += pl.collectibleAtkBonus
        pl.def += pl.collectibleDefBonus
        pl.spd += pl.collectibleSpdBonus
        log("装备收藏品：${c.name} Lv${c.level}")
        return true
    }

    fun trainMethod(index: Int): Boolean {
        if (!ensureAlive()) return false
        val pl = state.player
        if (index !in pl.methods.indices) return false
        if (pl.lingshi <= 0) {
            log("灵石不足，无法修炼功法")
            return false
        }
        pl.lingshi -= 1
        val m = pl.methods[index]
        val gain = 3 + m.stage
        m.progress += gain
        log("功法 ${m.name} 进度 +$gain (${m.progress}/${m.need})")
        if (m.progress >= m.need) {
            m.progress -= m.need
            m.stage += 1
            m.need = (m.need * 1.25 + 8).toInt()
            if (m.stage >= 4) {
                pl.atk += 1
                pl.def += 1
                log("${m.name} 圆满增益触发，攻击+1 防御+1")
            } else {
                log("${m.name} 达到 ${methodStageName(m.stage)}")
            }
        }
        return true
    }

    fun skillList(): List<SkillState> = state.player.skills

    fun npcList(): List<NpcState> = npcs.filter { it.alive }

    fun setNpcInferenceProvider(provider: NpcInferenceProvider?) {
        npcInferenceProvider = provider
        npcLastError = ""
        npcLastRaw = ""
    }

    fun npcModelStatusText(): String {
        val mode = if (npcInferenceProvider == null) "规则回复" else "本地LLM"
        val tail = when {
            npcLastError.isNotBlank() -> " | 最近错误: $npcLastError"
            npcLastRaw.isNotBlank() -> " | 最近输出: ${npcLastRaw.take(56)}"
            else -> ""
        }
        return "$mode$tail"
    }

    fun npcStatusText(npc: NpcState): String {
        val legacyTag = if (npc.isLegacyEcho) " | 遗骸ID:${npc.lifeIdRef}" else ""
        return "阵营:${npc.faction} 心情:${npc.mood} 关系:${npc.relation} 提示:${npc.hint} 跟随:${if (npc.follow) "是" else "否"}$legacyTag"
    }

    fun npcTalk(npc: NpcState, playerText: String): String {
        if (!ensureAlive()) return "你已死亡，无法互动"
        if (!npc.alive) return "${npc.name} 已陨落"
        if (npc.isLegacyEcho) {
            val line = "吾名已葬于旧世，若觊觎遗物，便来战。"
            npc.lastReply = line
            appendNpcMemory(npc, "NPC:$line")
            log("${npc.name}: $line")
            state.chapter.questTalk += 1
            return line
        }
        val msg = playerText.trim()
        if (msg.isBlank()) return "你没有说话。"
        appendNpcMemory(npc, "玩家:$msg")

        val prompt = buildNpcPrompt(npc, msg)
        val llmRaw = npcInferenceProvider?.let { provider ->
            try {
                provider.generate(prompt)
            } catch (e: Throwable) {
                npcLastError = "LLM异常:${e.message ?: "unknown"}"
                null
            }
        }
        if (!llmRaw.isNullOrBlank()) {
            npcLastRaw = llmRaw
            npcLastError = ""
        }

        val llmReply = if (llmRaw.isNullOrBlank()) null else parseNpcLlmReply(npc, llmRaw)
        val reply = llmReply ?: when {
            msg.contains("你好") -> "你好，我是${npc.name}。"
            msg.contains("任务") -> "这章建议优先清战斗目标，再去出口。"
            msg.contains("技能") -> "速度高的敌人可能先手，建议先堆防御。"
            msg.contains("材料") -> "本章会掉落 ${chapterMaterial()}。"
            else -> "此地不太平，谨慎行动。"
        }
        if (llmReply == null) {
            if (npcInferenceProvider != null) {
                val reason = npcLastError.take(64)
                if (reason.isBlank()) {
                    log("[NPC模型] 未获取有效回复，已回退规则")
                } else {
                    log("[NPC模型] 回退规则: $reason")
                }
            }
            npc.relation = min(100, npc.relation + 1)
        }
        if (npc.relation >= 80 && !npc.follow) {
            npc.follow = true
            log("${npc.name} 好感已满，成为随行者（全属性+2）")
            state.player.atk += 2
            state.player.def += 2
            state.player.spd += 2
        }
        appendNpcMemory(npc, "NPC:$reply")
        npc.lastReply = reply
        log("${npc.name}: $reply")
        state.chapter.questTalk += 1
        return reply
    }

    fun npcGift(npc: NpcState, itemId: String): Boolean {
        if (!ensureAlive()) return false
        if (!npc.alive) {
            log("${npc.name} 已陨落，无法赠礼")
            return false
        }
        if (npc.isLegacyEcho) {
            log("${npc.name} 执念缠身，无法受礼")
            return false
        }
        val bag = state.player.bag
        val have = bag[itemId] ?: 0
        if (have <= 0) {
            log("赠礼失败，物品不足")
            return false
        }
        if (have == 1) bag.remove(itemId) else bag[itemId] = have - 1
        npc.relation = min(100, npc.relation + 6)
        npc.mood = "友好"
        adjustFactionRep(npc.faction, 1)
        log("赠礼 $itemId 给 ${npc.name}，关系提升至 ${npc.relation}")
        return true
    }

    fun npcTrade(npc: NpcState, itemId: String, price: Int): Boolean {
        if (!ensureAlive()) return false
        if (!npc.alive) {
            log("${npc.name} 已陨落，无法交易")
            return false
        }
        if (npc.isLegacyEcho) {
            log("${npc.name} 仅存战意，无法交易")
            return false
        }
        val pl = state.player
        if (pl.gold < price) {
            log("金币不足，交易失败")
            return false
        }
        pl.gold -= price
        addItem(itemId, 1)
        npc.relation = min(100, npc.relation + 2)
        adjustFactionRep(npc.faction, 1)
        log("向 ${npc.name} 购买 $itemId 成功")
        return true
    }

    fun npcAttack(npc: NpcState): Boolean {
        if (!ensureAlive()) return false
        val pl = state.player
        if (!npc.alive) {
            log("${npc.name} 已经陨落")
            return false
        }
        if (npc.isLegacyEcho) {
            val playerPower = pl.level * 8 + pl.atk + pl.def + pl.gearAtkBonus + pl.gearDefBonus + pl.spd / 2
            val npcPower = npc.combatPower + rng.nextInt(-6, 7)
            if (playerPower + rng.nextInt(0, 12) >= npcPower) {
                npc.alive = false
                npc.hostile = false
                npc.relation = -100
                val loot = if (npc.lootItem.isBlank()) "基础锻造箱" else npc.lootItem
                addItem(loot, 1)
                if (rng.nextDouble() < 0.5) {
                    addItem("修理包", 1)
                }
                val bonusGold = 12 + pl.level * 2
                pl.gold += bonusGold
                log("你斩杀了 ${npc.name}，其残魂彻底消散（不再复生）")
                log("战利品：${displayItemName(loot)} x1，金币 +$bonusGold")
                lastBattleSummary = "斩杀遗骸NPC ${npc.name}"
                return true
            }
            val failDmg = max(12, pl.maxHp / 3 + npc.combatPower / 8)
            pl.hp = max(0, pl.hp - failDmg)
            log("你挑战 ${npc.name} 失败，反噬受到 $failDmg 伤害")
            if (pl.hp <= 0) {
                onPlayerDeath("挑战遗骸NPC失败")
            }
            return true
        }
        val dmg = max(10, pl.maxHp / 3)
        pl.hp = max(1, pl.hp - dmg)
        npc.relation = 0
        npc.hostile = true
        npc.mood = "仇恨"
        adjustFactionRep(npc.faction, -3)
        log("你攻击了 ${npc.name}，无法逃跑，反击造成 $dmg 伤害")
        return true
    }

    fun createSect(name: String): Boolean {
        if (!ensureAlive()) return false
        val s = state.sect
        if (s.created) {
            log("宗门已创建")
            return false
        }
        s.created = true
        s.name = if (name.isBlank()) "无名宗" else name
        s.month = currentMonth()
        s.lastAutoMonth = currentMonth()
        val used = s.disciples.map { it.name }.toMutableSet()
        val nameA = randomDiscipleName(used)
        used.add(nameA)
        val nameB = randomDiscipleName(used)
        s.disciples.add(DiscipleState(nameA, 1, 6))
        s.disciples.add(DiscipleState(nameB, 1, 7))
        if ((s.uniqueRelics["护宗灵印"] ?: 0) <= 0) {
            s.uniqueRelics["护宗灵印"] = 1
        }
        log("宗门 ${s.name} 建立完成")
        return true
    }

    fun sectSummary(): String {
        val s = state.sect
        if (!s.created) return "未创建宗门"
        val alive = s.disciples.count { it.alive }
        val vaultItems = s.vault.values.sum()
        val relicCount = s.uniqueRelics.values.sum()
        return "${s.name} | 月${s.month} | 灵田${s.spiritField} 矿脉${s.mine} 经阁${s.library} 戒备${s.defense} | 资源 灵石${s.lingshi} 草药${s.herb} 矿石${s.ore} | 仓库${vaultItems}件 宝物${relicCount}件 | 弟子 ${alive}/${s.disciples.size}"
    }

    fun sectDiscipleLines(): List<String> {
        val s = state.sect
        if (!s.created) return emptyList()
        return s.disciples.mapIndexed { idx, d ->
            val life = if (d.alive) "存活" else "陨落"
            val relic = if (d.relicCharges > 0) " | 护命:${d.lifeGuardRelic}(${d.relicCharges})" else ""
            val equip = if (d.equippedTag.isNotBlank()) " | 装备:${d.equippedTag}" else ""
            "${idx + 1}.${d.name} Lv${d.level} 资质${d.apt} 攻+${d.atkBonus} 防+${d.defBonus} 速+${d.spdBonus} | $life$equip$relic"
        }
    }

    fun sectVaultItems(): List<Pair<String, Int>> {
        val s = state.sect
        if (!s.created) return emptyList()
        return s.vault.entries.filter { it.value > 0 }.sortedBy { it.key }.map { it.key to it.value }
    }

    fun sectRelicItems(): List<Pair<String, Int>> {
        val s = state.sect
        if (!s.created) return emptyList()
        return s.uniqueRelics.entries.filter { it.value > 0 }.sortedBy { it.key }.map { it.key to it.value }
    }

    fun sectDepositToVault(itemId: String): Boolean {
        if (!ensureAlive()) return false
        val s = state.sect
        if (!s.created) {
            log("请先创建宗门")
            return false
        }
        val bag = state.player.bag
        val have = bag[itemId] ?: 0
        if (have <= 0) {
            log("背包没有该物品")
            return false
        }
        if (have == 1) bag.remove(itemId) else bag[itemId] = have - 1
        s.vault[itemId] = (s.vault[itemId] ?: 0) + 1
        log("物品入库：$itemId")
        return true
    }

    fun sectAssignVaultItem(discipleIndex: Int, itemId: String): Boolean {
        if (!ensureAlive()) return false
        val s = state.sect
        if (!s.created) return false
        if (discipleIndex !in s.disciples.indices) {
            log("未选择有效弟子")
            return false
        }
        val d = s.disciples[discipleIndex]
        if (!d.alive) {
            log("该弟子已陨落，无法分配")
            return false
        }
        val have = s.vault[itemId] ?: 0
        if (have <= 0) {
            log("仓库没有该物品")
            return false
        }
        val bonus = discipleItemBonus(itemId)
        d.atkBonus += bonus.first
        d.defBonus += bonus.second
        d.spdBonus += bonus.third
        d.equippedTag = itemId
        if (have == 1) s.vault.remove(itemId) else s.vault[itemId] = have - 1
        log("已指定分配：$itemId -> ${d.name}（攻+${bonus.first} 防+${bonus.second} 速+${bonus.third}）")
        return true
    }

    fun sectAssignRelic(discipleIndex: Int, relicName: String): Boolean {
        if (!ensureAlive()) return false
        val s = state.sect
        if (!s.created) return false
        if (discipleIndex !in s.disciples.indices) {
            log("未选择有效弟子")
            return false
        }
        val d = s.disciples[discipleIndex]
        if (!d.alive) {
            log("该弟子已陨落，无法授予")
            return false
        }
        val have = s.uniqueRelics[relicName] ?: 0
        if (have <= 0) {
            log("没有可用唯一宝物：$relicName")
            return false
        }
        if (have == 1) s.uniqueRelics.remove(relicName) else s.uniqueRelics[relicName] = have - 1
        d.lifeGuardRelic = relicName
        d.relicCharges += 1
        log("已授予唯一宝物：$relicName -> ${d.name}（保命次数 ${d.relicCharges}）")
        return true
    }

    fun sectRecruit(): Boolean {
        if (!ensureAlive()) return false
        val s = state.sect
        if (!s.created) {
            log("请先创建宗门")
            return false
        }
        val used = s.disciples.map { it.name }.toSet()
        val d = DiscipleState(randomDiscipleName(used), 1, rng.nextInt(4, 10))
        s.disciples.add(d)
        log("招收弟子 ${d.name}，资质 ${d.apt}")
        return true
    }

    fun sectPlant(): Boolean {
        if (!ensureAlive()) return false
        val s = state.sect
        if (!s.created) return false
        val gain = s.spiritField * 3
        s.herb += gain
        log("灵田收成，草药 +$gain")
        return true
    }

    fun sectMine(): Boolean {
        if (!ensureAlive()) return false
        val s = state.sect
        if (!s.created) return false
        if (s.mine <= 0) {
            log("没有矿脉建筑")
            return false
        }
        val gain = s.mine * 2
        s.ore += gain
        log("矿脉收成，矿石 +$gain")
        return true
    }

    fun sectBuild(type: String): Boolean {
        if (!ensureAlive()) return false
        val s = state.sect
        if (!s.created) return false
        if (state.player.gold < 200) {
            log("金币不足，建设需要 200")
            return false
        }
        state.player.gold -= 200
        when (type) {
            "field" -> s.spiritField += 1
            "mine" -> s.mine += 1
            "library" -> s.library += 1
            "defense" -> s.defense += 1
            else -> return false
        }
        log("宗门建设完成: $type")
        return true
    }

    fun sectTrain(): Boolean {
        if (!ensureAlive()) return false
        val s = state.sect
        if (!s.created) return false
        var cnt = 0
        s.disciples.filter { it.alive }.forEach {
            it.level += 1
            cnt += 1
        }
        if (cnt > 0) {
            log("弟子训练完成，$cnt 名弟子等级+1")
            return true
        }
        return false
    }

    fun sectExpedition(): Boolean {
        if (!ensureAlive()) return false
        val s = state.sect
        if (!s.created) return false
        val alive = s.disciples.filter { it.alive }
        if (alive.isEmpty()) {
            log("无可出战弟子")
            return false
        }
        val lead = alive.maxByOrNull { discipleCombatPower(it) } ?: return false
        val reward = rng.nextInt(20, 60) + discipleCombatPower(lead) / 3
        state.player.gold += reward
        if (rng.nextDouble() < 0.2) s.lingshi += 1
        if (rng.nextDouble() < max(0.02, 0.18 - s.defense * 0.02 - discipleCombatPower(lead) * 0.002)) {
            if (tryConsumeRelicProtection(lead, "宗门历练")) {
                lead.level = max(1, lead.level - 1)
            } else {
                lead.alive = false
                log("宗门历练遭遇重创，弟子 ${lead.name} 牺牲")
            }
        } else {
            lead.level += 1
            log("宗门历练成功，${lead.name} 归来，金币 +$reward")
        }
        if (rng.nextDouble() < 0.06) {
            s.uniqueRelics["护宗灵印"] = (s.uniqueRelics["护宗灵印"] ?: 0) + 1
            log("宗门历练发现唯一宝物：护宗灵印")
        }
        return true
    }

    fun dumpState(): String {
        val pl = state.player
        val root = JSONObject()
        root.put("name", pl.name)
        root.put("lifeId", pl.lifeId)
        root.put("level", pl.level)
        root.put("exp", pl.exp)
        root.put("expNext", pl.expNext)
        root.put("hp", pl.hp)
        root.put("maxHp", pl.maxHp)
        root.put("atk", pl.atk)
        root.put("def", pl.def)
        root.put("spd", pl.spd)
        root.put("gold", pl.gold)
        root.put("lingshi", pl.lingshi)
        root.put("freePoints", pl.freePoints)
        root.put("timeTick", pl.timeTick)
        root.put("ageMonths", pl.ageMonths)
        root.put("lifespanMonths", pl.lifespanMonths)
        root.put("realmIdx", pl.realmIdx)
        root.put("gearLevel", pl.gearLevel)
        root.put("legacyForgeAtkBonus", pl.legacyForgeAtkBonus)
        root.put("legacyForgeDefBonus", pl.legacyForgeDefBonus)
        root.put("gearAtkBonus", pl.gearAtkBonus)
        root.put("gearDefBonus", pl.gearDefBonus)
        root.put("mountName", pl.mountName)
        root.put("mountSpdBonus", pl.mountSpdBonus)
        root.put("luck", pl.luck)
        root.put("collectibleName", pl.collectibleName)
        root.put("collectibleHpBonus", pl.collectibleHpBonus)
        root.put("collectibleAtkBonus", pl.collectibleAtkBonus)
        root.put("collectibleDefBonus", pl.collectibleDefBonus)
        root.put("collectibleSpdBonus", pl.collectibleSpdBonus)
        root.put("isDead", pl.isDead)
        root.put("deathCount", pl.deathCount)
        root.put("kills", pl.kills)
        root.put("chapterIdx", state.chapter.idx)
        root.put("chapterBattles", state.chapter.battles)
        root.put("chapterTalk", state.chapter.questTalk)
        root.put("chapterTalkTarget", state.chapter.questTalkTarget)
        root.put("secretMode", secretMode)
        root.put("nextLifeId", nextLifeId)
        root.put("maze", mazeToJson(state.maze))
        root.put("pos", posToJson(state.pos))
        root.put("bossMarker", bossMarkerPos?.let { posToJson(it) } ?: JSONObject.NULL)
        root.put("mountMarker", mountMarkerPos?.let { posToJson(it) } ?: JSONObject.NULL)
        root.put("treasureMarker", treasureMarkerPos?.let { posToJson(it) } ?: JSONObject.NULL)
        val exploredArr = JSONArray()
        exploredCells.forEach { exploredArr.put(posToJson(it)) }
        root.put("mapExplored", exploredArr)

        val usedIdsArr = JSONArray()
        usedLifeIds.sorted().forEach { usedIdsArr.put(it) }
        root.put("usedLifeIds", usedIdsArr)
        val deadIdsArr = JSONArray()
        deadLifeIds.sorted().forEach { deadIdsArr.put(it) }
        root.put("deadLifeIds", deadIdsArr)

        val bagObj = JSONObject()
        pl.bag.forEach { (k, v) -> bagObj.put(k, v) }
        root.put("bag", bagObj)

        val methodsArr = JSONArray()
        pl.methods.forEach {
            methodsArr.put(JSONObject().apply {
                put("id", it.id)
                put("name", it.name)
                put("element", it.element)
                put("stage", it.stage)
                put("progress", it.progress)
                put("need", it.need)
            })
        }
        root.put("methods", methodsArr)

        val talentsArr = JSONArray()
        pl.talents.forEach {
            talentsArr.put(JSONObject().apply {
                put("id", it.id)
                put("name", it.name)
                put("tier", it.tier)
                put("hp", it.hp)
                put("atk", it.atk)
                put("def", it.def)
                put("spd", it.spd)
                put("luck", it.luck)
            })
        }
        root.put("talents", talentsArr)

        val collArr = JSONArray()
        pl.collectibles.forEach {
            collArr.put(JSONObject().apply {
                put("id", it.id)
                put("name", it.name)
                put("rarity", it.rarity)
                put("level", it.level)
                put("hp", it.hp)
                put("atk", it.atk)
                put("def", it.def)
                put("spd", it.spd)
            })
        }
        root.put("collectibles", collArr)

        val eqArr = JSONArray()
        pl.equipments.values.forEach {
            eqArr.put(JSONObject().apply {
                put("id", it.id)
                put("name", it.name)
                put("slot", it.slot)
                put("tier", it.tier)
                put("atk", it.atk)
                put("def", it.def)
                put("spd", it.spd)
                put("durability", it.durability)
                put("maxDurability", it.maxDurability)
            })
        }
        root.put("equipments", eqArr)

        val bpArr = JSONArray()
        pl.knownBlueprints.sorted().forEach { bpArr.put(it) }
        root.put("knownBlueprints", bpArr)

        val npcArr = JSONArray()
        npcs.forEach {
            npcArr.put(JSONObject().apply {
                put("id", it.id)
                put("name", it.name)
                put("faction", it.faction)
                put("background", it.background)
                put("goal", it.goal)
                put("relation", it.relation)
                put("mood", it.mood)
                put("hint", it.hint)
                put("hostile", it.hostile)
                put("follow", it.follow)
                put("alive", it.alive)
                put("isLegacyEcho", it.isLegacyEcho)
                put("lifeIdRef", it.lifeIdRef)
                put("noRespawn", it.noRespawn)
                put("combatPower", it.combatPower)
                put("lootItem", it.lootItem)
                put("lastReply", it.lastReply)
                val memArr = JSONArray()
                it.memory.forEach { m -> memArr.put(m) }
                put("memory", memArr)
            })
        }
        root.put("npcs", npcArr)

        val sect = state.sect
        val sectObj = JSONObject().apply {
            put("created", sect.created)
            put("name", sect.name)
            put("month", sect.month)
            put("lastAutoMonth", sect.lastAutoMonth)
            put("spiritField", sect.spiritField)
            put("mine", sect.mine)
            put("library", sect.library)
            put("defense", sect.defense)
            put("lingshi", sect.lingshi)
            put("herb", sect.herb)
            put("ore", sect.ore)
            val vaultObj = JSONObject()
            sect.vault.forEach { (k, v) -> vaultObj.put(k, v) }
            put("vault", vaultObj)
            val relicObj = JSONObject()
            sect.uniqueRelics.forEach { (k, v) -> relicObj.put(k, v) }
            put("uniqueRelics", relicObj)
            val dArr = JSONArray()
            sect.disciples.forEach { d ->
                dArr.put(JSONObject().apply {
                    put("name", d.name)
                    put("level", d.level)
                    put("apt", d.apt)
                    put("alive", d.alive)
                    put("atkBonus", d.atkBonus)
                    put("defBonus", d.defBonus)
                    put("spdBonus", d.spdBonus)
                    put("equippedTag", d.equippedTag)
                    put("lifeGuardRelic", d.lifeGuardRelic)
                    put("relicCharges", d.relicCharges)
                })
            }
            put("disciples", dArr)
        }
        root.put("sect", sectObj)

        return root.toString()
    }

    fun loadState(json: String): Boolean {
        return try {
            val root = JSONObject(json)
            val pl = state.player
            pl.name = root.optString("name", pl.name)
            pl.lifeId = root.optInt("lifeId", pl.lifeId).coerceAtLeast(1)
            pl.level = root.optInt("level", pl.level)
            pl.exp = root.optInt("exp", pl.exp)
            pl.expNext = root.optInt("expNext", pl.expNext)
            pl.hp = root.optInt("hp", pl.hp)
            pl.maxHp = root.optInt("maxHp", pl.maxHp)
            pl.atk = root.optInt("atk", pl.atk)
            pl.def = root.optInt("def", pl.def)
            pl.spd = root.optInt("spd", pl.spd)
            pl.gold = root.optInt("gold", pl.gold)
            pl.lingshi = root.optInt("lingshi", pl.lingshi)
            pl.freePoints = root.optInt("freePoints", 0)
            pl.realmIdx = root.optInt("realmIdx", pl.realmIdx)
            pl.timeTick = root.optInt("timeTick", pl.timeTick)
            pl.ageMonths = root.optInt("ageMonths", pl.timeTick / 3)
            pl.lifespanMonths = root.optInt("lifespanMonths", computeLifespanMonths())
            pl.gearLevel = root.optInt("gearLevel", 0)
            pl.legacyForgeAtkBonus = root.optInt("legacyForgeAtkBonus", root.optInt("gearAtkBonus", 0))
            pl.legacyForgeDefBonus = root.optInt("legacyForgeDefBonus", root.optInt("gearDefBonus", 0))
            pl.gearAtkBonus = 0
            pl.gearDefBonus = 0
            pl.mountName = root.optString("mountName", "")
            pl.mountSpdBonus = root.optInt("mountSpdBonus", 0)
            pl.luck = root.optInt("luck", 0)
            pl.collectibleName = root.optString("collectibleName", "")
            pl.collectibleHpBonus = root.optInt("collectibleHpBonus", 0)
            pl.collectibleAtkBonus = root.optInt("collectibleAtkBonus", 0)
            pl.collectibleDefBonus = root.optInt("collectibleDefBonus", 0)
            pl.collectibleSpdBonus = root.optInt("collectibleSpdBonus", 0)
            pl.isDead = root.optBoolean("isDead", false)
            pl.deathCount = root.optInt("deathCount", 0)
            pl.kills = root.optInt("kills", pl.kills)
            nextLifeId = root.optInt("nextLifeId", max(nextLifeId, pl.lifeId + 1)).coerceAtLeast(pl.lifeId + 1)

            usedLifeIds.clear()
            val usedIds = root.optJSONArray("usedLifeIds")
            if (usedIds != null) {
                for (i in 0 until usedIds.length()) {
                    usedLifeIds.add(usedIds.optInt(i, 0))
                }
            }
            usedLifeIds.add(pl.lifeId)
            deadLifeIds.clear()
            val deadIds = root.optJSONArray("deadLifeIds")
            if (deadIds != null) {
                for (i in 0 until deadIds.length()) {
                    deadLifeIds.add(deadIds.optInt(i, 0))
                }
            }
            val idMax = (usedLifeIds + deadLifeIds).maxOrNull() ?: pl.lifeId
            nextLifeId = max(nextLifeId, idMax + 1)

            pl.bag.clear()
            val bag = root.optJSONObject("bag")
            if (bag != null) {
                bag.keys().forEach { k ->
                    pl.bag[k] = bag.optInt(k, 0)
                }
            }

            pl.methods.clear()
            val methods = root.optJSONArray("methods")
            if (methods != null) {
                for (i in 0 until methods.length()) {
                    val m = methods.getJSONObject(i)
                    pl.methods.add(
                        MethodState(
                            id = m.optString("id"),
                            name = m.optString("name"),
                            element = m.optString("element"),
                            stage = m.optInt("stage", 0),
                            progress = m.optInt("progress", 0),
                            need = m.optInt("need", 12),
                        )
                    )
                }
            }

            pl.talents.clear()
            val talents = root.optJSONArray("talents")
            if (talents != null) {
                for (i in 0 until talents.length()) {
                    val t = talents.getJSONObject(i)
                    pl.talents.add(
                        TalentState(
                            id = t.optString("id", "tal_$i"),
                            name = t.optString("name", "未知天赋"),
                            tier = t.optInt("tier", 0),
                            hp = t.optInt("hp", 0),
                            atk = t.optInt("atk", 0),
                            def = t.optInt("def", 0),
                            spd = t.optInt("spd", 0),
                            luck = t.optInt("luck", 0)
                        )
                    )
                }
            }

            pl.collectibles.clear()
            val cols = root.optJSONArray("collectibles")
            if (cols != null) {
                for (i in 0 until cols.length()) {
                    val c = cols.getJSONObject(i)
                    pl.collectibles.add(
                        CollectibleState(
                            id = c.optString("id", "col_$i"),
                            name = c.optString("name", "未知收藏"),
                            rarity = c.optString("rarity", "白"),
                            level = c.optInt("level", 1),
                            hp = c.optInt("hp", 0),
                            atk = c.optInt("atk", 0),
                            def = c.optInt("def", 0),
                            spd = c.optInt("spd", 0)
                        )
                    )
                }
            }

            pl.equipments.clear()
            val eqArr = root.optJSONArray("equipments")
            if (eqArr != null) {
                for (i in 0 until eqArr.length()) {
                    val e = eqArr.getJSONObject(i)
                    val slot = e.optString("slot")
                    if (slot.isBlank()) continue
                    pl.equipments[slot] = EquipmentState(
                        id = e.optString("id", "eq_$slot"),
                        name = e.optString("name", "无名装备"),
                        slot = slot,
                        tier = e.optInt("tier", 0),
                        atk = e.optInt("atk", 0),
                        def = e.optInt("def", 0),
                        spd = e.optInt("spd", 0),
                        durability = e.optInt("durability", 0),
                        maxDurability = e.optInt("maxDurability", 80),
                    )
                }
            }

            pl.knownBlueprints.clear()
            val bpArr = root.optJSONArray("knownBlueprints")
            if (bpArr != null) {
                for (i in 0 until bpArr.length()) {
                    pl.knownBlueprints.add(bpArr.optString(i))
                }
            }

            val npcArr = root.optJSONArray("npcs")
            if (npcArr != null) {
                for (i in 0 until npcArr.length()) {
                    val n = npcArr.getJSONObject(i)
                    val id = n.optString("id")
                    if (id.isBlank()) continue
                    val target = npcs.find { it.id == id } ?: NpcState(
                        id = id,
                        name = n.optString("name", "未知NPC"),
                        faction = n.optString("faction", "中立"),
                    ).also { npcs.add(it) }
                    target.name = n.optString("name", target.name)
                    target.faction = n.optString("faction", target.faction)
                    target.background = n.optString("background", target.background)
                    target.goal = n.optString("goal", target.goal)
                    target.relation = n.optInt("relation", target.relation)
                    target.mood = n.optString("mood", target.mood)
                    target.hint = n.optString("hint", target.hint)
                    target.hostile = n.optBoolean("hostile", target.hostile)
                    target.follow = n.optBoolean("follow", target.follow)
                    target.alive = n.optBoolean("alive", target.alive)
                    target.isLegacyEcho = n.optBoolean("isLegacyEcho", target.isLegacyEcho)
                    target.lifeIdRef = n.optInt("lifeIdRef", target.lifeIdRef)
                    target.noRespawn = n.optBoolean("noRespawn", target.noRespawn)
                    target.combatPower = n.optInt("combatPower", target.combatPower)
                    target.lootItem = n.optString("lootItem", target.lootItem)
                    target.lastReply = n.optString("lastReply", target.lastReply)
                    target.memory.clear()
                    val memArr = n.optJSONArray("memory")
                    if (memArr != null) {
                        for (k in 0 until memArr.length()) {
                            val m = memArr.optString(k)
                            if (m.isNotBlank()) target.memory.add(m)
                        }
                    }
                }
            }

            val sectObj = root.optJSONObject("sect")
            if (sectObj != null) {
                val s = state.sect
                s.created = sectObj.optBoolean("created", false)
                s.name = sectObj.optString("name", "")
                s.month = sectObj.optInt("month", 0)
                s.lastAutoMonth = sectObj.optInt("lastAutoMonth", s.month)
                s.spiritField = sectObj.optInt("spiritField", 1)
                s.mine = sectObj.optInt("mine", 0)
                s.library = sectObj.optInt("library", 0)
                s.defense = sectObj.optInt("defense", 0)
                s.lingshi = sectObj.optInt("lingshi", 0)
                s.herb = sectObj.optInt("herb", 0)
                s.ore = sectObj.optInt("ore", 0)
                s.vault.clear()
                val vaultObj = sectObj.optJSONObject("vault")
                if (vaultObj != null) {
                    vaultObj.keys().forEach { k ->
                        s.vault[k] = vaultObj.optInt(k, 0)
                    }
                }
                s.uniqueRelics.clear()
                val relicObj = sectObj.optJSONObject("uniqueRelics")
                if (relicObj != null) {
                    relicObj.keys().forEach { k ->
                        s.uniqueRelics[k] = relicObj.optInt(k, 0)
                    }
                }
                s.disciples.clear()
                val dArr = sectObj.optJSONArray("disciples")
                if (dArr != null) {
                    for (i in 0 until dArr.length()) {
                        val d = dArr.getJSONObject(i)
                        s.disciples.add(
                            DiscipleState(
                                name = d.optString("name", "弟子"),
                                level = d.optInt("level", 1),
                                apt = d.optInt("apt", 5),
                                alive = d.optBoolean("alive", true),
                                atkBonus = d.optInt("atkBonus", 0),
                                defBonus = d.optInt("defBonus", 0),
                                spdBonus = d.optInt("spdBonus", 0),
                                equippedTag = d.optString("equippedTag", ""),
                                lifeGuardRelic = d.optString("lifeGuardRelic", ""),
                                relicCharges = d.optInt("relicCharges", 0),
                            )
                        )
                    }
                }
                if (s.created && (s.uniqueRelics["护宗灵印"] ?: 0) <= 0 && s.disciples.none { it.relicCharges > 0 }) {
                    s.uniqueRelics["护宗灵印"] = 1
                }
            }

            val cIdx = root.optInt("chapterIdx", state.chapter.idx).coerceIn(0, chapters.lastIndex)
            val savedMazeObj = root.optJSONObject("maze")
            val savedPosObj = root.optJSONObject("pos")
            val savedBossObj = if (root.has("bossMarker")) root.optJSONObject("bossMarker") else null
            val savedMountObj = if (root.has("mountMarker")) root.optJSONObject("mountMarker") else null
            val savedTreasureObj = if (root.has("treasureMarker")) root.optJSONObject("treasureMarker") else null
            val savedExplored = root.optJSONArray("mapExplored")
            loadChapter(cIdx)
            mazeFromJson(savedMazeObj)?.let { restoredMaze ->
                state.maze = restoredMaze
            }
            posFromJson(savedPosObj)?.let { restoredPos ->
                if (canWalkInMaze(state.maze, restoredPos)) {
                    state.pos = restoredPos
                }
            }
            if (savedBossObj != null || root.has("bossMarker")) {
                bossMarkerPos = posFromJson(savedBossObj)?.takeIf { canWalkInMaze(state.maze, it) }
            }
            if (savedMountObj != null || root.has("mountMarker")) {
                mountMarkerPos = posFromJson(savedMountObj)?.takeIf { canWalkInMaze(state.maze, it) }
            }
            if (savedTreasureObj != null || root.has("treasureMarker")) {
                treasureMarkerPos = posFromJson(savedTreasureObj)?.takeIf { canWalkInMaze(state.maze, it) }
            }
            exploredCells.clear()
            if (savedExplored != null) {
                for (i in 0 until savedExplored.length()) {
                    val p = posFromJson(savedExplored.optJSONObject(i)) ?: continue
                    if (p.x in 0 until state.maze.width && p.y in 0 until state.maze.height) {
                        exploredCells.add(p)
                    }
                }
            }
            if (exploredCells.isEmpty()) {
                revealAroundCurrentPos()
            } else {
                exploredCells.add(state.pos)
            }
            state.chapter.battles = root.optInt("chapterBattles", 0)
            state.chapter.questTalk = root.optInt("chapterTalk", 0)
            state.chapter.questTalkTarget = root.optInt("chapterTalkTarget", state.chapter.questTalkTarget)
            secretMode = root.optBoolean("secretMode", false)
            ensurePlayerSystems()
            initStarterBlueprints()
            refreshGearBonuses()
            if (pl.talents.isEmpty()) {
                initTalentsForNewLife()
            }
            log("读档成功")
            true
        } catch (_: Throwable) {
            false
        }
    }

    private fun ensurePlayerSystems() {
        val pl = state.player
        if (pl.methods.isEmpty()) {
            pl.methods.add(MethodState("m_gold", "玄金诀", "金"))
            pl.methods.add(MethodState("m_wood", "青木诀", "木"))
            pl.methods.add(MethodState("m_water", "碧水诀", "水"))
            pl.methods.add(MethodState("m_fire", "赤炎诀", "火"))
            pl.methods.add(MethodState("m_earth", "厚土诀", "土"))
        }
        if (pl.skills.isEmpty()) {
            pl.skills.add(SkillState("sk_slash", "断岳斩", 1.4, 2))
            pl.skills.add(SkillState("sk_stun", "镇魄印", 1.0, 4, effect = "stun"))
            pl.skills.add(SkillState("sk_guard", "护体诀", 0.8, 3, effect = "shield"))
        }
        pl.ageMonths = pl.timeTick / 3
        syncLifespanCap()
        refreshGearBonuses()
    }

    private fun initStarterBlueprints() {
        val known = state.player.knownBlueprints
        if (known.isEmpty()) {
            known.addAll(
                listOf(
                    "bp_weapon_t0",
                    "bp_head_t0",
                    "bp_body_t0",
                    "bp_boots_t0",
                    "bp_accessory_t0",
                )
            )
        }
    }

    private fun adjustFactionRep(faction: String, delta: Int) {
        val pl = state.player
        when (faction) {
            "人族" -> pl.factionRepHuman += delta
            "妖族" -> pl.factionRepYao += delta
            "魔族" -> pl.factionRepMo += delta
            "仙族" -> pl.factionRepXian += delta
        }
    }

    private fun loadChapter(idx: Int) {
        val chap = chapters[idx]
        state.chapter.idx = idx
        state.chapter.battles = 0
        state.chapter.battleTarget = chap.battleTarget
        state.chapter.questTalk = 0
        state.chapter.questTalkTarget = 1 + (idx / 3)
        state.maze = generateMaze(chap.width, chap.height)
        state.pos = state.maze.start
        exploredCells.clear()
        revealAroundCurrentPos()
        rollChapterMarkers()
        refreshGearBonuses()
        log("进入章节：${chap.name} (${chap.width}x${chap.height})")
        log("本章目标：战斗 ${chap.battleTarget} 次，对话 ${state.chapter.questTalkTarget} 次")
    }

    private fun rollChapterMarkers() {
        val used = mutableSetOf(state.maze.start, state.maze.exit)
        bossMarkerPos = randomWalkableMarker(used)
        mountMarkerPos = randomWalkableMarker(used)
        treasureMarkerPos = randomWalkableMarker(used)
    }

    private fun randomWalkableMarker(used: MutableSet<Pos>): Pos? {
        val width = state.maze.width
        val height = state.maze.height
        repeat(800) {
            val x = rng.nextInt(1, width - 1)
            val y = rng.nextInt(1, height - 1)
            val p = Pos(x, y)
            if (p in used) return@repeat
            if (!canWalk(p)) return@repeat
            used.add(p)
            return p
        }
        return null
    }

    private fun directionHint(from: Pos, to: Pos): String {
        val vertical = when {
            to.y < from.y -> "向上"
            to.y > from.y -> "向下"
            else -> ""
        }
        val horizontal = when {
            to.x < from.x -> "向左"
            to.x > from.x -> "向右"
            else -> ""
        }
        return listOf(vertical, horizontal).filter { it.isNotBlank() }.joinToString(" ").ifBlank { "原地" }
    }

    private fun visibleCellsAt(center: Pos): Set<Pos> {
        val halfLeft = (miniMapSpan - 1) / 2
        val halfRight = miniMapSpan / 2
        val xs = (center.x - halfLeft)..(center.x + halfRight)
        val ys = (center.y - halfLeft)..(center.y + halfRight)
        val result = mutableSetOf<Pos>()
        for (x in xs) {
            for (y in ys) {
                val p = Pos(x, y)
                if (x in 0 until state.maze.width && y in 0 until state.maze.height) {
                    result.add(p)
                }
            }
        }
        return result
    }

    private fun revealAroundCurrentPos() {
        exploredCells.addAll(visibleCellsAt(state.pos))
    }

    private fun triggerMapMarkersIfNeeded(): Boolean {
        var triggered = false
        val pos = state.pos
        if (mountMarkerPos == pos) {
            mountMarkerPos = null
            val mount = mountCatalog().random(rng).first
            addItem("坐骑:$mount", 1)
            log("发现坐骑踪迹，获得坐骑契约：$mount")
            triggered = true
        }
        if (treasureMarkerPos == pos) {
            treasureMarkerPos = null
            val mat = chapterMaterial()
            addItem(mat, 2)
            if (rng.nextDouble() < 0.55) addItem("灵石", 1)
            if (rng.nextDouble() < 0.25) addItem("基础锻造箱", 1)
            log("找到宝材点：${displayItemName(mat)} +2")
            triggered = true
        }
        if (bossMarkerPos == pos) {
            bossMarkerPos = null
            log("首领现身，迎战中")
            battle(buildBossEnemy())
            triggered = true
        }
        return triggered
    }

    private fun buildBossEnemy(): Enemy {
        val chap = state.chapter.idx
        val scale = chapters[chap].enemyScale
        val secretFactor = if (secretMode) 1.25 else 1.0
        val hp = ((180 + chap * 56) * scale * secretFactor).toInt()
        val atk = ((24 + chap * 7) * scale * secretFactor).toInt()
        val def = ((10 + chap * 3) * scale * secretFactor).toInt()
        val spd = ((11 + chap) * scale * secretFactor).toInt()
        val exp = 36 + chap * 24
        val gold = 24 + chap * 10
        return Enemy("首领·第${chap + 1}章守关者", hp, hp, atk, def, spd, exp, gold)
    }

    private fun randomEnemy(): Enemy {
        val chap = state.chapter.idx
        val scale = chapters[chap].enemyScale
        val secretFactor = if (secretMode) 1.18 else 1.0
        val hp = ((70 + chap * 28) * scale * secretFactor).toInt() + rng.nextInt(0, 18)
        val atk = ((12 + chap * 4) * scale * secretFactor).toInt() + rng.nextInt(0, 5)
        val def = ((5 + chap * 2) * scale * secretFactor).toInt() + rng.nextInt(0, 4)
        val spd = ((8 + chap) * scale * secretFactor).toInt() + rng.nextInt(0, 3)
        val exp = 10 + chap * 14 + rng.nextInt(0, 8)
        val gold = 8 + chap * 6 + rng.nextInt(0, 8)
        val namePool = listOf("矿区恶徒", "石皮虫", "裂岩巨蜥", "影刃游侠")
        val name = namePool.random(rng)
        return Enemy(name, hp, hp, atk, def, spd, exp, gold)
    }

    private fun battle(enemy: Enemy) {
        val pl = state.player
        lastBattleSummary = "遭遇 ${enemy.name}（HP ${enemy.maxHp}）"
        log("遭遇 ${enemy.name}")
        var stunnedEnemy = 0
        var shieldTurns = 0
        var round = 1

        while (pl.hp > 0 && enemy.hp > 0 && round <= 30) {
            pl.skills.forEach { if (it.cdNow > 0) it.cdNow -= 1 }
            val playerFirst = (pl.spd + pl.mountSpdBonus + gearSpdBonus()) >= enemy.spd

            fun playerAct() {
                val useSkill = rng.nextDouble() < 0.55
                val skill = if (useSkill) pl.skills.filter { it.cdNow <= 0 }.randomOrNull(rng) else null
                if (skill != null) {
                    val base = max(1, ((pl.atk + pl.gearAtkBonus) * skill.ratio).toInt() - enemy.def / 2)
                    enemy.hp -= base
                    log("你施放 ${skill.name}，造成 $base 伤害")
                    skill.cdNow = skill.cdMax
                    if (skill.effect == "stun" && rng.nextDouble() < 0.45) {
                        stunnedEnemy = 1
                        log("${enemy.name} 被眩晕")
                    }
                    if (skill.effect == "shield") {
                        shieldTurns = 1
                        log("你获得一回合护盾")
                    }
                } else {
                    val dmg = max(1, (pl.atk + pl.gearAtkBonus) - enemy.def / 2)
                    enemy.hp -= dmg
                    log("你普通攻击造成 $dmg 伤害")
                }
            }

            fun enemyAct() {
                if (stunnedEnemy > 0) {
                    stunnedEnemy -= 1
                    log("${enemy.name} 眩晕，无法行动")
                    return
                }
                var edmg = max(1, enemy.atk - (pl.def + pl.gearDefBonus) / 2)
                if (shieldTurns > 0) {
                    edmg = max(1, (edmg * 0.6).toInt())
                    shieldTurns -= 1
                }
                pl.hp -= edmg
                log("${enemy.name} 造成 $edmg 伤害")
            }

            if (playerFirst) {
                playerAct()
                if (enemy.hp > 0) enemyAct()
            } else {
                enemyAct()
                if (pl.hp > 0) playerAct()
            }

            round += 1
        }

        if (pl.hp <= 0) {
            pl.hp = 0
            applyBattleDurability(round)
            lastBattleSummary = "败给 ${enemy.name}"
            onPlayerDeath("战斗败亡:${enemy.name}")
            return
        }

        pl.kills += 1
        state.chapter.battles += 1
        pl.gold += enemy.gold
        addExp(enemy.exp)
        lastBattleSummary = "击败 ${enemy.name}（经验+${enemy.exp} 金币+${enemy.gold}）"
        log("战斗胜利：经验 +${enemy.exp} 金币 +${enemy.gold}")

        val luckMul = 1.0 + (pl.luck.coerceAtLeast(0) * 0.01)
        val dropMul = (if (secretMode) 1.35 else 1.0) * luckMul
        if (rng.nextDouble() < 0.18 * dropMul) addItem("灵石", 1)
        if (rng.nextDouble() < 0.22 * dropMul) addItem("回春药", 1)
        if (rng.nextDouble() < 0.28 * dropMul) addItem(chapterMaterial(), 1)
        if (rng.nextDouble() < 0.08 * dropMul) addItem("基础锻造箱", 1)
        if (rng.nextDouble() < 0.06 * dropMul) addItem("修理包", 1)
        if (rng.nextDouble() < 0.08 * dropMul) dropCollectible()
        applyBattleDurability(round)

        if (state.chapter.battles >= state.chapter.battleTarget) {
            log("本章目标已完成，前往出口后可进入下一章")
        }
    }

    private fun triggerNpcEncounter() {
        val pool = npcs.filter { it.alive }
        if (pool.isEmpty()) return
        val npc = pool.random(rng)
        if (npc.hostile) {
            val dmg = max(10, state.player.maxHp / 3)
            state.player.hp = max(1, state.player.hp - dmg)
            log("遭遇仇敌 ${npc.name} 伏击，损失 $dmg 生命")
        } else {
            if (npc.isLegacyEcho) {
                log("你遇见遗骸NPC ${npc.name}，可在 NPC 面板选择攻击夺取遗物")
            } else {
                log("你遇见了 ${npc.name}，可在 NPC 面板互动")
            }
        }
    }

    private fun addExp(amount: Int) {
        val pl = state.player
        pl.exp += amount
        while (pl.exp >= pl.expNext) {
            pl.exp -= pl.expNext
            pl.level += 1
            pl.expNext = (pl.expNext * 1.22 + 18).toInt()
            pl.maxHp += 10
            pl.hp = pl.maxHp
            pl.atk += 2
            pl.def += 1
            pl.spd += 1
            pl.freePoints += 3
            syncLifespanCap()
            log("升级到 Lv${pl.level}，属性提升，自由点 +3")
        }
    }

    private fun computeLifespanMonths(): Int {
        val pl = state.player
        return 240 + pl.realmIdx * 120 + pl.level * 6
    }

    private fun syncLifespanCap() {
        val pl = state.player
        pl.lifespanMonths = max(pl.lifespanMonths, computeLifespanMonths())
    }

    private fun currentMonth(): Int {
        return state.player.timeTick / 3
    }

    private fun advanceTime(ticks: Int = 1) {
        if (ticks <= 0) return
        val pl = state.player
        pl.timeTick += ticks
        pl.ageMonths = currentMonth()
        syncLifespanCap()
        val s = state.sect
        if (pl.timeTick % 3 == 0 && s.created) {
            autoRunSectMonthly()
            if (rng.nextDouble() < 0.25) {
                sectUnderAttack()
            }
        }
        if (pl.ageMonths >= pl.lifespanMonths) {
            pl.hp = 0
            lastBattleSummary = "寿元耗尽"
            onPlayerDeath("寿元耗尽")
        }
    }

    private fun strongestFactionTag(): String {
        val pl = state.player
        val scores = listOf(
            "人族" to pl.factionRepHuman,
            "妖族" to pl.factionRepYao,
            "魔族" to pl.factionRepMo,
            "仙族" to pl.factionRepXian,
        )
        val top = scores.maxByOrNull { it.second } ?: ("中立" to 0)
        return if (top.second <= 0) listOf("人族", "妖族", "魔族", "仙族").random(rng) else top.first
    }

    private fun generateLegacyStory(name: String, lifeId: Int, faction: String, cause: String): String {
        val chap = chapters[state.chapter.idx].name
        val fragments = listOf(
            "${name}#${lifeId}曾在${chap}鏖战不退",
            "其主修${faction}路数，执念不散",
            "终因${cause}陨落，遗恨化作残魂",
            "传闻其身携旧器，败之可得遗物",
        )
        return fragments.joinToString("，")
    }

    private fun onPlayerDeath(cause: String) {
        val pl = state.player
        if (pl.isDead && deadLifeIds.contains(pl.lifeId)) {
            return
        }
        pl.isDead = true
        pl.deathCount += 1
        usedLifeIds.add(pl.lifeId)
        deadLifeIds.add(pl.lifeId)
        val faction = strongestFactionTag()
        val legacyId = "legacy_${pl.lifeId}"
        if (npcs.none { it.id == legacyId }) {
            val loot = when {
                pl.level >= 18 -> "基础锻造箱"
                pl.level >= 10 -> listOf("basic_sword", "basic_armor", "基础锻造箱").random(rng)
                else -> listOf("basic_sword", "basic_armor").random(rng)
            }
            val npc = NpcState(
                id = legacyId,
                name = "遗骸·${pl.name}#${pl.lifeId}",
                faction = faction,
                background = generateLegacyStory(pl.name, pl.lifeId, faction, cause),
                goal = "守住生前遗物",
                relation = -80,
                mood = "执念",
                hint = "可击杀掉落装备",
                hostile = true,
                follow = false,
                alive = true,
                isLegacyEcho = true,
                lifeIdRef = pl.lifeId,
                noRespawn = true,
                combatPower = max(24, pl.level * 10 + pl.atk + pl.def),
                lootItem = loot,
                lastReply = "此身已朽，唯战而已。",
                memory = mutableListOf("死因:$cause"),
            )
            npcs.add(npc)
            log("ID#${pl.lifeId} 已封存，不可重用。遗骸NPC【${npc.name}】已生成")
        } else {
            log("ID#${pl.lifeId} 已封存，不可重用")
        }
        log("你已死亡，无法继续当前ID。请新生为新ID")
    }

    private fun addItem(itemId: String, n: Int) {
        val bag = state.player.bag
        bag[itemId] = (bag[itemId] ?: 0) + n
        if (itemId == "灵石") {
            state.player.lingshi += n
        }
        log("获得物品 ${rarityBadge(itemId)} ${displayItemName(itemId)} x$n")
    }

    private fun chapterMaterial(): String {
        return when (state.chapter.idx) {
            0 -> "灵草"
            1 -> "寒露"
            2 -> "赤砂"
            3 -> "玄铁"
            4 -> "星砂"
            5 -> "冰魄"
            6 -> "幽晶"
            7 -> "天火砂"
            8 -> "时纹石"
            else -> "星骸粉"
        }
    }

    private fun autoRunSectMonthly() {
        val s = state.sect
        if (!s.created) return
        val month = currentMonth()
        if (month <= s.lastAutoMonth) return
        s.lastAutoMonth = month
        s.month = month
        val lingshiGain = s.spiritField + s.library
        val herbGain = s.spiritField * 2
        val oreGain = s.mine * 2
        s.lingshi += lingshiGain
        s.herb += herbGain
        s.ore += oreGain

        s.disciples.filter { it.alive }.forEach {
            it.level += 1
        }

        state.player.gold += 15 + s.library * 4
        log("宗门月度结算：灵石+$lingshiGain 草药+$herbGain 矿石+$oreGain")
    }

    private fun sectUnderAttack() {
        val s = state.sect
        if (!s.created) return
        val aliveDisciples = s.disciples.filter { it.alive }
        if (aliveDisciples.isEmpty()) return
        val avgPower = aliveDisciples.map { discipleCombatPower(it) }.average()
        val casualtyChance = max(0.15, 0.5 - s.defense * 0.06 - avgPower * 0.008)
        val victim = aliveDisciples.random(rng)
        if (rng.nextDouble() < casualtyChance) {
            if (tryConsumeRelicProtection(victim, "宗门被袭")) {
                victim.defBonus += 1
            } else {
                victim.alive = false
                log("宗门被袭，弟子 ${victim.name} 陨落")
            }
        } else {
            val reward = 8 + s.defense
            state.player.gold += reward
            log("宗门击退来敌，守成奖励 金币+$reward")
        }
    }

    fun isDead(): Boolean = state.player.isDead

    private fun resetForLife(newName: String, lifeId: Int, deathCount: Int): Boolean {
        state.log.clear()
        state.player.apply {
            this.name = newName
            this.lifeId = lifeId
            level = 1
            exp = 0
            expNext = 30
            hp = 120
            maxHp = 120
            atk = 14
            def = 6
            spd = 8
            gold = 50
            lingshi = 0
            freePoints = 0
            timeTick = 0
            ageMonths = 0
            lifespanMonths = 246
            realmIdx = 0
            gearLevel = 0
            legacyForgeAtkBonus = 0
            legacyForgeDefBonus = 0
            gearAtkBonus = 0
            gearDefBonus = 0
            mountName = ""
            mountSpdBonus = 0
            luck = 0
            collectibleName = ""
            collectibleHpBonus = 0
            collectibleAtkBonus = 0
            collectibleDefBonus = 0
            collectibleSpdBonus = 0
            isDead = false
            this.deathCount = deathCount
            factionRepHuman = 0
            factionRepYao = 0
            factionRepMo = 0
            factionRepXian = 0
            bag.clear()
            methods.clear()
            skills.clear()
            talents.clear()
            collectibles.clear()
            equipments.clear()
            knownBlueprints.clear()
            kills = 0
        }
        ensurePlayerSystems()
        initTalentsForNewLife()
        initStarterBlueprints()
        state.sect.apply {
            created = false
            name = ""
            month = 0
            lastAutoMonth = -1
            spiritField = 1
            mine = 0
            library = 0
            defense = 0
            lingshi = 0
            herb = 0
            ore = 0
            vault.clear()
            uniqueRelics.clear()
            disciples.clear()
        }
        npcs.filter { !it.isLegacyEcho }.forEach {
            it.alive = true
            it.relation = if (it.id == "npc_fengyin") 5 else 0
            it.mood = "平静"
            it.hint = "不引导"
            it.hostile = false
            it.follow = false
            it.lastReply = ""
            it.memory.clear()
        }
        moveTick = 0
        secretMode = false
        npcLastRaw = ""
        npcLastError = ""
        lastBattleSummary = "暂无战斗"
        loadChapter(0)
        refreshGearBonuses()
        usedLifeIds.add(lifeId)
        nextLifeId = max(nextLifeId, lifeId + 1)
        return true
    }

    fun restartCurrentLife(): Boolean {
        if (state.player.isDead) {
            log("当前ID#${state.player.lifeId}已陨落，禁止重开复用。请点击新生")
            return false
        }
        val oldName = state.player.name
        val oldId = state.player.lifeId
        val oldDeath = state.player.deathCount
        resetForLife(oldName, state.player.lifeId, oldDeath)
        appendOpeningStory("restart", oldId)
        log("已重开：沿用当前ID#${state.player.lifeId}与名字重新开始")
        return true
    }

    fun rebirth(newName: String): Boolean {
        val oldId = state.player.lifeId
        while (usedLifeIds.contains(nextLifeId) || deadLifeIds.contains(nextLifeId)) {
            nextLifeId += 1
        }
        val assignedId = nextLifeId
        nextLifeId += 1
        val name = newName.trim().ifEmpty { "新生旅者$assignedId" }
        val deathCount = state.player.deathCount
        resetForLife(name, assignedId, deathCount)
        appendOpeningStory("rebirth", oldId)
        log("新生完成：${state.player.name}（新ID#$assignedId，旧ID#$oldId 已封存）")
        return true
    }

    private fun ensureAlive(): Boolean {
        if (!state.player.isDead) return true
        log("你已死亡，当前ID已封存。请点击新生")
        return false
    }

    private fun appendOpeningStory(mode: String, oldId: Int = 0) {
        val p = state.player
        val chapter = chapters[state.chapter.idx]
        val base = listOf(
            "【序章】灵潮复苏三百年，凡俗王朝退居一隅，人妖魔仙四族争夺灵脉。",
            "【身世】你名为${p.name}（ID#${p.lifeId}），以散修之身踏入${chapter.name}。",
            "【目标】先活下来，再立宗门、收弟子、争地盘，最终问鼎天门。",
            "【规则】陨落者会化作遗骸NPC，遗物可夺，命数不可回头。"
        )
        val extra = when (mode) {
            "restart" -> "【回溯】你以同一命格重走旧路，这一次要改写开局。"
            "rebirth" -> "【新生】旧ID#$oldId 已封存，你将以全新命格再入尘世。"
            else -> "【开局】矿道风声如刃，第一步便是生死分界。"
        }
        base.forEach { log(it) }
        log(extra)
    }

    private fun buildTalentPool(): List<TalentState> {
        val names = listOf(
            "凡骨", "坚韧", "敏捷", "灵息", "护体", "锋锐", "沉稳", "悟道", "天听", "神行",
            "黄阶金骨", "黄阶木灵", "黄阶水脉", "黄阶火种", "黄阶土息", "黄阶迅影", "黄阶韧甲", "黄阶灵慧", "黄阶气府", "黄阶雷感",
            "玄阶金体", "玄阶木魄", "玄阶水纹", "玄阶火魄", "玄阶土魄", "玄阶风息", "玄阶镇岳", "玄阶破军", "玄阶灵眼", "玄阶天筹",
            "地阶道体", "地阶剑心", "地阶丹魂", "地阶器骨", "地阶战脉", "地阶护心", "地阶疾风", "地阶厚土", "地阶烈阳", "地阶寒月",
            "天阶圣体", "天阶神识", "天阶龙血", "天阶凤骨", "天阶玄武", "天阶麒麟", "天阶星眸", "天阶命格", "天阶无垢", "天阶道种"
        )
        val list = mutableListOf<TalentState>()
        names.forEachIndexed { idx, n ->
            val tier = idx / 10
            val scale = tier + 1
            list.add(
                TalentState(
                    id = "tal_$idx",
                    name = n,
                    tier = tier,
                    hp = 4 * scale,
                    atk = 1 * scale,
                    def = if (idx % 2 == 0) 1 * scale else 0,
                    spd = if (idx % 3 == 0) 1 * scale else 0,
                    luck = scale
                )
            )
        }
        return list
    }

    private fun initTalentsForNewLife() {
        val pl = state.player
        if (pl.talents.isNotEmpty()) return
        val count = rng.nextInt(1, 4)
        val rolled = talentPool.shuffled(rng).take(count)
        pl.talents.clear()
        pl.talents.addAll(rolled)
        rolled.forEach {
            pl.maxHp += it.hp
            pl.hp += it.hp
            pl.atk += it.atk
            pl.def += it.def
            pl.spd += it.spd
            pl.luck += it.luck
        }
        val names = rolled.joinToString("、") { it.name }
        log("天赋觉醒：$names")
    }

    private fun initDefaultCollectibleCatalog() {
        if (collectibleTemplatesByRarity.isNotEmpty()) return
        val defaults = listOf(
            CollectibleTemplate("W-001", "道纹贴纸·简线套装", "白", hp = 6, atk = 1, def = 1, spd = 0),
            CollectibleTemplate("W-002", "矿务票据·常制", "白", hp = 7, atk = 1, def = 1, spd = 0),
            CollectibleTemplate("W-003", "药坊绷带·常备", "白", hp = 8, atk = 1, def = 1, spd = 0),
            CollectibleTemplate("W-004", "宗门令牌·通用款", "白", hp = 9, atk = 1, def = 1, spd = 0),
            CollectibleTemplate("W-005", "巡山木哨·民制", "白", hp = 8, atk = 1, def = 1, spd = 0),
            CollectibleTemplate("W-006", "玄铁徽记·试铸", "白", hp = 10, atk = 1, def = 1, spd = 0),
            CollectibleTemplate("L-001", "修行手札·周计划本", "绿", hp = 10, atk = 2, def = 1, spd = 0),
            CollectibleTemplate("L-002", "古玉佩·民匠款", "绿", hp = 11, atk = 2, def = 1, spd = 0),
            CollectibleTemplate("L-003", "灵纹护符·简刻", "绿", hp = 12, atk = 2, def = 2, spd = 0),
            CollectibleTemplate("L-004", "星纹戒·素胚", "绿", hp = 12, atk = 2, def = 2, spd = 0),
            CollectibleTemplate("L-005", "丹诀残页·拓本", "绿", hp = 13, atk = 2, def = 2, spd = 0),
            CollectibleTemplate("L-006", "天工符·草绘", "绿", hp = 14, atk = 2, def = 2, spd = 0),
            CollectibleTemplate("B-001", "东荒地志·折页地图", "蓝", hp = 14, atk = 3, def = 2, spd = 1),
            CollectibleTemplate("B-002", "古路残卷·抄录本", "蓝", hp = 15, atk = 3, def = 2, spd = 1),
            CollectibleTemplate("B-003", "阵图铜片·星桥款", "蓝", hp = 16, atk = 3, def = 3, spd = 1),
            CollectibleTemplate("B-004", "玄甲纹拓·寒渊版", "蓝", hp = 17, atk = 3, def = 3, spd = 1),
            CollectibleTemplate("B-005", "裂谷风标·战地版", "蓝", hp = 18, atk = 3, def = 3, spd = 1),
            CollectibleTemplate("B-006", "工匠印契·官铸", "蓝", hp = 18, atk = 3, def = 3, spd = 1),
            CollectibleTemplate("P-001", "荒古圣体·血脉徽章", "紫", hp = 20, atk = 4, def = 4, spd = 1),
            CollectibleTemplate("P-002", "太阴玉兔·图谱铭片", "紫", hp = 21, atk = 4, def = 4, spd = 1),
            CollectibleTemplate("P-003", "星骸终局·指挥纹章", "紫", hp = 22, atk = 5, def = 4, spd = 1),
            CollectibleTemplate("P-004", "时隙回廊·断章", "紫", hp = 23, atk = 5, def = 4, spd = 1),
            CollectibleTemplate("P-005", "禁庭废都·龙纹砖拓", "紫", hp = 24, atk = 5, def = 5, spd = 1),
            CollectibleTemplate("P-006", "暗域裂谷·魔印封片", "紫", hp = 24, atk = 5, def = 5, spd = 1),
            CollectibleTemplate("G-001", "吞天魔罐·迷你陈列罐", "金", hp = 28, atk = 6, def = 5, spd = 1),
            CollectibleTemplate("G-002", "无始钟·共鸣摆件", "金", hp = 30, atk = 6, def = 5, spd = 1),
            CollectibleTemplate("G-003", "九龙拉棺·微缩遗座", "金", hp = 32, atk = 6, def = 6, spd = 1),
            CollectibleTemplate("R-001", "荒塔·道痕浮雕", "红", hp = 36, atk = 8, def = 7, spd = 2),
            CollectibleTemplate("R-002", "不死山·禁区拓卷", "红", hp = 38, atk = 8, def = 7, spd = 2),
        )
        defaults.forEach { item ->
            collectibleTemplatesByRarity.getOrPut(item.rarity) { mutableListOf() }.add(item)
        }
    }

    private fun collectiblePoolByRarity(rarity: String): List<CollectibleTemplate> {
        val direct = collectibleTemplatesByRarity[rarity].orEmpty()
        if (direct.isNotEmpty()) return direct
        val fallbackOrder = listOf("白", "绿", "蓝", "紫", "金", "红")
        val idx = fallbackOrder.indexOf(rarity).coerceAtLeast(0)
        for (i in idx downTo 0) {
            val picked = collectibleTemplatesByRarity[fallbackOrder[i]].orEmpty()
            if (picked.isNotEmpty()) return picked
        }
        return collectibleTemplatesByRarity.values.flatten()
    }

    private fun dropCollectible() {
        val chap = state.chapter.idx
        val rarity = when {
            chap >= 8 -> listOf("紫", "金", "红")
            chap >= 5 -> listOf("蓝", "紫", "金")
            chap >= 2 -> listOf("绿", "蓝", "紫")
            else -> listOf("白", "绿", "蓝")
        }.random(rng)
        addCollectibleByRarity(rarity)
    }

    private fun openLowCollectiblePack(): Boolean {
        val roll = rng.nextInt(1, 101)
        val rarity = when {
            roll <= 60 -> "白"
            roll <= 90 -> "绿"
            else -> "蓝"
        }
        addCollectibleByRarity(rarity)
        log("开启低阶收藏品包")
        return true
    }

    private fun addCollectibleByRarity(rarity: String) {
        val pool = collectiblePoolByRarity(rarity)
        if (pool.isEmpty()) return
        val pick = pool.random(rng)
        val existed = state.player.collectibles.find { it.id == pick.id }
            ?: state.player.collectibles.find { it.name == pick.name && it.rarity == pick.rarity }
        if (existed != null) {
            existed.level += 1
            log("收藏品升级：${existed.name} ${existed.rarity} Lv${existed.level}")
            return
        }
        val c = CollectibleState(
            id = pick.id,
            name = pick.name,
            rarity = pick.rarity,
            level = 1,
            hp = pick.hp,
            atk = pick.atk,
            def = pick.def,
            spd = pick.spd,
        )
        state.player.collectibles.add(c)
        log("获得收藏品：${c.name}·${c.rarity}")
    }

    private fun useInsightPill(itemId: String): Boolean {
        val parts = itemId.split("_")
        if (parts.size < 4) {
            log("悟性丹格式错误")
            return false
        }
        val element = parts[2]
        val method = state.player.methods.find { it.element == element } ?: state.player.methods.randomOrNull()
        if (method == null) {
            log("当前无可提升功法")
            return false
        }
        val gain = if (element == "时间" || element == "空间") 10 else 8
        method.progress += gain
        log("服用悟性丹：${element}系功法进度 +$gain")
        while (method.progress >= method.need) {
            method.progress -= method.need
            method.stage += 1
            method.need = (method.need * 1.25 + 8).toInt()
            if (method.stage >= 4) {
                state.player.atk += 1
                state.player.def += 1
                log("${method.name} 圆满增益触发，攻击+1 防御+1")
            } else {
                log("${method.name} 达到 ${methodStageName(method.stage)}")
            }
        }
        return true
    }

    private fun buildBlueprintCatalog(): List<BlueprintState> {
        return listOf(
            BlueprintState("bp_weapon_t0", "矿道短刃", "weapon", 0, atk = 3, def = 0, spd = 0, materials = mapOf("灵草" to 2, "寒露" to 1)),
            BlueprintState("bp_head_t0", "青藤冠", "head", 0, atk = 0, def = 2, spd = 1, materials = mapOf("灵草" to 1, "寒露" to 1)),
            BlueprintState("bp_body_t0", "矿皮甲", "body", 0, atk = 0, def = 4, spd = 0, materials = mapOf("灵草" to 2, "赤砂" to 1)),
            BlueprintState("bp_boots_t0", "踏尘履", "boots", 0, atk = 0, def = 1, spd = 2, materials = mapOf("寒露" to 1, "赤砂" to 1)),
            BlueprintState("bp_accessory_t0", "凝息佩", "accessory", 0, atk = 1, def = 1, spd = 0, materials = mapOf("灵草" to 1, "赤砂" to 1)),

            BlueprintState("bp_weapon_t1", "裂岩锋", "weapon", 1, atk = 6, def = 1, spd = 0, materials = mapOf("赤砂" to 2, "玄铁" to 2)),
            BlueprintState("bp_head_t1", "玄铁盔", "head", 1, atk = 0, def = 5, spd = 0, materials = mapOf("赤砂" to 1, "玄铁" to 2)),
            BlueprintState("bp_body_t1", "护脉铠", "body", 1, atk = 0, def = 8, spd = 0, materials = mapOf("赤砂" to 2, "玄铁" to 2)),
            BlueprintState("bp_boots_t1", "逐风靴", "boots", 1, atk = 0, def = 2, spd = 4, materials = mapOf("赤砂" to 2, "玄铁" to 1)),
            BlueprintState("bp_accessory_t1", "镇心符", "accessory", 1, atk = 2, def = 2, spd = 1, materials = mapOf("玄铁" to 1, "寒露" to 2)),

            BlueprintState("bp_weapon_t2", "寒星刃", "weapon", 2, atk = 10, def = 2, spd = 1, materials = mapOf("星砂" to 2, "冰魄" to 2)),
            BlueprintState("bp_head_t2", "冰纹冕", "head", 2, atk = 0, def = 8, spd = 2, materials = mapOf("星砂" to 1, "冰魄" to 2)),
            BlueprintState("bp_body_t2", "星河战铠", "body", 2, atk = 1, def = 12, spd = 0, materials = mapOf("星砂" to 2, "冰魄" to 2)),
            BlueprintState("bp_boots_t2", "流云履", "boots", 2, atk = 0, def = 3, spd = 7, materials = mapOf("星砂" to 1, "冰魄" to 2)),
            BlueprintState("bp_accessory_t2", "凝魄环", "accessory", 2, atk = 3, def = 3, spd = 1, materials = mapOf("冰魄" to 2, "寒露" to 2)),

            BlueprintState("bp_weapon_t3", "焚天戟", "weapon", 3, atk = 14, def = 3, spd = 2, materials = mapOf("幽晶" to 2, "天火砂" to 2)),
            BlueprintState("bp_head_t3", "玄幽冠", "head", 3, atk = 1, def = 11, spd = 2, materials = mapOf("幽晶" to 2, "天火砂" to 1)),
            BlueprintState("bp_body_t3", "幽火战袍", "body", 3, atk = 2, def = 16, spd = 1, materials = mapOf("幽晶" to 2, "天火砂" to 2)),
            BlueprintState("bp_boots_t3", "天火步", "boots", 3, atk = 0, def = 5, spd = 10, materials = mapOf("幽晶" to 1, "天火砂" to 2)),
            BlueprintState("bp_accessory_t3", "镇域印", "accessory", 3, atk = 4, def = 4, spd = 2, materials = mapOf("天火砂" to 2, "玄铁" to 2)),

            BlueprintState("bp_weapon_t4", "星骸诛仙刃", "weapon", 4, atk = 19, def = 4, spd = 3, materials = mapOf("时纹石" to 2, "星骸粉" to 2)),
            BlueprintState("bp_head_t4", "时轮冕", "head", 4, atk = 1, def = 15, spd = 3, materials = mapOf("时纹石" to 2, "星骸粉" to 1)),
            BlueprintState("bp_body_t4", "天阙神铠", "body", 4, atk = 3, def = 22, spd = 1, materials = mapOf("时纹石" to 2, "星骸粉" to 2)),
            BlueprintState("bp_boots_t4", "裂空履", "boots", 4, atk = 1, def = 6, spd = 14, materials = mapOf("时纹石" to 2, "星骸粉" to 1)),
            BlueprintState("bp_accessory_t4", "命星佩", "accessory", 4, atk = 6, def = 6, spd = 3, materials = mapOf("时纹石" to 1, "星骸粉" to 2)),
        )
    }

    private fun slotLabel(slot: String): String {
        return slotName[slot] ?: slot
    }

    private fun tierName(tier: Int): String {
        return when (tier.coerceIn(0, 4)) {
            0 -> "黄"
            1 -> "玄"
            2 -> "地"
            3 -> "天"
            else -> "神"
        }
    }

    private fun refreshGearBonuses() {
        val pl = state.player
        var atk = pl.legacyForgeAtkBonus
        var def = pl.legacyForgeDefBonus
        pl.equipments.values.forEach { eq ->
            if (eq.durability > 0) {
                atk += eq.atk
                def += eq.def
            }
        }
        pl.gearAtkBonus = atk
        pl.gearDefBonus = def
    }

    private fun gearSpdBonus(): Int {
        return state.player.equipments.values.filter { it.durability > 0 }.sumOf { it.spd }
    }

    private fun applyBattleDurability(round: Int) {
        val loss = max(1, round / 8)
        equipmentSlots.forEach { applyDurabilityLoss(it, loss, silent = true) }
        refreshGearBonuses()
    }

    private fun applyDurabilityLoss(slot: String, amount: Int, silent: Boolean = false) {
        if (amount <= 0) return
        val eq = state.player.equipments[slot] ?: return
        val prev = eq.durability
        eq.durability = max(0, eq.durability - amount)
        if (!silent && prev > 0 && eq.durability == 0) {
            log("${eq.name} 耐久归零，效果失效，请尽快修理")
        }
        if (prev > 0 && eq.durability == 0) {
            refreshGearBonuses()
        }
    }

    private fun repairEquipment(slot: String, silent: Boolean): Boolean {
        val pl = state.player
        val eq = pl.equipments[slot] ?: return false
        val missing = eq.maxDurability - eq.durability
        if (missing <= 0) return false

        val kit = pl.bag["修理包"] ?: 0
        if (kit > 0) {
            if (kit == 1) pl.bag.remove("修理包") else pl.bag["修理包"] = kit - 1
            eq.durability = eq.maxDurability
            if (!silent) log("使用修理包修复 ${eq.name}")
            refreshGearBonuses()
            return true
        }

        val mat = repairMaterialForTier(eq.tier)
        val matNeed = max(1, missing / 25)
        val goldNeed = max(12, missing * (eq.tier + 1))
        if ((pl.bag[mat] ?: 0) < matNeed || pl.gold < goldNeed) {
            if (!silent) log("修理失败：需要 $mat x$matNeed 与金币$goldNeed")
            return false
        }
        pl.gold -= goldNeed
        val left = (pl.bag[mat] ?: 0) - matNeed
        if (left <= 0) pl.bag.remove(mat) else pl.bag[mat] = left
        eq.durability = eq.maxDurability
        if (!silent) log("修理完成：${eq.name}（-$matNeed $mat，-$goldNeed 金币）")
        refreshGearBonuses()
        return true
    }

    private fun repairMaterialForTier(tier: Int): String {
        return when (tier.coerceIn(0, 4)) {
            0 -> "赤砂"
            1 -> "玄铁"
            2 -> "星砂"
            3 -> "天火砂"
            else -> "时纹石"
        }
    }

    private fun buildNpcPrompt(npc: NpcState, playerText: String): String {
        val pl = state.player
        val chap = chapters[state.chapter.idx]
        val memory = if (npc.memory.isEmpty()) {
            "无"
        } else {
            npc.memory.takeLast(3).joinToString(" | ") { it.take(24) }
        }
        return """
角色:${npc.name} 阵营:${npc.faction}
背景:${npc.background.take(32)} 目标:${npc.goal.take(24)}
心情:${npc.mood} 关系:${npc.relation} 提示:${npc.hint.take(16)}
记忆:${memory}
玩家:Lv${pl.level} ${realms[pl.realmIdx.coerceIn(0, realms.lastIndex)]} ${chap.name}
玩家发言:${playerText.take(60)}
仅输出一行JSON:
{"reply":"中文回复","mood":"平静","relation_delta":0,"hint":"简短提示","memory":"新增记忆"}
reply需直接回应玩家, 不超28字, 禁止模板复读.
""".trimIndent()
    }

    private fun parseNpcLlmReply(npc: NpcState, raw: String): String? {
        val jsonText = extractJsonObject(raw)
        if (jsonText.isNullOrBlank()) {
            val plain = raw.lineSequence().firstOrNull { it.isNotBlank() }?.trim().orEmpty()
            return if (plain.isBlank()) null else plain
        }
        return try {
            val obj = JSONObject(jsonText)
            val reply = obj.optString("reply", "").trim().ifBlank {
                obj.optString("text", "").trim()
            }
            val moodValue = obj.opt("mood")
            if (moodValue != null) {
                npc.mood = when (moodValue) {
                    is Number -> when {
                        moodValue.toInt() >= 80 -> "亲近"
                        moodValue.toInt() >= 40 -> "友好"
                        moodValue.toInt() >= 0 -> "平静"
                        else -> "警惕"
                    }
                    else -> moodValue.toString().take(10)
                }
            }
            if (obj.has("relation_delta")) {
                val delta = obj.optInt("relation_delta", 0).coerceIn(-5, 5)
                npc.relation = (npc.relation + delta).coerceIn(-100, 100)
            } else if (obj.has("relation")) {
                val rel = obj.optInt("relation", npc.relation).coerceIn(-100, 100)
                npc.relation = rel
            }
            val hint = obj.optString("hint", "").trim()
            if (hint.isNotBlank()) npc.hint = hint.take(32)
            val memory = obj.optString("memory", "").trim()
            if (memory.isNotBlank()) appendNpcMemory(npc, "记忆:$memory")
            if (reply.isBlank()) null else reply.take(40)
        } catch (e: Throwable) {
            npcLastError = "JSON解析失败:${e.message ?: "unknown"}"
            null
        }
    }

    private fun extractJsonObject(text: String): String? {
        val start = text.indexOf('{')
        if (start < 0) return null
        val end = text.lastIndexOf('}')
        if (end <= start) return null
        return text.substring(start, end + 1)
    }

    private fun appendNpcMemory(npc: NpcState, line: String) {
        val content = line.trim()
        if (content.isBlank()) return
        npc.memory.add(content.take(80))
        while (npc.memory.size > 10) {
            npc.memory.removeAt(0)
        }
    }

    private fun discipleItemBonus(itemId: String): Triple<Int, Int, Int> {
        return when {
            itemId.contains("剑") || itemId.contains("刃") || itemId.contains("戟") || itemId.contains("枪") || itemId.contains("sword", true) ->
                Triple(3, 1, 0)
            itemId.contains("甲") || itemId.contains("盔") || itemId.contains("盾") ->
                Triple(1, 3, 0)
            itemId.contains("靴") || itemId.contains("履") || itemId.contains("boots", true) ->
                Triple(0, 1, 3)
            itemId.contains("treasure_", true) || itemId.contains("收藏", true) ->
                Triple(2, 2, 1)
            else -> Triple(1, 1, 1)
        }
    }

    private fun discipleCombatPower(d: DiscipleState): Int {
        return d.level * 3 + d.apt * 2 + d.atkBonus * 2 + d.defBonus + d.spdBonus
    }

    private fun tryConsumeRelicProtection(d: DiscipleState, scene: String): Boolean {
        if (d.relicCharges <= 0) return false
        d.relicCharges -= 1
        val relic = if (d.lifeGuardRelic.isBlank()) "护命宝物" else d.lifeGuardRelic
        log("${d.name} 触发${relic}，在${scene}中保住性命")
        if (d.relicCharges <= 0) {
            d.lifeGuardRelic = ""
        }
        return true
    }

    private fun methodStageName(stage: Int): String {
        return when {
            stage <= 0 -> "入门"
            stage == 1 -> "小成"
            stage == 2 -> "中期"
            stage == 3 -> "大成"
            else -> "圆满"
        }
    }

    private fun randomDiscipleName(existing: Set<String>): String {
        repeat(240) {
            val surname = discipleSurnames.random(rng)
            val givenLen = when (surname.length) {
                1 -> rng.nextInt(1, 4) // total 2-4
                else -> rng.nextInt(1, 3) // total 3-4
            }
            val given = buildString {
                repeat(givenLen) {
                    append(discipleGivenChars.random(rng))
                }
            }
            val full = surname + given
            if (full.length in 2..4 && !existing.contains(full)) {
                return full
            }
        }
        while (true) {
            val fallback = "赵" + discipleGivenChars.random(rng) + discipleGivenChars.random(rng)
            if (!existing.contains(fallback)) return fallback
        }
    }

    private fun posToJson(pos: Pos): JSONObject {
        return JSONObject().apply {
            put("x", pos.x)
            put("y", pos.y)
        }
    }

    private fun posFromJson(obj: JSONObject?): Pos? {
        if (obj == null) return null
        if (!obj.has("x") || !obj.has("y")) return null
        val x = obj.optInt("x", Int.MIN_VALUE)
        val y = obj.optInt("y", Int.MIN_VALUE)
        if (x == Int.MIN_VALUE || y == Int.MIN_VALUE) return null
        return Pos(x, y)
    }

    private fun mazeToJson(maze: Maze): JSONObject {
        val blocksArr = JSONArray()
        maze.blocks.forEach { b ->
            blocksArr.put(posToJson(b))
        }
        return JSONObject().apply {
            put("width", maze.width)
            put("height", maze.height)
            put("start", posToJson(maze.start))
            put("exit", posToJson(maze.exit))
            put("blocks", blocksArr)
        }
    }

    private fun mazeFromJson(obj: JSONObject?): Maze? {
        if (obj == null) return null
        val width = obj.optInt("width", -1)
        val height = obj.optInt("height", -1)
        if (width < 8 || height < 8) return null
        val start = posFromJson(obj.optJSONObject("start")) ?: Pos(1, height - 2)
        val exit = posFromJson(obj.optJSONObject("exit")) ?: Pos(width - 2, 1)
        if (start.x !in 0 until width || start.y !in 0 until height) return null
        if (exit.x !in 0 until width || exit.y !in 0 until height) return null

        val blocks = mutableSetOf<Pos>()
        val arr = obj.optJSONArray("blocks")
        if (arr != null) {
            for (i in 0 until arr.length()) {
                val p = posFromJson(arr.optJSONObject(i)) ?: continue
                if (p.x in 0 until width && p.y in 0 until height && p != start && p != exit) {
                    blocks.add(p)
                }
            }
        }
        return Maze(width, height, start, exit, blocks)
    }

    private fun canWalkInMaze(maze: Maze, pos: Pos): Boolean {
        if (pos.x < 0 || pos.y < 0 || pos.x >= maze.width || pos.y >= maze.height) return false
        return !maze.blocks.contains(pos)
    }

    private fun canWalk(pos: Pos): Boolean {
        return canWalkInMaze(state.maze, pos)
    }

    private fun log(text: String) {
        state.log.addLast(text)
        while (state.log.size > 260) state.log.removeFirst()
    }

    private fun generateMaze(width: Int, height: Int): Maze {
        val start = Pos(1, height - 2)
        val exit = Pos(width - 2, 1)
        val blocks = mutableSetOf<Pos>()

        for (x in 0 until width) {
            blocks.add(Pos(x, 0))
            blocks.add(Pos(x, height - 1))
        }
        for (y in 0 until height) {
            blocks.add(Pos(0, y))
            blocks.add(Pos(width - 1, y))
        }

        val spine = mutableSetOf<Pos>()
        for (x in 1 until width - 1) spine.add(Pos(x, height - 2))
        for (y in 1 until height - 1) spine.add(Pos(width - 2, y))

        val density = 0.22
        for (x in 1 until width - 1) {
            for (y in 1 until height - 1) {
                val p = Pos(x, y)
                if (p == start || p == exit || p in spine) continue
                if (rng.nextDouble() < density) blocks.add(p)
            }
        }
        blocks.remove(start)
        blocks.remove(exit)

        return Maze(width, height, start, exit, blocks)
    }
}
