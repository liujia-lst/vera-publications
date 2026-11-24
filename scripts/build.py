#!/usr/bin/env python3
"""Build the publications page with Python 3 (standard library only)."""
import csv,html,json,re,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
PUBLICATION_TYPES={'journal':'Journal','conference':'Conference','workshop':'Workshop','preprint':'Preprint','other':'Other'}
MEDAL='<svg class="award-medal" viewBox="0 0 24 28" aria-hidden="true" focusable="false"><path d="M4 1h6l4 11-5 3z" fill="#326b92"/><path d="M14 1h6l-5 14-5-3z" fill="#6294b5"/><circle cx="12" cy="18" r="8" fill="#e9bd59" stroke="#9b6c18"/><path d="m12 13 1.4 2.8 3.1.5-2.2 2.2.5 3.1-2.8-1.5-2.8 1.5.5-3.1L7.5 16.3l3.1-.5z" fill="#fff4cc"/></svg>'
def esc(s):return html.escape(str(s),quote=True)
def safe_url(s):
 return not s or bool(re.match(r'^https?://[^\s<>"\x00-\x1f]+$',s))
def validate(pubs,topics):
 ids=set(); known={t['id'] for t in topics}
 if len(known)!=len(topics):raise ValueError('Duplicate topic identifiers')
 for t in topics:
  if not re.fullmatch(r'[a-z][a-z0-9-]*',t['id']) or not t['label'].strip():raise ValueError('Invalid topic identifier or label')
 if not pubs:raise ValueError('No publications; refusing to publish an empty list')
 for p in pubs:
  if p['id'] in ids:raise ValueError('Duplicate publication ID: '+p['id'])
  ids.add(p['id'])
  for field in ['id','title','authors','venue']:
   if not isinstance(p.get(field),str) or not p[field].strip():raise ValueError(f"{p['id']}: missing {field}")
  if not re.fullmatch(r'[a-zA-Z0-9-]+',p['id']):raise ValueError('Invalid publication ID')
  if type(p['year']) is not int or not 1900<=p['year']<=2100:raise ValueError('Invalid year')
  if p.get('publication_type') not in PUBLICATION_TYPES:raise ValueError(f"{p['id']}: invalid publication type")
  if not isinstance(p.get('remarks',''),str):raise ValueError('Remarks must be plain text')
  if not isinstance(p.get('topics'),list) or not p['topics'] or not set(p['topics'])<=known:raise ValueError(f"{p['id']}: unknown or missing topic")
  for u in [p.get('paper_url','')]+[a['url'] for a in p.get('links',[])]:
   if not safe_url(u):raise ValueError(f"{p['id']}: invalid web URL")
 return True

def display_links(p):
 # Keep one paper destination; PDF, DOI and arXiv are versions of the same paper.
 paper_url=p.get('paper_url','')
 links=[{'label':'Paper','url':paper_url}] if paper_url else []
 seen={paper_url}
 for link in p.get('links',[]):
  if link['label'].lower()=='project' and link['url'] not in seen:
   links.append({'label':'Project','url':link['url']});seen.add(link['url'])
 return links

def build():
 catalog=json.loads((ROOT/'data/catalog.json').read_text());pubs=catalog['publications'];topics=catalog['topics'];validate(pubs,topics)
 counts={t['id']:sum(t['id'] in p['topics'] for p in pubs) for t in topics};labels={t['id']:t['label'] for t in topics}
 filters=''.join(f'<label class="topic-option"><input type="checkbox" name="topic" value="{esc(t["id"])}"><span>{esc(t["label"])}</span><span class="topic-count">{counts[t["id"]]}</span></label>' for t in topics)
 type_filters=''.join(f'<label class="type-option"><input type="checkbox" name="publication_type" value="{key}"><span>{label}</span></label>' for key,label in PUBLICATION_TYPES.items())
 sections=[]
 for year in sorted({p['year'] for p in pubs},reverse=True):
  items=[]; subset=[p for p in pubs if p['year']==year]
  for p in subset:
   title=esc(p['title'])
   badges=''.join(f'<button class="paper-topic" type="button" data-topic="{esc(t)}" aria-label="Show topic: {esc(labels[t])}">{esc(labels[t])}</button>' for t in p['topics'])
   kind=p['publication_type'];type_badge=f'<button class="paper-type" type="button" data-type="{kind}" aria-label="Show publication type: {PUBLICATION_TYPES[kind]}">{PUBLICATION_TYPES[kind]}</button>'
   links=''.join(f'<a href="{esc(a["url"])}" aria-label="{esc(a["label"]+": "+p["title"])}">{esc(a["label"])}</a>' for a in display_links(p))
   award=bool(re.search(r'\bbest\b[^.!()]*\bpaper\b[^.!()]*\baward\b',p.get('remarks',''),re.I))
   remark=f'<p class="remarks {"award" if "award" in p.get("remarks","").lower() else ""}">{MEDAL if award else ""}<span>{esc(p["remarks"])}</span></p>' if p.get('remarks') else ''
   items.append(f'<article class="publication" id="{esc(p["id"])}" data-year="{year}" data-type="{kind}" data-topics="{esc(" ".join(p["topics"]))}"><div class="publication-main"><h3>{title}</h3><p class="authors">{esc(p["authors"])}</p><p class="venue">{esc(p["venue"])}</p>{remark}<div class="paper-tags"><div class="paper-topics">{badges}</div>{type_badge}</div></div><div class="paper-links">{links}</div></article>')
  sections.append(f'<section class="year-section" aria-labelledby="year-{year}"><div class="year-heading"><h2 id="year-{year}">{year}</h2><span>{len(subset)} publications</span></div>{"".join(items)}</section>')
 template=(ROOT/'templates/index.html').read_text()
 year_options=''.join(f'<option value="{year}">{year}</option>' for year in sorted({p['year'] for p in pubs},reverse=True))
 for key,value in {'FILTERS':filters,'TYPE_FILTERS':type_filters,'PUBLICATIONS':''.join(sections),'COUNT':str(len(pubs)),'YEAR_OPTIONS':year_options}.items():template=template.replace('{{'+key+'}}',value)
 (ROOT/'index.html').write_text(template)
 # One common data file for the offline-capable form; no fetch or hosted account needed.
 (ROOT/'assets/editor-data.js').write_text('window.publicationData = '+json.dumps({'publications':pubs,'topics':topics},ensure_ascii=False).replace('<','\\u003c')+';\n')
 with (ROOT/'data/publications.csv').open('w',newline='',encoding='utf-8-sig') as f:
  cols=['id','year','title','authors','venue','publication_type','paper_url','remarks','topics'];writer=csv.DictWriter(f,fieldnames=cols);writer.writeheader()
  for p in pubs:writer.writerow({k:'; '.join(p[k]) if k=='topics' else p.get(k,'') for k in cols})
 with (ROOT/'data/topics.csv').open('w',newline='',encoding='utf-8-sig') as f:
  writer=csv.DictWriter(f,fieldnames=['id','label','status']);writer.writeheader();writer.writerows(topics)
 print(f'Built {len(pubs)} publications, {len(topics)} topics; all records validated.')
if __name__=='__main__':
 try:build()
 except (ValueError,KeyError,TypeError,json.JSONDecodeError) as e:print('Build failed:',e,file=sys.stderr);sys.exit(1)
