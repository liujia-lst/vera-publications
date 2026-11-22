#!/usr/bin/env python3
"""Optional Google Sheets adapter. Nothing runs until the owner configures it.
SHEET_PUBLICATIONS_CSV_URL and SHEET_TOPICS_CSV_URL must be published CSV URLs.
"""
import csv,io,json,os,sys
from urllib.request import Request,urlopen
from urllib.parse import urlparse
from build import ROOT
from import_csv import import_catalog

def download(name):
 url=os.environ.get(name,'');parsed=urlparse(url)
 if parsed.scheme!='https' or parsed.hostname!='docs.google.com' or not parsed.path.startswith('/spreadsheets/'):
  raise ValueError(name+' must be an HTTPS Google Sheets publication URL')
 with urlopen(Request(url,headers={'User-Agent':'PublicationsWebsite/1.0'}),timeout=30) as response:
  text=response.read(5_000_001)
  if len(text)>5_000_000:raise ValueError('CSV is too large')
  decoded=text.decode('utf-8-sig')
  if decoded.lstrip().startswith('<'):raise ValueError('Expected CSV; check publishing permissions and the export URL')
  return list(csv.DictReader(io.StringIO(decoded)))
if __name__=='__main__':
 try:
  old=json.loads((ROOT/'data/catalog.json').read_text())
  new=import_catalog(download('SHEET_PUBLICATIONS_CSV_URL'),download('SHEET_TOPICS_CSV_URL'),old)
  if len(new['publications'])<len(old['publications']) and os.environ.get('ALLOW_REMOVALS')!='true':
   raise ValueError('Record count decreased; check the sheet or explicitly allow removals')
  target=ROOT/'data/catalog.json';tmp=target.with_suffix('.tmp');tmp.write_text(json.dumps(new,ensure_ascii=False,indent=2)+'\n');tmp.replace(target)
  print('Imported',len(new['publications']),'publications from Sheets.')
 except Exception as e:sys.exit('Sheet sync failed; current published site stays unchanged: '+str(e))
