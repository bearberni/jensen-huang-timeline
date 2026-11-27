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
    v=json.loads((ROOT/'data/relationships.json').read_text())
    nodes={n['id']:n for n in v['nodes']}
    relations={r['id']:r for r in v['relations']}
    out='<section class="section relationship-section" id="network"><div class="section-head"><div><p class="eyebrow">PEOPLE · INSTITUTIONS · EVIDENCE</p><h2>人物与机构关系图</h2><p class="section-intro">把关系的性质与证据等级一起看。选择主题，再点击连线标签或下方关系按钮，查看其来源和限定条件。</p></div><p class="section-note">连线表示特定关系或调查动作，不能沿连线推导知情、共谋或违法责任。</p></div><div class="network-tabs js-only" role="group" aria-label="关系图主题">'
    for i,view in enumerate(v['views']):
        out+=f'<button type="button" data-network-view="{E(view["id"])}" aria-pressed="{str(i==0).lower()}" aria-controls="network-{E(view["id"])}">{E(view["label"])}</button>'
    out+='</div><div class="network-legend"><span><i class="person-key" aria-hidden="true"></i>人物</span><span><i class="org-key" aria-hidden="true"></i>机构</span><span><i class="line-key t1" aria-hidden="true"></i>T1 原始材料</span><span><i class="line-key t2" aria-hidden="true"></i>T2 报道</span><span><i class="line-key t3" aria-hidden="true"></i>T3 未独立核实</span></div>'
    for vi,view in enumerate(v['views']):
        out+=f'<div class="network-view" id="network-{E(view["id"])}" data-view="{E(view["id"])}"><h3 class="network-view-heading">{E(view["label"])}</h3><p class="network-context">{E(view["context"])}</p><p class="network-mobile-hint">图可横向滑动；图下文字按钮也能查看全部关系与证据。</p><div class="network-scroll" tabindex="0" aria-label="{E(view["label"])}关系图，小屏可横向滚动"><svg class="relationship-svg" viewBox="0 0 900 480" role="group" aria-label="{E(view["label"])}关系图"><title>{E(view["label"])}关系图</title>'
        for edge in view['edges']:
            r=relations[edge['id']]; x,y=edge['label_xy']; width=max(100,len(r['short'])*14+46)
            out+=f'<a class="graph-edge {E(r["grade"].lower())}" href="#relation-{E(r["id"])}" data-relation="{E(r["id"])}" aria-label="{E(r["title"])}，{E(r["grade"])}，查看来源"><path class="edge-path" d="{E(edge["path"])}"/><path class="edge-hit" d="{E(edge["path"])}"/><rect class="edge-label-bg" x="{x-width/2}" y="{y-15}" width="{width}" height="30" rx="4"/><text class="edge-label" x="{x}" y="{y+5}" text-anchor="middle">{E(r["short"])} · {E(r["grade"])}</text></a>'
        for pos in view['nodes']:
            n=nodes[pos['id']]; x,y=pos['xy']; p=n['kind']=='person'
            out+=f'<g class="graph-node {"person" if p else "institution"}" data-node="{E(n["id"])}"><rect x="{x-92}" y="{y-37}" width="184" height="74" rx="{37 if p else 5}"/><text class="node-label" x="{x}" y="{y-2}" text-anchor="middle">{E(n["label"])}</text><text class="node-subtitle" x="{x}" y="{y+20}" text-anchor="middle">{E(n["role"])}</text></g>'
        out+='</svg></div><div class="relation-buttons js-only" role="group" aria-label="选择关系">'
        for edge in view['edges']:
            r=relations[edge['id']]
            out+=f'<button type="button" data-select-relation="{E(r["id"])}" aria-pressed="false" aria-controls="relation-{E(r["id"])}">{E(r["short"])} <span>{E(r["grade"])}</span></button>'
        out+='</div></div>'
    out+='<div class="relation-detail-wrap" aria-live="polite">'
    for r in v['relations']:
        out+=f'<article class="relation-detail" id="relation-{E(r["id"])}" data-relation-detail="{E(r["id"])}"><div class="relation-detail-top"><span class="badge {E(r["grade"].lower())}">{E(r["grade"])}</span><span>{E(r["date"])}</span></div><h3>{E(r["title"])}</h3><p>{E(r["body"])}</p><p class="relation-boundary"><b>证据边界：</b>{E(r["boundary"])}</p><div class="link-row">'+''.join(ext(s['label'],s['url']) for s in r['sources'])+'</div></article>'
    out+='</div><p class="visual-caption">不同线型和文字标签共同表示证据级别；分级针对连线上这一具体命题。<a href="data/relationships.json" download>下载关系与证据数据</a></p>'
    if short:out+='<p class="short-cta"><a href="index.html#evidence-questions">继续查看四项核心问题的证据边界</a></p>'
    return out+'</section>'

def render_t4_followup(data, short=False):
    audited=[e for e in data['timeline'] if e['stable_id'] in ['F-002-b','F-081','F-088','F-099','F-136']]
    if not any(e.get('followup_audit') for e in audited):return ''
    out='<details class="archive-details audit-followup" id="t4-followup"><summary>本次 5 条待核记录：1 条升为 T1，4 条保留 T4</summary><p class="archive-intro">官方信函补齐了调查请求的证据。四条历史报价取得了分钟级对照，但分钟收盘值不能还原当时精确到秒的实时响应，成交量也有未解决的异常。</p><div class="table-scroll"><table><thead><tr><th>原记录 / UTC 时点</th><th>旧报价</th><th>同分钟 Close</th><th>结论</th></tr></thead><tbody>'
    comparisons=[('F-081','11-16 14:54','160.64','160.3100','旧价落在该分钟范围内；实时价与累计量仍待核'),('F-088','11-16 19:31','156.12','156.0350','旧价落在该分钟范围内；实时价与累计量仍待核'),('F-099','11-18 13:42','160.40','160.2423','160.40 对应前一分钟 13:41 的 Close，不能移动时间后视作原快照已证实'),('F-136','11-25 12:41','147.21','147.2395','旧价落在该分钟范围内；精确实时响应尚未恢复')]
    prefix='index.html' if short else ''
    out+=f'<tr><td><a href="{prefix}#F-002-b">2025-10-13 发信 / 10-14 公开</a></td><td colspan="2">Cotton 官方信函 + Reuters 原稿</td><td><span class="badge t1">T4 → T1</span> 仅确认发信要求调查</td></tr>'
    for ident,time,old,close,conclusion in comparisons:
        out+=f'<tr><td><a href="{prefix}#{ident}">{time}</a></td><td>${old}</td><td>${close}</td><td><span class="badge t4">保留 T4</span> {conclusion}</td></tr>'
    out+='</tbody></table></div><p class="visual-caption">另可复算：11-24 19:59 EST 盘后分钟 Close 为 $151.9531，相对常规收盘 $155.38 为 −2.21%（T2 历史分钟字段）；这不验证次日盘前快照。<a href="data/nvda-minute-audit-comparison.csv" download>分钟对照 CSV</a> · <a href="data/nvda-minute-audit-provenance.json">来源与口径</a></p></details>'
    return out
