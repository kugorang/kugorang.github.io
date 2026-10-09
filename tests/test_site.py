import importlib.util
import json
import re
import unittest
import xml.etree.ElementTree as ET
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('portfolio_build', ROOT / 'scripts/build.py')
build = importlib.util.module_from_spec(spec)
spec.loader.exec_module(build)


class Document(HTMLParser):
    def __init__(self, source):
        super().__init__(convert_charrefs=True)
        self.elements = []
        self.ids = []
        self.feed(source)

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        self.elements.append((tag, attrs))
        if 'id' in attrs:
            self.ids.append(attrs['id'])

    def attrs(self, tag, **attributes):
        return [a for t, a in self.elements if t == tag and all(a.get(k) == v for k, v in attributes.items())]


class PortfolioContract(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.output = build.output_files()
        cls.texts = build.translations()

    def test_exact_runtime_language_union(self):
        self.assertEqual(build.CODES, ['ko', 'en', 'ja', 'de', 'fr', 'es', 'pt-BR'])
        self.assertEqual(len(self.texts['ko']), 108)

    def test_source_messages_and_catalog_remain_consistent(self):
        for item in build.catalog():
            for field in ('headline', 'description'):
                self.assertEqual(item[field], self.texts['ko'][item['id'] + '.' + field])

    def test_missing_translation_fails_instead_of_falling_back(self):
        with self.assertRaises(KeyError):
            build.Copy(self.texts['en'])('absent.key')

    def test_pages_seo_navigation_and_accessibility(self):
        for code in build.CODES:
            for page, route in build.ROUTES.items():
                with self.subTest(code=code, page=page):
                    file = f'{code}{route}';file = file.rstrip('/') + '/index.html' if route.endswith('/') else file
                    source = self.output[file]
                    doc = Document(source)
                    self.assertEqual(doc.attrs('html')[0]['lang'], code)
                    self.assertEqual(doc.attrs('link', rel='canonical')[0]['href'], build.SITE + build.path_for(code, route))
                    alt = doc.attrs('link', rel='alternate')
                    self.assertEqual({a['hreflang'] for a in alt}, set(build.CODES) | {'x-default'})
                    self.assertEqual(len(alt), 8)
                    self.assertEqual(len(doc.ids), len(set(doc.ids)))
                    for a in alt:
                        if a['hreflang'] != 'x-default':
                            target = a['href'].removeprefix(build.SITE).lstrip('/')
                            if target.endswith('/'): target += 'index.html'
                            self.assertIn(target, self.output)
                    for _, attrs in doc.elements:
                        for name in ('aria-controls', 'aria-describedby', 'aria-labelledby'):
                            for target in attrs.get(name, '').split(): self.assertIn(target, doc.ids)
                    for image in doc.attrs('img'): self.assertTrue(image['alt'])
                    if page != '404':
                        self.assertEqual(len(doc.attrs('a', **{'aria-current': 'page'})), 1)
                    if code not in ('ko','ja'):
                        # Established Korean brand names may remain; Korean prose may not.
                        cleaned = source
                        for name in ('한국어','필데이','달빛 고물상','오선로','일정','퍼즐','스토리','리듬'):
                            cleaned = cleaned.replace(name, '')
                        self.assertIsNone(re.search('[가-힣]', cleaned))

    def test_featured_and_development_preservation(self):
        items = build.catalog()
        self.assertEqual([x['id'] for x in items if x['featured']], ['fillday', 'facet'])
        self.assertEqual([x['id'] for x in items if x['status'] == 'released'], ['fillday'])
        for code in build.CODES:
            home = self.output[f'{code}/index.html']
            games = self.output[f'{code}/games/index.html']
            self.assertNotIn('moonjunk-description', home)
            for id in ('facet','moonjunk','oseonro'): self.assertIn(f'id="{id}-description"', games)
            self.assertNotIn('store-link"', games)
            doc = Document(home)
            stores = doc.attrs('a', **{'class':'button button-outline store-link'})
            self.assertEqual(len(stores), 2)
            self.assertEqual(stores[0]['href'], 'https://apps.apple.com/app/id6797272470')
            self.assertEqual(stores[1]['href'], 'https://play.google.com/store/apps/details?id=com.kugorang.fillday')

    def test_install_links_reject_unreleased_projects(self):
        data = json.loads((ROOT / 'data/projects.json').read_text())
        data[0]['status'] = 'development'
        from unittest.mock import patch
        actual_read = Path.read_text
        def fake_read(path, *args, **kwargs):
            if path == ROOT / 'data/projects.json': return json.dumps(data)
            return actual_read(path, *args, **kwargs)
        with patch.object(Path, 'read_text', fake_read), self.assertRaisesRegex(ValueError, 'Unreleased'):
            build.catalog()

    def test_sitemap_uses_reciprocal_language_links(self):
        root = ET.fromstring(self.output['sitemap.xml'])
        self.assertEqual(len(root), 21)
        for entry in root:
            self.assertEqual(len(entry), 9)
        self.assertNotIn('/404.html', self.output['sitemap.xml'])

    def test_legacy_facet_destination_is_preserved(self):
        for path, text in self.output.items():
            if '/Facet/' in path or path == 'Facet/index.html':
                self.assertIn('url=https://facet.kugora.ng/', text)
                self.assertIn('href="https://facet.kugora.ng/"', text)


if __name__ == '__main__':
    unittest.main()
