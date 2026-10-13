# -*- coding: utf-8 -*-
"""生成《孙宇晨访谈记录-8周训练打卡表.xlsx》（仓库可复用版）

数据源：docs/black-book.md 第六章「训练手册：8 周实操行动清单」
      （四阶段逐日表、动作速查卡；数据与源文件逐字一致）
输出：templates/checkin.xlsx（默认）
校验声明：working/validation.json 写入系统临时目录（不入库）

用法：
    python scripts/generate_checkin_xlsx.py
    python scripts/generate_checkin_xlsx.py --output 自定义输出路径.xlsx
依赖：python3 + openpyxl（pip install openpyxl）
"""
import argparse
import json
import os
import sys
import tempfile
from pathlib import Path

from openpyxl import Workbook
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import get_column_letter
from openpyxl.worksheet.datavalidation import DataValidation

# ---------------- 路径：相对本脚本定位仓库根，便于从任意位置运行 ----------------
SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parent
DEFAULT_OUTPUT = REPO_ROOT / "templates" / "checkin.xlsx"
VAL_DIR = Path(tempfile.gettempdir()) / "lean-muscle-playbook-build"
os.makedirs(VAL_DIR, exist_ok=True)
VALIDATION = VAL_DIR / "validation.json"

# ---------------- 配色（与交付版一致） ----------------
FONT_NAME = "Arial"
INK = "2B2B2B"            # 正文深灰
GOLD = "B08D3E"           # 强调金
HEADER_BG = "3A4A4D"      # 深灰青表头
HEADER_FG = "FFFFFF"
STAGE_BG_A = "F6F2E9"     # 奇数阶段浅底
STAGE_BG_B = "FFFFFF"     # 偶数阶段白底
BORDER_CC = "CCCCCC"
GRAY_NOTE = "666666"

thin = Side(style="thin", color=BORDER_CC)
BORDER = Border(left=thin, right=thin, top=thin, bottom=thin)

F_TITLE = Font(name=FONT_NAME, size=20, bold=True, color=INK)
F_SUB = Font(name=FONT_NAME, size=11, bold=False, color=GRAY_NOTE)
F_HEADER = Font(name=FONT_NAME, size=12, bold=True, color=HEADER_FG)
F_BODY = Font(name=FONT_NAME, size=11, color=INK)
F_BOLD = Font(name=FONT_NAME, size=11, bold=True, color=INK)
F_NOTE = Font(name=FONT_NAME, size=10, italic=True, color=GRAY_NOTE)

AL_C = Alignment(horizontal="center", vertical="center", wrap_text=True)
AL_L = Alignment(horizontal="left", vertical="center", wrap_text=True)

# ---------------- 第六章程数据（与 docs/black-book.md 逐字一致） ----------------
# (星期, 训练内容, 目标组次/动作明细, 时长/间歇)
W1 = [
    ("周一", "力量 A·下肢+核心", "徒手深蹲 3×8–10（退阶：椅子辅助深蹲）；臀桥 3×10–12；平板支撑 3×20–30 秒（退阶：跪姿平板）", "30–35 分钟；组间 60–90 秒"),
    ("周二", "有氧：中等强度", "快走/骑行/椭圆机，中等强度（能说话但不太能唱歌）", "20–25 分钟"),
    ("周三", "力量 B·上肢+核心", "跪姿俯卧撑 3×6–8（退阶：上斜俯卧撑）；弹力带划船 3×10–12；平板支撑 3×20–30 秒", "30–35 分钟；组间 60–90 秒"),
    ("周四", "休息或散步", "—", "—"),
    ("周五", "力量 C·全身补弱", "徒手深蹲 3×8–10；跪姿俯卧撑 3×6–8；臀桥 3×10–12；平板支撑 3×20–30 秒", "30–35 分钟；组间 60–90 秒"),
    ("周六", "有氧：较长一次", "快走/爬坡走/骑行", "25–30 分钟"),
    ("周日", "完全休息", "—", "—"),
]
W2 = [
    ("周一", "力量 A·下肢+核心", "深蹲 3–4×10–12（进阶：双手各持 2.5–5kg 哑铃）；臀桥 3×12–15（进阶：负重/单腿）；平板支撑 3×30–45 秒", "35–40 分钟；组间 60–90 秒"),
    ("周二", "有氧：中等强度", "快走/骑行/椭圆机，中等强度", "25–30 分钟"),
    ("周三", "力量 B·上肢+核心", "标准俯卧撑 3×8–10（退阶：跪姿）；哑铃或弹力带划船 3×10–12；侧平举 2–3×12–15；平板支撑 3×30–45 秒", "35–40 分钟；组间 60–90 秒"),
    ("周四", "休息或散步", "—", "—"),
    ("周五", "力量 C·全身补弱", "深蹲 3×10–12；俯卧撑 3×8–10；臀桥 3×12–15；死虫/登山者 3×10–12（每侧）", "35–40 分钟；组间 60–90 秒"),
    ("周六", "有氧：较长一次", "按能力加 5 分钟", "30–35 分钟"),
    ("周日", "完全休息", "—", "—"),
]
W3 = [
    ("周一", "力量 A·下肢+核心", "高脚杯深蹲（哑铃 5–10kg）4×8–12；罗马尼亚硬拉（哑铃/弹力带）3×8–10；臀桥 3×12–15（负重）；平板支撑 3×45–60 秒", "40–45 分钟；组间 60–90 秒"),
    ("周二", "有氧：中等强度", "快走/骑行/椭圆机，中等强度", "30 分钟"),
    ("周三", "力量 B·上肢+核心", "俯卧撑 3–4×10–12（进阶：下斜）；单臂哑铃划船/弹力带划船 3×10–12；哑铃推举 3×8–10；侧平举 3×12–15；平板支撑 3×45–60 秒", "40–45 分钟；组间 60–90 秒"),
    ("周四", "休息或散步", "—", "—"),
    ("周五", "力量 C·全身补弱", "高脚杯深蹲 4×8–12；俯卧撑 3×10–12；罗马尼亚硬拉 3×8–10；死虫/登山者 3×12–16", "40–45 分钟；组间 60–90 秒"),
    ("周六", "有氧：较长一次", "可爬山/骑行", "35–45 分钟"),
    ("周日", "完全休息", "—", "—"),
]
W4 = [
    ("周一", "力量 A·下肢+核心", "沿用阶段三重量，深蹲/高脚杯深蹲 4×8–12；臀桥 3×12–15；平板支撑 3×45–60 秒；最后一组做到力竭（安全前提下）", "40–45 分钟；组间 75–90 秒"),
    ("周二", "有氧：中等强度", "快走/骑行/椭圆机，中等强度", "30 分钟"),
    ("周三", "力量 B·上肢+核心", "俯卧撑 4×10–12；划船 3×10–12；推举 3×8–10；平板支撑 3×45–60 秒", "40–45 分钟；组间 75–90 秒"),
    ("周四", "休息或散步", "—", "—"),
    ("周五", "力量 C·全身补弱", "高脚杯深蹲 4×8–12；俯卧撑 3×10–12；罗马尼亚硬拉 3×8–10；死虫 3×12–16", "40–45 分钟；组间 75–90 秒"),
    ("周六", "有氧：较长一次", "最后 1 次按计划完成即可", "35–45 分钟"),
    ("周日", "完全休息 + 终期复盘", "对照第 1 周基线做终期复盘（体重/腰围/照片/训练日志）", "—"),
]

STAGES = [
    {"stage": "阶段一", "weeks": [1, 2], "days": W1},
    {"stage": "阶段二", "weeks": [3, 4], "days": W2},
    {"stage": "阶段三", "weeks": [5, 6], "days": W3},
    {"stage": "阶段四", "weeks": [7, 8], "days": W4},
]

QUICK_CARD = [
    ("深蹲", "双脚与肩同宽，下蹲到膝盖约 90°、膝盖不内扣，臀部向后坐，起身时收紧臀部与核心", "椅子辅助 → 徒手 → 高脚杯哑铃"),
    ("臀桥", "仰卧屈膝，脚跟踩地，臀部顶起至躯干成直线，顶端停顿 1 秒，缓慢下落", "徒手 → 负重（哑铃放髋上）→ 单腿"),
    ("俯卧撑", "身体成直线、核心收紧，下落至胸部接近地面，推起时肘部不完全锁死", "跪姿/上斜 → 标准 → 下斜/负重背心"),
    ("划船", "腰背挺直，肩胛后收带动手臂拉向肋骨方向，顶端停顿，慢放", "弹力带 → 哑铃 → 单臂哑铃"),
    ("推举", "哑铃从肩部推至头顶正上方，核心收紧，避免过度挺腰", "空手 → 轻哑铃（2–4kg）→ 加重"),
    ("罗马尼亚硬拉", "微屈膝，髋部后移、背部平直，哑铃沿大腿下放至小腿中上部，臀部发力站起", "空杆/轻哑铃 → 加重 → 壶铃"),
    ("平板支撑", "肘撑、身体成直线，收腹提臀，不塌腰不撅臀，均匀呼吸", "跪姿平板 → 标准 → 加时间/抬腿"),
    ("侧平举", "肩部发力向两侧抬起至与肩同高，肘微屈，慢放不耸肩", "空手 → 1–2kg → 加重"),
    ("死虫/登山者", "核心收紧、腰背贴地（死虫）；登山者保持躯干稳定、交替提膝", "死虫慢速 → 标准 → 加快"),
]

CHECKIN_HEADERS = ["周次", "星期", "阶段", "训练内容", "目标组次（动作明细）", "时长/间歇", "完成勾选", "备注"]


def _style_header_row(ws, row, ncols):
    for col in range(1, ncols + 1):
        c = ws.cell(row=row, column=col)
        c.font = F_HEADER
        c.fill = PatternFill("solid", fgColor=HEADER_BG)
        c.alignment = AL_C
        c.border = BORDER
    ws.row_dimensions[row].height = 40


def _style_title(ws, row, text, span):
    ws.merge_cells(start_row=row, start_column=1, end_row=row, end_column=span)
    c = ws.cell(row=row, column=1)
    c.value = text
    c.font = F_TITLE
    c.alignment = Alignment(horizontal="left", vertical="center")
    ws.row_dimensions[row].height = 46


def build_usage(wb):
    ws = wb.create_sheet("使用说明")
    ws.sheet_view.showGridLines = True
    for i, w in enumerate([4, 40, 16, 16, 16, 16, 16, 16]):
        ws.column_dimensions[get_column_letter(i + 1)].width = w

    _style_title(ws, 1, "8 周训练打卡表", 8)
    ws.merge_cells("A2:H2")
    c = ws.cell(row=2, column=1)
    c.value = "配套《孙宇晨访谈记录·黑皮书小书》第六章·训练手册：8 周实操行动清单"
    c.font = F_SUB
    c.alignment = AL_L
    ws.row_dimensions[2].height = 20

    rows = [
        ("一、口径说明", True),
        ("本表动作编排来自第六章「训练手册：8 周实操行动清单」，是整理者依据公开健康资料（卫健委、三甲医院、运动科学综述）与通用训练编排整合的实操建议，非《薄肌圣经》原文。", False),
        ("书中对训练的表述仅见于公开解读（每天约 30 分钟、八周见效、三步启动法），未披露逐周动作明细；本表给出的是可照做的落地方案，仅供健康成人参考。", False),
        ("体脂已低于健康下限、有慢性病或孕期者，应先咨询专业人士再执行；本表不构成医学、营养学或运动处方建议。", False),
        ("阶段一在原文标注为「第 2 周」，为保持 8 周四阶段完整使用，本表将同一周安排用于第 1–2 周（搭底子）；如需从第 2 周开始，可跳过第 1 周各行。", False),
        ("", False),
        ("二、打卡方式", True),
        ("1. 每周力量日 A/B/C 轮换一次，两次力量训练间隔 ≥48 小时；4 个阶段共 8 周，逐日安排见「8周打卡总表」。", False),
        ("2. 「完成勾选」列使用下拉：完成 / 未完成 / 部分完成 / 休息日；顺手把当日实际重量、次数或感受记在「备注」列。", False),
        ("3. 力量不足时一律先做「退阶版」，标准姿势优先，不要跳过退阶直接上重量。", False),
        ("4. 渐进超负荷：同一动作连续两周都能完成目标组次数、且最后 1–2 次仍有余力时，下一周加 1 组数、或加 2–5kg 负重、或加 10–15 秒平板时间，三者每次只动一个变量，并在备注里记录。", False),
        ("", False),
        ("三、四阶段总览", True),
        ("第 1–2 周｜阶段一｜搭底子：掌握动作，不追求数量", False),
        ("第 3–4 周｜阶段二｜容量递增：每组加次数，开始加轻负重", False),
        ("第 5–6 周｜阶段三｜负重进阶：重量小幅上调，容量维持", False),
        ("第 7–8 周｜阶段四｜冲刺收官：维持容量，做终期复盘", False),
        ("", False),
        ("四、注意事项", True),
        ("每个动作首次做时对着镜子或拍视频自查一次；居家无镜子可请家人帮忙看或拍 30 秒视频回看「腰背是否平直、膝盖是否内扣」。", False),
        ("第 8 周周日对照第 1 周基线做终期复盘：体重、腰围、照片、训练日志。", False),
        ("", False),
        ("数据来源：第六章训练手册（整理者依据公开健康资料整合，非书中原文）；动作速查卡 9 个动作均可在「动作速查卡」工作表查询退阶/标准/进阶。", True),
        ("生成/更新时间：2026-10-13", True),
    ]
    r = 4
    for text, bold in rows:
        ws.merge_cells(start_row=r, start_column=1, end_row=r, end_column=8)
        c = ws.cell(row=r, column=1)
        c.value = text
        c.font = F_BOLD if bold else F_BODY
        c.alignment = AL_L
        ws.row_dimensions[r].height = 22 if bold else 30
        r += 1
    return ws


def build_checkin(wb):
    ws = wb.create_sheet("8周打卡总表")
    ws.sheet_view.showGridLines = True
    widths = [10, 12, 12, 22, 62, 24, 12, 20]
    for i, w in enumerate(widths):
        ws.column_dimensions[get_column_letter(i + 1)].width = w

    _style_title(ws, 1, "8 周逐日打卡总表", len(CHECKIN_HEADERS))
    ws.row_dimensions[1].height = 40
    for j, h in enumerate(CHECKIN_HEADERS, start=1):
        ws.cell(row=2, column=j, value=h)
    _style_header_row(ws, 2, len(CHECKIN_HEADERS))

    r = 3
    for si, stage in enumerate(STAGES):
        bg = STAGE_BG_A if si % 2 == 0 else STAGE_BG_B
        fill = PatternFill("solid", fgColor=bg)
        for week in stage["weeks"]:
            for day in stage["days"]:
                values = ["第%d周" % week, day[0], stage["stage"], day[1], day[2], day[3], "", ""]
                for j, v in enumerate(values, start=1):
                    c = ws.cell(row=r, column=j, value=v)
                    c.font = F_BODY
                    c.border = BORDER
                    c.fill = fill
                    c.alignment = AL_C if j in (1, 2, 3, 7, 8) else AL_L
                ws.row_dimensions[r].height = 34
                r += 1

    dv = DataValidation(
        type="list",
        formula1='"完成,未完成,部分完成,休息日"',
        allow_blank=True,
        showDropDown=False,
    )
    ws.add_data_validation(dv)
    dv.add("G3:G%d" % (r - 1))

    ws.freeze_panes = "A3"
    ws.print_area = "A1:H%d" % (r - 1)
    ws.sheet_view.zoomScale = 90
    return ws


def build_quickcard(wb):
    ws = wb.create_sheet("动作速查卡")
    ws.sheet_view.showGridLines = True
    widths = [16, 68, 40]
    for i, w in enumerate(widths):
        ws.column_dimensions[get_column_letter(i + 1)].width = w

    _style_title(ws, 1, "动作速查卡（退阶 / 标准 / 进阶）", 3)
    headers = ["动作", "标准做法要点", "退阶 → 进阶"]
    for j, h in enumerate(headers, start=1):
        ws.cell(row=2, column=j, value=h)
    _style_header_row(ws, 2, 3)

    for i, row in enumerate(QUICK_CARD):
        r = 3 + i
        for j, v in enumerate(row, start=1):
            c = ws.cell(row=r, column=j, value=v)
            c.font = F_BODY
            c.border = BORDER
            c.alignment = AL_C if j == 1 else AL_L
            if i % 2 == 1:
                c.fill = PatternFill("solid", fgColor="F6F2E9")
        ws.row_dimensions[r].height = 34

    ws.freeze_panes = "A3"
    ws.print_area = "A1:C11"
    ws.sheet_view.zoomScale = 100
    return ws


def write_spec():
    spec = {
        "tables": [
            {
                "name": "checkin",
                "sheet": "8周打卡总表",
                "header_row": 2,
                "data_start_row": 3,
                "start_column": "A",
                "expected_headers": CHECKIN_HEADERS,
                "column_rules": {
                    "周次": {"type": "text", "pattern": "第[1-8]周"},
                    "星期": {"type": "text", "pattern": "周[一二三四五六日]"},
                    "阶段": {"type": "text", "pattern": "阶段[一二三四]"},
                    "训练内容": {"type": "text"},
                    "目标组次（动作明细）": {"type": "text"},
                    "时长/间歇": {"type": "text"},
                    "完成勾选": {"type": "text"},
                    "备注": {"type": "text"},
                },
            },
            {
                "name": "quickcard",
                "sheet": "动作速查卡",
                "header_row": 2,
                "data_start_row": 3,
                "start_column": "A",
                "expected_headers": ["动作", "标准做法要点", "退阶 → 进阶"],
                "column_rules": {
                    "动作": {"type": "text"},
                    "标准做法要点": {"type": "text"},
                    "退阶 → 进阶": {"type": "text"},
                },
            },
        ],
        "gap_columns": 0,
        "gap_rows": 0,
        "sheets": [
            {"sheet": "8周打卡总表", "protected_ranges": ["A1:H58"]},
            {"sheet": "动作速查卡", "protected_ranges": ["A1:C11"]},
            {"sheet": "使用说明", "protected_ranges": ["A1:H28"]},
        ],
    }
    with open(VALIDATION, "w", encoding="utf-8") as f:
        json.dump(spec, f, ensure_ascii=False, indent=2)


def main():
    parser = argparse.ArgumentParser(description="生成 8 周训练打卡表 xlsx")
    parser.add_argument("--output", default=str(DEFAULT_OUTPUT), help="输出 xlsx 路径（默认 templates/checkin.xlsx）")
    args = parser.parse_args()

    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)

    wb = Workbook()
    wb.remove(wb.active)
    build_usage(wb)
    build_checkin(wb)
    build_quickcard(wb)
    wb.save(out)

    write_spec()
    print("OK output.xlsx ->", out)
    print("validation.json ->", VALIDATION)


if __name__ == "__main__":
    sys.exit(main())