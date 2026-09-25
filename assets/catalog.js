(() => {
  const catalog = document.querySelector('[data-catalog]');
  if (!catalog) return;
  const tools = catalog.querySelector('.catalog-tools');
  const input = tools.querySelector('input');
  const filters = [...tools.querySelectorAll('[data-filter]')];
  const cards = [...catalog.querySelectorAll('[data-project]')];
  const empty = catalog.querySelector('.empty-state');
  const count = catalog.querySelector('[data-result-count]');
  let tag = '';
  const normalize = value => value.normalize('NFKC').toLocaleLowerCase().trim();
  function update() {
    const words = normalize(input.value).split(/\s+/).filter(Boolean);
    let visible = 0;
    for (const card of cards) {
      const matches = (!tag || card.dataset.tag === tag) && words.every(word => normalize(card.dataset.search).includes(word));
      card.hidden = !matches;
      if (matches) visible++;
    }
    count.textContent = `${visible}개의 작업${visible === cards.length ? '' : ` / 전체 ${cards.length}개`}`;
    empty.hidden = visible !== 0;
    for (const button of filters) button.setAttribute('aria-pressed', String(button.dataset.filter === tag));
  }
  input.addEventListener('input', update);
  for (const button of filters) button.addEventListener('click', () => { tag = button.dataset.filter; update(); });
  catalog.querySelector('[data-reset]').addEventListener('click', () => { tag = ''; input.value = ''; update(); input.focus(); });
  tools.hidden = false;
})();
