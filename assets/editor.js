(() => {
  'use strict';
  const clone = x => JSON.parse(JSON.stringify(x));
  let catalog = clone(window.publicationData), editing = '';
  const key = 'demberg-publications-draft-v1';
  const form = document.querySelector('#paper-form');
  const chooser = document.querySelector('#paper-select');
  const status = document.querySelector('#editor-status');
  let dirty = false;
  const say = (s, error = false) => { status.textContent = s; status.className = error ? 'error' : ''; };
  const validURL = s => { if (!s) return true; try { const u = new URL(s); return ['https:','http:'].includes(u.protocol); } catch { return false; } };
  function valid(data) {
    if (!data || !Array.isArray(data.publications) || !data.publications.length || !Array.isArray(data.topics) || !data.topics.length) return false;
    const ids = new Set(data.topics.map(t => t.id));
    return ids.size === data.topics.length && data.topics.every(t => /^[a-z][a-z0-9-]*$/.test(t.id) && typeof t.label === 'string' && t.label.trim()) &&
      new Set(data.publications.map(p => p.id)).size === data.publications.length && data.publications.every(p =>
        /^[a-zA-Z0-9-]+$/.test(p.id) && ['title','authors','venue'].every(k => typeof p[k] === 'string' && p[k].trim()) &&
        Number.isInteger(p.year) && p.year >= 1900 && p.year <= 2100 && Array.isArray(p.topics) && p.topics.length && p.topics.every(t => ids.has(t)) && validURL(p.paper_url) &&
        (!p.links || (Array.isArray(p.links) && p.links.every(a => typeof a.label === 'string' && validURL(a.url)))));
  }
  function persist(message) {
    try { localStorage.setItem(key, JSON.stringify(catalog)); say(message); }
    catch { say(message + ' Browser storage is unavailable; download the updated data before closing.'); }
  }
  function choices() {
    chooser.replaceChildren(new Option('New publication', ''));
    [...catalog.publications].sort((a,b) => b.year-a.year).forEach(p => chooser.add(new Option(`${p.year} · ${p.title}`,p.id)));
    chooser.value = editing;
  }
  function topicInputs(selected = []) {
    const root = document.querySelector('#editor-topic-list'); root.replaceChildren();
    catalog.topics.forEach(t => {
      const label = document.createElement('label'), input = document.createElement('input');
      input.type = 'checkbox'; input.name = 'topics'; input.value = t.id; input.checked = selected.includes(t.id);
      label.append(input, document.createTextNode(t.label)); root.append(label);
    });
  }
  function load(id) {
    editing = id; form.reset(); const paper = catalog.publications.find(p => p.id === id);
    for (const field of ['title','authors','venue','year','paper_url','remarks']) form.elements.namedItem(field).value = paper ? (paper[field] || '') : field === 'year' ? new Date().getFullYear() : '';
    topicInputs(paper?.topics || []); choices(); dirty = false;
  }
  function maySwitch() { return !dirty || confirm('Discard the changes currently in the form? Saved drafts will remain.'); }
  try { const saved = JSON.parse(localStorage.getItem(key)); if (valid(saved)) { catalog = saved; say('Your previous browser draft has been restored. Open a current catalog.json to replace it.'); } } catch { /* File-mode storage may be unavailable. */ }
  load('');
  form.addEventListener('input', () => { dirty = true; });
  chooser.addEventListener('change', () => { const id = chooser.value; if(maySwitch()) load(id); else chooser.value = editing; });
  document.querySelector('#new-paper').addEventListener('click', () => { if(maySwitch()) { load(''); form.elements.namedItem('title').focus(); } });
  document.querySelector('#add-topic').addEventListener('click', () => {
    const name = document.querySelector('#new-topic-name'), label = name.value.trim();
    if (!label) { say('Enter a topic name first.',true); name.focus(); return; }
    if (catalog.topics.some(t => t.label.toLowerCase() === label.toLowerCase())) { say('That topic already exists. Select it below.',true); return; }
    let id = label.normalize('NFD').replace(/[\u0300-\u036f]/g,'').toLowerCase().replace(/[^a-z0-9]+/g,'-').replace(/^-|-$/g,'');
    if (!/^[a-z]/.test(id)) id = 'topic-' + id;
    const base=id; let n=2; while(catalog.topics.some(t=>t.id===id)) id=base+'-'+n++;
    const selected = Array.from(form.querySelectorAll('[name=topics]:checked')).map(i=>i.value);
    catalog.topics.push({id,label,status:'Added by editor'}); topicInputs([...selected,id]); name.value=''; dirty=true;
    persist(`Topic “${label}” added to this draft. Save the publication to assign it.`);
  });
  form.addEventListener('submit', event => {
    event.preventDefault(); const data = new FormData(form), tags = data.getAll('topics');
    if (!tags.length) { say('Select at least one topic.',true); return; }
    const old = catalog.publications.find(p=>p.id===editing);
    let id=editing || 'pub-'+Date.now().toString(36);while(!old && catalog.publications.some(p=>p.id===id)) id+='x';
    const paper = {...old,id,year:Number(data.get('year')),topics:tags,topic_status:'editor-reviewed'};
    for (const field of ['title','authors','venue','paper_url','remarks']) paper[field] = String(data.get(field)||'').trim();
    if (!validURL(paper.paper_url)) { say('Use an http:// or https:// paper URL.',true);return; }
    if (old) catalog.publications[catalog.publications.findIndex(p=>p.id===id)] = paper; else catalog.publications.push(paper);
    dirty=false;editing=id;choices();persist(`Saved to your browser draft. ${catalog.publications.length} publications. Download the updated data to publish.`);
  });
  document.querySelector('#export-data').addEventListener('click', () => {
    if (dirty) { say('Save the current publication before downloading.',true);return; }
    if (!valid(catalog)) { say('The collection contains invalid data. Open a valid catalog.json.',true);return; }
    const blob = new Blob([JSON.stringify(catalog,null,2)+'\n'],{type:'application/json'}), url=URL.createObjectURL(blob), a=document.createElement('a');
    a.href=url;a.download='catalog.json';a.click();setTimeout(()=>URL.revokeObjectURL(url),1000);
    say('Download started. Upload catalog.json into the GitHub repository’s data folder to update the website.');
  });
  document.querySelector('#import-data').addEventListener('change', async event => {
    const input=event.target, file=input.files[0];if(!file)return;
    try {
      if (!maySwitch()) return;
      const parsed=JSON.parse(await file.text());if(!valid(parsed))throw new Error('Invalid collection');
      catalog=parsed;load('');persist(`Opened ${catalog.publications.length} publications and ${catalog.topics.length} topics.`);
    } catch { say('Could not open this file. Choose a valid catalog.json exported by this editor.',true); }
    finally { input.value=''; }
  });
  window.addEventListener('beforeunload',event=>{if(dirty){event.preventDefault();event.returnValue='';}});
})();
