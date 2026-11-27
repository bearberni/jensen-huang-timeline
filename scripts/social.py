"""Restore the existing social archive without claiming a fresh collection."""
from html import escape
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def _e(value):
    return escape(str(value), quote=True)


def _external(label, url):
    return f'<a href="{_e(url)}" target="_blank" rel="noopener noreferrer">{_e(label)}</a>'


def _links(items):
    return '<div class="social-links">' + ''.join(
        _external(item['label'], item['url']) for item in items
    ) + '</div>'


def _number(value):
    return f'{int(value):,}'


def _inventory(data, short):
    prefix = 'index.html' if short else ''
    records = [
        ('public_responses', '公开回应', 'social-voices', '公司、本人及各方表态'),
        ('x_posts', 'X 原帖', 'social-x', '旧版热帖索引'),
        ('hacker_news', 'HN 讨论楼', 'social-hn', '原讨论链接'),
        ('youtube', 'YouTube 视频', 'social-videos', '原视频链接'),
    ]
    out = '<div class="social-inventory" aria-label="完整档案当前收录数量">'
    for key, label, anchor, caption in records:
        out += f'<a class="social-count" href="{prefix}#{anchor}"><strong>{data["inventory"][key]}</strong><span>{label}</span><small>{caption}</small></a>'
    return out + '</div><p class="social-caption">以上是完整档案可逐项查看的条目数；下方点赞、浏览和平台语料数量是旧版快照，两者的证据状态不同。</p>'


def _featured(data, short):
    prefix = 'index.html' if short else ''
    out = '<div class="social-featured" aria-label="三类公开回应与证据范围">'
    for item in data['featured']:
        out += f'<article class="social-feature"><div class="social-card-meta"><span class="badge {item["grade"].lower()}">{item["grade"]}</span><span>{_e(item["kind"])}</span><time datetime="{item["date"]}">{item["date"]}</time></div><h3>{_e(item["title"])}</h3><p>{_e(item["body"])}</p><p class="social-boundary">{_e(item["boundary"])}</p>'
        out += _links(item['links'])
        out += f'<a class="social-record-link" href="{prefix}#{_e(item["event_id"])}">查看对应时间线记录</a></article>'
    return out + '</div>'


def _platforms(data, short):
    total = sum(item['count'] for item in data['platforms'])
    out = '<div class="social-block" id="social-platforms"><div class="social-block-head"><div><p class="social-kicker">ARCHIVED COUNTS</p><h3>六个平台的旧版数量</h3></div><span class="badge t4">T4 · 旧快照未复算</span></div>'
    out += f'<p class="social-block-intro">六行算术合计 <strong>{_number(total)}</strong> 条。这是旧表所列数字的加总，不是本次新增采集，也不能换算为平台舆论份额。</p><div class="social-platform-grid">'
    for item in data['platforms']:
        status = '旧称刷新 396/400' if item['name'] == 'X' else '沿用旧快照'
        out += f'<div class="social-platform"><span>{_e(item["name"])}</span><strong>{_number(item["count"])}</strong><small>{status}</small></div>'
    out += '</div><div class="social-snapshot-warning"><strong>时间标签冲突，互动指标继续待核。</strong><p>旧平台表标注 11-26 12:54 UTC，X 热帖榜标注 11-16 19:31 UTC，却收录了 11-23 复职帖。公开仓库未附采集明细；点赞、浏览、分数和播放量均不是当前数值。</p></div>'
    if short:
        out += '<p class="social-caption">旧版另记“15,182 条旧帖 + 268 条新帖”，采集和去重方法未复核。</p><p class="social-full-link"><a href="index.html#gossip">查看完整平台表、原帖和口径说明</a></p>'
    else:
        out += _table('旧版平台采集表', ['平台', '旧表条数', '旧版刷新说明'], [
            [_e(item['name']), _number(item['count']), _e(item['legacy_status'])]
            for item in data['platforms']
        ], 'social-platform-table')
        out += '<details class="social-method"><summary>查看时间、采样及汇总口径的未决问题</summary><div class="social-method-content">'
        for limit in data['limitations']:
            out += f'<p><strong>{_e(limit["title"])}：</strong>{_e(limit["text"])}</p>'
        out += '<p>旧版另记“15,182 条旧帖 + 268 条新帖”。此处保留该档案注释，未据此确认增量采集或去重结果。</p></div></details>'
    return out + '</div>'


def _table(caption, headings, rows, klass=''):
    out = f'<div class="social-table-wrap {_e(klass)}" tabindex="0" role="region" aria-label="{_e(caption)}；小屏可横向滚动"><table class="social-table"><caption>{_e(caption)}</caption><thead><tr>'
    out += ''.join(f'<th scope="col">{_e(label)}</th>' for label in headings)
    out += '</tr></thead><tbody>'
    for row in rows:
        out += '<tr>' + ''.join(f'<td>{cell}</td>' for cell in row) + '</tr>'
    return out + '</tbody></table></div>'


def _voices(data):
    out = '<div class="social-block" id="social-voices"><div class="social-block-head"><div><p class="social-kicker">PUBLIC RESPONSES</p><h3>15 条公开回应与历史表态</h3></div><span class="social-context-label">摘录与译述</span></div><p class="social-block-intro">保留旧版全部 15 条回应。按当时身份和日期阅读；官方声明、媒体转述与个人表态的证明范围不同。</p>'

    def cards(items):
        result = '<div class="social-voice-grid">'
        for item in items:
            result += f'<article class="social-voice"><h4>{_e(item["label"])}</h4><blockquote>{_e(item["text"])}</blockquote>{_links(item["links"])}</article>'
        return result + '</div>'

    out += cards(data['public_responses'][:6])
    out += '<details class="social-more"><summary>查看其余 9 条公开回应</summary>' + cards(data['public_responses'][6:]) + '</details>'
    return out + '</div>'


def _post_tables(data):
    out = '<div class="social-block" id="social-x"><div class="social-block-head"><div><p class="social-kicker">X · ORIGINAL POSTS</p><h3>16 条 X 热帖原始索引</h3></div><span class="badge t4">互动量 · T4</span></div><p class="social-block-intro">保留旧榜顺序、截断帖文和原链接。下列标题包含评论、玩笑或未经证实的指控，仅用于辨认原帖；本页不据此确认指控。所有互动数字均为未复算的旧快照。</p>'
    out += _table('X 热帖旧榜：点赞与浏览均未复算', ['旧排名', '账号', '原索引帖文', '旧点赞', '旧浏览'], [
        [str(item['rank']), _e(item['account_label']), _external(item['excerpt'], item['url']), _number(item['likes']), _number(item['views'])]
        for item in data['posts']
    ], 'social-post-table') + '</div>'
    out += '<div class="social-block" id="social-accounts"><div class="social-block-head"><div><p class="social-kicker">ACCOUNT INDEX</p><h3>公众账号的旧版汇总</h3></div><span class="badge t4">汇总口径 · T4</span></div><p class="social-block-intro">旧版称覆盖 136 个账号，展示前 12 行。当前保留这 12 行；覆盖范围、分类与累计点赞未独立复算。Musk 汇总与上方热帖榜口径不一致，不能合并比较。</p><details class="social-more"><summary>展开 12 行账号汇总</summary>'
    out += _table('旧版公众账号汇总：不可与热帖榜视作同一快照', ['人物／账号名', '账号', '旧版类别', '旧帖数', '旧累计点赞'], [
        [_e(item['name']), _e(item['handle']), _e(item['category']), _number(item['posts']), _number(item['likes'])]
        for item in data['accounts']
    ]) + '</details></div>'
    out += '<div class="social-block" id="social-hn"><div class="social-block-head"><div><p class="social-kicker">HACKER NEWS</p><h3>8 个讨论楼</h3></div><span class="badge t4">旧分数 · T4</span></div><p class="social-block-intro">保留旧版所列的讨论链接与提交日期；分数沿用旧快照，不是当前值。</p>'
    out += _table('Hacker News 讨论索引', ['讨论楼', '旧分数', '旧录提交日期'], [
        [_external(item['title'], item['url']), _number(item['score']), _e(item['submission_date'])]
        for item in data['hacker_news']
    ]) + '</div>'
    out += '<div class="social-block" id="social-videos"><div class="social-block-head"><div><p class="social-kicker">YOUTUBE</p><h3>6 条视频原始索引</h3></div><span class="badge t4">旧播放量 · T4</span></div><p class="social-block-intro">保留旧版搜索结果中的截断标题及链接。标题的断言不构成本页结论；播放量沿用旧快照。</p>'
    out += _table('YouTube 视频旧版索引', ['原索引视频标题', '频道', '旧播放量'], [
        [_external(item['title'], item['url']), _e(item['channel']), _number(item['views'])]
        for item in data['youtube']
    ]) + '</div>'
    return out


def render_social(short=False):
    """Return one visible, anchorable archive section for either edition."""
    data = json.loads((ROOT / 'data/social.json').read_text())
    out = '<section class="section social-section' + (' social-short' if short else '') + '" id="reactions"><span id="gossip" class="social-anchor" aria-hidden="true"></span><div class="section-head"><div><p class="eyebrow">PUBLIC VOICES & SOCIAL ARCHIVE</p><h2>社交媒体与公开回应</h2><p class="section-intro">公开表态、原帖索引和传播快照一起保留。先看谁说了什么，再查看来源与数字的限定。</p></div><p class="section-note">完整档案收录数可以逐项核对；旧互动数字标为 T4，不代表当前热度或总体舆论。</p></div>'
    out += _inventory(data, short)
    out += _featured(data, short)
    if not short:
        out += '<nav class="social-mini-nav" aria-label="公开回应与社交档案分组">'
        for anchor, label in [('social-voices','公开回应'),('social-platforms','平台快照'),('social-x','X 原帖'),('social-accounts','账号汇总'),('social-hn','Hacker News'),('social-videos','YouTube')]:
            out += f'<a href="#{anchor}">{label}</a>'
        out += '</nav>' + _voices(data)
    out += _platforms(data, short)
    if not short:
        out += _post_tables(data)
        out += '<div class="social-coverage"><h3>旧版采样覆盖边界</h3><ul>'
        out += ''.join(f'<li>{_e(item)}</li>' for item in data['coverage_limits'])
        out += '</ul><p>本轮恢复和整理已有内容，未启动新的社媒采集。原表数据与本次分级说明均可下载核对。</p></div>'
    out += '<p class="social-caption social-download"><a href="data/social.json" download>下载完整社交档案与口径说明</a>'
    if short:
        out += ' · <a href="index.html#reactions">打开完整公开回应与原帖索引</a>'
    out += '</p></section>'
    return out
