(() => {
  'use strict';
  const checks = Array.from(document.querySelectorAll('.topic-option input'));
  const articles = Array.from(document.querySelectorAll('.publication'));
  const sections = Array.from(document.querySelectorAll('.year-section'));
  const reset = document.querySelector('#clear-topics');
  const result = document.querySelector('#result-count');
  const valid = new Set(checks.map(c => c.value));
  function apply(fromHash = false) {
    if (fromHash) {
      const params = new URLSearchParams(location.hash.slice(1));
      const active = new Set((params.get('topic') || '').split(',').filter(t => valid.has(t)));
      checks.forEach(c => { c.checked = active.has(c.value); });
    }
    const selected = checks.filter(c => c.checked).map(c => c.value);
    let count = 0;
    for (const paper of articles) {
      const tags = paper.dataset.topics.split(' ');
      const visible = !selected.length || selected.some(t => tags.includes(t));
      paper.hidden = !visible;
      if (visible) count++;
    }
    for (const section of sections) {
      const n = Array.from(section.querySelectorAll('.publication')).filter(p => !p.hidden).length;
      section.hidden = n === 0;
      section.querySelector('.year-heading span').textContent = `${n} publication${n === 1 ? '' : 's'}`;
    }
    reset.setAttribute('aria-pressed', String(!selected.length));
    result.textContent = selected.length ? `Showing ${count} of ${articles.length} publications` : `Showing all ${articles.length} publications`;
    document.querySelector('#empty-state').hidden = count !== 0;
    if (!fromHash) {
      const url = location.pathname + location.search + (selected.length ? '#topic=' + selected.join(',') : '');
      history.pushState(null, '', url);
    }
  }
  checks.forEach(c => c.addEventListener('change', () => apply()));
  reset.addEventListener('click', () => { checks.forEach(c => { c.checked = false; }); apply(); });
  document.querySelectorAll('.paper-topic').forEach(b => b.addEventListener('click', () => {
    checks.forEach(c => { c.checked = c.value === b.dataset.topic; });
    apply(); document.querySelector('#results').focus();
    document.querySelector('.results-heading').scrollIntoView({behavior:'auto',block:'start'});
  }));
  window.addEventListener('popstate', () => apply(true));
  window.addEventListener('hashchange', () => apply(true));
  apply(true);
})();
