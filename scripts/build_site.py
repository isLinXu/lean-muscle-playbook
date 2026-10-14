#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""构建 lean-muscle-playbook 的静态在线阅读站点（site/）。

用法：
    python3 scripts/build_site.py            # 以仓库根目录为工作目录
    python3 scripts/build_site.py /abs/repo  # 或显式指定仓库根目录

把 README/docs/guides 等内容渲染为有统一顶栏导航、页内目录、
正文排版与资源引用的多页静态站点，并拷入图片与可下载资源。
构建产物提交 git 后，GitHub Actions（.github/workflows/pages.yml）
会直接把 site/ 发布为 GitHub Pages。

内容真源仍是仓库内 Markdown / HTML / 模板文件；修改源后重跑本脚本即可。
"""
import html as html_mod
import pathlib
import posixpath
import re
import shutil
import subprocess
import sys

ROOT = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else ".").resolve()
SITE = ROOT / "site"

# ---------- 页面清单：src（仓库相对路径）→ site 输出路径 ----------
MD_PAGES = [
    # (仓库源路径, site 输出路径, 页面标题, 顶栏高亮 key)
    ("README.md", "index.html", "薄肌行动手册 · 在线阅读", "home"),
    ("docs/black-book.md", "docs/black-book.html", "黑皮书：孙宇晨访谈记录整理", "book"),
    ("docs/glossary.md", "docs/glossary.html", "术语统一口径", "glossary"),
    ("guides/8-week-plan/README.md", "guides/8-week-plan/index.html", "8 周实操行动清单 · 分阶段明细", "plan"),
    ("guides/8-week-plan/stage-1.md", "guides/8-week-plan/stage-1.html", "阶段一 · 搭底子（第 2 周）", "plan"),
    ("guides/8-week-plan/stage-2.md", "guides/8-week-plan/stage-2.html", "阶段二 · 容量递增（第 3–4 周）", "plan"),
    ("guides/8-week-plan/stage-3.md", "guides/8-week-plan/stage-3.html", "阶段三 · 负重进阶（第 5–6 周）", "plan"),
    ("guides/8-week-plan/stage-4.md", "guides/8-week-plan/stage-4.html", "阶段四 · 冲刺收官（第 7–8 周）", "plan"),
    ("guides/8-week-plan/exercise-cards.md", "guides/8-week-plan/exercise-cards.html", "动作速查卡（退阶 / 标准 / 进阶）", "plan"),
]

# 需要注入站点导航的已有 HTML（读取源文件，保留正文，插入顶栏）
NAV_HTML_PAGES = [
    ("guides/practice-guide.html", "guides/practice-guide.html", "薄肌实操指南 · 8 周行动手册", "guide"),
]

# 直接复制的资源（仓库相对路径 → site 相对路径）
COPY_FILES = [
    ("assets/lean-vs-thin.png", "assets/lean-vs-thin.png"),
    ("docs/interview-notes.docx", "docs/interview-notes.docx"),
    ("templates/checkin.xlsx", "templates/checkin.xlsx"),
    ("templates/checkin-print.pdf", "templates/checkin-print.pdf"),
    ("LICENSE", "LICENSE"),
]

# markdown 链接目标 → site 输出路径（仓库相对路径为 key）
LINK_MAP = {
    "README.md": "index.html",
    "LICENSE": "LICENSE",
    "docs/black-book.md": "docs/black-book.html",
    "docs/glossary.md": "docs/glossary.html",
    "docs/interview-notes.docx": "docs/interview-notes.docx",
    "guides/practice-guide.html": "guides/practice-guide.html",
    "guides/8-week-plan/README.md": "guides/8-week-plan/index.html",
    "guides/8-week-plan/stage-1.md": "guides/8-week-plan/stage-1.html",
    "guides/8-week-plan/stage-2.md": "guides/8-week-plan/stage-2.html",
    "guides/8-week-plan/stage-3.md": "guides/8-week-plan/stage-3.html",
    "guides/8-week-plan/stage-4.md": "guides/8-week-plan/stage-4.html",
    "guides/8-week-plan/exercise-cards.md": "guides/8-week-plan/exercise-cards.html",
    "assets/lean-vs-thin.png": "assets/lean-vs-thin.png",
    "templates/checkin.xlsx": "templates/checkin.xlsx",
    "templates/checkin-print.pdf": "templates/checkin-print.pdf",
}

# 顶栏导航定义（key → 目标 site 相对路径模板，{p} 为相对前缀含尾部斜杠）
NAV_ITEMS = [
    ("home", "首页", "{p}index.html"),
    ("book", "黑皮书", "{p}docs/black-book.html"),
    ("glossary", "术语表", "{p}docs/glossary.html"),
    ("guide", "实操指南", "{p}guides/practice-guide.html"),
    ("plan", "8 周行动清单", "{p}guides/8-week-plan/index.html"),
]

PLAN_SUBPAGES = [
    ("stage-1", "阶段一", "stage-1.html"),
    ("stage-2", "阶段二", "stage-2.html"),
    ("stage-3", "阶段三", "stage-3.html"),
    ("stage-4", "阶段四", "stage-4.html"),
    ("cards", "动作速查卡", "exercise-cards.html"),
]


def pandoc_md_to_html(src: pathlib.Path) -> str:
    """用 pandoc 把 GFM 渲染成 HTML 正文片段。"""
    proc = subprocess.run(
        ["pandoc", "-f", "gfm+pipe_tables", "-t", "html5", "--wrap=none", str(src)],
        capture_output=True, text=True, check=True,
    )
    return proc.stdout


def relative_prefix(site_rel: str) -> str:
    """site 输出路径（如 docs/black-book.html）→ 相对根目录的前缀（..）。"""
    depth = len(pathlib.PurePosixPath(site_rel).parts) - 1
    return "/".join([".."] * depth) if depth > 0 else ""


def prefix_slash(site_rel: str) -> str:
    """带尾部斜杠的相对前缀：docs/black-book.html -> ../，index.html -> ''。"""
    p = relative_prefix(site_rel)
    return f"{p}/" if p else ""


def rewrite_links(html_body: str, src_rel: str, site_rel: str) -> str:
    """把 HTML 正文中指向仓库内文件的相对链接重写为 site 内正确路径。

    在 pandoc 渲染后的 HTML 上操作：所有 `href`/`src` 指向仓库内文件
    （.md / .png / .xlsx / .docx / .pdf 等）时，按「源文件所在目录 + 目标」
    解析为仓库相对路径，再由 LINK_MAP 映射到 site 路径，最后转成相对前缀。
    外部链接与纯锚点链接保持不变。
    """
    prefix = relative_prefix(site_rel)
    src_dir = pathlib.PurePosixPath(src_rel).parent.as_posix()

    def url(target: str) -> str:
        if re.match(r"^(https?:|mailto:|#)", target):
            return target
        path_part, sep, frag = target.partition("#")
        if not path_part:
            return target
        repo_rel = posixpath.normpath(posixpath.join(src_dir, path_part))
        site_target = LINK_MAP.get(repo_rel)
        if site_target is None:
            return target
        new_href = f"{prefix}/{site_target}" if prefix else site_target
        if sep:
            new_href += "#" + frag
        return new_href

    return re.sub(r'(href|src)="([^"]+)"',
                  lambda m: f'{m.group(1)}="{url(m.group(2))}"', html_body)


def assign_ids_and_toc(html_body: str):
    """给 h2/h3/h4 分配稳定 id，并生成目录（两层：章/节）。

    返回 (html_body, toc_html)。标题 id 规则：
      h2 -> ch-1, ch-2 ...；h3 -> ch-1-s1 ...；h4 -> ch-1-s1-1 ...
    目录只收录 h2 与 h3（避免正文过长时目录膨胀）。
    """
    counters = {"h2": 0, "h3": 0, "h4": 0}
    toc_items = []  # (level, text, id)

    def repl(m):
        tag = m.group(1)
        inner = m.group(3)
        counters[tag] += 1
        if tag == "h2":
            cid = f"ch-{counters['h2']}"
            counters["h3"] = 0
            counters["h4"] = 0
        elif tag == "h3":
            cid = f"ch-{counters['h2']}-s{counters['h3']}"
            counters["h4"] = 0
        else:
            cid = f"ch-{counters['h2']}-s{counters['h3']}-{counters['h4']}"
        text = re.sub(r"<[^>]+>", "", inner)
        text = html_mod.unescape(text).strip()
        if tag in ("h2", "h3"):
            toc_items.append((tag, text, cid))
        return f'<{tag} id="{cid}">{inner}</{tag}>'

    body = re.sub(r"<(h[234])([^>]*)>((?:(?!</\1>).)*?)</\1>", repl, html_body, flags=re.S)

    if not toc_items:
        return body, ""
    lines = ['<nav class="toc"><div class="toc-title">本页目录</div><ol>']
    for lvl, text, cid in toc_items:
        cls = "lvl2" if lvl == "h2" else "lvl3"
        lines.append(f'<li class="{cls}"><a href="#{cid}">{html_mod.escape(text)}</a></li>')
    lines.append("</ol></nav>")
    return body, "\n".join(lines)


NAV_TMPL = """<header class="topbar"><div class="topbar-inner">
<a class="brand" href="{p}index.html"><span class="dot"></span>薄肌行动手册</a>
<nav><ul>
{nav}
</ul></nav>
<a class="gh-link" href="https://github.com/isLinXu/lean-muscle-playbook" target="_blank" rel="noopener">GitHub ↗</a>
</div></header>"""

PAGE_TMPL = """<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{title}</title>
<meta name="description" content="{desc}">
<link rel="stylesheet" href="{p}assets/site.css">
</head>
<body>
{topbar}
<main>
<div class="page">
{crumbs}
{toc}
{extra}
{content}
<footer>
  <div>薄肌行动手册 · lean-muscle-playbook —— 内容仅供学习参考，不构成医学、营养学或运动处方建议。</div>
  <div class="warn">体脂已低于健康下限、有慢性病或孕期者，应先咨询专业人士再执行。</div>
  <div>在线阅读版由 <code>scripts/build_site.py</code> 从仓库源文件生成 · 内容真源见 <code>docs/</code> 与 <code>guides/</code></div>
</footer>
</div>
</main>
</body>
</html>
"""


def build_nav(active_key: str, prefix: str) -> str:
    items = []
    for key, label, tmpl in NAV_ITEMS:
        href = tmpl.format(p=prefix)
        cls = ' class="active"' if key == active_key else ""
        items.append(f'<li><a{cls} href="{href}">{label}</a></li>')
    return "\n".join(items)


def crumbs(site_rel: str, title: str, prefix: str) -> str:
    parts = []
    parts.append(f'<a href="{prefix}index.html">首页</a>')
    if site_rel.startswith("docs/"):
        parts.append(f'<a href="{prefix}docs/black-book.html">黑皮书</a>')
    elif site_rel.startswith("guides/8-week-plan/"):
        parts.append(f'<a href="{prefix}guides/8-week-plan/index.html">8 周行动清单</a>')
    parts.append(title)
    return '<div class="crumb">' + " / ".join(parts) + "</div>"


def build_page(html_body: str, site_rel: str, title: str, active_key: str,
               desc: str, toc: str = "", extra_top: str = "") -> str:
    ps = prefix_slash(site_rel)
    topbar = NAV_TMPL.format(p=ps, nav=build_nav(active_key, ps))
    full_title = title if "薄肌行动手册" in title else f"{title} · 薄肌行动手册"
    page = PAGE_TMPL.format(
        title=html_mod.escape(full_title),
        desc=html_mod.escape(desc),
        p=ps,
        topbar=topbar,
        crumbs=crumbs(site_rel, title, ps),
        toc=toc,
        extra=extra_top,
        content=html_body,
    )
    return page


def index_hero() -> str:
    """首页门户区：hero + 四张入口卡片 + 「瘦 ≠ 薄肌」对比图预览。"""
    return """<div class="hero">
  <div class="kicker">LEAN MUSCLE PLAYBOOK</div>
  <h1>薄肌行动手册</h1>
  <p>围绕《孙宇晨访谈记录》整理的可执行训练资料库：访谈整理、AI 认知观点、8 周实操行动清单、打卡工具与可视化素材，让「照着做」这件事有据可依。</p>
  <span class="pill">书中口径：每天约 30 分钟 · 八周见效 · 三步启动法</span>
  <span class="pill">实操编排：9 个动作 · 4 个阶段 · 每周 3 次力量 + 2–3 次有氧</span>
  <span class="pill">口径纪律：书中口径 / 公开权威资料</span>
  <div class="hero-dl"><a class="dl-btn" href="https://raw.githubusercontent.com/isLinXu/lean-muscle-playbook/main/scripts/latex-book/main.pdf" target="_blank" rel="noopener">下载全书 PDF（138 页）↗</a><span class="dl-note">黑皮书完整 LaTeX 编译成品，A5 版式</span></div>
</div>
<div class="cards">
  <div class="card"><span class="tag">主书</span><h3>黑皮书</h3><p>《孙宇晨访谈记录整理》六章全文：议题整理、三书深潜、金句摘录、8 周行动清单与复盘模板。</p><a class="go" href="docs/black-book.html">开始阅读 →</a></div>
  <div class="card"><span class="tag">实操</span><h3>薄肌实操指南</h3><p>按健康前提、训练、饮食、睡眠与数据复盘组织的 8 周行动手册，可直接照做。</p><a class="go" href="guides/practice-guide.html">开始执行 →</a></div>
  <div class="card"><span class="tag">清单</span><h3>8 周行动清单</h3><p>四阶段逐日安排、加量规则与 9 个动作速查卡（退阶 / 标准 / 进阶）。</p><a class="go" href="guides/8-week-plan/index.html">查看清单 →</a></div>
  <div class="card"><span class="tag">口径</span><h3>术语统一口径</h3><p>「薄肌 / 瘦 ≠ 薄肌 / 搏击 / 渐进超负荷」等术语定义与口径纪律。</p><a class="go" href="docs/glossary.html">查看术语 →</a></div>
</div>
<figure>
  <img src="assets/lean-vs-thin.png" alt="瘦不等于薄肌对比图">
  <figcaption>「瘦 ≠ 薄肌」：左为单纯减重（肌肉流失），右为薄肌训练（低体脂 + 线条 + 力量）</figcaption>
</figure>"""


def plan_bottom_nav(active: str) -> str:
    """8 周计划子页面底部互链（同目录相对路径）：上一阶段 / 总览 / 下一阶段 / 速查卡。"""
    order = [("stage-1", "阶段一"), ("stage-2", "阶段二"),
             ("stage-3", "阶段三"), ("stage-4", "阶段四")]
    links = []
    idx = next((i for i, (k, _) in enumerate(order) if k == active), None)
    if idx is not None:
        if idx > 0:
            links.append(f'<a href="{order[idx-1][0]}.html">← {order[idx-1][1]}</a>')
        links.append('<a href="index.html">阶段总览</a>')
        if idx < len(order) - 1:
            links.append(f'<a href="{order[idx+1][0]}.html">{order[idx+1][1]} →</a>')
        links.append('<a href="exercise-cards.html">动作速查卡</a>')
    elif active == "cards":
        links.append('<a href="index.html">阶段总览</a>')
        links.append('<a href="stage-1.html">阶段一</a>')
    else:
        return ""
    return ('<div class="toc" style="display:flex;gap:18px;flex-wrap:wrap;margin-top:30px;">'
            + " · ".join(links) + "</div>")


def inject_nav_into_html(src: pathlib.Path, site_rel: str, title: str,
                         active_key: str, desc: str) -> str:
    """把已有单文件 HTML（如实操指南）注入站点顶栏，保留正文与样式。"""
    ps = prefix_slash(site_rel)
    topbar = NAV_TMPL.format(p=ps, nav=build_nav(active_key, ps))
    text = src.read_text(encoding="utf-8")
    # 保留原页 <style> 等 head 内容，追加 site.css（导航样式优先）
    if "<head>" in text:
        text = text.replace(
            "<head>",
            "<head>\n<meta name=\"description\" content=\"%s\">\n"
            "<link rel=\"stylesheet\" href=\"%sassets/site.css\">" % (
                html_mod.escape(desc), ps),
            1,
        )
    # 在 <body ...> 之后插入顶栏
    m = re.search(r"<body[^>]*>", text)
    if m:
        text = text[: m.end()] + "\n" + topbar + "\n" + text[m.end():]
    else:
        text = topbar + "\n" + text
    return text


def main() -> None:
    SITE.mkdir(parents=True, exist_ok=True)

    # 1) 渲染 markdown 页面
    for src_rel, site_rel, title, active_key in MD_PAGES:
        src = ROOT / src_rel
        body = pandoc_md_to_html(src)
        body = rewrite_links(body, src_rel, site_rel)
        body, toc = assign_ids_and_toc(body)
        # 首页渲染 README：加门户区，跳过目录
        extra = ""
        if site_rel == "index.html":
            toc = ""
            extra = index_hero()
        desc = f"{title} —— 薄肌行动手册（lean-muscle-playbook）在线阅读"
        page = build_page(body, site_rel, title, active_key, desc, toc, extra)
        if site_rel.startswith("guides/8-week-plan/") and site_rel != "guides/8-week-plan/index.html":
            key = site_rel.split("/")[-1].replace(".html", "")
            page = page.replace("</main>", plan_bottom_nav(key) + "\n</main>")
        out = SITE / site_rel
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(page, encoding="utf-8")
        print(f"[md] {site_rel}")

    # 2) 注入已有 HTML 页面
    for src_rel, site_rel, title, active_key in NAV_HTML_PAGES:
        src = ROOT / src_rel
        page = inject_nav_into_html(src, site_rel, title, active_key, title)
        out = SITE / site_rel
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(page, encoding="utf-8")
        print(f"[html] {site_rel}")

    # 3) 复制资源与站点基础文件
    css_src = SITE / "assets" / "site.css"
    if not css_src.exists():
        print("!! 缺少 site/assets/site.css —— 请先放置统一样式。", file=sys.stderr)
        sys.exit(1)
    for src_rel, site_rel in COPY_FILES:
        src = ROOT / src_rel
        out = SITE / site_rel
        out.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, out)
        print(f"[copy] {src_rel} -> {site_rel}")

    # GitHub Pages 静态站点标记（跳过 Jekyll 处理）
    (SITE / ".nojekyll").touch()

    print("站点构建完成 ->", SITE)


if __name__ == "__main__":
    main()