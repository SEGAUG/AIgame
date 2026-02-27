package com.jinhui.immortaldemo.ui

import android.content.Context
import android.graphics.Canvas
import android.graphics.Color
import android.graphics.Paint
import android.util.AttributeSet
import android.view.View
import com.jinhui.immortaldemo.core.MiniMapSnapshot

class MiniMapView @JvmOverloads constructor(
    context: Context,
    attrs: AttributeSet? = null,
) : View(context, attrs) {
    private var snapshot: MiniMapSnapshot? = null

    private val bgPaint = Paint(Paint.ANTI_ALIAS_FLAG).apply { color = Color.parseColor("#101114") }
    private val wallPaint = Paint(Paint.ANTI_ALIAS_FLAG).apply { color = Color.parseColor("#333840") }
    private val visiblePaint = Paint(Paint.ANTI_ALIAS_FLAG).apply { color = Color.parseColor("#252b35") }
    private val exitPaint = Paint(Paint.ANTI_ALIAS_FLAG).apply { color = Color.parseColor("#ffd54f") }
    private val bossPaint = Paint(Paint.ANTI_ALIAS_FLAG).apply { color = Color.parseColor("#ff5252") }
    private val mountPaint = Paint(Paint.ANTI_ALIAS_FLAG).apply { color = Color.parseColor("#00e5ff") }
    private val treasurePaint = Paint(Paint.ANTI_ALIAS_FLAG).apply { color = Color.parseColor("#ff9800") }
    private val playerPaint = Paint(Paint.ANTI_ALIAS_FLAG).apply { color = Color.parseColor("#00ff88") }
    private val borderPaint = Paint(Paint.ANTI_ALIAS_FLAG).apply {
        color = Color.parseColor("#2a2d34")
        style = Paint.Style.STROKE
        strokeWidth = 2f
    }

    fun submitSnapshot(value: MiniMapSnapshot) {
        snapshot = value
        invalidate()
    }

    override fun onDraw(canvas: Canvas) {
        super.onDraw(canvas)
        val snap = snapshot ?: return
        if (snap.width <= 0 || snap.height <= 0) return

        val widthF = width.toFloat()
        val heightF = height.toFloat()
        canvas.drawRect(0f, 0f, widthF, heightF, bgPaint)

        val pad = 8f
        val drawW = widthF - pad * 2f
        val drawH = heightF - pad * 2f
        val cell = minOf(drawW / snap.width, drawH / snap.height).coerceAtLeast(1f)
        val mapW = cell * snap.width
        val mapH = cell * snap.height
        val ox = (widthF - mapW) / 2f
        val oy = (heightF - mapH) / 2f

        canvas.drawRect(ox, oy, ox + mapW, oy + mapH, borderPaint)

        fun drawCell(x: Int, y: Int, paint: Paint) {
            val x1 = ox + x * cell
            val y1 = oy + y * cell
            canvas.drawRect(x1, y1, x1 + cell, y1 + cell, paint)
        }

        val visible = snap.visible.toSet()

        visible.forEach { p -> drawCell(p.x, p.y, visiblePaint) }
        snap.blocks.filter { it in visible }.forEach { p -> drawCell(p.x, p.y, wallPaint) }
        if (snap.exit in visible) drawCell(snap.exit.x, snap.exit.y, exitPaint)
        snap.boss?.takeIf { it in visible }?.let { drawCell(it.x, it.y, bossPaint) }
        snap.mount?.takeIf { it in visible }?.let { drawCell(it.x, it.y, mountPaint) }
        snap.treasure?.takeIf { it in visible }?.let { drawCell(it.x, it.y, treasurePaint) }

        val px = ox + snap.player.x * cell + cell / 2f
        val py = oy + snap.player.y * cell + cell / 2f
        val r = (cell * 0.42f).coerceAtLeast(2f)
        canvas.drawCircle(px, py, r, playerPaint)
    }
}
