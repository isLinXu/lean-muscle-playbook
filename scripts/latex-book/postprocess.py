#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""将 pandoc 生成的 body.tex 调整为 ctexbook 章节结构。"""
import re

SRC = "body.tex"

with open(SRC, "r", encoding="utf-8") as f:
    tex = f.read()

# 1. 去掉 hypertarget/{ 包装行
tex = re.sub(r"\\hypertarget\{[^}]*\}\{\%\n", "", tex)
# 2. 去掉标题行尾的 \label{...}}
tex = re.sub(r"\\label\{[^}]*\}\}", "", tex)

# 3. 删除文档主标题 chapter（封面已含）及其后的一句话主题 quote
tex = re.sub(
    r"\\chapter\{孙宇晨访谈记录整理\}\n\n"
    r"\\begin\{quote\}.*?\\end\{quote\}\n\n",
    "",
    tex,
    flags=re.S,
)

# 4. 一级章节：\section{一、概览} -> \chapter{概览}
chapter_map = [
    (r"\\section\{一、概览\}", r"\\chapter{概览}"),
    (r"\\section\{二、议题整理\}", r"\\chapter{议题整理}"),
    (r"\\section\{三、深潜：互联网检索补全的三本理论体系\}",
     r"\\chapter{深潜：互联网检索补全的三本理论体系}"),
    (r"\\section\{四、核心金句摘录\}", r"\\chapter{核心金句摘录}"),
    (r"\\section\{五、后续行动项\}", r"\\chapter{后续行动项}"),
    (r"\\section\{六、训练手册：8\s+周实操行动清单\}",
     r"\\chapter{训练手册：8 周实操行动清单}"),
]
for pat, rep in chapter_map:
    tex = re.sub(pat, rep, tex)

# 5. 议题：\subsection{1. 开场与日常...} -> \section{开场与日常...}（去掉数字前缀）
tex = re.sub(r"\\subsection\{(\d+)\.\s+", r"\\section{", tex)

# 5.1 金句标题：\subsection{金句一...} -> \section{金句一...}
tex = re.sub(r"\\subsection\{金句", r"\\section{金句", tex)

# 6. 三书小节：\subsection{（一）...} -> \section{...}
tex = re.sub(r"\\subsection\{（[一二三]）", r"\\section{", tex)

# 6.1 扩展小节（非数字前缀）：\subsection{议题全景图...} 等 -> \section{...}
_lift_sections = [
    "议题全景图", "从议题到行动", "议题中的五组张力", "三书横向对比",
    "思想进化时间线", "三书与访谈的互证清单", "薄肌科学性的逻辑核查",
    "争议与批评视角", "金句速记表", "阅读提示：如何区分事实、观点与预测",
    "行动路线图", "常见失败模式",
    "附录：信息缺口与来源说明", "附录：延伸阅读与核对建议",
    "附录：思维模型清单", "附录：整理者后记",
]
for _t in _lift_sections:
    tex = re.sub(r"\\subsection\{" + re.escape(_t), r"\\section{" + _t, tex)

# 6.2 修复 pandoc longtable 列宽：p{(\columnwidth - 2\tabcolsep) * \real{0.5000}} 在 XeTeX 下非法，
#     统一替换为除法形式 p{\dimexpr(\columnwidth - 2\tabcolsep)/2 \relax}
def _fix_colwidth(m):
    gap = int(m.group(1))            # 2 / 4 / 6 ...
    frac = float("0." + m.group(2))  # 0.5000 / 0.3333 / 0.2500 ...
    k = round(1.0 / frac)            # 2 / 3 / 4 ...
    return "p{\\dimexpr(\\columnwidth - %d\\tabcolsep)/%d \\relax}" % (gap, k)


tex = re.sub(
    r"p\{\(\\columnwidth - (\d+)\\tabcolsep\) \* \\real\{0\.(\d+)\}\}",
    _fix_colwidth,
    tex,
)

# 6.3 金句速记表：三列自然宽度（lll）会溢出 101.5pt，改为定宽 p 列
_fixed_quote_cols = (
    "\\begin{longtable}[]{@{}\n"
    "  >{\\raggedright\\arraybackslash}p{\\dimexpr0.40\\columnwidth-2\\tabcolsep\\relax}\n"
    "  >{\\raggedright\\arraybackslash}p{\\dimexpr0.48\\columnwidth-2\\tabcolsep\\relax}\n"
    "  >{\\raggedright\\arraybackslash}p{\\dimexpr0.12\\columnwidth-2\\tabcolsep\\relax}@{}}"
)
tex = re.sub(
    r"\\begin\{longtable\}\[\][ ]?\{\@\{\}lll@\{\}\}",
    lambda _m: _fixed_quote_cols,
    tex,
)

# 7. 三书"核心观点"独立小标题：从 itemize 中移出
def _lift_core_point(m):
    return "\n\\end{itemize}\n\n\\subsubsection*{核心观点}\n\n\\begin{itemize}\n\\item\n"


tex = re.sub(
    r"\n  \\textbf\{核心观点\}\n\\item\n",
    _lift_core_point,
    tex,
)

with open(SRC, "w", encoding="utf-8") as f:
    f.write(tex)

# 校验：应无残留 hypertarget/label/旧前缀
leftovers = re.findall(r"\\hypertarget|\\label\{|\\subsection\{|\\section\{一、|\\section\{二、|\\section\{三、|\\section\{四、|\\section\{五、|\\section\{六、", tex)
print("leftovers:", leftovers)
print("core points:", tex.count("核心观点"))
print("chapters:", re.findall(r"\\chapter\{([^}]*)\}", tex))