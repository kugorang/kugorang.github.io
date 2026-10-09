/* Static language URLs work without JavaScript. Unprefixed legacy URLs choose
   a saved preference, then the browser's first supported language, then English. */
(() => {
  const root = document.documentElement;
  const supported = root.dataset.supported.split(',');
  const key = 'hw.portfolio.language';
  const match = value => {
    if (typeof value !== 'string') return null;
    const lower = value.toLowerCase();
    return supported.find(code => code.toLowerCase() === lower) ||
      supported.find(code => code.split('-')[0].toLowerCase() === lower.split('-')[0]) || null;
  };
  const remember = code => { try { localStorage.setItem(key, code); } catch {} };
  const url = new URL(location.href);
  if (root.dataset.default === 'true') {
    let saved;
    try { saved = localStorage.getItem(key); } catch {}
    const preferred = match(url.searchParams.get('lang')) || match(saved) ||
      (navigator.languages || [navigator.language]).map(match).find(Boolean) || 'en';
    // The rendered 404 is also served at unknown paths by GitHub Pages.
    // Follow the locale in such a URL before consulting browser preferences.
    const pathLocale = match(url.pathname.split('/')[1]);
    const locale = pathLocale || preferred;
    const route = root.dataset.route;
    url.pathname = `/${locale}${route}`;
    url.searchParams.delete('lang');
    remember(locale);
    if (url.href !== location.href) location.replace(url.href);
  } else {
    remember(root.dataset.locale);
  }
  document.addEventListener('DOMContentLoaded', () => {
    for (const link of document.querySelectorAll('[data-language]')) {
      const target = new URL(link.href);
      target.search = url.search;
      target.searchParams.delete('lang');
      target.hash = url.hash;
      link.href = target.href;
      link.addEventListener('click', () => remember(link.dataset.language));
    }
    const picker = document.querySelector('.language-picker');
    picker?.addEventListener('keydown', event => {
      if (event.key === 'Escape') {
        picker.open = false;
        picker.querySelector('summary').focus();
      }
    });
  });
})();
