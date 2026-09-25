#!/usr/bin/env python3
"""Generate the public portfolio from one project catalog; no dependencies."""
import argparse
import html
import json
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[1]
SITE = 'https://hyeonwoo.kugora.ng'
ESC = html.escape
ARROW = '<span aria-hidden="true">↗</span>'


def catalog():
    items = json.loads((ROOT / 'data/projects.json').read_text())
    ids = set()
    for item in items:
        for key in ('id', 'name', 'english_name', 'category', 'headline', 'description', 'tags', 'platforms', 'technology', 'status', 'url', 'featured'):
            if key not in item:
                raise ValueError(f'Missing {key}: {item.get("id", "project")}')
        if item['id'] in ids or not item['id'].replace('-', '').isalnum():
            raise ValueError(f'Invalid or duplicate id: {item["id"]}')
        ids.add(item['id'])
        if item['category'] not in ('apps', 'games'):
            raise ValueError(f'Invalid category: {item["id"]}')
        url = urlparse(item['url'])
        if url.scheme != 'https' or not url.netloc:
            raise ValueError(f'An HTTPS detail URL is required: {item["id"]}')
        if not isinstance(item['tags'], list) or not item['tags']:
            raise ValueError(f'At least one tag is required: {item["id"]}')
    return items


def artwork(item):
    visual = item.get('visual', '')
    if visual == 'fillday':
        content = '<div class="calendar"><div class="calendar-heading"><span>오늘의 작은 계획</span><b>09</b></div><div class="calendar-week">M T W T F S S</div><div class="calendar-days">' + ''.join(f'<span class="day day-{n}">{n:02d}</span>' for n in range(1, 22)) + '</div><div class="calendar-note"><i></i> 나를 위한 시간</div></div><span class="art-sticker">a little, every day.</span>'
    elif visual == 'facet':
        content = '<div class="puzzle-back"></div><div class="puzzle-grid">' + ''.join(f'<span>{x}</span>' for x in ('1', '', '3', '', '5', '', '7', '', '9')) + '</div><span class="puzzle-orbit"></span><span class="art-sticker">a different perspective.</span>'
    elif visual == 'moonjunk':
        content = '<span class="moon"></span><span class="star star-one">✦</span><span class="star star-two">✧</span><div class="parcel"><span>TO: SOMEONE</span><i>☾</i></div><span class="art-sticker">every object has a story.</span>'
    elif visual == 'oseonro':
        content = '<div class="music-lines">' + '<i></i>' * 5 + '</div><div class="music-path"></div><span class="music-ball"></span><span class="music-note">♪</span><span class="art-sticker">draw your own rhythm.</span>'
    else:
        visual = 'default'
        content = f'<span class="project-initial">{ESC(item["name"][0])}</span>'
    return f'<div class="project-art art-{visual}" aria-hidden="true">{content}</div>'


def card(item):
    title = ESC(item['name'])
    english = f'<span class="project-english" lang="en">{ESC(item["english_name"])}</span>' if item['english_name'] else ''
    status = f'<span class="status">{ESC(item["status"])}</span>' if item['status'] else ''
    search = ESC(' '.join([item['name'], item['english_name'], item['description'], item['technology'], *item['tags']]), quote=True)
    tags = ' '.join(f'<span>{ESC(tag)}</span>' for tag in item['tags'])
    return f'''<article class="project-card" data-project data-search="{search}" data-tag="{ESC(item['tags'][0], quote=True)}">
      <a class="project-link" href="{ESC(item['url'], quote=True)}" aria-label="{title} 자세히 보기">
        {artwork(item)}
        <div class="project-copy"><div class="project-meta"><span>{ESC(item['technology'])} · {' / '.join(map(ESC, item['platforms']))}</span>{status}</div>
          <div class="project-title"><h3>{title}{english}</h3><span class="project-arrow" aria-hidden="true">↗</span></div>
          <p class="project-headline">{ESC(item['headline'])}</p><p class="project-description">{ESC(item['description'])}</p>
          <div class="project-tags">{tags}</div>
        </div>
      </a></article>'''


def page(title, description, route, body, active):
    links = [('home', '/', '메인'), ('apps', '/apps/', '앱'), ('games', '/games/', '게임')]
    nav = ''
    for key, path, label in links:
        current = ' aria-current="page"' if active == key else ''
        nav += f'<a href="{path}"{current}>{label}</a>'
    canonical = SITE + route
    return f'''<!doctype html>
<html lang="ko">
<head>
  <meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
  <meta name="theme-color" content="#f5f4ef"><meta name="description" content="{ESC(description, quote=True)}">
  <meta property="og:type" content="website"><meta property="og:title" content="{ESC(title, quote=True)}">
  <meta property="og:description" content="{ESC(description, quote=True)}"><meta property="og:url" content="{canonical}">
  <meta property="og:image" content="{SITE}/assets/profile.png"><meta property="og:image:alt" content="김현우의 일러스트 프로필">
  <meta name="twitter:card" content="summary"><link rel="canonical" href="{canonical}">
  <link rel="icon" href="/assets/mark.svg" type="image/svg+xml"><link rel="stylesheet" href="/assets/site.css">
  <script src="/assets/catalog.js" defer></script><title>{ESC(title)}</title>
</head>
<body>
  <a class="skip-link" href="#main">본문으로 바로 가기</a>
  <header class="site-header wrap"><a class="brand" href="/" aria-label="김현우 포트폴리오 메인"><span class="brand-mark">hw<span>.</span></span><span class="brand-name">Hyeonwoo Kim<small>independent developer</small></span></a>
    <nav class="site-nav" aria-label="주 메뉴">{nav}</nav><a class="header-contact" href="mailto:ialskdji@gmail.com">이야기 나누기 {ARROW}</a></header>
  <main id="main">{body}</main>
  <footer class="site-footer wrap"><a class="footer-brand" href="/">Hyeonwoo Kim <span>© 2026</span></a><p>일상을 위한 앱, 호기심을 위한 게임.</p><div><a href="https://github.com/kugorang">GitHub {ARROW}</a><a href="mailto:ialskdji@gmail.com">Email {ARROW}</a></div></footer>
</body>
</html>
'''


def home(items):
    apps = sum(x['category'] == 'apps' for x in items)
    games = len(items) - apps
    featured = ''.join(card(x) for x in items if x['featured'])
    return f'''<section class="hero wrap" aria-labelledby="hero-title"><div class="hero-copy"><p class="eyebrow"><span class="little-star" aria-hidden="true">✳</span> HELLO, I'M HYEONWOO</p>
      <h1 id="hero-title">쓸모 있는 일상,<br><span>오래 남는 놀이.</span></h1>
      <p class="hero-intro">안녕하세요, <strong>김현우</strong>입니다.<br>생활에 스며드는 앱과<br class="mobile-break"> 나만의 리듬으로 즐기는 게임을 만듭니다.</p>
      <div class="hero-actions"><a class="button button-blue" href="/apps/">앱 둘러보기 {ARROW}</a><a class="button button-outline" href="/games/">게임 둘러보기 {ARROW}</a></div>
      <p class="hero-note"><span aria-hidden="true">↳</span> 아이디어를 화면으로, 화면을 일상으로.</p></div>
      <figure class="portrait"><div class="portrait-frame"><img src="/assets/profile.png" width="2048" height="2048" alt="파란 배경에 둥근 안경을 쓴 김현우의 일러스트 프로필" fetchpriority="high"></div><figcaption><span>KIM HYEONWOO</span><span>also known as kugorang {ARROW}</span></figcaption><span class="portrait-label" aria-hidden="true">Made of curiosity.</span></figure>
    </section>
    <section class="selected-section wrap" aria-labelledby="selected-title"><div class="section-heading"><div><p class="eyebrow">A FEW THINGS I'VE MADE</p><h2 id="selected-title">이런 걸 만들고 있어요.</h2></div><p>작은 생각에서 시작한 앱과 게임들.</p></div><div class="project-grid">{featured}</div></section>
    <section class="collections wrap" aria-label="모든 작업 둘러보기"><a class="collection-link" href="/apps/"><span class="collection-index">01 / APPS</span><div><h2>일상을 조금 더 편하게.</h2><p>정리하고, 기록하고, 나에게 맞추는 도구.</p></div><span class="collection-count">{apps:02d}개의 앱</span>{ARROW}</a><a class="collection-link" href="/games/"><span class="collection-index">02 / GAMES</span><div><h2>호기심이 이끄는 쪽으로.</h2><p>풀어 보고, 그려 보고, 이야기를 만나는 놀이.</p></div><span class="collection-count">{games:02d}개의 게임</span>{ARROW}</a></section>
    <section class="about-section wrap" aria-labelledby="about-title"><div><p class="eyebrow">BEHIND THE WORK</p><h2 id="about-title">작은 아이디어도<br>끝까지 만들어 봅니다.</h2></div><div class="about-copy"><p>유용한 도구를 좋아하고, 새로운 놀이가 궁금합니다. 직접 쓰고 싶은 앱과 계속 들여다보고 싶은 게임을 기획하고 디자인하며 개발합니다.</p><p>Flutter와 Unity로 아이디어를 구현하고, 한 번의 터치부터 화면의 흐름까지 사용 경험을 다듬습니다. 이곳에 그 과정에서 만든 작업들을 모아 둡니다.</p><a class="text-link" href="https://github.com/kugorang">GitHub에서 더 보기 {ARROW}</a></div></section>
    {contact()}'''


def contact():
    return f'''<section class="contact-section" aria-labelledby="contact-title"><div class="wrap contact-inner"><div><p class="eyebrow">HAVE SOMETHING IN MIND?</p><h2 id="contact-title">다음 이야기를<br>함께 나눠요.</h2></div><div><p>작업에 관한 궁금한 점이나<br>함께 만들고 싶은 아이디어가 있다면.</p><a href="mailto:ialskdji@gmail.com">ialskdji@gmail.com {ARROW}</a></div></div></section>'''


def collection(items, category):
    filtered = [x for x in items if x['category'] == category]
    is_app = category == 'apps'
    label, english = ('앱', 'APPS') if is_app else ('게임', 'GAMES')
    title = '하루에 자연스럽게<br>스며드는 도구.' if is_app else '호기심을 따라,<br>새로운 놀이로.'
    desc = '일정과 기록처럼 매일 반복되는 일들을 조금 더 편하게. 직접 쓰고 싶은 도구를 만듭니다.' if is_app else '익숙한 퍼즐을 다른 각도에서 보고, 물건에 담긴 이야기를 만나고, 내가 그린 길에서 음악을 찾습니다.'
    tags = list(dict.fromkeys(x['tags'][0] for x in filtered))
    buttons = '<button type="button" class="filter-chip" data-filter="" aria-pressed="true">전체</button>' + ''.join(f'<button type="button" class="filter-chip" data-filter="{ESC(tag, quote=True)}" aria-pressed="false">{ESC(tag)}</button>' for tag in tags)
    return f'''<section class="collection-hero wrap" aria-labelledby="page-title"><p class="eyebrow">THE COLLECTION / {english}</p><div class="collection-hero-row"><h1 id="page-title">{title}</h1><div><span class="collection-total">{len(filtered):02d}<small>개의 {label}</small></span><p>{desc}</p></div></div></section>
    <section class="catalog-section wrap" data-catalog aria-label="{label} 목록"><div class="catalog-tools" hidden><div class="filters" role="group" aria-label="분야로 필터">{buttons}</div><label class="search-field"><span class="sr-only">{label} 이름이나 키워드 검색</span><span aria-hidden="true">⌕</span><input type="search" placeholder="이름이나 키워드로 찾기" aria-controls="project-list" autocomplete="off"></label></div><div class="catalog-heading"><h2>모든 {label}</h2><p data-result-count role="status" aria-live="polite">{len(filtered)}개의 작업</p></div><div class="project-grid catalog-grid" id="project-list">{''.join(card(x) for x in filtered)}</div><div class="empty-state" hidden><h3>아직 맞는 작업을 찾지 못했어요.</h3><p>다른 이름이나 키워드로 찾아보세요.</p><button type="button" class="button button-outline" data-reset>전체 작업 보기</button></div></section>
    <aside class="next-collection wrap"><span>{'새로운 놀이도 궁금하다면' if is_app else '일상을 위한 도구가 궁금하다면'}</span><a href="/{'games' if is_app else 'apps'}/">{'게임' if is_app else '앱'} 둘러보기 {ARROW}</a></aside>{contact()}'''


def build(check=False):
    items = catalog()
    output = {
        'index.html': page('김현우 · Hyeonwoo Kim — 앱과 게임을 만듭니다', '김현우의 포트폴리오. 일상을 위한 앱과 호기심을 위한 게임, 직접 만든 작업을 소개합니다.', '/', home(items), 'home'),
        'apps/index.html': page('앱 · 김현우의 포트폴리오', '일정과 기록처럼 매일 반복되는 일을 조금 더 편하게. 김현우가 만든 앱을 만나보세요.', '/apps/', collection(items, 'apps'), 'apps'),
        'games/index.html': page('게임 · 김현우의 포트폴리오', 'Facet Sudoku, 달빛 고물상, 오선로. 김현우가 만드는 게임과 새로운 놀이를 소개합니다.', '/games/', collection(items, 'games'), 'games'),
        '404.html': page('페이지를 찾을 수 없어요 · 김현우', '김현우의 앱과 게임 포트폴리오로 돌아가세요.', '/404.html', '<section class="not-found wrap"><p class="eyebrow">404 / A SMALL DETOUR</p><h1>여기엔 아직<br>아무것도 없네요.</h1><p>주소를 다시 확인하거나, 다른 작업을 둘러보세요.</p><a class="button button-blue" href="/">메인으로 돌아가기 ↗</a></section>', ''),
        'robots.txt': f'User-agent: *\nAllow: /\nSitemap: {SITE}/sitemap.xml\n',
        'sitemap.xml': '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' + ''.join(f'  <url><loc>{SITE}{path}</loc></url>\n' for path in ('/', '/apps/', '/games/')) + '</urlset>\n',
    }
    outdated = []
    for name, content in output.items():
        path = ROOT / name
        if check:
            if not path.exists() or path.read_text() != content:
                outdated.append(name)
        else:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content)
    if outdated:
        raise SystemExit('Run python3 scripts/build.py; stale files: ' + ', '.join(outdated))
    print(f'{"Verified" if check else "Built"} {len(output)} files from {len(items)} projects.')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--check', action='store_true')
    build(parser.parse_args().check)
