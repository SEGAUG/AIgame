package com.jinhui.immortaldemo

import android.content.Context
import android.graphics.Color
import android.os.Bundle
import android.view.View
import android.widget.ArrayAdapter
import android.widget.Button
import android.widget.CheckBox
import android.widget.EditText
import android.widget.LinearLayout
import android.widget.ScrollView
import android.widget.TextView
import android.widget.Toast
import androidx.appcompat.app.AlertDialog
import androidx.appcompat.app.AppCompatActivity
import com.jinhui.immortaldemo.core.GameCore
import com.jinhui.immortaldemo.core.LocalLlamaJni
import com.jinhui.immortaldemo.core.LocalLlamaProvider
import com.jinhui.immortaldemo.ui.MiniMapView

class MainActivity : AppCompatActivity() {
    private lateinit var core: GameCore
    private lateinit var info: TextView
    private lateinit var mapHint: TextView
    private lateinit var battleTop: TextView
    private lateinit var miniMap: MiniMapView
    private lateinit var logView: TextView
    private lateinit var logScroll: ScrollView

    private val saveKey = "immortal_demo_save_v1"
    private val npcLlmEnabledKey = "npc_llm_enabled"
    private val npcLlmModelKey = "npc_llm_model"
    private val npcLlmPredictKey = "npc_llm_predict"
    private val npcLlmThreadsKey = "npc_llm_threads"
    private var npcLlmEnabled = false
    private var npcLlmModelName = "Qwen2.5-0.5B-Instruct-Q4_K_M.gguf"
    private var npcLlmPredict = 48
    private var npcLlmThreads = 4
    private var deathPromptShown = false

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)

        core = GameCore()
        loadCollectibleCatalogFromAsset()
        info = findViewById(R.id.info)
        mapHint = findViewById(R.id.mapHint)
        battleTop = findViewById(R.id.battleTop)
        miniMap = findViewById(R.id.miniMapView)
        logView = findViewById(R.id.log)
        logScroll = findViewById(R.id.logScroll)
        loadNpcLlmConfig()
        bindSectionToggle(R.id.btnToggleExplore, R.id.sectionExplore, "战斗/探索", true)
        bindSectionToggle(R.id.btnToggleGrowth, R.id.sectionGrowth, "成长/养成", false)
        bindSectionToggle(R.id.btnToggleSocial, R.id.sectionSocial, "交互/势力", false)
        bindSectionToggle(R.id.btnToggleSystem, R.id.sectionSystem, "系统/存档", false)

        findViewById<Button>(R.id.btnUp).setOnClickListener { core.move(0, -1); refresh() }
        findViewById<Button>(R.id.btnDown).setOnClickListener { core.move(0, 1); refresh() }
        findViewById<Button>(R.id.btnLeft).setOnClickListener { core.move(-1, 0); refresh() }
        findViewById<Button>(R.id.btnRight).setOnClickListener { core.move(1, 0); refresh() }

        findViewById<Button>(R.id.btnNext).setOnClickListener { core.advanceChapter(); refresh() }
        findViewById<Button>(R.id.btnBag).setOnClickListener { showBag() }
        findViewById<Button>(R.id.btnCultivate).setOnClickListener { core.cultivate(); refresh() }
        findViewById<Button>(R.id.btnBreak).setOnClickListener { core.attemptBreakthrough(); refresh() }
        findViewById<Button>(R.id.btnPill).setOnClickListener { core.craftBreakthroughPill(); refresh() }
        findViewById<Button>(R.id.btnAllocate).setOnClickListener { showAllocatePanel() }
        findViewById<Button>(R.id.btnExchange).setOnClickListener { core.exchangeLingshi(); refresh() }
        findViewById<Button>(R.id.btnShop).setOnClickListener { showShop() }

        findViewById<Button>(R.id.btnNpc).setOnClickListener { showNpcList() }
        findViewById<Button>(R.id.btnChapter).setOnClickListener { showChapterList() }
        findViewById<Button>(R.id.btnMethod).setOnClickListener { showMethodList() }
        findViewById<Button>(R.id.btnSkill).setOnClickListener { showSkillList() }
        findViewById<Button>(R.id.btnSect).setOnClickListener { showSectPanel() }
        findViewById<Button>(R.id.btnSave).setOnClickListener { saveGame() }
        findViewById<Button>(R.id.btnLoad).setOnClickListener { loadGame() }
        findViewById<Button>(R.id.btnRestart).setOnClickListener {
            core.restartCurrentLife()
            deathPromptShown = false
            refresh()
        }
        findViewById<Button>(R.id.btnRebirth).setOnClickListener { showRebirthDialog() }
        findViewById<Button>(R.id.btnQuest).setOnClickListener { showQuestStatus() }
        findViewById<Button>(R.id.btnSecret).setOnClickListener { showSecretPanel() }
        findViewById<Button>(R.id.btnForge).setOnClickListener { showForgePanel() }
        findViewById<Button>(R.id.btnMount).setOnClickListener { showMountPanel() }
        findViewById<Button>(R.id.btnTalent).setOnClickListener { showTalentPanel() }
        findViewById<Button>(R.id.btnCollect).setOnClickListener { showCollectiblePanel() }

        refresh()
    }

    private fun refresh() {
        info.text = core.infoText()
        mapHint.text = core.mapHintText()
        battleTop.text = core.battleHudText()
        miniMap.submitSnapshot(core.miniMapSnapshot())
        logView.text = core.state.log.joinToString("\n")
        logScroll.post { logScroll.fullScroll(ScrollView.FOCUS_DOWN) }
        if (core.isDead()) {
            if (!deathPromptShown) {
                deathPromptShown = true
                showDeathDialog()
            }
        } else {
            deathPromptShown = false
        }
    }

    private fun loadCollectibleCatalogFromAsset() {
        try {
            val raw = assets.open("relic_catalog.json").bufferedReader(Charsets.UTF_8).use { it.readText() }
            val ok = core.importCollectibleCatalogJson(raw)
            if (!ok) {
                core.state.log.addLast("收藏目录加载失败，已使用内置目录。")
            }
        } catch (_: Exception) {
            core.state.log.addLast("未找到收藏目录资源，已使用内置目录。")
        }
    }

    private fun bindSectionToggle(toggleId: Int, sectionId: Int, title: String, expandedByDefault: Boolean) {
        val toggle = findViewById<Button>(toggleId)
        val section = findViewById<LinearLayout>(sectionId)
        section.visibility = if (expandedByDefault) View.VISIBLE else View.GONE
        toggle.text = if (expandedByDefault) "▼ $title" else "▶ $title"
        toggle.setOnClickListener {
            val expand = section.visibility != View.VISIBLE
            section.visibility = if (expand) View.VISIBLE else View.GONE
            toggle.text = if (expand) "▼ $title" else "▶ $title"
        }
    }

    private fun showDeathDialog() {
        AlertDialog.Builder(this)
            .setTitle("你已死亡")
            .setMessage("当前ID已封存不可复用，请新生为新ID。系统已生成对应遗骸NPC。")
            .setPositiveButton("新生") { _, _ ->
                showRebirthDialog()
            }
            .setNegativeButton("关闭", null)
            .show()
    }

    private fun showRebirthDialog() {
        val input = EditText(this)
        input.hint = "输入新名字"
        AlertDialog.Builder(this)
            .setTitle("新生")
            .setView(input)
            .setPositiveButton("确认") { _, _ ->
                core.rebirth(input.text.toString())
                deathPromptShown = false
                refresh()
            }
            .setNegativeButton("取消", null)
            .show()
    }

    private fun showBag() {
        val items = core.bagItems()
        if (items.isEmpty()) {
            AlertDialog.Builder(this).setTitle("背包").setMessage("空").setPositiveButton("关闭", null).show()
            return
        }
        val labels = items.map { "${core.rarityBadge(it.first)} ${core.displayItemName(it.first)} x${it.second}" }.toTypedArray()
        AlertDialog.Builder(this)
            .setTitle("背包（点击使用）")
            .setItems(labels) { _, which ->
                core.useItem(items[which].first)
                refresh()
            }
            .setNegativeButton("关闭", null)
            .show()
    }

    private fun showNpcList() {
        val npcs = core.npcList()
        val labels = npcs.map { "${it.name} | ${core.npcStatusText(it)}" }.toTypedArray()
        AlertDialog.Builder(this)
            .setTitle("NPC（${core.npcModelStatusText()}）")
            .setItems(labels) { _, idx -> showNpcActions(npcs[idx]) }
            .setNeutralButton("模型设置") { _, _ -> showNpcModelConfig() }
            .setNegativeButton("关闭", null)
            .show()
    }

    private fun showNpcActions(npc: com.jinhui.immortaldemo.core.NpcState) {
        val actions = arrayOf("对话", "赠礼", "交易", "攻击", "关闭")
        AlertDialog.Builder(this)
            .setTitle(npc.name)
            .setItems(actions) { dialog, which ->
                when (actions[which]) {
                    "对话" -> {
                        val input = EditText(this)
                        AlertDialog.Builder(this)
                            .setTitle("与${npc.name}对话")
                            .setView(input)
                            .setPositiveButton("发送") { _, _ ->
                                val text = input.text.toString()
                                Toast.makeText(this, "已发送，NPC思考中...", Toast.LENGTH_SHORT).show()
                                Thread {
                                    val reply = core.npcTalk(npc, text)
                                    runOnUiThread {
                                        refresh()
                                        if (reply.isNotBlank()) {
                                            Toast.makeText(this, "${npc.name}: $reply", Toast.LENGTH_LONG).show()
                                        }
                                    }
                                }.start()
                            }
                            .setNegativeButton("取消", null)
                            .show()
                    }
                    "赠礼" -> {
                        val items = core.bagItems()
                        if (items.isEmpty()) {
                            AlertDialog.Builder(this).setMessage("背包为空").setPositiveButton("关闭", null).show()
                            return@setItems
                        }
                        val labels = items.map { "${core.rarityBadge(it.first)} ${core.displayItemName(it.first)} x${it.second}" }.toTypedArray()
                        AlertDialog.Builder(this)
                            .setTitle("选择赠礼")
                            .setItems(labels) { _, i ->
                                core.npcGift(npc, items[i].first)
                                refresh()
                            }
                            .show()
                    }
                    "交易" -> {
                        val goods = listOf("回春药" to 20, "灵石" to 120, "破境丹" to 180)
                        val labels = goods.map { "${core.rarityBadge(it.first)} ${core.displayItemName(it.first)} - ${it.second}金币" }.toTypedArray()
                        AlertDialog.Builder(this)
                            .setTitle("交易")
                            .setItems(labels) { _, i ->
                                core.npcTrade(npc, goods[i].first, goods[i].second)
                                refresh()
                            }
                            .show()
                    }
                    "攻击" -> {
                        AlertDialog.Builder(this)
                            .setTitle("确认攻击")
                            .setMessage("攻击后该NPC将仇恨你")
                            .setPositiveButton("确认") { _, _ ->
                                core.npcAttack(npc)
                                refresh()
                            }
                            .setNegativeButton("取消", null)
                            .show()
                    }
                    else -> dialog.dismiss()
                }
            }
            .show()
    }

    private fun loadNpcLlmConfig() {
        val prefs = getSharedPreferences("immortal_demo", Context.MODE_PRIVATE)
        npcLlmEnabled = prefs.getBoolean(npcLlmEnabledKey, false)
        npcLlmModelName = prefs.getString(npcLlmModelKey, npcLlmModelName) ?: npcLlmModelName
        if (npcLlmModelName.startsWith("http://") || npcLlmModelName.startsWith("https://")) {
            npcLlmModelName = "Qwen2.5-0.5B-Instruct-Q4_K_M.gguf"
        }
        npcLlmPredict = prefs.getInt(npcLlmPredictKey, npcLlmPredict).coerceIn(16, 96)
        npcLlmThreads = prefs.getInt(npcLlmThreadsKey, npcLlmThreads).coerceIn(1, 8)
        applyNpcLlmConfig()
    }

    private fun applyNpcLlmConfig() {
        val provider = if (npcLlmEnabled) {
            LocalLlamaProvider(
                context = applicationContext,
                modelFileName = npcLlmModelName,
                nPredict = npcLlmPredict,
                nThreads = npcLlmThreads,
                nCtx = 1024,
                inferTimeoutMs = 12000,
            )
        } else {
            null
        }
        core.setNpcInferenceProvider(provider)
    }

    private fun showNpcModelConfig() {
        val panel = LinearLayout(this).apply {
            orientation = LinearLayout.VERTICAL
            setPadding(24, 12, 24, 8)
        }
        val enableCheck = CheckBox(this).apply {
            text = "启用本地LLM"
            isChecked = npcLlmEnabled
        }
        val modelInput = EditText(this).apply {
            hint = "模型文件名（已打包到APK资产）"
            setText(npcLlmModelName)
        }
        val predictInput = EditText(this).apply {
            hint = "每次回复最大token（建议 24~64）"
            setText(npcLlmPredict.toString())
        }
        val threadsInput = EditText(this).apply {
            hint = "推理线程数（建议 3~6）"
            setText(npcLlmThreads.toString())
        }
        panel.addView(enableCheck)
        panel.addView(modelInput)
        panel.addView(predictInput)
        panel.addView(threadsInput)

        AlertDialog.Builder(this)
            .setTitle("NPC模型配置")
            .setMessage("启用后直接使用手机本地模型推理；首次对话会拷贝+加载模型，可能需要10-60秒。失败会回退规则回复。")
            .setView(panel)
            .setPositiveButton("保存") { _, _ ->
                npcLlmEnabled = enableCheck.isChecked
                npcLlmModelName = modelInput.text.toString().trim().ifBlank { "Qwen2.5-0.5B-Instruct-Q4_K_M.gguf" }
                npcLlmPredict = predictInput.text.toString().toIntOrNull()?.coerceIn(16, 96) ?: 48
                npcLlmThreads = threadsInput.text.toString().toIntOrNull()?.coerceIn(1, 8) ?: 4
                val prefs = getSharedPreferences("immortal_demo", Context.MODE_PRIVATE)
                prefs.edit()
                    .putBoolean(npcLlmEnabledKey, npcLlmEnabled)
                    .putString(npcLlmModelKey, npcLlmModelName)
                    .putInt(npcLlmPredictKey, npcLlmPredict)
                    .putInt(npcLlmThreadsKey, npcLlmThreads)
                    .apply()
                applyNpcLlmConfig()
                refresh()
            }
            .setNegativeButton("取消", null)
            .show()
    }

    private fun showChapterList() {
        val list = core.chapterList().toTypedArray()
        AlertDialog.Builder(this)
            .setTitle("章节目录")
            .setItems(list, null)
            .setPositiveButton("关闭", null)
            .show()
    }

    private fun showMethodList() {
        val methods = core.methodList()
        val labels = methods.map {
            "${it.name}(${it.element}) 阶段${it.stage} 进度${it.progress}/${it.need}"
        }.toTypedArray()
        AlertDialog.Builder(this)
            .setTitle("功法（点击修炼）")
            .setItems(labels) { _, which ->
                core.trainMethod(which)
                refresh()
            }
            .setNegativeButton("关闭", null)
            .show()
    }

    private fun showSkillList() {
        val skills = core.skillList()
        val labels = skills.map { "${it.name} 倍率${it.ratio} 冷却${it.cdMax}" }.toTypedArray()
        AlertDialog.Builder(this)
            .setTitle("战斗技能（自动释放）")
            .setItems(labels, null)
            .setPositiveButton("关闭", null)
            .show()
    }

    private fun showShop() {
        val goods = core.shopCatalogDetailed()
        val labels = goods.map {
            if (it.desc.isBlank()) "${core.rarityBadge(it.id)} ${core.displayItemName(it.id)} - ${it.price}金币"
            else "${core.rarityBadge(it.id)} ${core.displayItemName(it.id)} - ${it.price}金币 | ${it.desc}"
        }.toTypedArray()
        AlertDialog.Builder(this)
            .setTitle("商店")
            .setItems(labels) { _, i ->
                core.buyFromShop(goods[i].id, goods[i].price)
                refresh()
            }
            .setNegativeButton("关闭", null)
            .show()
    }

    private fun showQuestStatus() {
        AlertDialog.Builder(this)
            .setTitle("任务")
            .setMessage(core.questStatus())
            .setPositiveButton("关闭", null)
            .show()
    }

    private fun showAllocatePanel() {
        val root = LinearLayout(this).apply {
            orientation = LinearLayout.VERTICAL
            setPadding(20, 8, 20, 8)
        }
        val summary = TextView(this)
        root.addView(summary)

        fun refreshSummary() {
            summary.text = core.pointSummary()
            refresh()
        }

        fun addPointButton(label: String, stat: String) {
            val btn = Button(this).apply { text = label }
            btn.setOnClickListener {
                core.allocatePlayerPoint(stat)
                refreshSummary()
            }
            root.addView(btn)
        }

        addPointButton("生命 +12", "hp")
        addPointButton("攻击 +1", "atk")
        addPointButton("防御 +1", "def")
        addPointButton("速度 +1", "spd")
        addPointButton("幸运 +1", "luck")
        refreshSummary()

        AlertDialog.Builder(this)
            .setTitle("分配自由点")
            .setView(root)
            .setNegativeButton("关闭", null)
            .show()
    }

    private fun showSecretPanel() {
        val actions = arrayOf("进入秘境", "离开秘境", "关闭")
        AlertDialog.Builder(this)
            .setTitle("秘境")
            .setItems(actions) { dialog, which ->
                when (actions[which]) {
                    "进入秘境" -> { core.enterSecret(); refresh() }
                    "离开秘境" -> { core.leaveSecret(); refresh() }
                    else -> dialog.dismiss()
                }
            }
            .show()
    }

    private fun showMountPanel() {
        val actions = arrayOf("购买坐骑", "上阵坐骑", "关闭")
        AlertDialog.Builder(this)
            .setTitle("坐骑")
            .setItems(actions) { dialog, which ->
                when (actions[which]) {
                    "购买坐骑" -> {
                        val list = core.mountCatalog()
                        val labels = list.map { "${it.first} - ${it.second}金币" }.toTypedArray()
                        AlertDialog.Builder(this)
                            .setTitle("购买坐骑")
                            .setItems(labels) { _, i ->
                                core.buyMount(list[i].first, list[i].second)
                                refresh()
                            }
                            .show()
                    }
                    "上阵坐骑" -> {
                        val bagMounts = core.bagItems()
                            .map { it.first }
                            .filter { it.startsWith("坐骑:") }
                            .map { it.removePrefix("坐骑:") }
                        if (bagMounts.isEmpty()) {
                            AlertDialog.Builder(this).setMessage("没有可上阵坐骑").setPositiveButton("关闭", null).show()
                            return@setItems
                        }
                        AlertDialog.Builder(this)
                            .setTitle("上阵坐骑")
                            .setItems(bagMounts.toTypedArray()) { _, i ->
                                core.equipMount(bagMounts[i])
                                refresh()
                            }
                            .show()
                    }
                    else -> dialog.dismiss()
                }
            }
            .show()
    }

    private fun showForgePanel() {
        val actions = arrayOf("装备概览", "蓝图打造", "研习蓝图", "蓝图总览", "修理全部", "修理单件", "基础淬炼", "关闭")
        AlertDialog.Builder(this)
            .setTitle("炼器")
            .setItems(actions) { dialog, which ->
                when (actions[which]) {
                    "装备概览" -> {
                        val lines = core.equipmentSummaryLines()
                        AlertDialog.Builder(this)
                            .setTitle("装备部位")
                            .setItems(lines.toTypedArray(), null)
                            .setPositiveButton("关闭", null)
                            .show()
                    }
                    "蓝图打造" -> {
                        val ids = core.knownBlueprintIds()
                        if (ids.isEmpty()) {
                            AlertDialog.Builder(this).setMessage("暂无已掌握蓝图").setPositiveButton("关闭", null).show()
                            return@setItems
                        }
                        val labels = ids.map { core.blueprintLabel(it) }.toTypedArray()
                        AlertDialog.Builder(this)
                            .setTitle("选择蓝图打造")
                            .setItems(labels) { _, i ->
                                core.craftFromBlueprint(ids[i])
                                refresh()
                            }
                            .setNegativeButton("关闭", null)
                            .show()
                    }
                    "研习蓝图" -> {
                        core.learnBlueprintFromBox()
                        refresh()
                    }
                    "蓝图总览" -> {
                        val lines = core.blueprintStatusLines(learnedOnly = false)
                        AlertDialog.Builder(this)
                            .setTitle("蓝图链路")
                            .setItems(lines.toTypedArray(), null)
                            .setPositiveButton("关闭", null)
                            .show()
                    }
                    "修理全部" -> {
                        core.repairAllEquipment()
                        refresh()
                    }
                    "修理单件" -> {
                        val lines = core.equipmentSummaryLines()
                        AlertDialog.Builder(this)
                            .setTitle("选择修理部位")
                            .setItems(lines.toTypedArray()) { _, i ->
                                val slots = listOf("weapon", "head", "body", "boots", "accessory")
                                core.repairEquipment(slots[i])
                                refresh()
                            }
                            .setNegativeButton("关闭", null)
                            .show()
                    }
                    "基础淬炼" -> {
                        core.forgeOnce()
                        refresh()
                    }
                    else -> dialog.dismiss()
                }
            }
            .show()
    }

    private fun showTalentPanel() {
        val talents = core.talentList()
        if (talents.isEmpty()) {
            AlertDialog.Builder(this).setMessage("暂无天赋").setPositiveButton("关闭", null).show()
            return
        }
        val labels = talents.map {
            "【${tierName(it.tier)}】${it.name} HP+${it.hp} 攻+${it.atk} 防+${it.def} 速+${it.spd} 运+${it.luck}"
        }.toTypedArray()
        AlertDialog.Builder(this)
            .setTitle("天赋")
            .setItems(labels, null)
            .setPositiveButton("关闭", null)
            .show()
    }

    private fun showCollectiblePanel() {
        val actions = arrayOf("收藏阁（全图鉴）", "已拥有收藏（可装备）", "关闭")
        AlertDialog.Builder(this)
            .setTitle("收藏系统")
            .setItems(actions) { dialog, which ->
                when (actions[which]) {
                    "收藏阁（全图鉴）" -> showCollectibleAtlasPanel()
                    "已拥有收藏（可装备）" -> showOwnedCollectiblePanel()
                    else -> dialog.dismiss()
                }
            }
            .show()
    }

    private fun showOwnedCollectiblePanel() {
        val cols = core.collectibleList()
        if (cols.isEmpty()) {
            AlertDialog.Builder(this).setMessage("暂无收藏品").setPositiveButton("关闭", null).show()
            return
        }
        val labels = cols.map {
            "${it.name}·${it.rarity} Lv${it.level} HP+${it.hp * it.level} 攻+${it.atk * it.level} 防+${it.def * it.level} 速+${it.spd * it.level}"
        }.toTypedArray()
        AlertDialog.Builder(this)
            .setTitle("收藏品（点击装备）")
            .setItems(labels) { _, i ->
                core.equipCollectible(i)
                refresh()
            }
            .setNegativeButton("关闭", null)
            .show()
    }

    private fun showCollectibleAtlasPanel() {
        val atlas = core.collectibleAtlas()
        val labels = atlas.map { entry ->
            val ownText = if (entry.ownedLevel > 0) "已拥有 Lv${entry.ownedLevel}" else "未拥有"
            "${core.rarityBadgeByRarity(entry.rarity)} ${entry.name}·${entry.rarity} | $ownText"
        }
        val adapter = object : ArrayAdapter<String>(this, android.R.layout.simple_list_item_1, labels) {
            override fun getView(position: Int, convertView: View?, parent: android.view.ViewGroup): View {
                val view = super.getView(position, convertView, parent)
                val tv = view.findViewById<TextView>(android.R.id.text1)
                val owned = atlas[position].ownedLevel > 0
                tv.setTextColor(if (owned) Color.parseColor("#202124") else Color.parseColor("#9AA0A6"))
                return view
            }
        }
        AlertDialog.Builder(this)
            .setTitle("收藏阁（灰色=未拥有）")
            .setAdapter(adapter, null)
            .setPositiveButton("关闭", null)
            .show()
    }

    private fun tierName(tier: Int): String {
        return when (tier) {
            0 -> "黄"
            1 -> "玄"
            2 -> "地"
            3 -> "天"
            else -> "神"
        }
    }

    private fun showSectPanel() {
        val actions = arrayOf("创建宗门", "宗门概览", "弟子状态", "招收弟子", "灵田收成", "矿脉收成", "建设灵田", "建设矿脉", "建设经阁", "建设戒备", "弟子训练", "宗门历练", "宗门仓库", "唯一宝物", "关闭")
        AlertDialog.Builder(this)
            .setTitle("宗门")
            .setItems(actions) { dialog, which ->
                when (actions[which]) {
                    "创建宗门" -> {
                        val input = EditText(this)
                        input.hint = "输入宗门名"
                        AlertDialog.Builder(this)
                            .setTitle("创建宗门")
                            .setView(input)
                            .setPositiveButton("创建") { _, _ ->
                                core.createSect(input.text.toString())
                                refresh()
                            }
                            .setNegativeButton("取消", null)
                            .show()
                    }
                    "宗门概览" -> {
                        AlertDialog.Builder(this)
                            .setTitle("宗门概览")
                            .setMessage(core.sectSummary())
                            .setPositiveButton("关闭", null)
                            .show()
                    }
                    "弟子状态" -> showSectDisciples()
                    "招收弟子" -> { core.sectRecruit(); refresh() }
                    "灵田收成" -> { core.sectPlant(); refresh() }
                    "矿脉收成" -> { core.sectMine(); refresh() }
                    "建设灵田" -> { core.sectBuild("field"); refresh() }
                    "建设矿脉" -> { core.sectBuild("mine"); refresh() }
                    "建设经阁" -> { core.sectBuild("library"); refresh() }
                    "建设戒备" -> { core.sectBuild("defense"); refresh() }
                    "弟子训练" -> { core.sectTrain(); refresh() }
                    "宗门历练" -> { core.sectExpedition(); refresh() }
                    "宗门仓库" -> showSectVaultPanel()
                    "唯一宝物" -> showSectRelicPanel()
                    else -> dialog.dismiss()
                }
            }
            .show()
    }

    private fun showSectDisciples() {
        val lines = core.sectDiscipleLines()
        if (lines.isEmpty()) {
            AlertDialog.Builder(this).setMessage("暂无弟子或尚未创建宗门").setPositiveButton("关闭", null).show()
            return
        }
        AlertDialog.Builder(this)
            .setTitle("弟子状态")
            .setItems(lines.toTypedArray(), null)
            .setPositiveButton("关闭", null)
            .show()
    }

    private fun showSectVaultPanel() {
        val actions = arrayOf("背包入库", "指定分配给弟子", "查看仓库", "关闭")
        AlertDialog.Builder(this)
            .setTitle("宗门仓库")
            .setItems(actions) { dialog, which ->
                when (actions[which]) {
                    "背包入库" -> {
                        val bag = core.bagItems()
                        if (bag.isEmpty()) {
                            AlertDialog.Builder(this).setMessage("背包为空").setPositiveButton("关闭", null).show()
                            return@setItems
                        }
                        val labels = bag.map { "${core.rarityBadge(it.first)} ${core.displayItemName(it.first)} x${it.second}" }.toTypedArray()
                        AlertDialog.Builder(this)
                            .setTitle("选择入库物品")
                            .setItems(labels) { _, idx ->
                                core.sectDepositToVault(bag[idx].first)
                                refresh()
                            }
                            .setNegativeButton("关闭", null)
                            .show()
                    }
                    "指定分配给弟子" -> {
                        val disciples = core.sectDiscipleLines()
                        val vault = core.sectVaultItems()
                        if (disciples.isEmpty()) {
                            AlertDialog.Builder(this).setMessage("暂无弟子可分配").setPositiveButton("关闭", null).show()
                            return@setItems
                        }
                        if (vault.isEmpty()) {
                            AlertDialog.Builder(this).setMessage("仓库为空").setPositiveButton("关闭", null).show()
                            return@setItems
                        }
                        AlertDialog.Builder(this)
                            .setTitle("选择弟子")
                            .setItems(disciples.toTypedArray()) { _, dIdx ->
                                val labels = vault.map { "${core.rarityBadge(it.first)} ${core.displayItemName(it.first)} x${it.second}" }.toTypedArray()
                                AlertDialog.Builder(this)
                                    .setTitle("选择分配物品")
                                    .setItems(labels) { _, vIdx ->
                                        core.sectAssignVaultItem(dIdx, vault[vIdx].first)
                                        refresh()
                                    }
                                    .setNegativeButton("关闭", null)
                                    .show()
                            }
                            .setNegativeButton("关闭", null)
                            .show()
                    }
                    "查看仓库" -> {
                        val vault = core.sectVaultItems()
                        val lines = if (vault.isEmpty()) {
                            arrayOf("仓库为空")
                        } else {
                            vault.map { "${core.rarityBadge(it.first)} ${core.displayItemName(it.first)} x${it.second}" }.toTypedArray()
                        }
                        AlertDialog.Builder(this)
                            .setTitle("仓库清单")
                            .setItems(lines, null)
                            .setPositiveButton("关闭", null)
                            .show()
                    }
                    else -> dialog.dismiss()
                }
            }
            .show()
    }

    private fun showSectRelicPanel() {
        val relics = core.sectRelicItems()
        val disciples = core.sectDiscipleLines()
        if (disciples.isEmpty()) {
            AlertDialog.Builder(this).setMessage("暂无弟子可保护").setPositiveButton("关闭", null).show()
            return
        }
        if (relics.isEmpty()) {
            AlertDialog.Builder(this).setMessage("当前没有可用唯一宝物").setPositiveButton("关闭", null).show()
            return
        }
        val relicLabels = relics.map { "${core.rarityBadge(it.first)} ${core.displayItemName(it.first)} x${it.second}" }.toTypedArray()
        AlertDialog.Builder(this)
            .setTitle("选择唯一宝物")
            .setItems(relicLabels) { _, rIdx ->
                AlertDialog.Builder(this)
                    .setTitle("指定保护弟子")
                    .setItems(disciples.toTypedArray()) { _, dIdx ->
                        core.sectAssignRelic(dIdx, relics[rIdx].first)
                        refresh()
                    }
                    .setNegativeButton("关闭", null)
                    .show()
            }
            .setNegativeButton("关闭", null)
            .show()
    }

    private fun saveGame() {
        val prefs = getSharedPreferences("immortal_demo", Context.MODE_PRIVATE)
        prefs.edit().putString(saveKey, core.dumpState()).apply()
        AlertDialog.Builder(this).setMessage("存档成功").setPositiveButton("关闭", null).show()
    }

    private fun loadGame() {
        val prefs = getSharedPreferences("immortal_demo", Context.MODE_PRIVATE)
        val text = prefs.getString(saveKey, null)
        if (text.isNullOrBlank()) {
            AlertDialog.Builder(this).setMessage("没有存档").setPositiveButton("关闭", null).show()
            return
        }
        if (core.loadState(text)) {
            deathPromptShown = false
            refresh()
            AlertDialog.Builder(this).setMessage("读档成功").setPositiveButton("关闭", null).show()
        } else {
            AlertDialog.Builder(this).setMessage("读档失败").setPositiveButton("关闭", null).show()
        }
    }

    override fun onDestroy() {
        LocalLlamaJni.release()
        super.onDestroy()
    }
}
