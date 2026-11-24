const fs = require('node:fs'), vm = require('node:vm'), assert = require('node:assert/strict');
const root = require('node:path').resolve(__dirname, '..');
const catalog = JSON.parse(fs.readFileSync(root + '/data/catalog.json', 'utf8'));
const element = (props = {}) => ({...props, handlers: {}, addEventListener(k, f) { this.handlers[k] = f; }, setAttribute(k, v) { this[k] = v; }});
const checks = catalog.topics.map(t => element({value: t.id, checked: false}));
const typeChecks = ['journal','conference','workshop','preprint','other'].map(value => element({value, checked: false}));
const articles = catalog.publications.map(p => element({id: p.id, dataset: {topics: p.topics.join(' '), year: String(p.year), type: p.publication_type}, hidden: false}));
const years = [...new Set(catalog.publications.map(p => String(p.year)))];
const sections = years.map(year => ({hidden: false, counter: {}, querySelectorAll() { return articles.filter(a => a.dataset.year === year); }, querySelector() { return this.counter; }}));
const year = element({value: '', options: ['', ...years].map(value => ({value}))});
const reset = element(), result = {}, empty = {}, focus = {focus() {}, scrollIntoView() {}};
const badge = element({dataset: {topic: 'speech'}});
const typeBadge = element({dataset: {type: 'conference'}});
const document = {querySelectorAll(s) { return {'.topic-option input': checks, '.type-option input': typeChecks, '.paper-type': [typeBadge], '.publication': articles, '.year-section': sections, '.paper-topic': [badge]}[s]; }, querySelector(s) { return {'#year-filter': year, '#clear-topics': reset, '#result-count': result, '#empty-state': empty, '#results': focus, '.results-heading': focus}[s]; }};
const location = {hash: '', pathname: '/vera-publications/', search: ''}, events = {}, history = [];
vm.runInNewContext(fs.readFileSync(root + '/assets/filters.js', 'utf8'), {document, location, URLSearchParams, history: {pushState(a, b, url) { history.push(url); location.hash = url.includes('#') ? '#' + url.split('#')[1] : ''; }}, window: {addEventListener(k, f) { events[k] = f; }}});
const visibleIds = () => articles.filter(a => !a.hidden).map(a => a.id).sort();
const verify = (tags = [], selectedYear = '', types = []) => {
 const expected = catalog.publications.filter(p => (!selectedYear || String(p.year) === selectedYear) && (!tags.length || tags.some(t => p.topics.includes(t))) && (!types.length || types.includes(p.publication_type)));
 assert.deepEqual(visibleIds(), expected.map(p => p.id).sort());
 assert.equal(empty.hidden, expected.length !== 0);
 assert.equal(result.textContent, `${expected.length} publication${expected.length === 1 ? '' : 's'}`);
 assert.equal(sections.filter(s => !s.hidden).length, new Set(expected.map(p => p.year)).size);
};
verify();
for (const t of catalog.topics) for (const y of ['', ...years]) {
 checks.forEach(c => c.checked = c.value === t.id); year.value = y; year.handlers.change(); verify([t.id], y);
 assert.equal(new URLSearchParams(location.hash.slice(1)).get('year') || '', y);
}
checks.forEach(c => c.checked = ['discourse', 'gestures'].includes(c.value)); year.value = '2025'; checks[0].handlers.change(); verify(['discourse', 'gestures'], '2025');
location.hash = '#topic=speech&year=2013'; events.popstate(); verify(['speech'], '2013'); assert.equal(year.value, '2013');
location.hash = '#topic=other&year=2027'; events.hashchange(); verify(['other'], '2027'); assert.equal(empty.hidden, false);
location.hash = '#topic=gestures,unknown&year=not-a-year'; events.hashchange(); verify(['gestures']); assert.equal(year.value, '');
year.value = '2013'; year.handlers.change(); badge.handlers.click(); verify(['speech'], '2013');
reset.handlers.click(); verify(); assert.equal(year.value, ''); assert.equal(location.hash, ''); assert.equal(reset['aria-pressed'], 'true');
for (const kind of typeChecks) for (const topic of ['', ...catalog.topics.map(t => t.id)]) for (const y of ['', ...years]) {
 typeChecks.forEach(c => c.checked = c.value === kind.value); checks.forEach(c => c.checked = c.value === topic); year.value = y;
 kind.handlers.change(); verify(topic ? [topic] : [], y, [kind.value]);
}
reset.handlers.click();
typeChecks.forEach(c => c.checked = ['journal','conference'].includes(c.value)); typeChecks[0].handlers.change(); verify([], '', ['journal','conference']);
location.hash = '#topic=discourse&type=workshop&year=2023'; events.popstate(); verify(['discourse'], '2023', ['workshop']);
location.hash = '#type=preprint&year=2027'; events.hashchange(); verify([], '2027', ['preprint']); assert.equal(empty.hidden, false);
location.hash = '#type=invalid&year=2022'; events.hashchange(); verify([], '2022');
typeBadge.handlers.click(); verify([], '2022', ['conference']);
reset.handlers.click(); verify(); assert(typeChecks.every(c => !c.checked)); assert.equal(location.hash, '');
const historySize = history.length; reset.handlers.click(); assert.equal(history.length, historySize);
console.log('PASS: every topic/type/year combination, topic and type unions, empty results, URL/history restoration, invalid filters, topic and type badges, and reset.');
