# scripts —— 版本化生成脚本

仓库维护采用「内容真源化」：`docs/` 与 `guides/` 下的 markdown 为正文真源，
PDF / XLSX / PNG / HTML 为构建产物。修改源后运行本目录脚本重新生成，
避免多版本漂移。

## 脚本清单

| 脚本 | 作用 | 依赖 | 生成物 |
| --- | --- | --- | --- |
| `generate_checkin_xlsx.py` | 由黑皮书第六章数据生成 8 周打卡表 xlsx（四阶段逐日表 + 使用说明 + 动作速查卡 9 动作，完成列下拉） | python3 + openpyxl | `templates/checkin.xlsx` |
| `render_lean_chart.py` | 确定性渲染「瘦≠薄肌」对比图（PIL + Noto Sans CJK SC，2160×2880） | python3 + Pillow + Noto CJK 字体 | `assets/lean-vs-thin.png` |
| `print/body.typ` | 打卡表打印版（A4）typst 源 | typst（Python 包或 CLI）+ Zhuque Fangsong 字体 | `templates/checkin-print.pdf` |
| `latex-book/main.tex` + `postprocess.py` | 黑皮书 LaTeX 工程骨架（正文源 `docs/black-book.md`，经 pandoc 转 tex 后编译） | pandoc + XeLaTeX + Noto CJK 字体 | 黑皮书 PDF |

## 重新生成命令

```bash
# 1. 打卡表 xlsx（输出到 templates/checkin.xlsx）
python scripts/generate_checkin_xlsx.py

# 自定义输出
python scripts/generate_checkin_xlsx.py --output /tmp/checkin.xlsx

# 2. 对比图 PNG（输出到 assets/lean-vs-thin.png）
python scripts/render_lean_chart.py
python scripts/render_lean_chart.py --output /tmp/lean-vs-thin.png

# 3. 打印版 PDF（需 typst；字体路径按本机环境调整）
#    参考：python -c "import typst; typst.compile('scripts/print/body.typ', output='templates/checkin-print.pdf', font_paths=[<字体目录>])"

# 4. 黑皮书 PDF（需 pandoc + XeLaTeX）
#    pandoc docs/black-book.md -o body.tex --top-level-division=chapter
#    python scripts/latex-book/postprocess.py
#    xelatex -interaction=nonstopmode scripts/latex-book/main.tex   # 连续三遍
```

## 口径提醒

打卡表数据与 `docs/black-book.md` 第六章、`guides/8-week-plan/` 三处必须一致；
修改动作清单时请三处同步（可先改 `docs/black-book.md`，再运行生成脚本并人工核对
`guides/8-week-plan/` 派生文件）。生成物只是构建结果，冲突时以 md 源为准。

## 环境说明

- 本仓库脚本在隔离 Linux 沙箱中开发验证；字体路径（Noto Sans CJK、Zhuque Fangsong）
  为沙箱路径，换环境时请按本机字体实际路径调整 `render_lean_chart.py` 顶部常量与
  typst `font_paths` 参数。
- typst 无二进制时可用 Python 包：`pip install typst`。