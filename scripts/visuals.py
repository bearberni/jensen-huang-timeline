"""Accessible, source-bound visual components shared by both static editions."""
from html import escape
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
E = lambda x: escape(str(x), quote=True)

def ext(label, url):
    return f'<a href="{E(url)}" target="_blank" rel="noopener noreferrer">{E(label)}</a>'

def render_portrait():
    return '''<div class="hero-visual"><figure class="archive-portrait"><img src="assets/jensen-portrait.jpg" width="1311" height="1748" alt="黄仁勋于2026年4月30日在斯坦福大学参加交流活动的资料照片" fetchpriority="high"><figcaption>资料照片 · 2026-04-30，斯坦福大学<br><a href="https://commons.wikimedia.org/wiki/File:Jensen_huang_stanford_2026-04-30_009_(cropped).jpg" target="_blank" rel="noopener noreferrer">Anders Eidesvik / Commons 裁剪版</a> · <a href="https://creativecommons.org/licenses/by/4.0/" target="_blank" rel="noopener noreferrer">CC BY 4.0</a></figcaption></figure><aside class="hero-aside"><h2>当前状态</h2><p><strong>已复职，调查仍继续。</strong><br>行政列单已有官方文件；匿名情报判断仍需公开证据。</p></aside></div>'''

def render_doc_previews():
    docs=[
      ('document-cotton.png','Cotton 的调查请求','2025-10-13 发信 · 10-14 公开','两页信函的第一页。直接确认要求调查，信中引用的指控仍须另行举证。','https://www.cotton.senate.gov/wp-content/uploads/media/doc/101325lutnickletter.pdf'),
      ('document-doj.png','商务部／司法部联合声明','2026-11-16 署日 · 网页11-17发布','两页声明的第一页。明确调查分工；开展调查不等于罪名成立。','https://www.justice.gov/opa/media/1472536/dl?inline'),
      ('document-entity-list.png','实体清单最终规则','2026-11-23 生效 · 11-25 刊登','原PDF公报76148页；BIS标题在中栏下部，同页保留前项FAA规则。共三页。','https://www.govinfo.gov/content/pkg/FR-2026-11-25/pdf/2026-23999.pdf')]
    out='<div class="document-previews">'
    for file,title,date,body,url in docs:
        out+=f'<figure class="document-preview"><a class="document-image" href="{E(url)}" target="_blank" rel="noopener noreferrer" aria-label="打开{E(title)}原始PDF"><img src="assets/{E(file)}" width="600" height="777" alt="{E(title)}的真实PDF首页预览" loading="lazy"></a><figcaption><p class="doc-type">{E(date)}</p><h3>{E(title)}</h3><p>{E(body)}</p>{ext("打开官方 PDF ↗",url)}</figcaption></figure>'
    return out+'</div><p class="visual-caption">预览直接由官方PDF完整首页生成；点击图片打开原文件。图片帮助识别文件，结论仍以完整文本支持的命题为限。</p>'

def render_progress():
    v = json.loads((ROOT/'data/visuals.json').read_text())
    out = '<section class="section" id="overview"><div class="section-head"><div><p class="eyebrow">THREE PARALLEL RECORDS</p><h2>三条线，看清进展</h2><p class="section-intro">公司治理、出口监管与情报说法并行发展。沿每一行阅读，点击节点查看日期、来源和证据边界。</p></div><p class="section-note">日期按区段排列，间距不代表时长；三条线不表示因果关系。</p></div><div class="track-scroll" tabindex="0" aria-label="三轨事件图；小屏可横向滚动"><div class="track-chart"><div class="track-axis"><span>记录类型</span>'
    out += ''.join(f'<span>{E(p)}</span>' for p in v['periods'])+'</div>'
    for lane in v['lanes']:
        out += f'<div class="track-lane {E(lane["id"])}"><div class="track-label"><span aria-hidden="true">{E(lane["number"])}</span><h3>{E(lane["label"])}</h3><p>{E(lane["scope"])}</p></div>'
        for cell in lane['cells']:
            out += '<div class="track-cell">'
            if not cell:
                out += '<span class="track-empty" aria-label="本图未列重点事件">—</span>'
            for point in cell:
                out += f'<details class="track-point"><summary><time>{E(point["date"])}</time><span class="track-point-title">{E(point["title"])}</span><span class="track-grade {E(point["grade"].lower())}">{E(point["grade"])}</span><span class="track-expand" aria-hidden="true">+</span></summary><div class="track-detail"><p>{E(point["body"])}</p>{ext(point["source_label"],point["url"])}</div></details>'
            out += '</div>'
        out += '</div>'
    return out+'</div></div><p class="visual-caption">实线边框表示文件或公开动作；虚线边框涉及媒体转述的未公开判断。展开后可直接查看原始出处。</p></section>'

def render_grade_bar(counts, total):
    labels={'T1':'原始材料','T2':'可归属报道','T3':'未独立核实','T4':'待核实'}
    out='<div class="grade-distribution" role="img" aria-label="'+E('，'.join(f'{g} {counts[g]}条' for g in labels))+'">'
    for g,label in labels.items():
        out+=f'<div class="grade-segment {g.lower()}" style="flex:{counts[g]}" title="{g} {label}：{counts[g]}条"><span>{g}</span></div>'
    out+='</div><p class="visual-caption">色带面积按记录条数计算，反映资料构成，不代表某项指控成立的概率。</p>'
    return out

def render_network(short=False):
    """Direct relationships, browsable by actor; all records survive without JS."""
    v = json.loads((ROOT/'data/relationships.json').read_text())
    nodes = {n['id']: n for n in v['nodes']}
    relations = v['relations']
    counts = {key: sum(key in (r['subject'], r['object']) for r in relations) for key in nodes}
    presentation = v['presentation']
    initials = {'huang':'黄', 'alice':'黄乐', 'board':'董事会', 'mega':'M', 'nvidia':'N'}
    kinds = {'decision':'治理决定', 'statement':'公开表态', 'reported':'媒体转述', 'historical':'历史记载', 'oversight':'监督问询', 'procedure':'调查与监管'}
    grades = {'T1':'原始材料', 'T2':'可归属报道', 'T3':'未独立核实'}
    out = '<section class="section relationship-section" id="network"><div class="section-head"><div><p class="eyebrow">PEOPLE &amp; DIRECT RELATIONSHIPS</p><h2>从人物，看清每一段关系</h2><p class="section-intro">选择人物或机构，逐段看谁作出什么动作、发生在何时，以及证据支持到哪里。</p></div><p class="section-note">每张卡只描述一段直接关系。不能沿关系推导知情、共谋或违法责任。</p></div><div class="actor-explorer">'
    out += '<aside class="actor-directory js-only" aria-label="选择人物或机构"><p class="actor-directory-label">从这些对象开始</p><div class="actor-featured" role="group" aria-label="常看人物与机构">'
    for ident in presentation['featured_actors']:
        n = nodes[ident]
        out += f'<button class="actor-choice" type="button" data-actor="{E(ident)}" aria-controls="relationshipList" aria-pressed="false"><span class="actor-monogram" aria-hidden="true">{E(initials[ident])}</span><span><b>{E(n["label"])}</b><small>{E(n["role"])}</small></span><span class="actor-count">{counts[ident]}<span class="sr-only">段关系</span></span></button>'
    out += '</div><label class="actor-select-label" for="actorSelect">全部人物与机构</label><select id="actorSelect" class="actor-select" aria-controls="relationshipList"><option value="all">全部 14 段关系</option>'
    for kind, label in [('person','人物'), ('institution','机构'), ('unverified','报道中的未证实对象')]:
        out += f'<optgroup label="{E(label)}">'
        for ident in presentation['actor_order']:
            n = nodes[ident]
            if n['kind'] != kind: continue
            out += f'<option value="{E(ident)}" data-label="{E(n["label"])}" data-role="{E(n["role"])}" data-kind="{E(n["kind"])}">{E(n["label"])} · {counts[ident]} 段关系</option>'
        out += '</optgroup>'
    out += '</select><p class="actor-directory-note">数字只表示此页收录的关系数量。</p><div class="actor-evidence-key"><span class="badge t1">T1 原始材料</span><span class="badge t2">T2 报道</span><span class="badge t3">T3 未独立核实</span></div></aside><div class="actor-workspace"><div class="actor-focus js-only"><div><p class="actor-focus-label">当前查看</p><h3 id="actorName">黄仁勋</h3><p id="actorRole">NVIDIA 创始人</p></div><p class="actor-result" id="actorResult" role="status" aria-live="polite"></p></div><noscript><p class="noscript-message">当前显示全部 14 段关系；每张卡都可展开查看完整来源。启用 JavaScript 后可按人物筛选。</p></noscript><div class="relationship-list" id="relationshipList">'
    for r in relations:
        subject, obj = nodes[r['subject']], nodes[r['object']]
        qualifier = r['kind'] in ('reported', 'historical')
        out += f'<article class="relationship-card {E(r["grade"].lower())}" id="relation-{E(r["id"])}" data-relationship="{E(r["id"])}" data-subject="{E(r["subject"])}" data-object="{E(r["object"])}"><div class="relationship-meta"><span class="badge {E(r["grade"].lower())}">{E(r["grade"])} · {E(grades[r["grade"]])}</span><span>{E(kinds[r["kind"]])}</span></div><div class="relationship-pair {"qualified" if qualifier else "directed"}"><div class="relationship-endpoint"><span class="endpoint-kind">{"未证实对象" if subject["kind"] == "unverified" else "人物" if subject["kind"] == "person" else "机构"}</span><b>{E(subject["label"])}</b></div><div class="relationship-action"><span>{E(r["action"])}</span><i aria-hidden="true"></i></div><div class="relationship-endpoint"><span class="endpoint-kind">{"未证实对象" if obj["kind"] == "unverified" else "人物" if obj["kind"] == "person" else "机构"}</span><b>{E(obj["label"])}</b></div></div><p class="relationship-date">{E(r["date"])}</p><h4 class="sr-only">{E(r["title"])}</h4><p class="relationship-limit"><b>限定</b>{E(r["key_boundary"])}</p><div class="relationship-source">{ext(r["sources"][0]["label"], r["sources"][0]["url"])}</div><details class="relationship-evidence"><summary>完整依据与限定 · {len(r["sources"])} 个出处</summary><p>{E(r["body"])}</p><p>{E(r["boundary"])}</p><div class="link-row">' + ''.join(ext(s['label'], s['url']) for s in r['sources']) + '</div></details><div class="relationship-traverse js-only"><span>继续查看</span>'
        for n in [subject, obj]:
            out += f'<button type="button" data-actor="{E(n["id"])}" aria-controls="relationshipList">{E(n["label"])}</button>'
        out += f'<a class="relationship-permalink" href="#relation-{E(r["id"])}" aria-label="{E(r["title"])}的永久链接">此条链接</a></div></article>'
    out += '</div></div></div><p class="visual-caption">等级针对卡片中的具体命题。关系数量不表示影响力，也不代表独立来源数。<a href="data/relationships.json" download>下载全部关系与证据数据</a></p>'
    if short:
        out += '<p class="short-cta"><a href="index.html#evidence-questions">查看四项核心问题的证据边界</a></p>'
    return out + '</section>'


def render_t4_followup(data, short=False):
    audited=[e for e in data['timeline'] if e['stable_id'] in ['F-002-b','F-081','F-088','F-099','F-136']]
    if not any(e.get('followup_audit') for e in audited):return ''
    out='<details class="archive-details audit-followup" id="t4-followup"><summary>此前 5 条待核记录的补核：1 条升为 T1，4 条保留 T4</summary><p class="archive-intro">此表跟踪此前指定的五条记录，不是当前全部T4目录。官方信函补齐了调查请求的证据。四条历史报价取得了分钟级对照，但分钟收盘值不能还原当时精确到秒的实时响应，成交量也有未解决的异常。</p><div class="table-scroll"><table><thead><tr><th>原记录 / UTC 时点</th><th>旧报价</th><th>同分钟 Close</th><th>结论</th></tr></thead><tbody>'
    comparisons=[('F-081','11-16 14:54','160.64','160.3100','旧价落在该分钟范围内；实时价与累计量仍待核'),('F-088','11-16 19:31','156.12','156.0350','旧价落在该分钟范围内；实时价与累计量仍待核'),('F-099','11-18 13:42','160.40','160.2423','160.40 对应前一分钟 13:41 的 Close，不能移动时间后视作原快照已证实'),('F-136','11-25 12:41','147.21','147.2395','旧价落在该分钟范围内；精确实时响应尚未恢复')]
    prefix='index.html' if short else ''
    out+=f'<tr><td><a href="{prefix}#F-002-b">2025-10-13 发信 / 10-14 公开</a></td><td colspan="2">Cotton 官方信函 + Reuters 原稿</td><td><span class="badge t1">T4 → T1</span> 仅确认发信要求调查</td></tr>'
    for ident,time,old,close,conclusion in comparisons:
        out+=f'<tr><td><a href="{prefix}#{ident}">{time}</a></td><td>${old}</td><td>${close}</td><td><span class="badge t4">保留 T4</span> {conclusion}</td></tr>'
    out+='</tbody></table></div><p class="visual-caption">另可复算：11-24 19:59 EST 盘后分钟 Close 为 $151.9531，相对常规收盘 $155.38 为 −2.21%（T2 历史分钟字段）；这不验证次日盘前快照。<a href="data/nvda-minute-audit-comparison.csv" download>分钟对照 CSV</a> · <a href="data/nvda-minute-audit-provenance.json">来源与口径</a></p></details>'
    return out
