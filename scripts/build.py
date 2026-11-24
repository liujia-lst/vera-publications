#!/usr/bin/env python3
"""Build the publications page with Python 3 (standard library only)."""
import csv,html,json,re,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
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
  if not isinstance(p.get('remarks',''),str):raise ValueError('Remarks must be plain text')
  if not isinstance(p.get('topics'),list) or not p['topics'] or not set(p['topics'])<=known:raise ValueError(f"{p['id']}: unknown or missing topic")
  for u in [p.get('paper_url','')]+[a['url'] for a in p.get('links',[])]:
   if not safe_url(u):raise ValueError(f"{p['id']}: invalid web URL")
 return True

def build():
 catalog=json.loads((ROOT/'data/catalog.json').read_text());pubs=catalog['publications'];topics=catalog['topics'];validate(pubs,topics)
 counts={t['id']:sum(t['id'] in p['topics'] for p in pubs) for t in topics};labels={t['id']:t['label'] for t in topics}
 filters=''.join(f'<label class="topic-option"><input type="checkbox" value="{esc(t["id"])}"><span>{esc(t["label"])}</span><span class="topic-count">{counts[t["id"]]}</span></label>' for t in topics)
 sections=[]
 for year in sorted({p['year'] for p in pubs},reverse=True):
  items=[]; subset=[p for p in pubs if p['year']==year]
  for p in subset:
   title=f'<a href="{esc(p["paper_url"])}">{esc(p["title"])}</a>' if p.get('paper_url') else esc(p['title'])
   badges=''.join(f'<button class="paper-topic" type="button" data-topic="{esc(t)}" aria-label="Show topic: {esc(labels[t])}">{esc(labels[t])}</button>' for t in p['topics'])
   urls=[];seen=set()
   if p.get('paper_url'):urls.append({'label':'Paper','url':p['paper_url']});seen.add(p['paper_url'])
   for link in p.get('links',[]):
    if link['url'] not in seen and 'award' not in link['label'].lower():urls.append(link);seen.add(link['url'])
   links=''.join(f'<a href="{esc(a["url"])}">{esc(a["label"])}</a>' for a in urls)
   remark=f'<p class="remarks {"award" if "award" in p.get("remarks","").lower() else ""}">{esc(p["remarks"])}</p>' if p.get('remarks') else ''
   items.append(f'<article class="publication" id="{esc(p["id"])}" data-year="{year}" data-topics="{esc(" ".join(p["topics"]))}"><h3>{title}</h3><p class="authors">{esc(p["authors"])}</p><p class="venue">{esc(p["venue"])}</p>{remark}<div class="paper-bottom"><div class="paper-topics">{badges}</div><div class="paper-links">{links}</div></div></article>')
  sections.append(f'<section class="year-section" aria-labelledby="year-{year}"><div class="year-heading"><h2 id="year-{year}">{year}</h2><span>{len(subset)} publications</span></div>{"".join(items)}</section>')
 template=(ROOT/'templates/index.html').read_text()
 year_options=''.join(f'<option value="{year}">{year}</option>' for year in sorted({p['year'] for p in pubs},reverse=True))
 for key,value in {'FILTERS':filters,'PUBLICATIONS':''.join(sections),'COUNT':str(len(pubs)),'YEAR_OPTIONS':year_options}.items():template=template.replace('{{'+key+'}}',value)
 (ROOT/'index.html').write_text(template)
 # One common data file for the offline-capable form; no fetch or hosted account needed.
 (ROOT/'assets/editor-data.js').write_text('window.publicationData = '+json.dumps({'publications':pubs,'topics':topics},ensure_ascii=False).replace('<','\\u003c')+';\n')
 with (ROOT/'data/publications.csv').open('w',newline='',encoding='utf-8-sig') as f:
  cols=['id','year','title','authors','venue','paper_url','remarks','topics'];writer=csv.DictWriter(f,fieldnames=cols);writer.writeheader()
  for p in pubs:writer.writerow({k:'; '.join(p[k]) if k=='topics' else p.get(k,'') for k in cols})
 with (ROOT/'data/topics.csv').open('w',newline='',encoding='utf-8-sig') as f:
  writer=csv.DictWriter(f,fieldnames=['id','label','status']);writer.writeheader();writer.writerows(topics)
 print(f'Built {len(pubs)} publications, {len(topics)} topics; all records validated.')
if __name__=='__main__':
 try:build()
 except (ValueError,KeyError,TypeError,json.JSONDecodeError) as e:print('Build failed:',e,file=sys.stderr);sys.exit(1)
