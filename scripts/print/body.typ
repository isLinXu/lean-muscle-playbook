// ── Package imports ───────────────────────────────────────
#import "@preview/cetz:0.3.4" as cetz
#import "@preview/fletcher:0.5.7" as fletcher

// ── Color definitions ────────────────────────────────────
#let accent = rgb("#4A6070")
#let accent-lt = rgb("#E6EAEC")
#let dark = rgb("#1A1A1A")
#let body-text = rgb("#2C2C2C")
#let muted-color = rgb("#888888")

// ── Spacing system ──────────────────────────────────────
// All vertical rhythm derives from these two base tokens.
// Adjust tokens.json to scale the entire document proportionally.
#let section-gap = 26pt   // Major section break (default 26pt)
#let para-gap = 16pt         // Inter-paragraph rhythm (default 8pt)

// ── Page setup ───────────────────────────────────────────
#set page(
  paper: "a4",
  columns: 1,
  margin: (left: 2.79cm, right: 2.79cm, top: 2.79cm, bottom: 2.50cm),
  header: if true {
    context {
      set text(size: 8pt, fill: muted-color)
      upper("8 周训练打卡表（打印版）")
      h(1fr)
      "2026-10-13"
      v(para-gap * 0.25)
      line(length: 100%, stroke: 1.5pt + accent)
    }
  },
  footer: if true {
    context {
      line(length: 100%, stroke: 0.5pt + luma(200))
      v(para-gap * 0.125)
      set text(size: 8pt, fill: muted-color)
      ""
      h(1fr)
      counter(page).display()
    }
  },
)

// ── Text defaults ────────────────────────────────────────
#set text(
  font: ("Zhuque Fangsong (technical preview)",),
  size: 10.5pt,
  fill: body-text,
  lang: "zh",
)
#let heading-font = ("Zhuque Fangsong (technical preview)",)
#set par(
  justify: true,
  leading: 1.14em,
  spacing: para-gap,
)

// ── Heading styles ───────────────────────────────────────
// Spacing stacks additively (prev.below + next.above).
// Ratio: above ≈ 2× below (heading belongs to content below it).
// Consecutive heading gaps: h1→h2 = 27pt, h2→h3 = 19pt, h3→h4 = 16pt.
#show heading: set block(above: 0pt, below: 0pt)

#show heading.where(level: 1): it => {
  v(section-gap)
  text(font: heading-font, size: 22pt, weight: "bold", fill: dark)[#it.body]
  v(section-gap * 0.5)
}

#show heading.where(level: 2): it => {
  v(para-gap * 0.875)
  text(font: heading-font, size: 15pt, weight: "bold", fill: dark)[#it.body]
  v(para-gap * 0.4375)
}

#show heading.where(level: 3): it => {
  v(para-gap * 0.875)
  text(font: heading-font, size: 11.5pt, weight: "bold", fill: dark)[#it.body]
  v(para-gap * 0.375)
}

#show heading.where(level: 4): it => {
  v(para-gap * 0.625)
  text(font: heading-font, size: 10.5pt, weight: "bold", fill: dark)[#it.body]
  v(para-gap * 0.3125)
}

#show heading.where(level: 5): it => {
  v(para-gap * 0.5)
  text(font: heading-font, size: 10.0pt, weight: "bold", fill: dark)[#it.body]
  v(para-gap * 0.25)
}

#show heading.where(level: 6): it => {
  v(para-gap * 0.375)
  text(font: heading-font, size: 10.0pt, fill: muted-color)[#it.body]
  v(para-gap * 0.1875)
}

// ── Helper functions ─────────────────────────────────────
#let callout-box(body) = {
  v(0pt)
  block(
    width: 100%,
    fill: accent-lt,
    stroke: (left: 4pt + accent),
    radius: 3pt,
    inset: (left: 16pt, right: 10pt, top: 10pt, bottom: 10pt),
    {
      set text(weight: "bold", size: 11.0pt, fill: dark, hyphenate: true)
      body
    }
  )
  v(0pt)
}

#let fit-math(body) = {
  layout(size => {
    let m = measure(body)
    if m.width > size.width {
      let ratio = size.width / m.width
      align(center, scale(x: ratio * 100%, y: ratio * 100%, origin: center + horizon, body))
    } else {
      body
    }
  })
}

#let caption-text(body) = {
  set text(size: 8.5pt, fill: muted-color)
  align(center)[#body]
  v(para-gap * 0.375)
}

#let accent-divider() = {
  v(para-gap * 0.875)
  line(length: 100%, stroke: 1.2pt + accent)
  v(para-gap * 0.875)
}

// ── Table styling ────────────────────────────────────────
// Global table style: accent header, alternating rows, light border.
// Python only emits structure (#table(columns:..., ...cells)); styling lives here.
#set table(
  stroke: 0.5pt + luma(200),
  inset: (x: 5pt, y: 4pt),
)
#show table: set block(width: 100%, breakable: true)
#show table.cell: set par(justify: false, leading: 0.5em)
#show table.cell: set text(size: 8pt, hyphenate: true)
#show table.cell.where(y: 0): set text(fill: white, weight: "bold")
#set table(
  fill: (x, y) => if y == 0 { accent } else if calc.rem(y, 2) == 0 { accent-lt } else { none },
)

// ── Code block helper ────────────────────────────────────
#let code-block(code, lang: none) = {
  v(para-gap * 0.5)
  if lang != none and lang != "" {
    text(font: "Courier New", size: 7pt, fill: muted-color)[#upper(lang)]
  }
  block(
    width: 100%,
    breakable: true,
    fill: accent-lt,
    stroke: (left: 3pt + accent, rest: 0.5pt + muted-color),
    inset: (left: 14pt, right: 10pt, top: 8pt, bottom: 8pt),
    radius: 0pt,
    {
      set text(size: 8pt, hyphenate: false)
      set par(justify: false, leading: 0.5em)
      show raw: set text(size: 8pt)
      code
    },
  )
  v(para-gap * 0.5)
}

// ── Block spacing helpers ────────────────────────────────
// block-gap: spacing only — used for breakable blocks (e.g. tables).
#let block-gap(body) = {
  v(para-gap * 0)
  body
  v(para-gap * 0)
}

// figure-block: spacing + breakable:false — used for images, charts, flowcharts.
#let figure-block(body) = {
  v(para-gap * 0)
  block(breakable: false, width: 100%, body)
  v(para-gap * 0)
}

// ── Cover page ──────────────────────────────────────────
#if false [
  #page(header: none, footer: none, columns: 1)[
    #align(center + horizon)[
      #layout(size => {
        let title-content = text(font: heading-font, size: 54pt, weight: "bold", fill: dark)[8 周训练打卡表（打印版）]
        let m = measure(title-content)
        let max-width = size.width * 0.85
        let max-height = size.height * 0.4
        if m.width > max-width or m.height > max-height {
          let ratio-w = if m.width > max-width { max-width / m.width } else { 1.0 }
          let ratio-h = if m.height > max-height { max-height / m.height } else { 1.0 }
          let ratio = calc.min(ratio-w, ratio-h)
          let new-size = 54pt * ratio
          let final-size = calc.max(new-size, 24pt)
          align(center, text(font: heading-font, size: final-size, weight: "bold", fill: dark)[8 周训练打卡表（打印版）])
        } else {
          align(center, title-content)
        }
      })
      #v(para-gap * 1.25)
      #line(length: 60%, stroke: 2pt + accent)
      #v(para-gap * 1)
      #if "" != "" [
        #text(size: 12pt, fill: muted-color)[]
        #v(para-gap * 0.5)
      ]
      #if "2026-10-13" != "" [
        #text(size: 12pt, fill: muted-color)[2026-10-13]
      ]
    ]
  ]
]
// ── Document content ──────────────────────────────────────


= 一、使用说明

== 1.1 口径说明

#h(2em)本表动作编排来自第六章"训练手册：8 周实操行动清单"，是整理者依据公开健康资料（卫健委、三甲医院、运动科学综述）与通用训练编排整合的实操建议，非《薄肌圣经》原文。

#h(2em)书中对训练的表述仅见于公开解读（每天约 30 分钟、八周见效、三步启动法），未披露逐周动作明细；本表给出的是可照做的落地方案，仅供健康成人参考。

#h(2em)体脂已低于健康下限、有慢性病或孕期者，应先咨询专业人士再执行；本表不构成医学、营养学或运动处方建议。

#h(2em)阶段一在原文标注为"第 2 周"，为保持 8 周四阶段完整使用，本表将同一周安排用于第 1–2 周（搭底子）；如需从第 2 周开始，可跳过第 1 周各行。

== 1.2 打卡方式
+ 每周力量日 A/B/C 轮换一次，两次力量训练间隔 ≥48 小时；4 个阶段共 8 周，逐日安排见"8周打卡总表"。
+ "完成勾选"列使用下拉：完成 / 未完成 / 部分完成 / 休息日；顺手把当日实际重量、次数或感受记在"备注"列。
+ 力量不足时一律先做"退阶版"，标准姿势优先，不要跳过退阶直接上重量。
+ 渐进超负荷：同一动作连续两周都能完成目标组次数、且最后 1–2 次仍有余力时，下一周加 1 组数、或加 2–5kg 负重、或加 10–15 秒平板时间，三者每次只动一个变量，并在备注里记录。

== 1.3 四阶段总览

#block-gap[
#block(width: 100%, breakable: true)[
#table(
  columns: (1.2fr, 1fr, 3fr),
  table.header(
    [周次],
    [阶段],
    [主题],
  ),
  [第 1–2 周],
  [阶段一],
  [搭底子：掌握动作，不追求数量],
  [第 3–4 周],
  [阶段二],
  [容量递增：每组加次数，开始加轻负重],
  [第 5–6 周],
  [阶段三],
  [负重进阶：重量小幅上调，容量维持],
  [第 7–8 周],
  [阶段四],
  [冲刺收官：维持容量，做终期复盘],
)
]
]

== 1.4 注意事项

#h(2em)每个动作首次做时对着镜子或拍视频自查一次；居家无镜子可请家人帮忙看或拍 30 秒视频回看"腰背是否平直、膝盖是否内扣"。

#h(2em)第 8 周周日对照第 1 周基线做终期复盘：体重、腰围、照片、训练日志。

#h(2em)数据来源：第六章训练手册（整理者依据公开健康资料整合，非书中原文）；动作速查卡 9 个动作均可在"动作速查卡"工作表查询退阶/标准/进阶。

#h(2em)生成/更新时间：2026-10-13

= 二、8 周逐日打卡总表

#h(2em)下方按阶段拆分为 4 张表，每张对应两周（14 天）。"完成勾选"与"备注"列为空白栏，打印后手写勾选或记录当日实际重量、次数与感受；力量日 A/B/C 每周轮换一次，两次力量训练间隔至少 48 小时，力量不足时先做退阶版。

== 2.1 阶段一（第 1–2 周）

#block-gap[
#block(width: 100%, breakable: true)[
#table(
  columns: (1fr, 1fr, 1.5fr, 3.5fr, 8fr, 3fr, 1.5fr, 1.5fr),
  table.header(
    [周次],
    [星期],
    [阶段],
    [训练内容],
    [目标组次（动作明细）],
    [时长/间歇],
    [完成勾选],
    [备注],
  ),
  [第1周],
  [周一],
  [阶段一],
  [力量 A·下肢+核心],
  [徒手深蹲 3×8–10（退阶：椅子辅助深蹲）；臀桥 3×10–12；平板支撑 3×20–30 秒（退阶：跪姿平板）],
  [30–35 分钟；组间 60–90 秒],
  [],
  [],
  [第1周],
  [周二],
  [阶段一],
  [有氧：中等强度],
  [快走/骑行/椭圆机，中等强度（能说话但不太能唱歌）],
  [20–25 分钟],
  [],
  [],
  [第1周],
  [周三],
  [阶段一],
  [力量 B·上肢+核心],
  [跪姿俯卧撑 3×6–8（退阶：上斜俯卧撑）；弹力带划船 3×10–12；平板支撑 3×20–30 秒],
  [30–35 分钟；组间 60–90 秒],
  [],
  [],
  [第1周],
  [周四],
  [阶段一],
  [休息或散步],
  [—],
  [—],
  [],
  [],
  [第1周],
  [周五],
  [阶段一],
  [力量 C·全身补弱],
  [徒手深蹲 3×8–10；跪姿俯卧撑 3×6–8；臀桥 3×10–12；平板支撑 3×20–30 秒],
  [30–35 分钟；组间 60–90 秒],
  [],
  [],
  [第1周],
  [周六],
  [阶段一],
  [有氧：较长一次],
  [快走/爬坡走/骑行],
  [25–30 分钟],
  [],
  [],
  [第1周],
  [周日],
  [阶段一],
  [完全休息],
  [—],
  [—],
  [],
  [],
  [第2周],
  [周一],
  [阶段一],
  [力量 A·下肢+核心],
  [徒手深蹲 3×8–10（退阶：椅子辅助深蹲）；臀桥 3×10–12；平板支撑 3×20–30 秒（退阶：跪姿平板）],
  [30–35 分钟；组间 60–90 秒],
  [],
  [],
  [第2周],
  [周二],
  [阶段一],
  [有氧：中等强度],
  [快走/骑行/椭圆机，中等强度（能说话但不太能唱歌）],
  [20–25 分钟],
  [],
  [],
  [第2周],
  [周三],
  [阶段一],
  [力量 B·上肢+核心],
  [跪姿俯卧撑 3×6–8（退阶：上斜俯卧撑）；弹力带划船 3×10–12；平板支撑 3×20–30 秒],
  [30–35 分钟；组间 60–90 秒],
  [],
  [],
  [第2周],
  [周四],
  [阶段一],
  [休息或散步],
  [—],
  [—],
  [],
  [],
  [第2周],
  [周五],
  [阶段一],
  [力量 C·全身补弱],
  [徒手深蹲 3×8–10；跪姿俯卧撑 3×6–8；臀桥 3×10–12；平板支撑 3×20–30 秒],
  [30–35 分钟；组间 60–90 秒],
  [],
  [],
  [第2周],
  [周六],
  [阶段一],
  [有氧：较长一次],
  [快走/爬坡走/骑行],
  [25–30 分钟],
  [],
  [],
  [第2周],
  [周日],
  [阶段一],
  [完全休息],
  [—],
  [—],
  [],
  [],
)
]
]

== 2.2 阶段二（第 3–4 周）

#block-gap[
#block(width: 100%, breakable: true)[
#table(
  columns: (1fr, 1fr, 1.5fr, 3.5fr, 8fr, 3fr, 1.5fr, 1.5fr),
  table.header(
    [周次],
    [星期],
    [阶段],
    [训练内容],
    [目标组次（动作明细）],
    [时长/间歇],
    [完成勾选],
    [备注],
  ),
  [第3周],
  [周一],
  [阶段二],
  [力量 A·下肢+核心],
  [深蹲 3–4×10–12（进阶：双手各持 2.5–5kg 哑铃）；臀桥 3×12–15（进阶：负重/单腿）；平板支撑 3×30–45 秒],
  [35–40 分钟；组间 60–90 秒],
  [],
  [],
  [第3周],
  [周二],
  [阶段二],
  [有氧：中等强度],
  [快走/骑行/椭圆机，中等强度],
  [25–30 分钟],
  [],
  [],
  [第3周],
  [周三],
  [阶段二],
  [力量 B·上肢+核心],
  [标准俯卧撑 3×8–10（退阶：跪姿）；哑铃或弹力带划船 3×10–12；侧平举 2–3×12–15；平板支撑 3×30–45 秒],
  [35–40 分钟；组间 60–90 秒],
  [],
  [],
  [第3周],
  [周四],
  [阶段二],
  [休息或散步],
  [—],
  [—],
  [],
  [],
  [第3周],
  [周五],
  [阶段二],
  [力量 C·全身补弱],
  [深蹲 3×10–12；俯卧撑 3×8–10；臀桥 3×12–15；死虫/登山者 3×10–12（每侧）],
  [35–40 分钟；组间 60–90 秒],
  [],
  [],
  [第3周],
  [周六],
  [阶段二],
  [有氧：较长一次],
  [按能力加 5 分钟],
  [30–35 分钟],
  [],
  [],
  [第3周],
  [周日],
  [阶段二],
  [完全休息],
  [—],
  [—],
  [],
  [],
  [第4周],
  [周一],
  [阶段二],
  [力量 A·下肢+核心],
  [深蹲 3–4×10–12（进阶：双手各持 2.5–5kg 哑铃）；臀桥 3×12–15（进阶：负重/单腿）；平板支撑 3×30–45 秒],
  [35–40 分钟；组间 60–90 秒],
  [],
  [],
  [第4周],
  [周二],
  [阶段二],
  [有氧：中等强度],
  [快走/骑行/椭圆机，中等强度],
  [25–30 分钟],
  [],
  [],
  [第4周],
  [周三],
  [阶段二],
  [力量 B·上肢+核心],
  [标准俯卧撑 3×8–10（退阶：跪姿）；哑铃或弹力带划船 3×10–12；侧平举 2–3×12–15；平板支撑 3×30–45 秒],
  [35–40 分钟；组间 60–90 秒],
  [],
  [],
  [第4周],
  [周四],
  [阶段二],
  [休息或散步],
  [—],
  [—],
  [],
  [],
  [第4周],
  [周五],
  [阶段二],
  [力量 C·全身补弱],
  [深蹲 3×10–12；俯卧撑 3×8–10；臀桥 3×12–15；死虫/登山者 3×10–12（每侧）],
  [35–40 分钟；组间 60–90 秒],
  [],
  [],
  [第4周],
  [周六],
  [阶段二],
  [有氧：较长一次],
  [按能力加 5 分钟],
  [30–35 分钟],
  [],
  [],
  [第4周],
  [周日],
  [阶段二],
  [完全休息],
  [—],
  [—],
  [],
  [],
)
]
]

== 2.3 阶段三（第 5–6 周）

#block-gap[
#block(width: 100%, breakable: true)[
#table(
  columns: (1fr, 1fr, 1.5fr, 3.5fr, 8fr, 3fr, 1.5fr, 1.5fr),
  table.header(
    [周次],
    [星期],
    [阶段],
    [训练内容],
    [目标组次（动作明细）],
    [时长/间歇],
    [完成勾选],
    [备注],
  ),
  [第5周],
  [周一],
  [阶段三],
  [力量 A·下肢+核心],
  [高脚杯深蹲（哑铃 5–10kg）4×8–12；罗马尼亚硬拉（哑铃/弹力带）3×8–10；臀桥 3×12–15（负重）；平板支撑 3×45–60 秒],
  [40–45 分钟；组间 60–90 秒],
  [],
  [],
  [第5周],
  [周二],
  [阶段三],
  [有氧：中等强度],
  [快走/骑行/椭圆机，中等强度],
  [30 分钟],
  [],
  [],
  [第5周],
  [周三],
  [阶段三],
  [力量 B·上肢+核心],
  [俯卧撑 3–4×10–12（进阶：下斜）；单臂哑铃划船/弹力带划船 3×10–12；哑铃推举 3×8–10；侧平举 3×12–15；平板支撑 3×45–60 秒],
  [40–45 分钟；组间 60–90 秒],
  [],
  [],
  [第5周],
  [周四],
  [阶段三],
  [休息或散步],
  [—],
  [—],
  [],
  [],
  [第5周],
  [周五],
  [阶段三],
  [力量 C·全身补弱],
  [高脚杯深蹲 4×8–12；俯卧撑 3×10–12；罗马尼亚硬拉 3×8–10；死虫/登山者 3×12–16],
  [40–45 分钟；组间 60–90 秒],
  [],
  [],
  [第5周],
  [周六],
  [阶段三],
  [有氧：较长一次],
  [可爬山/骑行],
  [35–45 分钟],
  [],
  [],
  [第5周],
  [周日],
  [阶段三],
  [完全休息],
  [—],
  [—],
  [],
  [],
  [第6周],
  [周一],
  [阶段三],
  [力量 A·下肢+核心],
  [高脚杯深蹲（哑铃 5–10kg）4×8–12；罗马尼亚硬拉（哑铃/弹力带）3×8–10；臀桥 3×12–15（负重）；平板支撑 3×45–60 秒],
  [40–45 分钟；组间 60–90 秒],
  [],
  [],
  [第6周],
  [周二],
  [阶段三],
  [有氧：中等强度],
  [快走/骑行/椭圆机，中等强度],
  [30 分钟],
  [],
  [],
  [第6周],
  [周三],
  [阶段三],
  [力量 B·上肢+核心],
  [俯卧撑 3–4×10–12（进阶：下斜）；单臂哑铃划船/弹力带划船 3×10–12；哑铃推举 3×8–10；侧平举 3×12–15；平板支撑 3×45–60 秒],
  [40–45 分钟；组间 60–90 秒],
  [],
  [],
  [第6周],
  [周四],
  [阶段三],
  [休息或散步],
  [—],
  [—],
  [],
  [],
  [第6周],
  [周五],
  [阶段三],
  [力量 C·全身补弱],
  [高脚杯深蹲 4×8–12；俯卧撑 3×10–12；罗马尼亚硬拉 3×8–10；死虫/登山者 3×12–16],
  [40–45 分钟；组间 60–90 秒],
  [],
  [],
  [第6周],
  [周六],
  [阶段三],
  [有氧：较长一次],
  [可爬山/骑行],
  [35–45 分钟],
  [],
  [],
  [第6周],
  [周日],
  [阶段三],
  [完全休息],
  [—],
  [—],
  [],
  [],
)
]
]

== 2.4 阶段四（第 7–8 周）

#block-gap[
#block(width: 100%, breakable: true)[
#table(
  columns: (1fr, 1fr, 1.5fr, 3.5fr, 8fr, 3fr, 1.5fr, 1.5fr),
  table.header(
    [周次],
    [星期],
    [阶段],
    [训练内容],
    [目标组次（动作明细）],
    [时长/间歇],
    [完成勾选],
    [备注],
  ),
  [第7周],
  [周一],
  [阶段四],
  [力量 A·下肢+核心],
  [沿用阶段三重量，深蹲/高脚杯深蹲 4×8–12；臀桥 3×12–15；平板支撑 3×45–60 秒；最后一组做到力竭（安全前提下）],
  [40–45 分钟；组间 75–90 秒],
  [],
  [],
  [第7周],
  [周二],
  [阶段四],
  [有氧：中等强度],
  [快走/骑行/椭圆机，中等强度],
  [30 分钟],
  [],
  [],
  [第7周],
  [周三],
  [阶段四],
  [力量 B·上肢+核心],
  [俯卧撑 4×10–12；划船 3×10–12；推举 3×8–10；平板支撑 3×45–60 秒],
  [40–45 分钟；组间 75–90 秒],
  [],
  [],
  [第7周],
  [周四],
  [阶段四],
  [休息或散步],
  [—],
  [—],
  [],
  [],
  [第7周],
  [周五],
  [阶段四],
  [力量 C·全身补弱],
  [高脚杯深蹲 4×8–12；俯卧撑 3×10–12；罗马尼亚硬拉 3×8–10；死虫 3×12–16],
  [40–45 分钟；组间 75–90 秒],
  [],
  [],
  [第7周],
  [周六],
  [阶段四],
  [有氧：较长一次],
  [最后 1 次按计划完成即可],
  [35–45 分钟],
  [],
  [],
  [第7周],
  [周日],
  [阶段四],
  [完全休息 + 终期复盘],
  [对照第 1 周基线做终期复盘（体重/腰围/照片/训练日志）],
  [—],
  [],
  [],
  [第8周],
  [周一],
  [阶段四],
  [力量 A·下肢+核心],
  [沿用阶段三重量，深蹲/高脚杯深蹲 4×8–12；臀桥 3×12–15；平板支撑 3×45–60 秒；最后一组做到力竭（安全前提下）],
  [40–45 分钟；组间 75–90 秒],
  [],
  [],
  [第8周],
  [周二],
  [阶段四],
  [有氧：中等强度],
  [快走/骑行/椭圆机，中等强度],
  [30 分钟],
  [],
  [],
  [第8周],
  [周三],
  [阶段四],
  [力量 B·上肢+核心],
  [俯卧撑 4×10–12；划船 3×10–12；推举 3×8–10；平板支撑 3×45–60 秒],
  [40–45 分钟；组间 75–90 秒],
  [],
  [],
  [第8周],
  [周四],
  [阶段四],
  [休息或散步],
  [—],
  [—],
  [],
  [],
  [第8周],
  [周五],
  [阶段四],
  [力量 C·全身补弱],
  [高脚杯深蹲 4×8–12；俯卧撑 3×10–12；罗马尼亚硬拉 3×8–10；死虫 3×12–16],
  [40–45 分钟；组间 75–90 秒],
  [],
  [],
  [第8周],
  [周六],
  [阶段四],
  [有氧：较长一次],
  [最后 1 次按计划完成即可],
  [35–45 分钟],
  [],
  [],
  [第8周],
  [周日],
  [阶段四],
  [完全休息 + 终期复盘],
  [对照第 1 周基线做终期复盘（体重/腰围/照片/训练日志）],
  [—],
  [],
  [],
)
]
]

= 三、动作速查卡

#h(2em)9 个动作的退阶 / 标准 / 进阶对照。首次做每个动作时对着镜子自查或拍 30 秒视频回看：腰背是否平直、膝盖是否内扣。

#block-gap[
#block(width: 100%, breakable: true)[
#table(
  columns: (1.2fr, 3fr, 1.6fr),
  table.header(
    [动作],
    [标准做法要点],
    [退阶 → 进阶],
  ),
  [深蹲],
  [双脚与肩同宽，下蹲到膝盖约 90°、膝盖不内扣，臀部向后坐，起身时收紧臀部与核心],
  [椅子辅助 → 徒手 → 高脚杯哑铃],
  [臀桥],
  [仰卧屈膝，脚跟踩地，臀部顶起至躯干成直线，顶端停顿 1 秒，缓慢下落],
  [徒手 → 负重（哑铃放髋上）→ 单腿],
  [俯卧撑],
  [身体成直线、核心收紧，下落至胸部接近地面，推起时肘部不完全锁死],
  [跪姿/上斜 → 标准 → 下斜/负重背心],
  [划船],
  [腰背挺直，肩胛后收带动手臂拉向肋骨方向，顶端停顿，慢放],
  [弹力带 → 哑铃 → 单臂哑铃],
  [推举],
  [哑铃从肩部推至头顶正上方，核心收紧，避免过度挺腰],
  [空手 → 轻哑铃（2–4kg）→ 加重],
  [罗马尼亚硬拉],
  [微屈膝，髋部后移、背部平直，哑铃沿大腿下放至小腿中上部，臀部发力站起],
  [空杆/轻哑铃 → 加重 → 壶铃],
  [平板支撑],
  [肘撑、身体成直线，收腹提臀，不塌腰不撅臀，均匀呼吸],
  [跪姿平板 → 标准 → 加时间/抬腿],
  [侧平举],
  [肩部发力向两侧抬起至与肩同高，肘微屈，慢放不耸肩],
  [空手 → 1–2kg → 加重],
  [死虫/登山者],
  [核心收紧、腰背贴地（死虫）；登山者保持躯干稳定、交替提膝],
  [死虫慢速 → 标准 → 加快],
)
]
]
