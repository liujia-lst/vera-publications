(() => {
  'use strict';
  const checks = Array.from(document.querySelectorAll('.topic-option input'));
  const articles = Array.from(document.querySelectorAll('.publication'));
  const sections = Array.from(document.querySelectorAll('.year-section'));
  const reset = document.querySelector('#clear-topics');
  const result = document.querySelector('#result-count');
  const yearFilter = document.querySelector('#year-filter');
  const years = new Set(Array.from(yearFilter.options, option => option.value));
  const valid = new Set(checks.map(c => c.value));
  function apply(fromHash = false) {
    if (fromHash) {
      const params = new URLSearchParams(location.hash.slice(1));
      const active = new Set((params.get('topic') || '').split(',').filter(t => valid.has(t)));
      checks.forEach(c => { c.checked = active.has(c.value); });
      yearFilter.value = years.has(params.get('year')) ? params.get('year') : '';
    }
    const selected = checks.filter(c => c.checked).map(c => c.value);
    const year = yearFilter.value;
    let count = 0;
    for (const paper of articles) {
      const tags = paper.dataset.topics.split(' ');
      const visible = (!year || paper.dataset.year === year) &&
        (!selected.length || selected.some(t => tags.includes(t)));
      paper.hidden = !visible;
      if (visible) count++;
    }
    for (const section of sections) {
      const n = Array.from(section.querySelectorAll('.publication')).filter(p => !p.hidden).length;
      section.hidden = n === 0;
      section.querySelector('.year-heading span').textContent = `${n} publication${n === 1 ? '' : 's'}`;
    }
    reset.setAttribute('aria-pressed', String(!selected.length && !year));
    result.textContent = `${count} publication${count === 1 ? '' : 's'}`;
    document.querySelector('#empty-state').hidden = count !== 0;
    if (!fromHash) {
      const params = new URLSearchParams();
      if (selected.length) params.set('topic', selected.join(','));
      if (year) params.set('year', year);
      const hash = params.size ? '#' + params.toString() : '';
      if (location.hash !== hash) history.pushState(null, '', location.pathname + location.search + hash);
    }
  }
  checks.forEach(c => c.addEventListener('change', () => apply()));
  yearFilter.addEventListener('change', () => apply());
  reset.addEventListener('click', () => { checks.forEach(c => { c.checked = false; }); yearFilter.value = ''; apply(); });
  document.querySelectorAll('.paper-topic').forEach(b => b.addEventListener('click', () => {
    checks.forEach(c => { c.checked = c.value === b.dataset.topic; });
    apply(); document.querySelector('#results').focus();
    document.querySelector('.results-heading').scrollIntoView({behavior:'auto',block:'start'});
  }));
  window.addEventListener('popstate', () => apply(true));
  window.addEventListener('hashchange', () => apply(true));
  apply(true);
})();
