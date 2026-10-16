#!/usr/bin/env python3
"""Render source-backed resource and explanation pages without JavaScript."""
from __future__ import annotations

from collections import defaultdict
from html import escape
import json
from pathlib import Path

from build_readme import COLLECTION_SECTIONS, KIND_LABELS, RELATIONSHIPS, TARGETS, collection_section


def jsonld(graph: list[dict]) -> str:
    payload = json.dumps({"@context": "https://schema.org", "@graph": graph}, ensure_ascii=False)
    # Metadata can contain upstream text; never let it terminate a script element.
    payload = payload.replace("<", "\\u003c").replace(">", "\\u003e").replace("&", "\\u0026")
    return '<script type="application/ld+json">' + payload + '</script>'


def website_graph(site_url: str) -> dict:
    return {"@type": "WebSite", "@id": site_url + "/#website", "url": site_url + "/",
            "name": "Awesome Reverse Engineering Anything", "alternateName": "AwesomeREA.org",
            "inLanguage": ["en", "zh-CN"]}


def page_graph(site_url: str, canonical: str, title: str, description: str,
               language: str, *, items: list[dict] | None = None,
               page_type: str = "CollectionPage", breadcrumbs: list[tuple[str, str]] | None = None) -> list[dict]:
    page = {"@type": page_type, "@id": canonical + "#page", "url": canonical,
            "name": title, "description": description, "inLanguage": language,
            "isPartOf": {"@id": site_url + "/#website"}}
    graph = [website_graph(site_url), page]
    if items is not None:
        page["mainEntity"] = {"@id": canonical + "#list"}
        graph.append({"@type": "ItemList", "@id": canonical + "#list", "numberOfItems": len(items),
                      "itemListElement": [{"@type": "ListItem", "position": i + 1, **item}
                                          for i, item in enumerate(items)]})
    if breadcrumbs:
        page["breadcrumb"] = {"@id": canonical + "#breadcrumbs"}
        graph.append({"@type": "BreadcrumbList", "@id": canonical + "#breadcrumbs",
                      "itemListElement": [{"@type": "ListItem", "position": i + 1, "name": name, "item": url}
                                          for i, (name, url) in enumerate(breadcrumbs)]})
    return graph


def localized_name(record: dict, language: str) -> str:
    return (record.get("name_zh") or record["name"]) if language == "zh" else record["name"]


def resource_card(record: dict, language: str) -> str:
    zh = language == "zh"
    index = int(zh)
    requirements = record.get("requirements_zh") if zh else record["requirements"]
    requirements = requirements or record["requirements"]
    if isinstance(requirements, str):
        requirements = [requirements]
    labels = " · ".join([KIND_LABELS[record["kind"]][index], RELATIONSHIPS[record["relationship"]][index],
                         ", ".join(TARGETS[target][index] for target in record["targets"])])
    requirements_html = "".join("<li>" + escape(text) + "</li>" for text in requirements)
    return f'''<article class="source-card discovery-card" id="{escape(record['id'], quote=True)}" data-resource-id="{escape(record['id'], quote=True)}">
  <h3><a href="{escape(record['url'], quote=True)}">{escape(localized_name(record, language))}</a></h3>
  <p>{escape(record['description_' + language])}</p>
  <p class="discovery-meta">{escape(labels)}</p>
  <details><summary>{('条件与限制' if zh else 'Requirements and limits')}</summary><ul>{requirements_html}</ul></details>
  <p class="discovery-meta"><a href="{escape(record['evidence_url'], quote=True)}">{('原始证据' if zh else 'Primary evidence')}</a> · {('来源核查' if zh else 'Source reviewed')}: <time datetime="{escape(record['verified_at'], quote=True)}">{escape(record['verified_at'][:10])}</time> · <a href="#{escape(record['id'], quote=True)}">{('条目链接' if zh else 'Entry link')}</a></p>
</article>'''


def about_content(language: str, count: int, repository_url: str) -> str:
    if language == "zh":
        sections = [
            ("这是什么目录？", "Awesome Reverse Engineering Anything 是独立维护的逆向工程资源目录，覆盖网站、游戏、桌面与移动应用、原生二进制和固件。条目包括工具、Agent 集成、案例、研究论文与学习资料。"),
            ("它和 REA 官方项目是什么关系？", '本站收录 <a href="https://github.com/morluto/rea">REA — Reverse Engineer Anything</a> 及其他独立项目。本站不是 REA 的官方网站；收录某个工具不代表该工具与 REA 集成或受到官方认可。'),
            ("如何选择合适的资源？", '先在<a href="/zh/resources/">精选目录</a>中按目标查找，再核对每条记录的条件、限制与原始证据。网站行为、游戏资源、Android APK 和原生二进制可能需要不同工具。'),
            ("精选资源是否都经过实际运行？", f'当前有 {count} 条精选资源记录。来源核查表示阅读过链接的原始材料，不表示已安装、审计或复现实验。论文中的结果属于作者报告；实际使用时应检查原论文的任务、版本和评测条件。'),
            ("仓库索引和精选目录有什么区别？", '<a href="/zh/browse/">仓库索引</a>来自自动 README 扫描，并保留单独的范围和来源说明。自动发现、简介翻译和推断分类不等于逐项人工核查；星标只是采集时的快照。'),
            ("如何核查、引用或提出修正？", f'精选条目都有稳定的页内链接、原始来源和核查日期。关于具体工具或论文的事实，请查看该条目的原始证据。可以下载 <a href="/catalog.json">JSON 目录</a>，或通过<a href="{repository_url}/blob/main/CONTRIBUTING.md">贡献说明</a>提出修正。本站原创内容使用 MIT 许可；被链接项目保留各自许可。'),
        ]
    else:
        sections = [
            ("What is Awesome Reverse Engineering Anything?", "An independent directory of reverse-engineering resources for websites, games, desktop and mobile apps, native binaries, and firmware. It collects tools, agent integrations, case studies, research papers, and learning material."),
            ("Is this the official REA website?", 'No. The collection includes <a href="https://github.com/morluto/rea">REA — Reverse Engineer Anything</a> alongside independent projects. A listing does not imply REA integration or endorsement. Follow the upstream project for official installation instructions.'),
            ("How do I choose a resource?", 'Start with the target in the <a href="/resources/">curated directory</a>, then read the entry’s requirements, limits, and primary evidence. Website behavior, game assets, Android packages, and native binaries can require different tools.'),
            ("Have all curated resources been run?", f'There are {count} curated resource records. Source review means the linked original material was read; it does not mean every tool was installed, audited, or independently reproduced. Paper results are author-reported and must be read with their original tasks, versions, and evaluation conditions.'),
            ("How is the repository index different?", 'The <a href="/browse/">repository index</a> comes from automated README scans with separate scope and provenance notes. Discovery, translated summaries, and inferred categories are not individual manual verification. Star counts are collection-time snapshots.'),
            ("How can I check, cite, or correct an entry?", f'Curated entries have stable section links, primary sources, and review dates. Follow the primary evidence for facts about a specific tool or paper. Download the <a href="/catalog.json">JSON catalog</a>, or use the <a href="{repository_url}/blob/main/CONTRIBUTING.md">contribution guide</a> to propose a correction. Original collection content is MIT licensed; linked projects keep their own licenses.'),
        ]
    return '\n'.join(f'<section class="discovery-answer"><h2>{escape(question)}</h2><p>{answer}</p></section>' for question, answer in sections)


def build_discovery_pages(output: Path, resources: list[dict], *, site_url: str, repository_url: str,
                          styles_href: str, discovery_styles_href: str, favicon_href: str,
                          social_image_href: str) -> list[str]:
    grouped = defaultdict(list)
    for record in resources:
        grouped[collection_section(record)].append(record)
    urls = []
    for language in ("en", "zh"):
        zh = language == "zh"
        index = int(zh)
        locale = "zh-CN" if zh else "en"
        prefix = "/zh" if zh else ""
        home = "/?lang=zh" if zh else "/"
        for kind in ("resources", "about"):
            path = f"{prefix}/{kind}/"
            canonical = site_url + path
            title = ({"resources": "精选逆向工程资源", "about": "关于这个目录"} if zh else
                     {"resources": "Curated reverse engineering resources", "about": "About the collection"})[kind]
            description = ("按目标查找工具、Agent 集成、案例与研究，查看原始来源、条件和核查日期。" if zh else
                           "Find tools, agent integrations, case studies, and research with primary sources, requirements, and review dates.") if kind == "resources" else (
                           "了解 AwesomeREA 的收录范围、核查方法、原始来源与项目关系。" if zh else
                           "Understand AwesomeREA’s scope, source-review method, primary evidence, and relationship to upstream projects.")
            if kind == "resources":
                toc = ''.join(f'<a href="#{slug}">{escape(labels[index])} <span>{len(grouped[slug])}</span></a>'
                              for slug, labels in COLLECTION_SECTIONS.items() if grouped[slug])
                sections = []
                ordered = []
                for slug, labels in COLLECTION_SECTIONS.items():
                    if not grouped[slug]:
                        continue
                    ordered.extend(grouped[slug])
                    cards = '\n'.join(resource_card(record, language) for record in grouped[slug])
                    sections.append(f'<section class="discovery-section" id="{slug}"><h2>{escape(labels[index])}</h2>{cards}</section>')
                note = (f'{len(resources)} 条来源核查记录；不表示已逐项运行。' if zh else
                        f'{len(resources)} source-reviewed records; inclusion does not imply execution testing.')
                content = f'<p>{note} <a href="{prefix}/about/">{("核查方法" if zh else "Review method")}</a></p><nav class="discovery-toc" aria-label="{("资源分类" if zh else "Resource categories")}">{toc}</nav>' + '\n'.join(sections)
                items = [{"name": localized_name(record, language), "url": canonical + '#' + record['id']} for record in ordered]
            else:
                content = about_content(language, len(resources), repository_url)
                items = None
            graph = page_graph(site_url, canonical, title, description, locale, items=items,
                               page_type="CollectionPage" if kind == "resources" else "AboutPage",
                               breadcrumbs=[("首页" if zh else "Home", site_url + "/"), (title, canonical)])
            english, chinese = f'{site_url}/{kind}/', f'{site_url}/zh/{kind}/'
            document = f'''<!doctype html>
<html lang="{locale}">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{escape(title)} · AwesomeREA.org</title>
  <meta name="description" content="{escape(description, quote=True)}">
  <link rel="canonical" href="{canonical}">
  <link rel="alternate" hreflang="en" href="{english}">
  <link rel="alternate" hreflang="zh-CN" href="{chinese}">
  <link rel="alternate" hreflang="x-default" href="{english}">
  <meta property="og:type" content="website">
  <meta property="og:site_name" content="AwesomeREA.org">
  <meta property="og:title" content="{escape(title, quote=True)} · AwesomeREA.org">
  <meta property="og:description" content="{escape(description, quote=True)}">
  <meta property="og:url" content="{canonical}">
  <meta property="og:image" content="{escape(social_image_href, quote=True)}">
  <meta name="twitter:card" content="summary_large_image">
  <link rel="icon" href="{escape(favicon_href, quote=True)}" type="image/svg+xml">
  <link rel="stylesheet" href="{escape(styles_href, quote=True)}">
  <link rel="stylesheet" href="{escape(discovery_styles_href, quote=True)}">
  {jsonld(graph)}
</head>
<body>
<a class="skip-link" href="#content">{('跳到正文' if zh else 'Skip to content')}</a>
<header class="site-header"><div class="shell header-inner">
  <a class="wordmark" href="{home}">Awesome<span class="wordmark-rea">REA</span><span class="wordmark-domain">.org</span></a>
  <nav class="header-nav" aria-label="{('主导航' if zh else 'Main navigation')}"><a href="{('/' if zh else '/zh/') + kind + '/'}" lang="{('en' if zh else 'zh-CN')}">{('English' if zh else '简体中文')}</a><a href="{escape(repository_url, quote=True)}">GitHub</a></nav>
</div></header>
<main id="content" class="shell discovery-main">
  <nav class="discovery-breadcrumbs" aria-label="{('当前位置' if zh else 'Breadcrumb')}"><a href="{home}">{('首页' if zh else 'Home')}</a> / <span aria-current="page">{escape(title)}</span></nav>
  <section class="collection-intro"><h1>{escape(title)}</h1><p>{escape(description)}</p></section>
  {content}
</main>
<footer class="site-footer"><div class="shell footer-top"><p>{('独立维护的逆向工程资源目录。' if zh else 'An independent reverse-engineering resource collection.')}</p><nav class="footer-links" aria-label="{('资源导航' if zh else 'Resources')}"><a href="{prefix}/resources/">{('精选资源' if zh else 'Curated resources')}</a><a href="{prefix}/browse/">{('仓库分类' if zh else 'Repository categories')}</a><a href="{prefix}/about/">{('关于目录' if zh else 'About')}</a><a href="/catalog.json">JSON</a></nav></div></footer>
</body>
</html>
'''
            destination = output / path.lstrip('/') / 'index.html'
            destination.parent.mkdir(parents=True, exist_ok=True)
            destination.write_text(document, encoding='utf-8')
            urls.append(canonical)
    (output / 'llms.txt').write_text(f'''# Awesome Reverse Engineering Anything

> An independent resource directory for reverse engineering websites, games, apps, native binaries, and firmware.

Curated records contain primary evidence, requirements, and source-review dates. Source review is not execution verification. The automated repository index has separate provenance. The collection includes REA and independent projects; inclusion does not establish integration or endorsement.

## Collection
- [About and review method]({site_url}/about/)
- [Curated resources]({site_url}/resources/)
- [Repository categories]({site_url}/browse/)
- [中文说明]({site_url}/zh/about/)
- [中文精选资源]({site_url}/zh/resources/)
- [中文仓库分类]({site_url}/zh/browse/)

## Data and source
- [Curated catalog JSON]({site_url}/catalog.json)
- [Public source repository]({repository_url})
- [Contribution guide]({repository_url}/blob/main/CONTRIBUTING.md)

Original collection content is MIT licensed. Linked projects retain their own licenses.
''', encoding='utf-8')
    return urls
