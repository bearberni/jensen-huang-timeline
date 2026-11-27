#!/usr/bin/env python3
"""Build both static editions from one set of audited editorial data. Python 3 only."""
from pathlib import Path
from html import escape
import json,re
from collections import Counter

ROOT=Path(__file__).resolve().parents[1]
read=lambda name: json.loads((ROOT/'data'/name).read_text(encoding='utf-8'))
E=lambda value:escape(str(value),quote=True)
data=read('content.json')
summary=read('summary.json')
assert data.get('content_state') == 'audit-revisions-applied', 'Apply audited content before publishing.'
events=data['timeline']
sources={s['id']:s for s in data['sources']}
counts=Counter(e['grade'] for e in events)
LABELS={'T1':'原始材料','T2':'可归属报道','T3':'匿名 / 未独立核实','T4':'待核实'}

def badge(grade,detail=True):
    return f'<span class="badge {E(grade.lower())}">{E(grade)}{(" · "+LABELS.get(grade,"混合命题")) if detail else ""}</span>'
def link(label,url,cls=''):
    return f'<a{(" class="+chr(34)+E(cls)+chr(34)) if cls else ""} href="{E(url)}" target="_blank" rel="noopener noreferrer">{E(label)}</a>'
def source_links(items):
    return '<div class="link-row">'+''.join(link(x['label'],x.get('url',x.get('href',''))) for x in items)+'</div>'
def sl(*ids):return source_links([dict(label=sources[s]['label'],url=sources[s]['url']) for s in ids])
def heading(id,title,desc='',eyebrow='',note=''):
    return f'<section id="{id}" class="section"><div class="section-head"><div>{("<p class=eyebrow>"+E(eyebrow)+"</p>") if eyebrow else ""}<h2>{E(title)}</h2>{("<p class=section-intro>"+E(desc)+"</p>") if desc else ""}</div>{("<p class=section-note>"+E(note)+"</p>") if note else ""}</div>'

def render_summary(short=False):
    out=heading('summary','30 秒看懂','从同一组资料中，分别呈现已经确认的动作与尚待证实的判断。','TL;DR')
    out+=f'<p class="summary-lead">{E(summary["lead"])}</p><div class="summary-grid">'
    for c in summary['cards']:
        out+=f'<article class="summary-card">{badge(c["grade"])}<p class="small-label">{E(c["label"])}</p><h3>{E(c["title"])}</h3><p>{E(c["body"])}</p>{source_links(c["links"])}</article>'
    out+='</div><p class="reading-boundary"><b>阅读边界：</b>复职、行政列单与调查程序可以由原始文件确认；情报身份、知情程度及违法责任仍需分别举证。未被调查与经过调查获免责，是不同状态。</p>'
    if not short:out+='<p class="short-cta"><a class="secondary-button" href="tldr.html">打开独立速读版</a></p>'
    return out+'</section>'

def render_milestones():
    out=heading('overview','关键进展','日期对应公开文件或报道的发生时点；后续评估变化单独记录。','THE RECORD')+'<div class="milestone-grid">'
    for m in summary['milestones']:
        out+=f'<article class="milestone"><time>{E(m["date"])}</time><h3>{E(m["title"])}</h3><p>{E(m.get("body",m.get("description","")))}</p>{source_links(m.get("links",[]))}</article>'
    return out+'</div></section>'

def render_confidence():
    rules={'T1':('直接核对材料','官方文件、原始声明或原始数据。只证明该材料实际支持的命题。'),'T2':('明确归属的报道','公开发言的报道、具名数据及口径清楚的估算。'),'T3':('仍需独立证据','匿名消息、内部动因、未公开情报或未独立核实的调查结论。'),'T4':('证据尚不充分','缺少历史快照，或数据冲突未解决。待核不等于已证伪。')}
    out=heading('confidence','证据分级','分级针对具体命题，不是媒体排行榜，也不是概率评分。','HOW TO READ',f'共 {len(events)} 条事件与报道；按每条主等级计数。')+'<div class="confidence-grid">'
    for g,(title,desc) in rules.items():
        out+=f'<article class="confidence-cell">{badge(g,False)}<p class="confidence-count">{counts[g]} <small>条</small></p><h3>{title}</h3><p>{desc}</p><button class="js-only" data-show-grade="{g}">查看{g}记录</button></article>'
    return out+'</div><details class="method-details"><summary>分级、原文访问状态和“独立来源”怎样区分？</summary><p>一条记录可能包含不同等级的命题，条内说明会保留这些区别；这里的数量只按主等级归类。来源标为“全文、部分正文、仅索引、访问受限”等，与 T 级分别记录。找回原文链接不自动提升匿名指控的等级。</p><p>转载同一报道不计为多次独立确认。政府信函引用新闻报道，只能直接确认发信行为与信函内容；其中的指控需要独立证据。搜索入口及 RSS 跳转保留为检索辅助，不能代替原文。</p></details></section>'

def render_timeline():
    out=heading('timeline','完整时间线','默认按最新日期排列。可以按关键词和证据等级筛选，每条保留出处与证据边界。','CHRONOLOGY')
    out+='''<div class="timeline-toolbar js-only"><div class="toolbar-top"><label class="sr-only" for="timelineSearch">搜索事件、人物或来源</label><input id="timelineSearch" class="search-input" type="search" placeholder="搜索事件、人物、来源，例如 Megaspeed" autocomplete="off"><label class="sr-only" for="timelineSort">时间排序</label><select id="timelineSort" class="sort-select"><option value="desc">最新在前</option><option value="asc">最早在前</option></select></div><div class="filter-row"><span class="filter-label">证据等级</span>'''
    for g,label in [('all','全部'),('T1','T1 原始材料'),('T2','T2 报道'),('T3','T3 未独立核实'),('T4','T4 待核')]:
        out+=f'<button class="filter-button" data-filter-grade="{g}" aria-pressed="{str(g=="all").lower()}">{label}</button>'
    out+='</div><p id="timelineResult" class="filter-result" role="status" aria-live="polite"></p></div><noscript><p class="noscript-message">当前显示全部记录。启用 JavaScript 后可按日期、关键词和证据等级筛选。</p></noscript><div class="events" id="eventList">'
    # Preserve audit snapshot anchors; split records use the first data record.
    legacy_aliases={}
    seen_aliases=set()
    for event in events:
        for original_index in event.get('original_indices',[]):
            alias=f'fact-{int(original_index):03d}'
            if alias not in seen_aliases:
                legacy_aliases.setdefault(event['stable_id'],[]).append(alias)
                seen_aliases.add(alias)
    ordered=sorted(enumerate(events),key=lambda x:(x[1]['date'],x[0]),reverse=True)
    for n,e in ordered:
        plain=re.sub('<[^>]+>',' ',e['title']+' '+e['body_html']+' '+e['note_html']+' '+' '.join(x['label'] for x in e['links']))
        aliases=''.join(f'<span id="{E(alias)}" hidden></span>' for alias in legacy_aliases.get(e['stable_id'],[]))
        out+=f'<article class="event" id="{E(e["stable_id"])}" data-date="{E(e["date"])}" data-order="{n}" data-grade="{E(e["grade"])}" data-search="{E(plain.lower())}"><div class="event-date">{aliases}<time datetime="{E(e["date"])}">{E(e["date"])}</time><a href="#{E(e["stable_id"])}" aria-label="此条记录永久链接">{E(e["stable_id"])}</a></div><div><div class="event-top">{badge(e["grade"])}</div><h3>{E(e["title"])}</h3><div class="event-body">{e["body_html"]}</div><div class="event-note">{e["note_html"]}</div>'
        if e.get('grade_detail') and e['grade_detail']!=e['grade']:
            out+=f'<p class="mixed-note">命题分级：{E(e["grade_detail"])}</p>'
        out+='<div class="event-sources">'+''.join(link(x['label'],x.get('href',x.get('url','')),'source-link') for x in e['links'])+'</div></div></article>'
    out+='</div><div id="timelineEmpty" class="empty-state" hidden><p>没有匹配的记录。可以调整关键词或取消等级筛选。</p><button id="timelineReset" class="secondary-button">清除筛选</button></div><div class="load-controls js-only"><button id="timelineMore" class="primary-button">再显示 24 条</button> <button id="timelineAll" class="secondary-button">显示全部记录</button></div></section>'
    return out

def render_evidence():
    out=heading('network','四个问题，分别看证据','关系、情报身份、出口合规与个人责任分别判断；一项结论不能代替另一项。','EVIDENCE MAP')+'<div class="evidence-grid">'
    rows=[('关系是否由情报机构指使？','T3','媒体转述闭门简报称未见策划关系的证据；后续报道仍描述官员对情报解释存在分歧。','没有公开原始情报，不能写成机构一致确认或正式全面排除。',['S12','S15']),('是否具有情报身份或联系？','T3','早期 NYT／FT 报道和后续媒体转述都涉及匿名情报判断。新加坡官方声明则说明其本地调查程序。','身份、联系、被监视与被指使是不同命题；不同机构与时段的说法需分别记录。',['S09','S11','S15']),('出口管制已确认哪些动作？','T1','BIS 已发布实体清单最终规则；DOJ 与商务部公开由司法部牵头的调查安排。','T1 只对应行政动作和程序，违规责任仍待调查。融资登记、列单和开展调查都不直接等于刑事定罪。',['S01','S03','S08']),('黄本人是否知情或承担责任？','T3','公司复职公告确认恢复职务，同时明确独立调查将继续；媒体另有关于未受调查及决策过程的报道。','复职、未被调查与调查后获免责分别记录。个人知情程度和法律责任需要各自证据。',['S40','S54'])]
    for i,(title,g,body,boundary,ids) in enumerate(rows):
        out+=f'<article class="evidence-card"><div class="evidence-heading"><span class="evidence-icon" aria-hidden="true">{["关","情","贸","责"][i]}</span><h3>{title}</h3></div>{badge(g)}<p>{body}</p>{sl(*ids)}<p class="boundary">{boundary}</p></article>'
    out+='</div><div class="role-list"><div><b>公司董事会</b><p>决定治理安排与人事，独立调查仍继续。</p></div><div><b>BIS 与司法部</b><p>分别涉及出口管制行政措施和刑事调查。</p></div><div><b>国会委员会</b><p>要求材料、简报和证词；问询不等于裁定。</p></div></div>'
    return out+'</section>'

def render_watch():
    out=heading('verdict','接下来观察什么','已经发布的安排与尚待出现的证据分别跟踪。','NEXT TO VERIFY')+'<div class="watch-grid">'
    for w in summary['watchlist']:
        out+=f'<article class="watch-card"><h3>{E(w["title"])}</h3><p>{E(w["body"])}</p>{source_links(w.get("links",[]))}</article>'
    out+='</div><p class="reading-boundary"><b>如何更新结论：</b>关注公开情报材料、调查报告及法庭证据；是否起诉、提出何种指控与指控是否成立分别记录。复职及行政列单都不关闭其他待核问题。</p></section>'
    return out

def render_docs():
    out=heading('docs','官方文件与原始出处','优先读能够直接支持关键命题的文件。以下为内容摘要，完整文本以链接原文为准。','PRIMARY DOCUMENTS')+'<div class="doc-grid">'
    for d in data['documents']:
        out+=f'<article class="doc-card"><p class="doc-type">{E(d["date"])} · {E(d["kind"])}</p><h3>{E(d["title"])}</h3><p>{E(d["body"])}</p>{source_links(d["links"])}</article>'
    return out+'</div></section>'

def render_archive():
    out=heading('reactions','公开回应与传播记录','保留历史表态与原帖入口；传播热度、支持态度和本人签署是不同证据。','PUBLIC RECORD')
    out+='<details class="archive-details"><summary>公开回应与历史表态</summary><p class="archive-intro">按当时身份和日期阅读。部分内容为媒体转述或中文译述；不同来源的公开程度见链接及条内说明。</p>'+data['reactions_html']+'</details>'
    out+='<details class="archive-details" id="gossip"><summary>历史传播快照与原帖索引 <span class="badge t4">数据快照待核</span></summary><p class="archive-intro">以下保留 11 月 26 日版本的传播记录。当前公开仓库未附采集明细，部分时间标签不一致；数量及互动指标暂不能独立复算，也不能代表总体舆论或验证签署身份。支持发言不等于签署，署名核验仍以本人原帖为准。</p>'+data['gossip_html']+'</details></section>'
    return out

def render_sources():
    n=data['source_row_count']
    out=heading('sources-chapter','来源索引','按具体文章和文件保留出处。尚未核对正文的历史入口明确标记，避免把链接可点击当作已核实。','SOURCE INDEX',f'{n} 条来源记录；转载与原稿不作为独立重复证据。')
    out+='<div class="sources-controls js-only"><label for="sourceSearch" class="sr-only">搜索来源</label><input type="search" class="search-input" id="sourceSearch" placeholder="搜索来源、日期、主题或访问状态"></div><div class="table-scroll source-index" id="sourceTable" tabindex="0" aria-label="来源表，可横向滚动">'+data['sources_html']+'</div>'
    out+=f'<p id="sourceResult" class="source-index-count" role="status">显示 {n} / {n} 条来源记录</p><div class="correction-note"><b>2026-11-27 信源修订：</b>补齐 Megaspeed 最终列单规则与 DOJ 调查文件，区分匿名判断与官方程序；校正融资金额含义、评级观察、市场比较基准及错配原链。既有基础官宣与本人签署原帖沿用。搜索入口及尚未还原的 RSS 仍保留访问说明，未声称全量正文已核。<p>审计存档：<a href="AUDIT-2026-11-27.md" download>下载修订说明</a> · <a href="data/source-audit-2026-11-27.json" download>下载机器可读清单</a>。这两份文件记录较早的139条审计快照；当前{len(events)}条记录及分级以<a href="data/content.json">当前数据</a>为准。</p><p><a href="https://github.com/bearberni/jensen-huang-timeline">查看仓库与版本记录</a></p></div></section>'
    return out

def render(short=False):
    title='黄仁勋事件档案 · 速读版' if short else '黄仁勋事件档案 · 完整时间线与信源'
    h1='黄仁勋事件档案<em>速读版</em>' if short else '黄仁勋事件档案<em>事实、报道与未定问题</em>'
    nav=[('summary','30 秒速读'),('overview','关键进展'),('market-details','市场数据'),('verdict','后续观察')] if short else [('summary','速读'),('overview','进展'),('timeline','时间线'),('network','证据边界'),('confidence','分级'),('market','市场'),('verdict','观察'),('docs','原始文件'),('sources-chapter','来源')]
    body=render_summary(short)+render_milestones()
    if not short:body+=render_confidence()+render_timeline()
    market=(ROOT/'templates/market.html').read_text(encoding='utf-8')
    if short:
        body+='<details class="archive-details" id="market-details"><summary>展开市场图表与计算口径</summary>'+market+'</details>'+render_watch()
    else:body+=render_evidence()+market+render_watch()
    if not short:body+=render_docs()+render_archive()+render_sources()
    else:body+='<section class="section"><h2>继续查看完整记录</h2><p class="section-intro">完整页面保留逐条时间线、证据分级、官方文件和来源访问状态。速读版与完整页面使用同一份内容生成。</p><div class="short-cta"><a class="primary-button" href="index.html#timeline">打开完整时间线</a><p><a href="index.html#sources-chapter">查看来源索引</a></p></div></section>'
    html='''<!doctype html><html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="color-scheme" content="light dark">'''
    html+=f'<title>{title}</title><meta name="description" content="黄仁勋事件的公开记录与信源审计：区分官方文件、媒体报道与待核判断。2026-11-27更新；完整时间线与TLDR同源。"><link rel="icon" href="data:image/svg+xml,%3Csvg xmlns=%27http://www.w3.org/2000/svg%27 viewBox=%270 0 64 64%27%3E%3Crect width=%2764%27 height=%2764%27 fill=%27%2314675c%27/%3E%3Ctext x=%2732%27 y=%2745%27 text-anchor=%27middle%27 fill=%27white%27 font-size=%2740%27 font-family=%27Georgia%27%3EN%3C/text%3E%3C/svg%3E"><link rel="stylesheet" href="assets/site.css"><link rel="stylesheet" href="assets/market.css"><script defer src="assets/site.js"></script><script defer src="assets/market.js"></script></head>'
    html+=f'<body class="{"short" if short else "full"}"><a class="skip" href="#main">跳到正文</a><header class="frame"><div class="topbar"><a class="brand" href="index.html"><span class="brand-mark" aria-hidden="true">N</span><span>事件档案<br>PUBLIC RECORD</span></a><nav class="edition-tabs" aria-label="阅读版本"><a href="index.html" {"aria-current=page" if not short else ""}>完整版</a><a href="tldr.html" {"aria-current=page" if short else ""}>TL;DR 速读</a></nav></div><div class="hero"><div><p class="eyebrow">NVIDIA · GOVERNANCE · EVIDENCE</p><h1>{h1}</h1><p class="hero-dek">从公开报道到董事会去留，再到出口管制与国会问询。把已经发生的动作，与仍待证实的判断分开读。</p></div><aside class="hero-aside"><h2>当前状态</h2><p><strong>已复职，调查仍继续。</strong><br>行政列单已有官方文件；匿名情报判断仍需公开证据。每项结论都保留自己的来源与边界。</p></aside></div><div class="audit-stamp"><span>信源更新 <b>2026-11-27 · 北京时间</b></span><span>价格截至 <b>2026-11-25 美股收盘</b></span><span>资料日期按原文标注</span></div></header><div class="nav-shell"><nav class="frame section-nav" aria-label="章节导航">'+''.join(f'<a href="#{id}">{label}</a>' for id,label in nav)+'</nav></div>'
    html+='<main class="frame" id="main">'+body+'</main><footer class="frame page-footer"><p>黄仁勋事件档案 · 2026-11-27 修订<br>等级反映命题的证据状态。官方声明、媒体转述及独立核实程度分别呈现；来源受限与待核内容不作确定结论。</p><div class="footer-links"><a href="index.html">完整版</a><a href="tldr.html">速读版</a><a href="https://github.com/bearberni/jensen-huang-timeline" target="_blank" rel="noopener noreferrer">GitHub</a></div></footer><button id="backTop" class="back-top js-only" hidden aria-label="返回页面顶部">顶部</button></body></html>'
    return html

for file,short in [('index.html',False),('tldr.html',True)]:
    (ROOT/file).write_text(render(short),encoding='utf-8')
print(json.dumps({'events':len(events),'grades':dict(counts),'source_rows':data['source_row_count'],'outputs':['index.html','tldr.html']},ensure_ascii=False))
