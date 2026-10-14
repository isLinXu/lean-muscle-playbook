# 孙宇晨访谈记录整理 · 黑皮书 LaTeX 小书

将《孙宇晨访谈记录整理-薄肌与AI认知》核心内容排版为 A5 开本、黑皮书风格的小书。

## 工程结构

```
scripts/latex-book/
├── main.tex           # 主文档：封面、版权页、目录、正文引入
├── body.tex           # 正文六章（pandoc 转换 + 后处理生成）
├── body_src.md        # 正文 Markdown 源（pandoc 输入）
├── body_src_orig.md   # 正文原始 Markdown（未扩展版本）
├── postprocess.py     # body.tex 后处理脚本（章节结构调整）
├── expand2.py / expand3.py / expand4.py
├── expand_books.py    # 扩写与素材插入脚本
├── insert_ext.py
├── main.pdf           # 已编译成品（138 页）
└── README.md
```

## 编译方法

仓库内已包含编译成品 `main.pdf`（138 页）；如需自行编译，需要 XeLaTeX 与中文支持：

```bash
# Debian / Ubuntu
apt install texlive-xetex texlive-lang-chinese fonts-noto-cjk

# 编译（至少两遍生成目录与书签）
xelatex -interaction=nonstopmode main.tex
xelatex -interaction=nonstopmode main.tex
xelatex -interaction=nonstopmode main.tex
```

生成 `main.pdf`（138 页）。

## 自动编译（GitHub Actions）

仓库 `.github/workflows/build-latex.yml` 会在以下时机自动重新编译本工程：

- `scripts/latex-book/` 下源文件（`.tex` / `.md` / `.py`）推送到 `main` 时；
- 手动触发（Actions → Build LaTeX Book PDF → Run workflow）。

工作流在 `ubuntu-latest` 上安装 `texlive-xetex`、`texlive-lang-chinese`、`fonts-noto-cjk`，
三遍 `xelatex` 编译 `main.pdf`，校验页数不少于 100 页，上传构建产物 artifact，
并在 PDF 内容变化时自动提交回 `main` 分支，在线阅读站「下载全书 PDF」随之保持最新。

## 黑皮书风格要点

- **封面**：纯黑底、居中白色书名、金色副标题与分隔线、底部灰色说明。
- **开本**：A5（148mm × 210mm），左 2.6cm / 右 2.6cm / 上 2.8cm / 下 3.0cm。
- **字体**：Noto Serif CJK SC 正文、Noto Sans CJK SC 标题。
- **章节**：章号金色大字置于页面左上，章题黑体 24pt，章节间大幅留白。
- **页眉页脚**：左侧书名、右侧当前章节名，页脚居中页码；章首页无页眉。

## 内容结构

1. 概览（含元信息表与术语说明）
2. 议题整理（14 个议题）
3. 深潜：互联网检索补全的三本理论体系（《薄肌圣经》《孙学》《财务自由革命之路》）
4. 核心金句摘录（12 条）
5. 后续行动项（含三列行动表）
6. 训练手册：8 周实操行动清单（4 阶段逐周动作清单、渐进超负荷规则与动作速查卡）

> 术语约定：全文统一"薄肌"；"搏击"仅用于术语说明及电影专名《搏击俱乐部》。