# -*- coding: utf-8 -*-
"""瘦≠薄肌 对比图确定性渲染（PIL + Noto Sans CJK SC）
结构：主标题+副标题 / 左栏「瘦」右栏「薄肌」五维对比表 / 底部结论条
文字来源：docs/black-book.md 第 3.1 节（与 storyboard.json V3 提示词逐字一致）
用法：python scripts/render_lean_chart.py [--output assets/lean-vs-thin.png]
依赖：python3 + Pillow；字体需要 Noto Sans CJK SC（本脚本内字体路径为 Linux 沙箱路径，
      其他环境请替换 F_REG/F_MED/F_BOLD 为本地字体路径）"""
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

# ---------- 常量 ----------
W, H = 2160, 2880
BG = (255, 255, 255)
INK = (43, 43, 43)
GRAY = (107, 107, 107)
GOLD = (176, 141, 62)
GOLD_LIGHT = (243, 235, 217)
LABEL_BG = (246, 242, 233)
LINE = (217, 217, 217)
OUTLINE = (166, 166, 166)

F_REG = "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc"
F_MED = "/usr/share/fonts/opentype/noto/NotoSansCJK-Medium.ttc"
F_BOLD = "/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc"

def font(path, size, idx=2):
    return ImageFont.truetype(path, size, index=idx)

TITLE = "瘦 ≠ 薄肌"
SUBTITLE = "看似相近，本质是两回事——摘自《孙宇晨访谈记录》3.1 节《薄肌圣经》之「常见误读与边界」"
HEAD_L = "瘦（单纯减重）"
HEAD_R = "薄肌（精瘦而有力量）"
ROWS = [
    ("定义核心",
     "单纯的低体重、苗条，甚至伴随肌肉流失",
     "低体脂约12%-15%、线条清晰、精瘦而有力量"),
    ("追求目标",
     "体重数字下降，以「更瘦」为唯一指标",
     "瘦体重/肌肉管理，追求「穿衣显瘦、脱衣有肉」"),
    ("实现方式",
     "节食与极端控食（如「只喝水不吃盐」等缺乏依据的做法）",
     "力量训练+营养管理+恢复，每天约30分钟、八周见效（自媒体解读口径，非官方数值）"),
    ("身体后果",
     "缺乏力量储备、肌肉流失，可能免疫力下降、激素紊乱",
     "肌肉是被动燃脂的「红莲斗篷」，同时拿满心肺与肌肉的寿命评分50分"),
    ("健康边界",
     "审美偏好被误当成健康标准，尤其女性追求极低体脂更伤身",
     "以健康为前提的低体脂才成立，体脂低于健康下限仍压脂同样危险"),
]
CONCLUSION = ("判断标准是「健康前提下的低体脂与线条」，不是「越瘦越好」；"
              "单纯节食造成的「瘦」缺乏力量储备，与薄肌是两回事。")

MARGIN = 150
COL_LABEL = 400
COLS = (W - 2 * MARGIN - COL_LABEL - 4) // 2   # 728
CELL_PAD_X = 36
CELL_PAD_Y = 42
LINE_W = 2
OUT_W = 3

TITLE_F = 148
SUBTITLE_F = 42
HEADER_F = 50
LABEL_F = 46
BODY_F = 42
CONCL_F = 46
BODY_LH = 70
CONCL_LH = 76

# ---------- 工具 ----------
def wrap(draw, text, f, max_w):
    lines, cur = [], ""
    for ch in text:
        cand = cur + ch
        if draw.textlength(cand, font=f) <= max_w or not cur:
            cur = cand
        else:
            if ch in "」）、。，；：！？》":
                cur = cand
                continue
            lines.append(cur)
            cur = ch
    if cur:
        lines.append(cur)
    return lines

def text_h(f):
    b = f.getbbox("中")
    return b[3] - b[1]

# ---------- 画布 ----------
img = Image.new("RGB", (W, H), BG)
d = ImageDraw.Draw(img)

f_title = font(F_BOLD, TITLE_F)
f_sub = font(F_REG, SUBTITLE_F)
f_head = font(F_BOLD, HEADER_F)
f_label = font(F_MED, LABEL_F)
f_body = font(F_REG, BODY_F)
f_concl = font(F_MED, CONCL_F)

# 几何计算
title_w = d.textlength(TITLE, font=f_title)
title_h = text_h(f_title)
sub_h = text_h(f_sub)
header_h = 148

cell_max_w = COLS - 2 * CELL_PAD_X
rows_meta = []
for name, l, r in ROWS:
    ll = wrap(d, l, f_body, cell_max_w)
    rl = wrap(d, r, f_body, cell_max_w)
    rows_meta.append((name, ll, rl))
row_hs = [max(len(ll), len(rl)) * BODY_LH + 2 * CELL_PAD_Y for (_, ll, rl) in rows_meta]
table_h = header_h + sum(row_hs)

concl_lines = wrap(d, CONCLUSION, f_concl, W - 2 * MARGIN - 2 * 54)
concl_h = len(concl_lines) * CONCL_LH + 2 * 54

gap_title_rule = 46
rule_th = 10
gap_rule_sub = 56
gap_sub_table = 88
gap_table_concl = 96

total = (title_h + gap_title_rule + rule_th + gap_rule_sub + sub_h
         + gap_sub_table + table_h + gap_table_concl + concl_h)
start = max(70, (H - total) // 2)

# ---------- 标题区 ----------
y = start
tx = (W - title_w) / 2
d.text((tx, y), TITLE, font=f_title, fill=INK)
rule_y = y + title_h + gap_title_rule
rule_w = 240
d.rectangle([(W - rule_w) / 2, rule_y, (W + rule_w) / 2, rule_y + rule_th], fill=GOLD)
sub_y = rule_y + rule_th + gap_rule_sub
sw = d.textlength(SUBTITLE, font=f_sub)
d.text(((W - sw) / 2, sub_y), SUBTITLE, font=f_sub, fill=GRAY)

# ---------- 表格 ----------
x0, x4 = MARGIN, W - MARGIN
x1 = x0 + COL_LABEL
x2 = x1 + LINE_W + COLS
x3 = x2 + LINE_W + COLS
tab_y = sub_y + sub_h + gap_sub_table

def center_text(x_min, x_max, y_top, text, f, fill):
    tw = d.textlength(text, font=f)
    th = text_h(f)
    d.text((x_min + (x_max - x_min - tw) / 2, y_top + (header_h - th) / 2), text, font=f, fill=fill)

# 表头
d.rectangle([x0, tab_y, x4, tab_y + header_h], fill=LABEL_BG)
d.rectangle([x1 + LINE_W, tab_y, x3, tab_y + header_h], fill=GOLD_LIGHT)
center_text(x0, x1, tab_y, "对比维度", f_label, INK)
center_text(x1 + LINE_W, x2, tab_y, HEAD_L, f_head, INK)
center_text(x2 + LINE_W, x3, tab_y, HEAD_R, f_head, INK)

# 数据行
yy = tab_y + header_h
for i, (name, ll, rl) in enumerate(rows_meta):
    rh = row_hs[i]
    y_top, y_bot = yy, yy + rh
    d.rectangle([x0, y_top, x1, y_bot], fill=LABEL_BG)
    # 维度标签：金色序号 + 深灰名称，垂直居中
    num_txt = f"维度{i+1} "
    nw = d.textlength(num_txt, font=f_label)
    name_w = d.textlength(name, font=f_label)
    th = text_h(f_label)
    lx = x0 + (COL_LABEL - nw - name_w) / 2
    ly = y_top + (rh - th) / 2
    d.text((lx, ly), num_txt, font=f_label, fill=GOLD)
    d.text((lx + nw, ly), name, font=f_label, fill=INK)
    # 左右内容
    cx = x1 + LINE_W + CELL_PAD_X
    ltop = y_top + CELL_PAD_Y
    for j, ln in enumerate(ll):
        d.text((cx, ltop + j * BODY_LH), ln, font=f_body, fill=INK)
    cx = x2 + LINE_W + CELL_PAD_X
    for j, ln in enumerate(rl):
        d.text((cx, ltop + j * BODY_LH), ln, font=f_body, fill=INK)
    yy = y_bot

# 表格线
for xx in (x1, x2):
    d.rectangle([xx, tab_y, xx + LINE_W, tab_y + table_h], fill=LINE)
y_line = tab_y + header_h
for rh in row_hs:
    d.rectangle([x0, y_line, x4, y_line + LINE_W], fill=LINE)
    y_line += rh
d.rectangle([x0, tab_y, x4, tab_y + OUT_W], fill=OUTLINE)
d.rectangle([x0, tab_y + table_h - OUT_W, x4, tab_y + table_h], fill=OUTLINE)
d.rectangle([x0, tab_y, x0 + OUT_W, tab_y + table_h], fill=OUTLINE)
d.rectangle([x4 - OUT_W, tab_y, x4, tab_y + table_h], fill=OUTLINE)

# ---------- 结论条 ----------
cy = tab_y + table_h + gap_table_concl
d.rectangle([x0, cy, x4, cy + concl_h], fill=GOLD_LIGHT)
d.rectangle([x0, cy, x0 + 14, cy + concl_h], fill=GOLD)
yy = cy + 54
for ln in concl_lines:
    d.text((x0 + 54, yy), ln, font=f_concl, fill=INK)
    yy += CONCL_LH

import argparse

_REPO = Path(__file__).resolve().parent.parent
_parser = argparse.ArgumentParser(description="生成瘦≠薄肌对比图")
_parser.add_argument("--output", default=str(_REPO / "assets" / "lean-vs-thin.png"))
_args = _parser.parse_args()

out = _args.output
img.save(out, "PNG")
print("saved", out, img.size, "concl_bottom", cy + concl_h, "H", H)