#!/usr/bin/env python3
"""Generate the existing portfolio and complete localized static pages."""
import argparse
import html
import json
import re
from pathlib import Path
from string import Formatter
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[1]
SITE = 'https://hw.kugora.ng'
ESC = html.escape
ARROW = '<span aria-hidden="true">↗</span>'
LANGUAGES = json.loads((ROOT / 'data/languages.json').read_text())
CODES = [x['code'] for x in LANGUAGES]
ROUTES = {'home': '/', 'apps': '/apps/', 'games': '/games/', '404': '/404.html'}


def translations():
    result = {code: json.loads((ROOT / f'data/locales/{code}.json').read_text()) for code in CODES}
    base = result['ko']
    fields = lambda value: {name for _, name, _, _ in Formatter().parse(value) if name}
    for code, messages in result.items():
        if set(messages) != set(base):
            raise ValueError(f'{code}: translation keys differ: {set(messages) ^ set(base)}')
        for key, value in messages.items():
            if not isinstance(value, str) or not value.strip() or fields(value) != fields(base[key]):
                raise ValueError(f'{code}: missing text or mismatched placeholders: {key}')
    return result


def catalog():
    items = json.loads((ROOT / 'data/projects.json').read_text())
    ids = set()
    for item in items:
        for key in ('id', 'name', 'english_name', 'category', 'headline', 'description', 'tags', 'platforms', 'technology', 'status', 'url', 'featured'):
            if key not in item:
                raise ValueError(f'Missing {key}: {item.get("id", "project")}')
        if item['id'] in ids or not re.fullmatch(r'[a-z0-9-]+', item['id']):
            raise ValueError(f'Invalid or duplicate id: {item["id"]}')
        ids.add(item['id'])
        if item['category'] not in ('apps', 'games') or item['status'] not in ('released', 'development'):
            raise ValueError(f'Invalid category or status: {item["id"]}')
        url = urlparse(item['url'])
        if url.scheme != 'https' or not url.netloc or not isinstance(item['tags'], list) or not item['tags']:
            raise ValueError(f'Invalid detail URL or tags: {item["id"]}')
        stores = item.get('stores', {})
        if stores and item['status'] != 'released':
            raise ValueError(f'Unreleased project cannot have install links: {item["id"]}')
        for store, address in stores.items():
            parsed = urlparse(address)
            expected_host = {'App Store': 'apps.apple.com', 'Google Play': 'play.google.com'}.get(store)
            if parsed.scheme != 'https' or not expected_host or parsed.netloc != expected_host:
                raise ValueError(f'Invalid store URL: {item["id"]}')
    return items


class Copy:
    def __init__(self, messages):
        self.messages = messages

    def raw(self, key, **values):
        return self.messages[key].format(**values)

    def __call__(self, key, **values):
        return ESC(self.raw(key, **values), quote=True)

    def lines(self, key):
        return '<br>'.join(ESC(x) for x in self.raw(key).split('\n'))


def path_for(code, route):
    return f'/{code}{route}'


def artwork(item, t):
    visual = item.get('visual', '')
    if visual == 'fillday':
        content = f'<div class="calendar"><div class="calendar-heading"><span>{t("art.today")}</span><b>09</b></div><div class="calendar-week">{t("art.week")}</div><div class="calendar-days">' + ''.join(f'<span class="day day-{n}">{n:02d}</span>' for n in range(1, 22)) + f'</div><div class="calendar-note"><i></i> {t("art.time")}</div></div><span class="art-sticker">{t("art.fillday")}</span>'
    elif visual == 'facet':
        content = '<div class="puzzle-back"></div><div class="puzzle-grid">' + ''.join(f'<span>{x}</span>' for x in ('1', '', '3', '', '5', '', '7', '', '9')) + f'</div><span class="puzzle-orbit"></span><span class="art-sticker">{t("art.facet")}</span>'
    elif visual == 'moonjunk':
        content = f'<span class="moon"></span><span class="star star-one">✦</span><span class="star star-two">✧</span><div class="parcel"><span>{t("art.parcel")}</span><i>☾</i></div><span class="art-sticker">{t("art.moonjunk")}</span>'
    elif visual == 'oseonro':
        content = '<div class="music-lines">' + '<i></i>' * 5 + f'</div><div class="music-path"></div><span class="music-ball"></span><span class="music-note">♪</span><span class="art-sticker">{t("art.oseonro")}</span>'
    else:
        visual = 'default'
        content = f'<span class="project-initial">{ESC(item["name"][0])}</span>'
    return f'<div class="project-art art-{visual}" aria-hidden="true">{content}</div>'


def card(item, t):
    title = ESC(item['name'])
    if re.search('[가-힣]', item['name']):
        title = f'<span lang="ko">{title}</span>'
    # Keep the established brand names, including their existing English forms.
    english = f'<span class="project-english" lang="en">{ESC(item["english_name"])}</span>' if item['english_name'] else ''
    search = ESC(' '.join([item['name'], item['english_name'], t.raw(item['id'] + '.description'), item['technology'], *[t.raw('tag.' + x) for x in item['tags']]]), quote=True)
    tags = ' '.join(f'<span>{t("tag." + tag)}</span>' for tag in item['tags'])
    stores = ''.join(f'<a class="button button-outline store-link" href="{ESC(address, quote=True)}" aria-label="{t("cta.store.label", name=item["name"], store=store)}">{t("cta.store", store=store)} {ARROW}</a>' for store, address in item.get('stores', {}).items())
    return f'''<article class="project-card" data-project data-status="{item['status']}" data-search="{search}" data-tag="{ESC(item['tags'][0], quote=True)}">
      <a class="project-link" href="{ESC(item['url'], quote=True)}" aria-label="{t('cta.detail.label', name=item['name'])}" aria-describedby="{item['id']}-description">
        {artwork(item, t)}<div class="project-copy"><div class="project-meta"><span>{ESC(item['technology'])} · {' / '.join(map(ESC, item['platforms']))}</span><span class="status status-{item['status']}">{t('status.' + item['status'])}</span></div>
        <div class="project-title"><h3>{title}{english}</h3><span class="project-arrow" aria-hidden="true">↗</span></div>
        <p class="project-headline">{t(item['id'] + '.headline')}</p><p class="project-description" id="{item['id']}-description">{t(item['id'] + '.description')}</p><div class="project-tags">{tags}</div><span class="detail-cta">{t('cta.detail')} {ARROW}</span></div>
      </a>{f'<div class="store-links">{stores}</div>' if stores else ''}</article>'''


def page(active, route, body, code, t, default=False):
    title, description = t('meta.' + active + '.title'), t('meta.' + active + '.desc')
    nav = ''.join(f'<a href="{path_for(code, ROUTES[key])}"' + (' aria-current="page"' if active == key else '') + f'>{t("nav." + key)}</a>' for key in ('home', 'apps', 'games'))
    canonical = SITE + path_for(code, route)
    alternates = ''.join(f'<link rel="alternate" hreflang="{x}" href="{SITE}{path_for(x, route)}">' for x in CODES)
    languages = ''.join(f'<a href="{path_for(x["code"], route)}" lang="{x["code"]}" hreflang="{x["code"]}" data-language="{x["code"]}"' + (' aria-current="true"' if x['code'] == code else '') + f'>{ESC(x["label"])}</a>' for x in LANGUAGES)
    label = next(x['label'] for x in LANGUAGES if x['code'] == code)
    return f'''<!doctype html>
<html lang="{code}" data-locale="{code}" data-route="{route}" data-default="{str(default).lower()}" data-supported="{','.join(CODES)}">
<head>
  <meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
  <script src="/assets/language.js"></script>
  <meta name="theme-color" content="#f5f4ef"><meta name="description" content="{description}">
  <meta property="og:type" content="website"><meta property="og:title" content="{title}"><meta property="og:description" content="{description}"><meta property="og:url" content="{canonical}">
  <meta property="og:image" content="{SITE}/assets/profile.png"><meta property="og:image:alt" content="{t('profile.alt')}"><meta property="og:locale" content="{ {'ko':'ko_KR','en':'en_US','ja':'ja_JP','de':'de_DE','fr':'fr_FR','es':'es_ES','pt-BR':'pt_BR'}[code]}">
  <meta name="twitter:card" content="summary"><link rel="canonical" href="{canonical}">{alternates}<link rel="alternate" hreflang="x-default" href="{SITE}{route}">
  {'<meta name="robots" content="noindex">' if active == '404' else ''}
  <link rel="icon" href="/assets/mark.svg" type="image/svg+xml"><link rel="stylesheet" href="/assets/site.css">
  <script src="/assets/catalog.js" defer></script><title>{title}</title>
</head>
<body>
  <a class="skip-link" href="#main">{t('nav.skip')}</a>
  <header class="site-header wrap"><a class="brand" href="{path_for(code, '/')}" aria-label="{t('nav.brand')}"><span class="brand-mark">hw<span>.</span></span><span class="brand-name">Hyeonwoo Kim<small>{t('nav.role')}</small></span></a>
    <nav class="site-nav" aria-label="{t('nav.label')}">{nav}</nav><div class="header-tools"><a class="header-contact" href="mailto:ialskdji@gmail.com">{t('nav.contact')} {ARROW}</a><details class="language-picker"><summary><span class="sr-only">{t('nav.language')}: </span>{ESC(label)} <span aria-hidden="true">⌄</span></summary><nav class="language-options" aria-label="{t('nav.language')}">{languages}</nav></details></div></header>
  <main id="main" tabindex="-1">{body}</main>
  <footer class="site-footer wrap"><a class="footer-brand" href="{path_for(code, '/')}">Hyeonwoo Kim <span>© 2026</span></a><p>{t('footer.line')}</p><div><a href="https://github.com/kugorang">GitHub {ARROW}</a><a href="mailto:ialskdji@gmail.com">{t('footer.email')} {ARROW}</a></div></footer>
</body>
</html>
'''.replace('  \n', '\n')


def contact(t):
    return f'''<section class="contact-section" aria-labelledby="contact-title"><div class="wrap contact-inner"><div><p class="eyebrow">{t('contact.eyebrow')}</p><h2 id="contact-title">{t.lines('contact.title')}</h2></div><div><p>{t.lines('contact.desc')}</p><a href="mailto:ialskdji@gmail.com">ialskdji@gmail.com {ARROW}</a></div></div></section>'''


def home(items, code, t):
    counts = {category: sum(x['category'] == category for x in items) for category in ('apps', 'games')}
    featured = ''.join(card(x, t) for x in items if x['featured'])
    collections = ''.join(f'<a class="collection-link" href="{path_for(code, ROUTES[category])}"><span class="collection-index">{t(category + ".index")}</span><div><h2>{t(category + ".shorttitle")}</h2><p>{t(category + ".shortdesc")}</p></div><span class="collection-count">{t(category + ".count", count=f"{counts[category]:02d}")}</span>{ARROW}</a>' for category in ('apps', 'games'))
    return f'''<section class="hero wrap" aria-labelledby="hero-title"><div class="hero-copy"><p class="eyebrow"><span class="little-star" aria-hidden="true">✳</span> {t('hero.eyebrow')}</p><h1 id="hero-title">{t('hero.first')}<br><span>{t('hero.second')}</span></h1><p class="hero-intro">{t.lines('hero.intro')}</p><div class="hero-actions"><a class="button button-blue" href="{path_for(code, '/apps/')}">{t('cta.apps')} {ARROW}</a><a class="button button-outline" href="{path_for(code, '/games/')}">{t('cta.games')} {ARROW}</a></div><p class="hero-note"><span aria-hidden="true">↳</span> {t('hero.note')}</p></div>
    <figure class="portrait"><div class="portrait-frame"><img src="/assets/profile.png" width="2048" height="2048" alt="{t('profile.alt')}" fetchpriority="high"></div><figcaption><span>KIM HYEONWOO</span><span>{t('profile.alias')} {ARROW}</span></figcaption><span class="portrait-label" aria-hidden="true">{t('profile.sticker')}</span></figure></section>
    <section class="selected-section wrap" aria-labelledby="selected-title"><div class="section-heading"><div><p class="eyebrow">{t('selected.eyebrow')}</p><h2 id="selected-title">{t('selected.title')}</h2></div><p>{t('selected.desc')}</p></div><div class="project-grid">{featured}</div></section>
    <section class="collections wrap" aria-label="{t('collections.label')}">{collections}</section>
    <section class="about-section wrap" aria-labelledby="about-title"><div><p class="eyebrow">{t('about.eyebrow')}</p><h2 id="about-title">{t.lines('about.title')}</h2></div><div class="about-copy"><p>{t('about.first')}</p><p>{t('about.second')}</p><a class="text-link" href="https://github.com/kugorang">{t('cta.github')} {ARROW}</a></div></section>{contact(t)}'''


def collection(items, category, code, t):
    filtered = [x for x in items if x['category'] == category]
    tags = list(dict.fromkeys(x['tags'][0] for x in filtered))
    buttons = '<button type="button" class="filter-chip" data-filter="" aria-pressed="true">' + t('filter.all') + '</button>' + ''.join(f'<button type="button" class="filter-chip" data-filter="{ESC(tag, quote=True)}" aria-pressed="false">{t("tag." + tag)}</button>' for tag in tags)
    groups = ''
    for status in ('released', 'development'):
        projects = [x for x in filtered if x['status'] == status]
        if projects:
            groups += f'<section class="release-group" data-release-group aria-labelledby="{status}-title"><div class="release-heading"><h2 id="{status}-title">{t("status." + status)}</h2><p>{t("status." + status + ".desc")}</p></div><div class="project-grid catalog-grid">' + ''.join(card(x, t) for x in projects) + '</div></section>'
    other = 'games' if category == 'apps' else 'apps'
    return f'''<section class="collection-hero wrap" aria-labelledby="page-title"><p class="eyebrow">{t(category + '.eyebrow')}</p><div class="collection-hero-row"><h1 id="page-title">{t.lines(category + '.title')}</h1><div><span class="collection-total">{len(filtered):02d}</span><p>{t(category + '.desc')}</p></div></div></section>
    <section class="catalog-section wrap" data-catalog data-count-all="{t('count.all', count='{count}')}" data-count-filtered="{t('count.filtered', count='{count}', total='{total}')}" aria-label="{t(category + '.list')}"><div class="catalog-tools" hidden><div class="filters" role="group" aria-label="{t('filter.label')}">{buttons}</div><label class="search-field"><span class="sr-only">{t('search.label')}</span><span aria-hidden="true">⌕</span><input type="search" placeholder="{t('search.placeholder')}" aria-controls="project-list" autocomplete="off"></label></div><div class="catalog-heading"><p data-result-count role="status" aria-live="polite">{t('count.all', count=len(filtered))}</p></div><div id="project-list">{groups}</div><div class="empty-state" hidden><h2>{t('empty.title')}</h2><p>{t('empty.desc')}</p><button type="button" class="button button-outline" data-reset>{t('empty.reset')}</button></div></section>
    <aside class="next-collection wrap"><span>{t('next.' + other)}</span><a href="{path_for(code, ROUTES[other])}">{t('cta.' + other)} {ARROW}</a></aside>{contact(t)}'''


def not_found(code, t):
    return f'<section class="not-found wrap"><p class="eyebrow">{t("404.eyebrow")}</p><h1>{t.lines("404.title")}</h1><p>{t("404.desc")}</p><a class="button button-blue" href="{path_for(code, "/")}">{t("404.home")} {ARROW}</a></section>'


def output_files():
    items, texts = catalog(), translations()
    output = {}
    for code in CODES:
        t = Copy(texts[code])
        for key, route in ROUTES.items():
            body = home(items, code, t) if key == 'home' else not_found(code, t) if key == '404' else collection(items, key, code, t)
            filename = route.lstrip('/') + ('index.html' if route.endswith('/') else '')
            output[f'{code}/{filename}'] = page(key, route, body, code, t)
            if code == 'ko':
                output[filename] = page(key, route, body, code, t, default=True)
        redirect = f'<!doctype html>\n<html lang="{code}"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><meta http-equiv="refresh" content="0; url=https://facet.kugora.ng/"><link rel="canonical" href="https://facet.kugora.ng/"><title>Facet</title></head><body><p><a href="https://facet.kugora.ng/">{t("redirect.facet")}</a></p></body></html>\n'
        output[f'{code}/Facet/index.html'] = redirect
        if code == 'ko':
            output['Facet/index.html'] = redirect
    output['robots.txt'] = f'User-agent: *\nAllow: /\nSitemap: {SITE}/sitemap.xml\n'
    urls = []
    for route in ('/', '/apps/', '/games/'):
        alternatives = ''.join(f'<xhtml:link rel="alternate" hreflang="{code}" href="{SITE}{path_for(code, route)}"/>' for code in CODES) + f'<xhtml:link rel="alternate" hreflang="x-default" href="{SITE}{route}"/>'
        for code in CODES:
            urls.append(f'  <url><loc>{SITE}{path_for(code, route)}</loc>{alternatives}</url>')
    output['sitemap.xml'] = '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" xmlns:xhtml="http://www.w3.org/1999/xhtml">\n' + '\n'.join(urls) + '\n</urlset>\n'
    return output


def build(check=False, output_dir=ROOT):
    output = output_files()
    outdated = []
    for name, content in output.items():
        path = output_dir / name
        if check:
            if not path.exists() or path.read_text() != content:
                outdated.append(name)
        else:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content)
    if outdated:
        raise SystemExit('Run python3 scripts/build.py; stale files: ' + ', '.join(outdated))
    print(f'{"Verified" if check else "Built"} {len(output)} files / {len(CODES)} languages.')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--check', action='store_true')
    args = parser.parse_args()
    build(args.check)
