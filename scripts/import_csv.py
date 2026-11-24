#!/usr/bin/env python3
"""Import publications and topics from CSV; no external dependencies.
Usage: python scripts/import_csv.py publications.csv topics.csv
"""
import csv,hashlib,json,re,sys
from pathlib import Path
from build import ROOT,validate

def read_csv(path):
 with Path(path).open(newline='',encoding='utf-8-sig') as f:return list(csv.DictReader(f))
def import_catalog(publication_rows,topic_rows,existing):
 topics=[]
 for r in topic_rows:
  label=(r.get('label') or '').strip()
  if not label:continue
  ident=(r.get('id') or '').strip() or re.sub(r'[^a-z0-9]+','-',label.lower()).strip('-')
  if not re.match(r'^[a-z]',ident):ident='topic-'+ident
  topics.append({'id':ident,'label':label,'status':r.get('status') or 'Entered in spreadsheet'})
 lookup={}
 for t in topics:
  for k in [t['id'],t['label']]:
   if k.casefold() in lookup and lookup[k.casefold()]!=t['id']:raise ValueError('Duplicate topic label: '+k)
   lookup[k.casefold()]=t['id']
 old={p['id']:p for p in existing['publications']};pubs=[]
 for row_index,r in enumerate(publication_rows,2):
  if not any((v or '').strip() for v in r.values()):continue
  title=(r.get('title') or '').strip();year=int(r.get('year') or 0)
  ident=(r.get('id') or '').strip() or 'pub-'+hashlib.sha256((title.casefold()+'|'+str(year)).encode()).hexdigest()[:12]
  raw_tags=[t.strip() for t in re.split(r'[;,]',r.get('topics') or '') if t.strip()]
  try: tags=list(dict.fromkeys(lookup[t.casefold()] for t in raw_tags))
  except KeyError as e:raise ValueError(f'Row {row_index}: unknown topic {e.args[0]!r}; add it to the topics sheet first')
  p={**old.get(ident,{}),'id':ident,'year':year,'topics':tags,'topic_status':(r.get('topic_status') or 'spreadsheet-entry').strip()}
  p['publication_type']=(r.get('publication_type') or old.get(ident,{}).get('publication_type','')).strip().lower()
  for k in ['title','authors','venue','paper_url','remarks']:p[k]=(r.get(k) or '').strip()
  pubs.append(p)
 validate(pubs,topics)
 return {'publications':pubs,'topics':topics}
if __name__=='__main__':
 if len(sys.argv)!=3:sys.exit(__doc__)
 try:
  existing=json.loads((ROOT/'data/catalog.json').read_text());updated=import_catalog(read_csv(sys.argv[1]),read_csv(sys.argv[2]),existing)
  target=ROOT/'data/catalog.json';tmp=target.with_suffix('.tmp');tmp.write_text(json.dumps(updated,ensure_ascii=False,indent=2)+'\n');tmp.replace(target)
  print('Imported',len(updated['publications']),'publications. Run scripts/build.py next.')
 except (ValueError,KeyError,TypeError) as e:sys.exit('Import failed; existing data was not changed: '+str(e))
